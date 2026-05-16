import logging,numpy as np
from dataclasses import dataclass
log = logging.getLogger("data_engine")

@dataclass
class MarketSnapshot:
    symbol:str; price:float; price_change_15m:float; price_change_1h:float
    price_change_4h:float; volume_15m:float; volume_ratio:float
    rsi_15m:float; rsi_1h:float; macd_signal:str; bb_position:float
    funding_rate:float; open_interest_change:float; bid_ask_imbalance:float; regime:str
    def to_text(self):
        lines = [
            "Symbol: "+self.symbol,
            "Price: $"+str(round(self.price,4)),
            "15m: "+str(round(self.price_change_15m,2))+"%",
            "1h: "+str(round(self.price_change_1h,2))+"%",
            "4h: "+str(round(self.price_change_4h,2))+"%",
            "Volume ratio: "+str(round(self.volume_ratio,1))+"x",
            "RSI 15m: "+str(round(self.rsi_15m,1)),
            "RSI 1h: "+str(round(self.rsi_1h,1)),
            "MACD: "+self.macd_signal,
            "BB position: "+str(round(self.bb_position,2)),
            "Funding: "+str(round(self.funding_rate*100,4))+"%",
            "OB imbalance: "+str(round(self.bid_ask_imbalance,3)),
            "Regime: "+self.regime,
        ]
        return "\n".join(lines)

class DataEngine:
    def __init__(self,bitget): self.bitget=bitget
    async def get_snapshot(self,symbol):
        try:
            c15=await self.bitget.get_candles(symbol,"15m",100)
            c1h=await self.bitget.get_candles(symbol,"1H",50)
            c4h=await self.bitget.get_candles(symbol,"4H",30)
            if not c15 or not c1h or not c4h: return None
            def parse(c): return {"close":[float(x[4]) for x in c],"volume":[float(x[5]) for x in c]}
            d15,d1h,d4h=parse(c15),parse(c1h),parse(c4h)
            price=d15["close"][-1]
            pc15=(d15["close"][-1]/d15["close"][-2]-1)*100
            pc1h=(d1h["close"][-1]/d1h["close"][-2]-1)*100
            pc4h=(d4h["close"][-1]/d4h["close"][-5]-1)*100 if len(d4h["close"])>=5 else 0
            vol15=d15["volume"][-1]; avg=float(np.mean(d15["volume"][-20:]))
            vr=vol15/avg if avg>0 else 1.0
            funding=await self.bitget.get_funding_rate(symbol)
            ob=await self.bitget.get_orderbook(symbol)
            bids=ob.get("bids",[]); asks=ob.get("asks",[])
            bv=sum(float(b[1]) for b in bids[:10]); av=sum(float(a[1]) for a in asks[:10])
            imb=(bv-av)/(bv+av) if bv+av>0 else 0
            closes=d15["close"]; regime=self._regime(d1h["close"])
            return MarketSnapshot(symbol,price,pc15,pc1h,pc4h,vol15,vr,
                self._rsi(closes),self._rsi(d1h["close"]),self._macd(closes),
                self._bb(closes),funding,0.0,imb,regime)
        except Exception as e: log.error("DataEngine "+symbol+": "+str(e)); return None
    def _rsi(self,c,p=14):
        if len(c)<p+1: return 50.0
        d=np.diff(c); g=np.where(d>0,d,0); l=np.where(d<0,-d,0)
        ag=np.mean(g[-p:]); al=np.mean(l[-p:])
        return 100.0 if al==0 else 100-(100/(1+ag/al))
    def _ema(self,d,p):
        k=2/(p+1); e=d[0]
        for v in d[1:]: e=v*k+e*(1-k)
        return e
    def _macd(self,c):
        if len(c)<35: return "neutral"
        m=self._ema(c,12)-self._ema(c,26); s=self._ema([m]*9,9)
        return "bullish" if m>s*1.001 else ("bearish" if m<s*0.999 else "neutral")
    def _bb(self,c,p=20):
        if len(c)<p: return 0.5
        w=c[-p:]; mn=float(np.mean(w)); sd=float(np.std(w))
        return 0.5 if sd==0 else (c[-1]-(mn-2*sd))/(4*sd)
    def _regime(self,c):
        if len(c)<20: return "ranging"
        cv=float(np.std(c[-20:])/np.mean(c[-20:]))
        ma5=float(np.mean(c[-5:])); ma20=float(np.mean(c[-20:]))
        if cv>0.03: return "volatile"
        return "trending_up" if ma5>ma20*1.005 else ("trending_down" if ma5<ma20*0.995 else "ranging")
