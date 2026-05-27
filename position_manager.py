import paper_trading
import asyncio,logging,uuid,time,traceback
from datetime import datetime,timezone
from typing import Optional
log=logging.getLogger("positions")

def _utcnow_iso():
    """Naive UTC ISO string (replaces deprecated datetime.utcnow().isoformat())."""
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
def _utcnow():
    """Naive UTC datetime (replaces deprecated datetime.utcnow())."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class PositionManager:
    def __init__(self,bitget,cfg,memory,judge,rl=None,data=None):
        self.bitget=bitget; self.cfg=cfg; self.memory=memory; self.judge=judge; self.rl=rl
        self.data=data  # DataEngine, optional — used for correlation checks
        self.open_trades={}
        self._peak_pnl={}
        # Serializes open_position so concurrent scan paths can't bypass
        # correlation/same-side gates between check and insertion (TOCTOU).
        self._open_lock=asyncio.Lock()
    async def setup(self):
        """Async restore of positions on startup. Dispatches paper vs live."""
        if getattr(self.cfg,"PAPER_MODE",False):
            self._restore_paper_state()
        else:
            await self._restore_live_state()
    async def _restore_live_state(self):
        try:
            positions=await self.bitget.get_positions() or []
            if not positions:
                log.info("live: no open positions on Bitget"); return
            from memory import TradeMemory
            for p in positions:
                symbol=p.get("symbol")
                if not symbol: continue
                side=p.get("holdSide") or p.get("posSide") or "long"
                if side not in ("long","short"): side="long"
                try: entry_price=float(p.get("openPriceAvg") or p.get("averageOpenPrice") or p.get("markPrice") or 0)
                except: entry_price=0.0
                if entry_price<=0:
                    log.warning("live restore: skipping "+symbol+", no entry price"); continue
                matches=[t for t in self.memory.trades if t.symbol==symbol and t.side==side and t.outcome=="open"]
                existing=max(matches,key=lambda t:t.opened_at) if matches else None
                if existing:
                    self.open_trades[symbol]=existing; continue
                log.warning("Synthesizing TradeMemory for live orphan: "+symbol+" "+side+" @"+str(entry_price))
                t=TradeMemory(
                    id=str(uuid.uuid4()),symbol=symbol,side=side,
                    entry_price=entry_price,exit_price=None,pnl_pct=None,
                    regime="unknown",rsi_at_entry=0.0,funding_at_entry=0.0,
                    volume_ratio_at_entry=0.0,bull_confidence=0,bear_confidence=0,
                    judge_confidence=0,judge_reasoning="restored from live positions",
                    outcome="open",opened_at=_utcnow_iso(),
                    closed_at=None,lessons=None,orphan=True)
                self.memory.add_trade(t); self.open_trades[symbol]=t
            longs=sum(1 for t in self.open_trades.values() if t.side=="long")
            shorts=sum(1 for t in self.open_trades.values() if t.side=="short")
            log.info("Restored "+str(len(self.open_trades))+" live positions ("+str(longs)+"L/"+str(shorts)+"S)")
        except Exception as e:
            log.error("Live restore: "+str(e)); log.error(traceback.format_exc())
    def _restore_paper_state(self):
        try:
            state=paper_trading._load_state()
            positions=state.get("positions",{})
            if not positions:
                log.info("paper_state: no open positions to restore"); return
            from memory import TradeMemory
            for symbol,p in positions.items():
                matches=[t for t in self.memory.trades if t.symbol==symbol and t.side==p["side"] and t.outcome=="open"]
                existing=max(matches,key=lambda t:t.opened_at) if matches else None
                if existing:
                    self.open_trades[symbol]=existing; continue
                log.warning("Synthesizing TradeMemory for orphan: "+symbol+" "+p["side"]+" @"+str(p["entry_price"]))
                t=TradeMemory(
                    id=str(uuid.uuid4()),symbol=symbol,side=p["side"],
                    entry_price=p["entry_price"],exit_price=None,pnl_pct=None,
                    regime="unknown",rsi_at_entry=0.0,funding_at_entry=0.0,
                    volume_ratio_at_entry=0.0,bull_confidence=0,bear_confidence=0,
                    judge_confidence=p.get("confidence",0),
                    judge_reasoning="restored from paper_state",outcome="open",
                    opened_at=p.get("opened_at",_utcnow_iso()),
                    closed_at=None,lessons=None,orphan=True)
                self.memory.add_trade(t); self.open_trades[symbol]=t
            longs=sum(1 for t in self.open_trades.values() if t.side=="long")
            shorts=sum(1 for t in self.open_trades.values() if t.side=="short")
            log.info("Restored "+str(len(self.open_trades))+" positions from paper_state ("+str(longs)+"L/"+str(shorts)+"S)")
        except Exception as e:
            log.error("Restore: "+str(e)); log.error(traceback.format_exc())
    async def open_position(self,symbol,decision,snapshot):
        async with self._open_lock:
            return await self._open_position_inner(symbol,decision,snapshot)
    async def _open_position_inner(self,symbol,decision,snapshot):
        from memory import TradeMemory
        if self.cfg.PAPER_MODE:
            ps=paper_trading._load_state()
            open_syms=set(ps["positions"].keys()) | set(self.open_trades.keys())
            open_sides=[p["side"] for p in ps["positions"].values()]+[t.side for s,t in self.open_trades.items() if s not in ps["positions"]]
        else:
            open_syms=set(self.open_trades.keys())
            open_sides=[t.side for t in self.open_trades.values()]
        if symbol in open_syms: log.info("Already in "+symbol); return None
        # Динамический лимит позиций по балансу
        balance=ps["balance"] if self.cfg.PAPER_MODE else (await self.bitget.get_account_balance() or 0)
        dyn_max=3 if balance<800 else (5 if balance<1000 else self.cfg.MAX_POSITIONS)
        if len(open_syms)>=dyn_max: log.info("Max positions reached ("+str(len(open_syms))+"/"+str(dyn_max)+" dyn)"); return None
        total=len(open_sides)
        if total>0:
            same_side=sum(1 for s in open_sides if s==decision.action)
            max_same=getattr(self.cfg,"MAX_SAME_SIDE",3)
            if same_side>=max_same:
                log.info("Same-side cap: skip "+decision.action.upper()+" "+symbol+" ("+str(same_side)+"/"+str(max_same)+" already "+decision.action+")")
                return None
            if total>=3 and same_side/total > 2/3:
                log.info("2/3 rule: skip "+decision.action.upper()+" "+symbol+" ("+str(same_side)+"/"+str(total)+" already "+decision.action+")")
                return None
        if self.data is not None:
            max_corr=getattr(self.cfg,"MAX_CORRELATION",0.85)
            n=getattr(self.cfg,"CORR_LOOKBACK_BARS",24)
            # Snapshot via list() to avoid 'dict changed during iteration' if
            # monitor_loop concurrently closes a position mid-check.
            snapshot_items=list(self.open_trades.items())
            same_side_open=[s for s,t in snapshot_items if t.side==decision.action and s!=symbol]
            for open_sym in same_side_open:
                try: c=await self.data.correlation(symbol,open_sym,granularity="1H",n=n)
                except Exception as e: log.warning("correlation "+symbol+"/"+open_sym+": "+str(e)); c=0.0
                if c>=max_corr:
                    log.info("Correlation block: skip "+decision.action.upper()+" "+symbol+" (corr "+str(round(c,2))+" >= "+str(max_corr)+" with "+open_sym+" "+decision.action+")")
                    return None
        if self.cfg.PAPER_MODE:
            balance=ps["balance"]
            fixed_size=getattr(self.cfg,"POSITION_SIZE_FIXED",100.0)
            size=min(fixed_size, balance*0.5)  # $100 fixed, max 50% of balance
            price=snapshot.price
            qty=round(size/price,4) if price>0 else 0
            leverage=getattr(self.cfg,"LEVERAGE",5)
            log.info("[PAPER] Opening "+decision.action.upper()+" "+symbol+" notional=$"+str(round(size,1))+" conf="+str(decision.confidence)+"%")
            trade_id=paper_trading.paper_open(symbol,decision.action,price,qty,decision.confidence,leverage=leverage)
            if not trade_id: return None
        else:
            balance=await self.bitget.get_account_balance()
            fixed_size=getattr(self.cfg,"POSITION_SIZE_FIXED",100.0)
            size=min(fixed_size, balance*0.5)
            log.info("Opening "+decision.action.upper()+" "+symbol+" $"+str(round(size,1))+" conf="+str(decision.confidence)+"%")
            result=await self.bitget.place_order(symbol,decision.action,size)
            if result.get("code")!="00000": log.error("Order failed: "+str(result)); return None
        trade=TradeMemory(
            id=str(uuid.uuid4()),symbol=symbol,side=decision.action,
            entry_price=snapshot.price,exit_price=None,pnl_pct=None,
            regime=snapshot.regime,rsi_at_entry=snapshot.rsi_15m,
            funding_at_entry=snapshot.funding_rate,volume_ratio_at_entry=snapshot.volume_ratio,
            bull_confidence=0,bear_confidence=0,judge_confidence=decision.confidence,
            judge_reasoning=decision.reasoning,outcome="open",
            opened_at=_utcnow_iso(),closed_at=None,lessons=None)
        self.open_trades[symbol]=trade; self.memory.add_trade(trade)
        return trade
    async def _paper_price(self,symbol):
        try:
            t=await self.bitget.get("/api/v2/mix/market/ticker",{"symbol":symbol,"productType":"USDT-FUTURES"})
            return float(t["data"][0]["lastPr"])
        except Exception as e:
            log.warning("paper_price "+symbol+": "+str(e)); return None
    async def _ask_direction(self,trade,current_price,pnl_pct):
        try:
            return await self.judge.ask_direction(trade,current_price,pnl_pct)
        except Exception as e:
            log.error("ask_direction "+trade.symbol+": "+str(e)); return "hold"
    async def _close(self,symbol,trade,cp,pnl,reason):
        try:
            if self.cfg.PAPER_MODE: paper_trading.paper_close(symbol,cp,reason)
            else: await self.bitget.close_position(symbol,trade.side)
        except Exception as e: log.error("Close "+symbol+": "+str(e))
        trade.exit_price=cp; trade.pnl_pct=pnl
        await self._finalize(trade,reason)
        self.open_trades.pop(symbol,None)
        self._peak_pnl.pop(symbol,None)
    async def monitor_loop(self,stop_event=None):
        log.info("Position monitor started")
        last_check={}
        sl_pct=getattr(self.cfg,"STOP_LOSS_PCT",-3.0)
        tp_pct=getattr(self.cfg,"TAKE_PROFIT_PCT",3.0)
        trail_arm=getattr(self.cfg,"TRAIL_ARM_PCT",1.5)
        trail_give=getattr(self.cfg,"TRAIL_GIVEBACK_PCT",1.0)
        emerg_pct=getattr(self.cfg,"EMERGENCY_STOP_PCT",-15.0)
        leverage=getattr(self.cfg,"LEVERAGE",5)
        # Liquidation threshold: at L× leverage, price moving -100/L % wipes margin.
        # Use safety margin of 1% to ensure close before broker liquidates in live mode.
        liquidation_pct=-(100.0/max(leverage,1))+1.0
        min_hold=getattr(self.cfg,"MIN_HOLD_SEC",7200)
        ask_interval=getattr(self.cfg,"JUDGE_EXIT_INTERVAL_SEC",3600)
        noise_band=getattr(self.cfg,"JUDGE_EXIT_NOISE_BAND_PCT",1.0)
        while True:
            if stop_event is not None and stop_event.is_set(): log.info("Position monitor stopped"); return
            try:
                now=time.time()
                try:
                    if self.cfg.PAPER_MODE:
                        paper_pos=paper_trading.paper_get_positions()
                        ex=[]
                        for p in paper_pos:
                            mp=await self._paper_price(p["symbol"])
                            ex.append({"symbol":p["symbol"],"marketPrice":mp,"total":p["qty"]})
                    else:
                        ex=await self.bitget.get_positions() or []
                except Exception:
                    ex=[]
                ex_syms={p["symbol"] for p in ex}
                ex_list=list(ex)
                for symbol,trade in list(self.open_trades.items()):
                    if symbol not in ex_syms:
                        if not self.cfg.PAPER_MODE:
                            # Bug fix: set exit_price and pnl_pct before finalizing
                            trade.exit_price = trade.entry_price
                            trade.pnl_pct = 0.0
                            await self._finalize(trade,"closed_externally"); del self.open_trades[symbol]
                        continue
                    ep=next((p for p in ex_list if p["symbol"]==symbol),None)
                    if ep is None or ep.get("marketPrice") is None: continue
                    cp=float(ep["marketPrice"])
                    pnl=(cp-trade.entry_price)/trade.entry_price*100 if trade.side=="long" else (trade.entry_price-cp)/trade.entry_price*100
                    peak=self._peak_pnl.get(symbol,pnl)
                    if pnl>peak: peak=pnl
                    self._peak_pnl[symbol]=peak
                    if pnl<=liquidation_pct:
                        log.warning("LIQUIDATION "+symbol+" "+trade.side+" PnL:"+str(round(pnl,2))+"% (threshold "+str(round(liquidation_pct,2))+"% at "+str(leverage)+"x)")
                        await self._close(symbol,trade,cp,pnl,"liquidation"); continue
                    if pnl<=emerg_pct:
                        log.warning("EMERGENCY STOP "+symbol+" "+trade.side+" PnL:"+str(round(pnl,2))+"%")
                        await self._close(symbol,trade,cp,pnl,"emergency_stop"); continue
                    # Max hold time enforced
                    try:
                        opened_dt=datetime.fromisoformat(trade.opened_at.replace("Z",""))
                        if opened_dt.tzinfo is not None: opened_dt=opened_dt.replace(tzinfo=None)
                        hold_sec=(_utcnow()-opened_dt).total_seconds()
                    except Exception: hold_sec=1e9
                    max_hold_hours=getattr(self.cfg,"MAX_HOLD_HOURS",24.0)
                    if hold_sec>=max_hold_hours*3600:
                        log.info("MAX_HOLD "+symbol+" "+trade.side+" hold:"+str(round(hold_sec/3600,1))+"h")
                        await self._close(symbol,trade,cp,pnl,"max_hold"); continue
                    # Breakeven: если цена прошла +1.5%, переносим SL на +0.5% (гарантия прибыли)
                    effective_sl=sl_pct
                    if peak>=1.5:
                        effective_sl=0.5
                    if pnl<=effective_sl:
                        reason="breakeven_stop" if effective_sl>=0.0 else "stop_loss"
                        log.info(reason.upper()+" "+symbol+" "+trade.side+" PnL:"+str(round(pnl,2))+"%")
                        await self._close(symbol,trade,cp,pnl,reason); continue
                    if pnl>=tp_pct:
                        log.info("TAKE-PROFIT "+symbol+" "+trade.side+" PnL:"+str(round(pnl,2))+"%")
                        await self._close(symbol,trade,cp,pnl,"take_profit"); continue
                    if peak>=trail_arm and pnl<=peak-trail_give:
                        log.info("TRAILING-STOP "+symbol+" "+trade.side+" peak:"+str(round(peak,2))+"% now:"+str(round(pnl,2))+"%")
                        await self._close(symbol,trade,cp,pnl,"trailing_stop"); continue
                    t=last_check.get(symbol,0)
                    in_noise=abs(pnl)<noise_band and peak<trail_arm
                    emergency_exit=pnl<-1.0
                    if (hold_sec>=min_hold or emergency_exit) and (now-t>ask_interval or emergency_exit) and not in_noise:
                        last_check[symbol]=now
                        should_exit=await self.judge.ask_exit(trade,cp,pnl,peak_pnl=peak)
                        if should_exit:
                            await self._close(symbol,trade,cp,pnl,"judge_exit")
            except Exception as e:
                log.error("Monitor: "+str(e))
                log.error(traceback.format_exc())
            if stop_event is not None:
                try:
                    await asyncio.wait_for(stop_event.wait(),timeout=30)
                    log.info("Position monitor stopped")
                    return
                except asyncio.TimeoutError:
                    pass
                except Exception as e:
                    log.error("Monitor wait error: "+str(e))
                    return
            else:
                await asyncio.sleep(30)
    async def _finalize(self,trade,reason):
        trade.closed_at=_utcnow_iso()
        trade.outcome="profit" if (trade.pnl_pct or 0)>0 else "loss"
        lessons=await self.judge.reflect(trade,reason+" PnL:"+str(round(trade.pnl_pct or 0,2))+"%")
        trade.lessons=lessons
        self.memory.update_trade(trade.id,closed_at=trade.closed_at,exit_price=trade.exit_price,pnl_pct=trade.pnl_pct,outcome=trade.outcome,lessons=lessons,close_reason=reason)
        e="OK" if trade.outcome=="profit" else "LOSS"
        log.info(e+" "+trade.symbol+" "+trade.side+" PnL:"+str(round(trade.pnl_pct or 0,2))+"% reason:"+reason)
        log.info("Lessons: "+str(lessons))
        if self.rl is not None:
            try: self.rl.learn(trade)
            except Exception as ex: log.error("RL.learn "+trade.symbol+": "+str(ex))
