import asyncio,logging,uuid
from datetime import datetime
from typing import Optional
log=logging.getLogger("positions")

class PositionManager:
    def __init__(self,bitget,cfg,memory,judge):
        self.bitget=bitget; self.cfg=cfg; self.memory=memory; self.judge=judge
        self.open_trades={}
    async def open_position(self,symbol,decision,snapshot):
        from memory import TradeMemory
        if symbol in self.open_trades: log.info("Already in "+symbol); return None
        if len(self.open_trades)>=self.cfg.MAX_POSITIONS: log.info("Max positions reached"); return None
        balance=await self.bitget.get_account_balance()
        size=balance*decision.position_size_pct
        log.info("Opening "+decision.action.upper()+" "+symbol+" $"+str(round(size,1))+" conf="+str(decision.confidence)+"%")
        result=await self.bitget.place_order(symbol,decision.action,size)
        if result.get("code")!="00000": log.error("Order failed: "+str(result)); return None
        trade=TradeMemory(
            id=str(uuid.uuid4())[:8],symbol=symbol,side=decision.action,
            entry_price=snapshot.price,exit_price=None,pnl_pct=None,
            regime=snapshot.regime,rsi_at_entry=snapshot.rsi_15m,
            funding_at_entry=snapshot.funding_rate,volume_ratio_at_entry=snapshot.volume_ratio,
            bull_confidence=0,bear_confidence=0,judge_confidence=decision.confidence,
            judge_reasoning=decision.reasoning,outcome="open",
            opened_at=datetime.utcnow().isoformat(),closed_at=None,lessons=None)
        self.open_trades[symbol]=trade; self.memory.add_trade(trade)
        return trade
    async def monitor_loop(self):
        log.info("Position monitor started")
        last_check={}
        while True:
            try:
                import time
                now=time.time()
                ex=await self.bitget.get_positions()
                ex_syms={p["symbol"] for p in ex}
                for symbol,trade in list(self.open_trades.items()):
                    if symbol not in ex_syms:
                        await self._finalize(trade,"closed_externally"); del self.open_trades[symbol]; continue
                    ep=next((p for p in ex if p["symbol"]==symbol),None)
                    if ep:
                        cp=float(ep.get("marketPrice",trade.entry_price))
                        pnl=(cp-trade.entry_price)/trade.entry_price*100 if trade.side=="long" else (trade.entry_price-cp)/trade.entry_price*100
                        t=last_check.get(symbol,0)
                        if now-t>300:
                            last_check[symbol]=now
                            should_exit=await self.judge.ask_exit(trade,cp,pnl)
                            if should_exit:
                                await self.bitget.close_position(symbol,trade.side)
                                trade.exit_price=cp; trade.pnl_pct=pnl
                                await self._finalize(trade,"judge_exit"); del self.open_trades[symbol]
            except Exception as e: log.error("Monitor: "+str(e))
            await asyncio.sleep(30)
    async def _finalize(self,trade,reason):
        trade.closed_at=__import__("datetime").datetime.utcnow().isoformat()
        trade.outcome="profit" if (trade.pnl_pct or 0)>0 else "loss"
        lessons=await self.judge.reflect(trade,reason+" PnL:"+str(round(trade.pnl_pct or 0,2))+"%")
        trade.lessons=lessons
        self.memory.update_trade(trade.id,closed_at=trade.closed_at,exit_price=trade.exit_price,pnl_pct=trade.pnl_pct,outcome=trade.outcome,lessons=lessons)
        e="OK" if trade.outcome=="profit" else "LOSS"
        log.info(e+" "+trade.symbol+" "+trade.side+" PnL:"+str(round(trade.pnl_pct or 0,2))+"% reason:"+reason)
        log.info("Lessons: "+str(lessons))
