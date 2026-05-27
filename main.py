#!/usr/bin/env python3
import asyncio,logging,signal,sys,random
from logging.handlers import RotatingFileHandler
from datetime import datetime,timezone
from config import Config
from bitget_client import BitgetClient
from data_engine import DataEngine
from agents import BullAgent,BearAgent,Judge
from memory import Memory
from rl_agent import RLAgent
from rl_context import ContextRL
from position_manager import PositionManager
import http_pool

_log_handler=RotatingFileHandler(
    "/opt/ensemble-agent/ensemble.log",
    maxBytes=50*1024*1024,backupCount=5,encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[_log_handler])
log=logging.getLogger("main")

class Orchestrator:
    def __init__(self):
        self.cfg=Config(); self.bitget=BitgetClient(self.cfg)
        self.data=DataEngine(self.bitget); self.bull=BullAgent(self.cfg)
        self.bear=BearAgent(self.cfg); self.judge=Judge(self.cfg)
        self.memory=Memory(self.cfg)
        self.rl=RLAgent(self.cfg)
        self.ctx=ContextRL()
        self.positions=PositionManager(self.bitget,self.cfg,self.memory,self.judge,self.rl,data=self.data)
        self.running=True; self.symbols=[]; self._stop_event=asyncio.Event()
    async def _wait(self,timeout):
        try: await asyncio.wait_for(self._stop_event.wait(),timeout=timeout)
        except asyncio.TimeoutError: pass
    async def start(self):
        await self.bitget.start()
        await self.positions.setup()
        log.info("=== Adversarial Trading Agent started ===")
        kimi_on=bool(getattr(self.cfg,"KIMI_API_KEY",None))
        groq_keys=len(getattr(self.cfg,"GROQ_API_KEYS",[]) or [])
        log.info("Bull: race(Kimi x"+("1" if kimi_on else "0")+", Groq x"+str(groq_keys)+") → Haiku fb | Bear: race(Groq x"+str(groq_keys)+", Kimi x"+("1" if kimi_on else "0")+") → Haiku fb | Judge: Haiku (decide) + Groq Llama (exit/dir/reflect)")
        loop=asyncio.get_event_loop()
        for sig in (signal.SIGINT,signal.SIGTERM): loop.add_signal_handler(sig,self.stop)
        closed_in_memory=sum(1 for t in self.memory.trades if t.outcome in ("profit","loss") and not getattr(t,"orphan",False))
        if self.rl.weights.episodes==0 and closed_in_memory>0 and getattr(self.cfg,"RL_PRIME_FROM_HISTORY",True):
            log.info("RL prime: learning from "+str(closed_in_memory)+" closed trades in memory")
            self.rl.learn_from_history(self.memory)
        elif self.rl.weights.episodes==0:
            log.info("RL: starting fresh (prime disabled, "+str(closed_in_memory)+" closed in memory)")
        await self._refresh_symbols()
        try:
            await asyncio.gather(self.scan_loop(),self.positions.monitor_loop(self._stop_event),self.symbol_refresh_loop())
        finally:
            # Best-effort drain of in-flight save tasks before exit
            try:
                pending=[t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
                if pending:
                    log.info("Draining "+str(len(pending))+" pending tasks before close")
                    await asyncio.wait(pending,timeout=5)
            except Exception as e: log.error("drain: "+str(e))
            # Final synchronous saves to ensure durability after pending tasks finish/timeout
            try: self.memory._save_sync()
            except Exception as e: log.error("memory final save: "+str(e))
            try: self.rl._save_sync()
            except Exception as e: log.error("rl final save: "+str(e))
            try: await self.bitget.close()
            except Exception as e: log.error("bitget close: "+str(e))
            try: await http_pool.close()
            except Exception as e: log.error("http_pool close: "+str(e))
    def stop(self): log.info("Shutting down..."); self.running=False; self._stop_event.set()
    async def symbol_refresh_loop(self):
        while self.running:
            await self._wait(3600)
            if not self.running: break
            await self._refresh_symbols()
    async def _refresh_symbols(self):
        try: self.symbols=await self.bitget.get_top_symbols(self.cfg.TOP_N_SYMBOLS); log.info("Symbols: "+str(len(self.symbols)))
        except Exception as e: log.error("Symbol refresh: "+str(e))
    def _next_interval(self):
        now=datetime.now(timezone.utc); wd=now.weekday(); h=now.hour
        if wd>=5: return 10800,"weekend"
        if 8<=h<22: return 3600,"weekday-active"
        return 7200,"weekday-quiet"
    async def scan_loop(self):
        while self.running:
            try: await self.scan_all()
            except Exception as e: log.error("Scan: "+str(e))
            interval,mode=self._next_interval()
            log.info("Next scan in "+str(interval//60)+"min ("+mode+")")
            await self._wait(interval)
    async def scan_all(self):
        if not self.symbols: return
        candidates=[s for s in self.symbols if s not in self.positions.open_trades]
        random.shuffle(candidates)
        log.info("Scanning "+str(len(candidates))+" symbols...")
        for symbol in candidates:
            if not self.running: break
            if len(self.positions.open_trades)>=self.cfg.MAX_POSITIONS: log.info("Max positions"); break
            try: await self.analyze(symbol); await self._wait(2)
            except Exception as e: log.error("Analyze "+symbol+": "+str(e))
    async def analyze(self,symbol):
        snapshot=await self.data.get_snapshot(symbol)
        if not snapshot: return
        market_text=snapshot.to_text()
        bull,bear=await asyncio.gather(self.bull.analyze(market_text),self.bear.analyze(market_text))
        log.info(symbol+" | Bull:"+bull.side+"("+str(bull.confidence)+"%) Bear:"+bear.side+"("+str(bear.confidence)+"%)")
        similar=self.memory.get_similar(snapshot)
        mem_ctx=self.memory.format_similar_for_judge(similar)
        decision=await self.judge.decide(market_text,bull,bear,mem_ctx)
        log.info(symbol+" | Judge:"+decision.action.upper()+" conf="+str(decision.confidence)+"% size="+str(round(decision.position_size_pct*100,1))+"%")
        rl_conf=self.rl.get_adjusted_confidence(bull.confidence,bear.confidence,decision.confidence,decision.action,bull.side,bear.side)
        rl_ok=self.rl.should_trade(rl_conf)
        log.info(str(symbol)+" | RL adj="+str(round(rl_conf,1))+"%")
        if decision.action in ("long","short"):
            # Explorer-learned context filter
            ctx_score=self.ctx.score(snapshot,decision.action)
            # Side-bias penalty: explorer shows shorts avg -1.91%, longs +1.37% (bullish market)
            if decision.action=="short":
                ctx_score-=0.10
            log.info(symbol+" | Context score="+str(round(ctx_score,2)))
            if ctx_score < -0.15:
                log.info(symbol+" | context BLOCK (explorer pattern score="+str(round(ctx_score,2))+")")
                return
            elif ctx_score >= 0.20:
                log.info(symbol+" | context BOOST (explorer pattern score="+str(round(ctx_score,2))+")")
            if snapshot.regime in ("volatile","unknown"):
                log.info(symbol+" | regime BLOCK ("+snapshot.regime+")"); return
            btc_regime=await self.data.get_btc_regime()
            if decision.action=="short" and btc_regime=="trending_up":
                log.info(symbol+" | macro BLOCK (short при BTC uptrend)"); return
            if decision.action=="long" and btc_regime=="trending_down":
                log.info(symbol+" | macro BLOCK (long при BTC downtrend)"); return
            if decision.action=="short" and snapshot.regime=="trending_down" and snapshot.rsi_1h>45:
                log.info(symbol+" | regime BLOCK (short × trending_down × rsi1h="+str(round(snapshot.rsi_1h,1))+"; late-entry guard)"); return
            if decision.action=="short" and snapshot.regime=="trending_up" and snapshot.rsi_1h<55:
                log.info(symbol+" | regime BLOCK (short × trending_up × rsi1h="+str(round(snapshot.rsi_1h,1))+"; counter-trend guard)"); return
            if decision.action=="long" and snapshot.regime=="trending_down" and snapshot.rsi_1h>45:
                log.info(symbol+" | regime BLOCK (long × trending_down × rsi1h="+str(round(snapshot.rsi_1h,1))+"; counter-trend guard)"); return
            if decision.action=="long" and snapshot.regime=="trending_up" and snapshot.rsi_1h<55:
                log.info(symbol+" | regime BLOCK (long × trending_up × rsi1h="+str(round(snapshot.rsi_1h,1))+"; late-entry guard)"); return
            slack=getattr(self.cfg,"THRESHOLD_SLACK",3)
            j_base=self.cfg.MIN_CONFIDENCE; r_base=self.rl.weights.conf_threshold
            j_dev=decision.confidence-j_base; r_dev=rl_conf-r_base
            soft_ok=(decision.confidence>=j_base-slack and rl_conf>=r_base-slack and j_dev+r_dev>=0)
            if soft_ok:
                log.info(symbol+" | gate PASS (Judge "+str(decision.confidence)+"/"+str(j_base)+" RL "+str(round(rl_conf,1))+"/"+str(r_base)+" slack=±"+str(slack)+")")
                trade=await self.positions.open_position(symbol,decision,snapshot)
                if trade: self.memory.update_trade(trade.id,bull_confidence=bull.confidence,bear_confidence=bear.confidence)

asyncio.run(Orchestrator().start())
