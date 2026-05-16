import asyncio,logging,json,re,aiohttp
from dataclasses import dataclass
log=logging.getLogger("agents")

@dataclass
class AgentVerdict:
    side:str; confidence:int; reasoning:str

@dataclass
class JudgeDecision:
    action:str; confidence:int; position_size_pct:float; reasoning:str; lessons_from_memory:str

BULL_SYS="You are the BULL agent. Find the strongest case for going LONG. Be rigorous. Respond ONLY in JSON: {side:long, confidence:0-100, reasoning:string}"
BEAR_SYS="You are the BEAR agent. Find the strongest case for SHORT or FLAT. Be rigorous. Respond ONLY in JSON: {side:short or flat, confidence:0-100, reasoning:string}"
JUDGE_SYS="You are the JUDGE. You see BULL and BEAR arguments plus past similar trades. Make the FINAL autonomous decision: action(long/short/hold), confidence(0-100), position_size_pct(0.01-0.15), reasoning, lessons_from_memory. Respond ONLY in JSON."

class BullAgent:
    def __init__(self,cfg): self.cfg=cfg
    async def analyze(self,market_text):
        try:
            r=await self._gemini("Analyze and make bullish case:\n"+market_text)
            d=self._parse(r)
            return AgentVerdict(d.get("side","long"),int(d.get("confidence",50)),d.get("reasoning",r))
        except Exception as e: log.error("Bull: "+str(e)); return AgentVerdict("long",30,"Error: "+str(e))
    async def _gemini(self,prompt):
        url="https://generativelanguage.googleapis.com/v1beta/models/"+self.cfg.BULL_MODEL+":generateContent"
        payload={"system_instruction":{"parts":[{"text":BULL_SYS}]},"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.3,"maxOutputTokens":1000}}
        async with aiohttp.ClientSession() as s:
            async with s.post(url,json=payload,params={"key":self.cfg.GEMINI_API_KEY}) as r:
                d=await r.json(); return d["candidates"][0]["content"]["parts"][0]["text"]
    def _parse(self,t):
        t=re.sub(r"```json|```","",t).strip()
        try: return json.loads(t)
        except: return {"reasoning":t}

class BearAgent:
    def __init__(self,cfg): self.cfg=cfg
    async def analyze(self,market_text):
        try:
            r=await self._grok("Analyze and make bearish/cautious case:\n"+market_text)
            d=self._parse(r)
            return AgentVerdict(d.get("side","flat"),int(d.get("confidence",50)),d.get("reasoning",r))
        except Exception as e: log.error("Bear: "+str(e)); return AgentVerdict("flat",50,"Error: "+str(e))
    async def _grok(self,prompt):
        url="https://api.x.ai/v1/chat/completions"
        payload={"model":self.cfg.BEAR_MODEL,"messages":[{"role":"system","content":BEAR_SYS},{"role":"user","content":prompt}],"temperature":0.3,"max_tokens":1000}
        headers={"Authorization":"Bearer "+self.cfg.GROK_API_KEY,"Content-Type":"application/json"}
        async with aiohttp.ClientSession() as s:
            async with s.post(url,json=payload,headers=headers) as r:
                d=await r.json(); return d["choices"][0]["message"]["content"]
    def _parse(self,t):
        t=re.sub(r"```json|```","",t).strip()
        try: return json.loads(t)
        except: return {"reasoning":t}

class Judge:
    def __init__(self,cfg): self.cfg=cfg
    async def decide(self,market_text,bull,bear,memory_ctx):
        prompt="## Market\n"+market_text+"\n\n## BULL ("+str(bull.confidence)+"%)\n"+bull.reasoning+"\n\n## BEAR ("+str(bear.confidence)+"%)\n"+bear.reasoning+"\n\n## Memory\n"+memory_ctx+"\n\nMake your final decision."
        try:
            r=await self._claude(prompt)
            d=self._parse(r)
            return JudgeDecision(d.get("action","hold"),int(d.get("confidence",50)),float(d.get("position_size_pct",0.03)),d.get("reasoning",r),d.get("lessons_from_memory",""))
        except Exception as e: log.error("Judge: "+str(e)); return JudgeDecision("hold",0,0,"Error: "+str(e),"")
    async def reflect(self,trade,outcome):
        prompt="Trade closed: "+trade.symbol+" "+trade.side+" PnL:"+str(round(trade.pnl_pct or 0,2))+"% Regime:"+trade.regime+"\nOriginal reasoning:"+trade.judge_reasoning+"\nOutcome:"+outcome+"\nIn 2-3 sentences what should be remembered?"
        try: return (await self._claude(prompt)).strip()
        except Exception as e: return "Reflection error: "+str(e)
    async def ask_exit(self,trade,current_price,pnl_pct):
        prompt="Open "+trade.side.upper()+" "+trade.symbol+" Entry:"+str(trade.entry_price)+" Current:"+str(current_price)+" PnL:"+str(round(pnl_pct,2))+"% Opened:"+trade.opened_at+"\nOriginal thesis:"+trade.judge_reasoning[:300]+"\nShould you EXIT now? Respond ONLY: EXIT or HOLD"
        try: r=await self._claude(prompt); return "EXIT" in r.upper()
        except: return False
    async def _claude(self,prompt):
        import anthropic
        c=anthropic.AsyncAnthropic(api_key=self.cfg.ANTHROPIC_API_KEY)
        msg=await c.messages.create(model=self.cfg.JUDGE_MODEL,max_tokens=1000,system=JUDGE_SYS,messages=[{"role":"user","content":prompt}])
        return msg.content[0].text
    def _parse(self,t):
        t=re.sub(r"```json|```","",t).strip()
        try: return json.loads(t)
        except: return {"reasoning":t}
