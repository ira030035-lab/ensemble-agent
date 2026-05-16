import json,logging,os,uuid
from dataclasses import dataclass,asdict
from typing import Optional
from datetime import datetime
log=logging.getLogger("memory")

@dataclass
class TradeMemory:
    id:str; symbol:str; side:str; entry_price:float; exit_price:Optional[float]
    pnl_pct:Optional[float]; regime:str; rsi_at_entry:float; funding_at_entry:float
    volume_ratio_at_entry:float; bull_confidence:int; bear_confidence:int
    judge_confidence:int; judge_reasoning:str; outcome:Optional[str]
    opened_at:str; closed_at:Optional[str]; lessons:Optional[str]

class Memory:
    def __init__(self,cfg):
        self.path=cfg.MEMORY_FILE; self.trades=[]; self._load()
    def _load(self):
        if os.path.exists(self.path):
            try:
                data=json.load(open(self.path))
                self.trades=[TradeMemory(**t) for t in data]
                log.info("Memory loaded: "+str(len(self.trades))+" trades")
            except Exception as e: log.error("Memory load: "+str(e)); self.trades=[]
    def _save(self):
        try: json.dump([asdict(t) for t in self.trades],open(self.path,"w"),indent=2,ensure_ascii=False)
        except Exception as e: log.error("Memory save: "+str(e))
    def add_trade(self,trade): self.trades.append(trade); self._save()
    def update_trade(self,tid,**kw):
        for t in self.trades:
            if t.id==tid:
                for k,v in kw.items(): setattr(t,k,v)
                self._save(); return
    def get_similar(self,snapshot,n=5):
        closed=[t for t in self.trades if t.outcome in ("profit","loss")]
        if not closed: return []
        def score(t):
            s=3.0 if t.regime==snapshot.regime else 0.0
            s-=abs(t.rsi_at_entry-snapshot.rsi_15m)/100
            if (t.funding_at_entry>0)==(snapshot.funding_rate>0): s+=1.0
            return s
        return sorted(closed,key=score,reverse=True)[:n]
    def format_similar_for_judge(self,similar):
        if not similar: return "No similar past trades found."
        lines=["=== Similar Past Situations ==="]
        for i,t in enumerate(similar,1):
            e="OK" if t.outcome=="profit" else "LOSS"
            lines.append(str(i)+". "+e+" "+t.symbol+" "+t.side+" | "+t.regime+" | PnL: "+str(round(t.pnl_pct or 0,1))+"%")
            lines.append("   RSI:"+str(round(t.rsi_at_entry,0))+" Fund:"+str(round(t.funding_at_entry*100,3))+"% Vol:"+str(round(t.volume_ratio_at_entry,1))+"x")
            lines.append("   Judge("+str(t.judge_confidence)+"%) reasoning: "+t.judge_reasoning[:150])
            lines.append("   Lessons: "+(t.lessons or "none"))
        return "\n".join(lines)
    def get_stats(self):
        closed=[t for t in self.trades if t.outcome in ("profit","loss")]
        if not closed: return {"total":0}
        wins=[t for t in closed if t.outcome=="profit"]
        pnls=[t.pnl_pct for t in closed if t.pnl_pct is not None]
        return {"total":len(closed),"win_rate":len(wins)/len(closed)*100,"avg_pnl":sum(pnls)/len(pnls) if pnls else 0}
