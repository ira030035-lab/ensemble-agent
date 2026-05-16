#!/usr/bin/env python3
import asyncio,logging,signal,sys,random
from config import Config
from bitget_client import BitgetClient
from data_engine import DataEngine
from agents import BullAgent,BearAgent,Judge
from memory import Memory
from position_manager import PositionManager

logging.basicConfig(level=logging.INFO,format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("/opt/ensemble-agent/ensemble.log"),logging.StreamHandler(sys.stdout)])
log=logging.getLogger("main")

class Orchestrator:
    def __init__(self):
        self.cfg=Config(); self.bitget=BitgetClient(self.cfg)
        self.data=DataEngine(self.bitget); self.bull=BullAgent(self.cfg)
        self.bear=BearAgent(self.cfg); self.judge=Judge(self.cfg)
        self.memory=Memory(self.cfg)
        self.positions=PositionManager(self.bitget,self.cfg,self.memory,self.judge)
        self.running=True; self.symbols=[]
    async def start(self):
        await self.bitget.start()
        log.info("=== Adversarial Trading Agent started ===")
        log.info("Bull: Gemini Flash | Bear: Grok | Judge: Claude Sonnet")
        loop=asyncio.get_event_loop()
        for sig in (signal.SIGINT,signal.SIGTERM): loop.add_signal_handler(sig,self.stop)
        await self._refresh_symbols()
        await asyncio.gather(self.scan_loop(),self.positions.monitor_loop(),self.symbol_refresh_loop())
    def stop(self): log.info("Shutting down..."); self.running=False
    async def symbol_refresh_loop(self):
        while self.running: await asyncio.sleep(3600); await self._refresh_symbols()
    async def _refresh_symbols(self):
        try: self.symbols=await self.bitget.get_top_symbols(self.cfg.TOP_N_SYMBOLS); log.info("Symbols: "+str(len(self.symbols)))
        except Exception as e: log.error("Symbol refresh: "+str(e))
    async def scan_loop(self):
        while self.running:
            try: await self.scan_all()
            except Exception as e: log.error("Scan: "+str(e))
            await asyncio.sleep(self.cfg.SCAN_INTERVAL)
    async def scan_all(self):
        if not self.symbols: return
        candidates=[s for s in self.symbols if s not in self.positions.open_trades]
        random.shuffle(candidates)
        log.info("Scanning "+str(len(candidates))+" symbols...")
        for symbol in candidates:
            if not self.running: break
            if len(self.positions.open_trades)>=self.cfg.MAX_POSITIONS: log.info("Max positions"); break
            try: await self.analyze(symbol); await asyncio.sleep(2)
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
        if decision.action in ("long","short") and decision.confidence>=self.cfg.MIN_CONFIDENCE:
            trade=await self.positions.open_position(symbol,decision,snapshot)
            if trade: self.memory.update_trade(trade.id,bull_confidence=bull.confidence,bear_confidence=bear.confidence)

asyncio.run(Orchestrator().start())
