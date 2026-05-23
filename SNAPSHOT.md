# Ensemble-agent snapshot

Generated: 2026-05-23 15:00:01 UTC

## agents.py
```python
import asyncio,logging,json,re,aiohttp,time
from dataclasses import dataclass
log=logging.getLogger("agents")

@dataclass
class AgentVerdict:
    side:str; confidence:int; reasoning:str

@dataclass
class JudgeDecision:
    action:str; confidence:int; position_size_pct:float; reasoning:str; lessons_from_memory:str

BULL_SYS='You are the BULL agent in an adversarial ensemble — your job is to argue the LONG case rigorously. Default to side="long" with confidence reflecting how strong the evidence is (35-90). Use side="flat" ONLY when the data is genuinely directionless (no trend, mid RSI, neutral MACD, flat volume) — not just because risk exists. A weak-but-real bullish case is still side="long" with confidence 40-55, not "flat". Respond ONLY in JSON: {"side":"long|flat","confidence":0-100,"reasoning":"brief specific"}.'
BEAR_SYS='You are the BEAR agent — a skeptical crypto analyst hunting for the strongest case to AVOID or SHORT this trade. Respond ONLY in JSON with no other text: {"side":"short|flat|long","confidence":0-100,"reasoning":"brief"}. Use side="short" if bearish, "flat" if unclear, "long" only if the data is overwhelmingly bullish. Be specific about why.'
JUDGE_SYS="""You are the JUDGE in an adversarial trading ensemble. BULL argues for LONG; BEAR argues for SHORT/avoid. A "flat" side from either agent means NEUTRAL — it is NOT opposition, just absence of conviction. Past similar trades may be empty (paper bot, no history) — that is normal, do not let it bias you toward HOLD.

Decision criteria:
- LONG if: BULL conviction >= 55 AND BEAR is flat OR BEAR conviction < BULL conviction. Set action="long".
- SHORT if: BEAR conviction >= 55 AND BULL is flat OR BULL conviction < BEAR conviction. Set action="short".
- HOLD only when: signals genuinely conflict (both > 60 in opposite directions) OR both sides agree it is flat/unclear. HOLD is a real cost — missed opportunity.

For action="long" or "short": confidence in 50-95 reflecting how aligned the evidence is; position_size_pct in 0.03-0.12 (bigger when conviction higher, smaller when conflicting).
For action="hold": confidence = max conviction of either side; position_size_pct = 0.0.

Respond ONLY with valid JSON, no prose, no markdown fences:
{"action":"long|short|hold","confidence":0-100,"position_size_pct":0.0-0.15,"reasoning":"brief","lessons_from_memory":"brief"}"""

async def _race(coros, fallback_coro):
    """Run coros concurrently; first non-empty wins; on all-empty, await fallback_coro."""
    tasks=[asyncio.create_task(c) for c in coros]
    text=""
    pending=set(tasks)
    while pending:
        done,pending=await asyncio.wait(pending,return_when=asyncio.FIRST_COMPLETED)
        for t in done:
            try:
                r=t.result()
                if r:
                    text=r
                    break
            except Exception as e:
                log.warning("race task: "+str(e))
        if text: break
    for t in tasks:
        if not t.done(): t.cancel()
    if not text:
        try: text=await fallback_coro
        except Exception as e: log.error("race fallback: "+str(e)); text=""
    else:
        # let fallback be garbage-collected without raising
        try: fallback_coro.close()
        except Exception: pass
    return text

class BullAgent:
    def __init__(self,cfg):
        self.cfg=cfg
        self._key_cd={}
        self._key_rr_g=0
        self._key_rr_q=0
    async def analyze(self,market_text):
        prompt="Analyze and make bullish case:\n"+market_text
        try:
            text=await _race(
                [self._gemini(prompt), self._groq(prompt)],
                self._claude(prompt))
            d=self._parse(text)
            side=d.get("side")
            if side not in ("long","flat"):
                log.warning("Bull: unparseable response → flat/25. raw="+(text or "")[:160].replace("\n"," "))
                return AgentVerdict("flat",25,"Unparseable: "+(text or "")[:200])
            conf=d.get("confidence")
            try: conf=int(conf)
            except: conf=50
            return AgentVerdict(side,conf,d.get("reasoning",text))
        except Exception as e: log.error("Bull: "+str(e)); return AgentVerdict("flat",25,"Error: "+str(e))
    async def _claude(self,prompt):
        import anthropic
        c=anthropic.AsyncAnthropic(api_key=self.cfg.ANTHROPIC_API_KEY)
        msg=await c.messages.create(model=self.cfg.BEAR_MODEL,max_tokens=300,system=BULL_SYS,messages=[{"role":"user","content":prompt}])
        return msg.content[0].text
    async def _groq(self,prompt):
        keys=list(getattr(self.cfg,"GROQ_API_KEYS",[]) or [])
        if not keys: return ""
        models=getattr(self.cfg,"BULL_MODELS_GROQ",None) or ["llama-3.3-70b-versatile"]
        now=time.time(); last_err=""
        for model in models:
            fresh=[k for k in keys if self._key_cd.get(("groq",model,k),0)<=now]
            if not fresh: continue
            self._key_rr_q=(self._key_rr_q+1)%len(fresh)
            ordered=fresh[self._key_rr_q:]+fresh[:self._key_rr_q]
            for api_key in ordered:
                try:
                    async with aiohttp.ClientSession() as s:
                        async with s.post("https://api.groq.com/openai/v1/chat/completions",
                            json={"model":model,"messages":[{"role":"system","content":BULL_SYS},{"role":"user","content":prompt}],"max_tokens":300,"temperature":0.3,"response_format":{"type":"json_object"}},
                            headers={"Authorization":"Bearer "+api_key,"Content-Type":"application/json"},
                            timeout=aiohttp.ClientTimeout(total=20)) as r:
                            try: d=await r.json()
                            except: d={}
                            if r.status==429:
                                self._key_cd[("groq",model,api_key)]=time.time()+3600
                                last_err=model+" 429 ("+api_key[:10]+")"; continue
                            if r.status==401:
                                for m in models: self._key_cd[("groq",m,api_key)]=time.time()+86400
                                last_err=model+" 401 "+api_key[:10]; continue
                            if r.status!=200:
                                last_err=model+" "+str(r.status); continue
                            txt=(d.get("choices") or [{}])[0].get("message",{}).get("content","").strip()
                            if txt: return txt
                            last_err=model+" empty"
                except Exception as e:
                    last_err=model+" exc: "+str(e)[:80]; continue
        if last_err: log.debug("Bull-Groq: "+last_err)
        return ""
    async def _gemini(self,prompt):
        keys=[k for k in (getattr(self.cfg,'GEMINI_API_KEYS',None) or [self.cfg.GEMINI_API_KEY]) if k]
        now=time.time()
        models=getattr(self.cfg,'BULL_MODELS_FALLBACK',None) or [self.cfg.BULL_MODEL]
        last_err=""
        for model in models:
            fresh=[k for k in keys if self._key_cd.get(("gemini",model,k),0)<=now]
            if fresh:
                self._key_rr_g=(self._key_rr_g+1)%len(fresh)
                ordered=fresh[self._key_rr_g:]+fresh[:self._key_rr_g]
            else:
                ordered=[]
            for api_key in ordered:
                url="https://generativelanguage.googleapis.com/v1beta/models/"+model+":generateContent"
                payload={"system_instruction":{"parts":[{"text":BULL_SYS}]},"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.3,"maxOutputTokens":500,"responseMimeType":"application/json","thinkingConfig":{"thinkingBudget":0}}}
                try:
                    async with aiohttp.ClientSession() as s:
                        async with s.post(url,json=payload,params={"key":api_key},timeout=aiohttp.ClientTimeout(total=20)) as r:
                            d=await r.json()
                            if r.status==429:
                                self._key_cd[("gemini",model,api_key)]=time.time()+3600
                                last_err=model+" 429 ("+api_key[:10]+")"; continue
                            if r.status==400:
                                blob=str(d)
                                if "API_KEY_INVALID" in blob:
                                    for m in models: self._key_cd[("gemini",m,api_key)]=time.time()+86400
                                    last_err="bad key "+api_key[:10]; continue
                                if "expired" in blob.lower():
                                    self._key_cd[("gemini",model,api_key)]=time.time()+86400
                                    last_err=model+" expired "+api_key[:10]; continue
                            if r.status!=200:
                                last_err=model+" "+str(r.status); continue
                            parts=(d.get("candidates") or [{}])[0].get("content",{}).get("parts") or []
                            text="".join(p.get("text","") for p in parts).strip()
                            if not text:
                                last_err=model+" empty"; continue
                            return text
                except Exception as e:
                    last_err=model+" exc: "+str(e)[:80]; continue
        if last_err: log.debug("Bull-Gemini: "+last_err)
        return ""
    def _parse(self,t):
        if not t: return {}
        t=re.sub(r"```json|```","",t).strip()
        try:
            d=json.loads(t)
            if isinstance(d,dict): return d
        except: pass
        m=re.search(r'\{[^{}]*?"side"\s*:\s*"(?:long|flat)"[^{}]*\}',t,re.IGNORECASE|re.DOTALL)
        if m:
            try: return json.loads(m.group(0))
            except: pass
        sm=re.search(r'"?side"?\s*:\s*"?(long|flat)"?',t,re.IGNORECASE)
        if sm:
            cm=re.search(r'"?confidence"?\s*:\s*(\d+)',t)
            return {"side":sm.group(1).lower(),"confidence":int(cm.group(1)) if cm else 50,"reasoning":t[:200]}
        return {}

class BearAgent:
    def __init__(self,cfg):
        self.cfg=cfg
        self._key_cd={}
        self._key_rr_q=0
        self._key_rr_g=0
    async def analyze(self,market_text):
        prompt="Analyze and make the bearish/cautious case for this market data:\n"+market_text
        try:
            text=await _race(
                [self._groq(prompt), self._gemini(prompt)],
                self._claude(prompt))
            d=self._parse(text)
            side=d.get("side")
            if side not in ("short","flat","long"):
                log.warning("Bear: unparseable response → flat/25. raw="+(text or "")[:160].replace("\n"," "))
                return AgentVerdict("flat",25,"Unparseable: "+(text or "")[:200])
            conf=d.get("confidence")
            try: conf=int(conf)
            except: conf=50
            return AgentVerdict(side,conf,d.get("reasoning",text))
        except Exception as e: log.error("Bear: "+str(e)); return AgentVerdict("flat",25,"Error: "+str(e))
    async def _groq(self,prompt):
        keys=list(getattr(self.cfg,"GROQ_API_KEYS",[]) or [])
        if not keys: return ""
        models=getattr(self.cfg,"BEAR_MODELS_GROQ",None) or ["llama-3.3-70b-versatile"]
        now=time.time(); last_err=""
        for model in models:
            fresh=[k for k in keys if self._key_cd.get(("groq",model,k),0)<=now]
            if not fresh: continue
            self._key_rr_q=(self._key_rr_q+1)%len(fresh)
            ordered=fresh[self._key_rr_q:]+fresh[:self._key_rr_q]
            for api_key in ordered:
                try:
                    async with aiohttp.ClientSession() as s:
                        async with s.post("https://api.groq.com/openai/v1/chat/completions",
                            json={"model":model,"messages":[{"role":"system","content":BEAR_SYS},{"role":"user","content":prompt}],"max_tokens":300,"temperature":0.3,"response_format":{"type":"json_object"}},
                            headers={"Authorization":"Bearer "+api_key,"Content-Type":"application/json"},
                            timeout=aiohttp.ClientTimeout(total=20)) as r:
                            try: d=await r.json()
                            except: d={}
                            if r.status==429:
                                self._key_cd[("groq",model,api_key)]=time.time()+3600
                                last_err=model+" 429 ("+api_key[:10]+")"; continue
                            if r.status==401:
                                for m in models: self._key_cd[("groq",m,api_key)]=time.time()+86400
                                last_err=model+" 401 "+api_key[:10]; continue
                            if r.status!=200:
                                last_err=model+" "+str(r.status); continue
                            txt=(d.get("choices") or [{}])[0].get("message",{}).get("content","").strip()
                            if txt: return txt
                            last_err=model+" empty"
                except Exception as e:
                    last_err=model+" exc: "+str(e)[:80]; continue
        if last_err: log.debug("Bear-Groq: "+last_err)
        return ""
    async def _gemini(self,prompt):
        keys=list(getattr(self.cfg,"GEMINI_API_KEYS",[]) or [])
        if not keys: return ""
        models=getattr(self.cfg,"BEAR_MODELS_GEMINI",None) or ["gemini-2.5-flash"]
        now=time.time(); last_err=""
        for model in models:
            fresh=[k for k in keys if self._key_cd.get(("gemini",model,k),0)<=now]
            if not fresh: continue
            self._key_rr_g=(self._key_rr_g+1)%len(fresh)
            ordered=fresh[self._key_rr_g:]+fresh[:self._key_rr_g]
            for api_key in ordered:
                url="https://generativelanguage.googleapis.com/v1beta/models/"+model+":generateContent"
                payload={"system_instruction":{"parts":[{"text":BEAR_SYS}]},"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.3,"maxOutputTokens":500,"responseMimeType":"application/json","thinkingConfig":{"thinkingBudget":0}}}
                try:
                    async with aiohttp.ClientSession() as s:
                        async with s.post(url,json=payload,params={"key":api_key},timeout=aiohttp.ClientTimeout(total=20)) as r:
                            d=await r.json()
                            if r.status==429:
                                self._key_cd[("gemini",model,api_key)]=time.time()+3600
                                last_err=model+" 429 ("+api_key[:10]+")"; continue
                            if r.status==400:
                                blob=str(d)
                                if "API_KEY_INVALID" in blob:
                                    for m in models: self._key_cd[("gemini",m,api_key)]=time.time()+86400
                                    last_err="bad key "+api_key[:10]; continue
                                if "expired" in blob.lower():
                                    self._key_cd[("gemini",model,api_key)]=time.time()+86400
                                    last_err=model+" expired "+api_key[:10]; continue
                            if r.status!=200:
                                last_err=model+" "+str(r.status); continue
                            parts=(d.get("candidates") or [{}])[0].get("content",{}).get("parts") or []
                            txt="".join(p.get("text","") for p in parts).strip()
                            if txt: return txt
                            last_err=model+" empty"
                except Exception as e:
                    last_err=model+" exc: "+str(e)[:80]; continue
        if last_err: log.debug("Bear-Gemini: "+last_err)
        return ""
    async def _claude(self,prompt):
        import anthropic
        c=anthropic.AsyncAnthropic(api_key=self.cfg.ANTHROPIC_API_KEY)
        msg=await c.messages.create(model=self.cfg.BEAR_MODEL,max_tokens=300,system=BEAR_SYS,messages=[{"role":"user","content":prompt}])
        return msg.content[0].text
    def _parse(self,t):
        if not t: return {}
        t=re.sub(r"```json|```","",t).strip()
        try:
            d=json.loads(t)
            if isinstance(d,dict): return d
        except: pass
        m=re.search(r'\{[^{}]*?"side"\s*:\s*"(?:short|flat|long)"[^{}]*\}',t,re.IGNORECASE|re.DOTALL)
        if m:
            try: return json.loads(m.group(0))
            except: pass
        sm=re.search(r'"?side"?\s*:\s*"?(short|flat|long)"?',t,re.IGNORECASE)
        if sm:
            cm=re.search(r'"?confidence"?\s*:\s*(\d+)',t)
            return {"side":sm.group(1).lower(),"confidence":int(cm.group(1)) if cm else 50,"reasoning":t[:200]}
        t2=t.strip().lower()
        if t2 in ("long","short","flat","hold"): return {"side":t2,"confidence":60,"reasoning":t2}
        return {}

class Judge:
    def __init__(self,cfg):
        self.cfg=cfg
        self._key_cd={}
        self._key_rr=0
    async def _groq(self,prompt,system_prompt="",json_mode=False,max_tokens=200,temperature=0.2):
        keys=list(getattr(self.cfg,"GROQ_API_KEYS",[]) or [])
        if not keys: return ""
        models=getattr(self.cfg,"JUDGE_MODELS_GROQ",None) or ["llama-3.3-70b-versatile"]
        now=time.time()
        last_err=""
        for model in models:
            fresh=[k for k in keys if self._key_cd.get((model,k),0)<=now]
            if not fresh: continue
            self._key_rr=(self._key_rr+1)%len(fresh)
            ordered=fresh[self._key_rr:]+fresh[:self._key_rr]
            for api_key in ordered:
                url="https://api.groq.com/openai/v1/chat/completions"
                msgs=[]
                if system_prompt: msgs.append({"role":"system","content":system_prompt})
                msgs.append({"role":"user","content":prompt})
                payload={"model":model,"messages":msgs,"max_tokens":max_tokens,"temperature":temperature}
                if json_mode: payload["response_format"]={"type":"json_object"}
                headers={"Authorization":"Bearer "+api_key,"Content-Type":"application/json"}
                try:
                    async with aiohttp.ClientSession() as s:
                        async with s.post(url,json=payload,headers=headers,timeout=aiohttp.ClientTimeout(total=20)) as r:
                            try: d=await r.json()
                            except: d={}
                            if r.status==429:
                                self._key_cd[(model,api_key)]=time.time()+3600
                                last_err=model+" 429 ("+api_key[:10]+" cooldown 1h)"; continue
                            if r.status==401:
                                for m in models: self._key_cd[(m,api_key)]=time.time()+86400
                                last_err=model+" 401 bad key "+api_key[:10]; continue
                            if r.status!=200:
                                last_err=model+" status "+str(r.status)+": "+str(d)[:120]; continue
                            text=(d.get("choices") or [{}])[0].get("message",{}).get("content","").strip()
                            if not text:
                                last_err=model+" empty"; continue
                            return text
                except Exception as e:
                    last_err=model+" exc: "+str(e)[:120]; continue
        if last_err: log.warning("Judge-Groq all failed: "+last_err)
        return ""
    async def decide(self,market_text,bull,bear,memory_ctx):
        prompt="## Market\n"+market_text+"\n\n## BULL ("+str(bull.confidence)+"%)\n"+bull.reasoning+"\n\n## BEAR ("+str(bear.confidence)+"%)\n"+bear.reasoning+"\n\n## Memory\n"+memory_ctx+"\n\nMake your final decision."
        try:
            r=await self._claude(prompt)
            d=self._parse(r)
            return JudgeDecision(d.get("action","hold"),int(d.get("confidence",50)),float(d.get("position_size_pct",0.03)),d.get("reasoning",r),d.get("lessons_from_memory",""))
        except Exception as e: log.error("Judge: "+str(e)); return JudgeDecision("hold",0,0,"Error: "+str(e),"")
    async def reflect(self,trade,outcome):
        prompt="Trade closed: "+trade.symbol+" "+trade.side+" PnL:"+str(round(trade.pnl_pct or 0,2))+"% Regime:"+trade.regime+"\nOriginal reasoning:"+trade.judge_reasoning+"\nOutcome:"+outcome+"\nIn 2-3 sentences what should be remembered? Plain text only, no JSON, no markdown fences."
        try:
            r=await self._groq(prompt,system_prompt="You write terse trade postmortems. Plain text, no JSON, no fences.",max_tokens=200,temperature=0.3)
            if not r: r=(await self._claude(prompt)).strip()
            return re.sub(r"```json|```","",r).strip()
        except Exception as e: return "Reflection error: "+str(e)
    async def ask_exit(self,trade,current_price,pnl_pct,peak_pnl=None):
        peak_txt=(" Peak-since-open: "+str(round(peak_pnl,2))+"%") if peak_pnl is not None else ""
        prompt=("Open "+trade.side.upper()+" "+trade.symbol+" Entry:"+str(trade.entry_price)+" Current:"+str(current_price)
                +" PnL:"+str(round(pnl_pct,2))+"%"+peak_txt+" Opened:"+trade.opened_at
                +"\nOriginal thesis: "+trade.judge_reasoning[:300]
                +"\n\nDefault is HOLD. TP=+3%, SL=-3%, trailing-stop handle everything in between. "
                +"Exit ONLY if BOTH conditions are true: (1) the original thesis is now clearly invalidated by a structural shift "
                +"(major regime change, key level break against position, decisive volume reversal), AND "
                +"(2) PnL is already adverse (>1% against entry) OR a clear topping/bottoming pattern is forming. "
                +"NEVER exit on small fluctuations, sideways noise, or because price merely paused. "
                +"If profitable: HOLD — let trailing-stop work. If unprofitable but thesis intact: HOLD — let SL work."
                +"\nRespond ONLY: EXIT or HOLD")
        try:
            r=await self._groq(prompt,system_prompt="You decide whether to close an open trade. Respond with exactly one word: EXIT or HOLD.",max_tokens=8,temperature=0.1)
            if not r: r=await self._claude(prompt)
            return "EXIT" in r.upper()
        except: return False
    async def ask_direction(self,trade,current_price,pnl_pct):
        prompt=("Open "+trade.side.upper()+" "+trade.symbol+" Entry:"+str(trade.entry_price)+" Current:"+str(current_price)
                +" PnL:"+str(round(pnl_pct,2))+"%\nThesis: "+(trade.judge_reasoning or "")[:300]
                +"\nWhat is your CURRENT directional view on "+trade.symbol+" right now? Respond ONE WORD only: LONG, SHORT, or HOLD.")
        try:
            r=await self._groq(prompt,system_prompt="You assess current market direction. Respond with exactly one word: LONG, SHORT, or HOLD.",max_tokens=8,temperature=0.1)
            if not r: r=await self._claude(prompt)
            u=r.upper()
            if "SHORT" in u: return "short"
            if "LONG" in u: return "long"
            return "hold"
        except Exception as e:
            log.error("ask_direction: "+str(e)); return "hold"
    async def _claude(self,prompt):
        import anthropic
        c=anthropic.AsyncAnthropic(api_key=self.cfg.ANTHROPIC_API_KEY)
        msg=await c.messages.create(model=self.cfg.JUDGE_MODEL,max_tokens=400,temperature=0.3,system=JUDGE_SYS,messages=[{"role":"user","content":prompt}])
        return msg.content[0].text
    def _parse(self,t):
        t=re.sub(r"```json|```","",t).strip()
        try: return json.loads(t)
        except: pass
        m=re.search(r"\{[^{}]*?\"action\"[^{}]*\}",t,re.DOTALL)
        if m:
            try: return json.loads(m.group(0))
            except: pass
        m=re.search(r"\"action\"\s*:\s*\"(long|short|hold)\"",t,re.IGNORECASE)
        if m:
            action=m.group(1).lower()
            cm=re.search(r"\"confidence\"\s*:\s*(\d+)",t)
            sm=re.search(r"\"position_size_pct\"\s*:\s*([\d.]+)",t)
            return {"action":action,"confidence":int(cm.group(1)) if cm else 60,"position_size_pct":float(sm.group(1)) if sm else (0.06 if action!="hold" else 0.0),"reasoning":t[:200]}
        log.warning("Judge JSON unparseable, defaulting to hold: "+t[:120].replace("\n"," "))
        return {"reasoning":t}

```

## audit.py
```python
#!/usr/bin/env python3
"""Daily/weekly audit + safe auto-fixes for ensemble-agent.

Usage: audit.py [daily|weekly]
Writes report to /opt/ensemble-agent/audit.log
Safe fixes: restart service on crash, rotate ensemble.log if >50MB,
mark Gemini keys as exhausted (sets EXHAUSTED_<key>=1 to be read by agent later).
"""
import sys, os, re, json, subprocess, gzip, shutil, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone
from collections import Counter
from pathlib import Path
from dotenv import load_dotenv
load_dotenv("/opt/ensemble-agent/.env")

ROOT = Path("/opt/ensemble-agent")
LOG = ROOT / "ensemble.log"
REPORT = ROOT / "audit.log"
DASH_LOG = ROOT / "dashboard.log"
PAPER_STATE = ROOT / "paper_state.json"

BEAR_COST = 0.00121
JUDGE_COST = 0.00170
SERVICES = ["ensemble-agent.service", "ensemble-dashboard.service"]


def now():
    return datetime.now(timezone.utc)


def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def append(lines):
    with open(REPORT, "a") as f:
        f.write("\n".join(lines) + "\n")


def telegram(text):
    token = os.getenv("TELEGRAM_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": chat,
            "text": text[:4000],
            "disable_web_page_preview": "true",
        }).encode()
        urllib.request.urlopen(url, data=data, timeout=10)
    except Exception:
        pass


def check_services():
    out, fixes = [], []
    for svc in SERVICES:
        r = run(f"systemctl is-active {svc}")
        state = r.stdout.strip()
        out.append(f"  {svc:35s} {state}")
        if state != "active":
            run(f"systemctl restart {svc}")
            fixes.append(f"restarted {svc} (was {state})")
    return out, fixes


def parse_log_window(hours):
    if not LOG.exists():
        return None
    cutoff = now() - timedelta(hours=hours)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
    cycles = Counter()
    judge_actions = Counter()
    judge_confs = []
    errors = Counter()
    trades_opened = 0
    trades_closed = 0
    judge_calls = 0
    bull_calls = 0
    bear_calls = 0
    last_scan_marker = None
    next_scan_modes = Counter()
    with open(LOG, "r", errors="ignore") as f:
        for line in f:
            if len(line) < 19 or line[:19] < cutoff_str:
                continue
            if " | Bull:" in line and " Bear:" in line:
                bull_calls += 1; bear_calls += 1
            if re.search(r"Judge:(LONG|SHORT|HOLD) conf=(\d+)%", line):
                m = re.search(r"Judge:(LONG|SHORT|HOLD) conf=(\d+)%", line)
                judge_calls += 1
                judge_actions[m.group(1)] += 1
                judge_confs.append(int(m.group(2)))
            if "[ERROR]" in line:
                if "Bull:" in line: errors["bull"] += 1
                elif "Bear:" in line: errors["bear"] += 1
                elif "Judge:" in line: errors["judge"] += 1
                else: errors["other"] += 1
            if "[PAPER] ОТКРЫТА" in line: trades_opened += 1
            if "[PAPER]" in line and "ЗАКРЫТА" in line: trades_closed += 1
            if "Scanning " in line: cycles["scans"] += 1
            m2 = re.search(r"Next scan in \d+min \((\w+[-\w]*)\)", line)
            if m2: next_scan_modes[m2.group(1)] += 1
            if "All keys/models failed" in line.lower() or "all keys/models failed" in line:
                errors["gemini_all_keys_failed"] += 1
    avg_conf = round(sum(judge_confs)/len(judge_confs), 1) if judge_confs else 0
    cost = bear_calls*BEAR_COST + judge_calls*JUDGE_COST
    return {
        "scans": cycles["scans"], "bull": bull_calls, "bear": bear_calls,
        "judge": judge_calls, "judge_actions": dict(judge_actions),
        "avg_judge_conf": avg_conf, "errors": dict(errors),
        "trades_opened": trades_opened, "trades_closed": trades_closed,
        "scan_modes": dict(next_scan_modes),
        "anthropic_cost": round(cost, 3),
    }


def rotate_log_if_big():
    fixes = []
    for path in [LOG, DASH_LOG]:
        if path.exists() and path.stat().st_size > 50 * 1024 * 1024:
            ts = now().strftime("%Y%m%d-%H%M%S")
            gz = path.with_name(f"{path.name}.{ts}.gz")
            with open(path, "rb") as src, gzip.open(gz, "wb") as dst:
                shutil.copyfileobj(src, dst)
            path.write_text("")
            fixes.append(f"rotated {path.name} ({gz.name})")
    return fixes


def check_paper():
    if not PAPER_STATE.exists():
        return ["  paper_state.json missing"]
    try:
        s = json.loads(PAPER_STATE.read_text())
        bal = s.get("balance", 0)
        pos = s.get("positions", {})
        hist = s.get("trade_history", [])
        wins = sum(1 for t in hist if t.get("pnl_pct", 0) > 0)
        wr = round(wins / len(hist) * 100, 1) if hist else 0
        return [f"  balance=${bal:.2f}  open={len(pos)}  closed={len(hist)}  win_rate={wr}%"]
    except Exception as e:
        return [f"  paper_state read error: {e}"]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "daily"
    hours = 24 if mode == "daily" else 168
    stamp = now().strftime("%Y-%m-%d %H:%M UTC")
    out = ["=" * 70, f"=== {mode.upper()} AUDIT {stamp} (window: {hours}h) ===", "=" * 70]

    out.append("\n[services]")
    svc_lines, svc_fixes = check_services()
    out.extend(svc_lines)

    out.append("\n[bot activity]")
    stats = parse_log_window(hours)
    if stats:
        out.append(f"  scans={stats['scans']}  Bull={stats['bull']}  Bear={stats['bear']}  Judge={stats['judge']}")
        out.append(f"  judge_actions={stats['judge_actions']}  avg_conf={stats['avg_judge_conf']}%")
        out.append(f"  trades opened={stats['trades_opened']}  closed={stats['trades_closed']}")
        out.append(f"  scan_modes={stats['scan_modes']}")
        out.append(f"  errors={stats['errors']}")
        out.append(f"  anthropic_cost=${stats['anthropic_cost']}")
    else:
        out.append("  (no log)")

    out.append("\n[paper trading]")
    out.extend(check_paper())

    out.append("\n[auto-fixes applied]")
    fixes = list(svc_fixes)
    fixes.extend(rotate_log_if_big())
    if not fixes:
        out.append("  (none)")
    else:
        for f in fixes:
            out.append(f"  - {f}")

    out.append("\n[warnings]")
    warnings = []
    if stats:
        if stats["judge"] == 0 and stats["scans"] > 0:
            warnings.append("Judge never called — gate misconfig or all snapshots empty")
        if stats["errors"].get("gemini_all_keys_failed", 0) > 5:
            warnings.append("Gemini all-keys-failed >5 times — check quotas / GEMINI_API_KEY3 still disabled")
        for k in ("bull", "bear", "judge"):
            if stats["errors"].get(k, 0) > 10:
                warnings.append(f"{k} errors >10 in window — investigate raw responses")
        if stats["anthropic_cost"] > (2.5 if mode == "daily" else 15.0):
            warnings.append(f"anthropic_cost ${stats['anthropic_cost']} above expected band — schedule may have drifted")
    if not warnings:
        out.append("  (clean)")
    else:
        for w in warnings:
            out.append(f"  ! {w}")

    out.append("")
    append(out)

    # Send summary to Telegram (compact form)
    has_warnings = bool(warnings)
    has_fixes = bool(fixes)
    tg_lines = [
        f"📊 {mode.upper()} audit · {stamp}",
        f"services: " + ", ".join(f"{s.split('.')[0]}=ok" if "active" in l else f"{s.split('.')[0]}=!" for s, l in zip(SERVICES, svc_lines)),
    ]
    if stats:
        tg_lines.append(
            f"bot: scans={stats['scans']} Judge={stats['judge']} "
            f"actions={stats['judge_actions']} avg_conf={stats['avg_judge_conf']}%"
        )
        tg_lines.append(f"trades: opened={stats['trades_opened']} closed={stats['trades_closed']}")
        tg_lines.append(f"cost: ${stats['anthropic_cost']} ({mode})")
        if stats["errors"]:
            tg_lines.append(f"errors: {stats['errors']}")
    if has_fixes:
        tg_lines.append("auto-fixes: " + "; ".join(fixes))
    if has_warnings:
        tg_lines.append("⚠️ warnings:")
        tg_lines.extend(f"  - {w}" for w in warnings)
    else:
        tg_lines.append("✅ clean")
    telegram("\n".join(tg_lines))


if __name__ == "__main__":
    main()

```

## bitget_client.py
```python
import hmac,hashlib,base64,time,aiohttp,logging
log=logging.getLogger("bitget")
class BitgetClient:
 def __init__(self,cfg):
  self.cfg=cfg;self.base=cfg.BITGET_BASE_URL;self.session=None
 async def start(self):self.session=aiohttp.ClientSession()
 async def close(self):
  if self.session:await self.session.close()
 def _sign(self,ts,method,path,body=""):
  import hmac,hashlib,base64
  msg=f"{ts}{method.upper()}{path}{body}"
  return base64.b64encode(hmac.new(self.cfg.BITGET_SECRET.encode(),msg.encode(),hashlib.sha256).digest()).decode()
 def _headers(self,method,path,body=""):
  import time;ts=str(int(time.time()*1000))
  return {"ACCESS-KEY":self.cfg.BITGET_API_KEY,"ACCESS-SIGN":self._sign(ts,method,path,body),"ACCESS-TIMESTAMP":ts,"ACCESS-PASSPHRASE":self.cfg.BITGET_PASSPHRASE,"Content-Type":"application/json","locale":"en-US"}
 async def get(self,path,params=None):
  async with self.session.get(self.base+path,headers=self._headers("GET",path),params=params) as r:return await r.json()
 async def post(self,path,body):
  import json;bs=json.dumps(body)
  async with self.session.post(self.base+path,headers=self._headers("POST",path,bs),data=bs) as r:return await r.json()
 async def get_top_symbols(self,n=50):
  data=await self.get("/api/v2/mix/market/tickers",{"productType":"USDT-FUTURES"})
  try:
   contracts=await self.get("/api/v2/mix/market/contracts",{"productType":"USDT-FUTURES"})
   rwa={c["symbol"] for c in contracts.get("data",[]) if c.get("isRwa")=="YES"}
  except Exception as e:
   log.warning("contracts fetch failed, no RWA filter: "+str(e)); rwa=set()
  rows=[x for x in data.get("data",[]) if x["symbol"] not in rwa]
  t=sorted(rows,key=lambda x:float(x.get("usdtVolume",0)),reverse=True)
  return [x["symbol"] for x in t[:n]]
 async def get_candles(self,symbol,granularity="15m",limit=100):
  data=await self.get("/api/v2/mix/market/candles",{"symbol":symbol,"productType":"USDT-FUTURES","granularity":granularity,"limit":str(limit)})
  return data.get("data",[])
 async def get_orderbook(self,symbol,limit=20):
  data=await self.get("/api/v2/mix/market/merge-depth",{"symbol":symbol,"productType":"USDT-FUTURES","limit":str(limit)})
  return data.get("data",{})
 async def get_funding_rate(self,symbol):
  data=await self.get("/api/v2/mix/market/current-fund-rate",{"symbol":symbol,"productType":"USDT-FUTURES"})
  try:return float(data["data"][0]["fundingRate"])
  except:return 0.0
 async def get_account_balance(self):
  data=await self.get("/api/v2/mix/account/accounts",{"productType":"USDT-FUTURES"})
  try:return float(data["data"][0]["usdtEquity"])
  except:return 0.0
 async def get_positions(self):
  data=await self.get("/api/v2/mix/position/all-position",{"productType":"USDT-FUTURES"})
  return [p for p in (data or {}).get("data",[]) if float(p.get("total",0))>0]
 async def place_order(self,symbol,side,size,leverage=5):
  await self.post("/api/v2/mix/account/set-leverage",{"symbol":symbol,"productType":"USDT-FUTURES","marginCoin":"USDT","leverage":str(leverage),"holdSide":side})
  t=await self.get("/api/v2/mix/market/ticker",{"symbol":symbol,"productType":"USDT-FUTURES"})
  price=float(t["data"][0]["lastPr"]);qty=round(size/price,4)
  return await self.post("/api/v2/mix/order/place-order",{"symbol":symbol,"productType":"USDT-FUTURES","marginMode":"isolated","marginCoin":"USDT","size":str(qty),"side":"open_long" if side=="long" else "open_short","orderType":"market","tradeSide":"open"})
 async def close_position(self,symbol,side):
  return await self.post("/api/v2/mix/order/place-order",{"symbol":symbol,"productType":"USDT-FUTURES","marginMode":"isolated","marginCoin":"USDT","size":"0","side":"close_long" if side=="long" else "close_short","orderType":"market","tradeSide":"close","reduceOnly":"YES"})

```

## config.py
```python
import os
from dotenv import load_dotenv
load_dotenv("/opt/ensemble-agent/.env")
class Config:
    BITGET_API_KEY = os.getenv("BITGET_API_KEY")
    BITGET_SECRET = os.getenv("BITGET_SECRET")
    BITGET_PASSPHRASE = os.getenv("BITGET_PASSPHRASE")
    BITGET_BASE_URL = "https://api.bitget.com"
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_API_KEY2 = os.getenv("GEMINI_API_KEY2")
    GEMINI_API_KEYS = [k for k in [os.getenv("GEMINI_API_KEY"+(str(i) if i>1 else "")) for i in range(1,6)] if k]
    GROQ_API_KEYS = [k for k in [os.getenv("GROQ_API_KEY"+(str(i) if i>1 else "")) for i in range(1,6)] if k]
    BULL_MODEL = "gemini-2.5-flash"
    BULL_MODELS_FALLBACK = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash-lite"]
    BULL_MODELS_GROQ = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b"]
    BEAR_MODELS_GROQ = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b"]
    BEAR_MODELS_GEMINI = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash-lite"]
    JUDGE_MODELS_GROQ = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b"]
    BEAR_MODEL = "claude-haiku-4-5-20251001"
    JUDGE_MODEL = "claude-haiku-4-5-20251001"
    TOP_N_SYMBOLS = 30
    SCAN_INTERVAL = 3600
    MAX_POSITIONS = 5
    MAX_SAME_SIDE = 3
    MIN_CONFIDENCE = 70
    THRESHOLD_SLACK = 3
    MIN_HOLD_SEC = 7200
    JUDGE_EXIT_INTERVAL_SEC = 3600
    JUDGE_EXIT_NOISE_BAND_PCT = 1.0
    STOP_LOSS_PCT = -3.0
    TAKE_PROFIT_PCT = 3.0
    TRAIL_ARM_PCT = 1.5
    TRAIL_GIVEBACK_PCT = 1.0
    EMERGENCY_STOP_PCT = -15.0
    PAPER_MODE = True
    PAPER_BALANCE = 1000.0
    LEVERAGE = 5
    RL_PRIME_FROM_HISTORY = False
    MEMORY_FILE = "/opt/ensemble-agent/memory.json"
    TRADE_LOG = "/opt/ensemble-agent/trade_log.json"
    STATE_FILE = "/opt/ensemble-agent/state.json"
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Paper Trading Mode
PAPER_MODE = True
PAPER_BALANCE = 1000.0  # виртуальный баланс в USDT

```

## dashboard_api.py
```python
import asyncio, json, re, os, logging, time
from datetime import datetime
from aiohttp import web, ClientSession, ClientTimeout
from dotenv import load_dotenv
load_dotenv("/opt/ensemble-agent/.env")
from config import PAPER_BALANCE
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("dashboard")

LOG_FILE = "/opt/ensemble-agent/ensemble.log"
STATE_FILE = "/opt/ensemble-agent/paper_state.json"

_price_cache = {}  # symbol -> (price, ts)
_PRICE_TTL = 20    # seconds


async def _fetch_mark_price(session, symbol):
    cached = _price_cache.get(symbol)
    if cached and time.time() - cached[1] < _PRICE_TTL:
        return cached[0]
    url = "https://api.bitget.com/api/v2/mix/market/ticker"
    try:
        async with session.get(url, params={"symbol": symbol, "productType": "USDT-FUTURES"}, timeout=ClientTimeout(total=4)) as r:
            data = await r.json()
            arr = data.get("data") or []
            if arr:
                price = float(arr[0].get("lastPr") or arr[0].get("markPrice") or 0)
                if price > 0:
                    _price_cache[symbol] = (price, time.time())
                    return price
    except Exception as e:
        log.warning(f"mark price {symbol}: {e}")
    return None


async def _enrich_positions(positions):
    if not positions:
        return [], 0.0
    async with ClientSession() as session:
        prices = await asyncio.gather(*[_fetch_mark_price(session, p["symbol"]) for p in positions])
    enriched = []
    unrealized_total = 0.0
    for pos, price in zip(positions, prices):
        entry = float(pos.get("entry_price") or 0)
        qty = float(pos.get("qty") or 0)
        side = pos.get("side", "long")
        mark = price if price else entry
        if side == "long":
            pnl_usdt = (mark - entry) * qty
        else:
            pnl_usdt = (entry - mark) * qty
        pnl_pct = ((mark - entry) / entry * 100 * (1 if side == "long" else -1)) if entry else 0
        age_sec = 0
        try:
            opened = datetime.fromisoformat(pos["opened_at"])
            age_sec = int((datetime.utcnow() - opened).total_seconds())
        except Exception:
            pass
        enriched.append({
            **pos,
            "mark_price": round(mark, 6),
            "live_pnl_usdt": round(pnl_usdt, 2),
            "live_pnl_pct": round(pnl_pct, 2),
            "age_sec": age_sec,
            "stale_price": price is None,
        })
        unrealized_total += pnl_usdt
    return enriched, round(unrealized_total, 2)


def parse_log():
    decisions = {}
    judge_confs = []
    errors = {"bull": 0, "bear": 0, "judge": 0}
    opens = []   # [PAPER] ОТКРЫТА ...
    closes = []  # [PAPER] ЗАКРЫТА ...
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()[-1500:]
    except Exception:
        return {}
    for line in lines:
        m = re.search(r"main: (\w+) \| Bull:(\w+)\((\d+)%\) Bear:(\w+)\((\d+)%\)", line)
        if m:
            sym, bs, bc, rs, rc = m.groups()
            decisions[sym] = {"symbol": sym, "bull_side": bs, "bull_conf": int(bc),
                              "bear_side": rs, "bear_conf": int(rc),
                              "judge_action": "HOLD", "judge_conf": 0, "time": line[:23]}
        m2 = re.search(r"main: (\w+) \| Judge:(\w+) conf=(\d+)%", line)
        if m2:
            sym, action, conf = m2.groups()
            if sym in decisions:
                decisions[sym]["judge_action"] = action
                decisions[sym]["judge_conf"] = int(conf)
            judge_confs.append(int(conf))
        if "[PAPER] ОТКРЫТА" in line:
            opens.append(line[:23] + " " + line.split("[PAPER]")[1].strip())
        if "[PAPER]" in line and "ЗАКРЫТА" in line:
            closes.append(line[:23] + " " + line.split("[PAPER]")[1].strip())
        if "[ERROR] agents: Bull:" in line: errors["bull"] += 1
        if "[ERROR] agents: Bear:" in line: errors["bear"] += 1
        if "[ERROR] agents: Judge:" in line: errors["judge"] += 1
    avg_conf = round(sum(judge_confs) / len(judge_confs)) if judge_confs else 0
    recent = sorted(decisions.values(), key=lambda x: x["time"], reverse=True)
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "symbols_scanned": len(decisions),
        "avg_judge_conf": avg_conf,
        "errors": errors,
        "decisions": recent[:50],
        "top_confident": sorted(recent, key=lambda x: x["judge_conf"], reverse=True)[:15],
        "log_opens": opens[-10:],
        "log_closes": closes[-10:],
    }


async def handle_html(request):
    return web.FileResponse("/opt/ensemble-agent/dashboard.html", headers={
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    })


async def handle_api(request):
    data = parse_log()
    return web.Response(text=json.dumps(data, ensure_ascii=False),
                        content_type="application/json",
                        headers={"Access-Control-Allow-Origin": "*"})


async def handle_options(request):
    return web.Response(headers={"Access-Control-Allow-Origin": "*",
                                 "Access-Control-Allow-Methods": "GET",
                                 "Access-Control-Allow-Headers": "Content-Type"})


def _load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"balance": PAPER_BALANCE, "positions": {}, "trade_history": [], "total_pnl": 0.0}


async def parse_paper():
    state = _load_state()
    positions = list(state.get("positions", {}).values())
    history = state.get("trade_history", [])
    enriched, unrealized = await _enrich_positions(positions)
    realized = round(float(state.get("total_pnl", 0.0)), 2)
    wins = sum(1 for t in history if t.get("outcome") == "profit")
    losses = sum(1 for t in history if t.get("outcome") == "loss")
    wr = round(wins / len(history) * 100, 1) if history else 0
    balance = round(float(state.get("balance", PAPER_BALANCE)), 2)
    equity = round(balance + sum(p["cost"] for p in positions) + unrealized, 2)
    recent = []
    for t in history[-20:][::-1]:
        recent.append({
            "symbol": t.get("symbol"),
            "side": t.get("side"),
            "entry_price": t.get("entry_price"),
            "exit_price": t.get("exit_price"),
            "qty": t.get("qty"),
            "pnl_pct": t.get("pnl_pct"),
            "pnl_usdt": t.get("pnl_usdt"),
            "reason": t.get("reason"),
            "outcome": t.get("outcome"),
            "opened_at": t.get("opened_at"),
            "closed_at": t.get("closed_at"),
        })
    return {
        "balance": balance,
        "equity": equity,
        "start_balance": PAPER_BALANCE,
        "realized_pnl": realized,
        "unrealized_pnl": unrealized,
        "total_pnl": round(realized + unrealized, 2),
        "trades": len(history),
        "wins": wins,
        "losses": losses,
        "win_rate": wr,
        "open_positions": len(positions),
        "positions": enriched,
        "recent_trades": recent,
        "timestamp": datetime.now().isoformat(),
    }


async def handle_paper(request):
    data = await parse_paper()
    return web.Response(text=json.dumps(data, ensure_ascii=False),
                        content_type="application/json",
                        headers={"Access-Control-Allow-Origin": "*"})


app = web.Application()
app.router.add_get("/ensemble-api", handle_api)
app.router.add_get("/paper-api", handle_paper)
app.router.add_get("/", handle_html)
app.router.add_options("/ensemble-api", handle_options)
app.router.add_options("/paper-api", handle_options)

if __name__ == "__main__":
    print("Ensemble API on port 8765")
    access_logger = logging.getLogger("aiohttp.access")
    access_logger.setLevel(logging.INFO)
    web.run_app(app, host="0.0.0.0", port=8765, access_log=access_logger,
                access_log_format='%a "%r" %s %b "%{User-Agent}i"')

```

## data_engine.py
```python
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
    def _ema_series(self,d,p):
        k=2/(p+1); out=[d[0]]
        for v in d[1:]: out.append(v*k+out[-1]*(1-k))
        return out
    def _macd(self,c):
        if len(c)<35: return "neutral"
        ema12=self._ema_series(c,12); ema26=self._ema_series(c,26)
        macd_line=[a-b for a,b in zip(ema12[-len(ema26):],ema26)]
        if len(macd_line)<9: return "neutral"
        signal=self._ema(macd_line[-9:],9)
        m=macd_line[-1]
        eps=max(abs(m),abs(signal),1e-9)*0.001
        if m>signal+eps: return "bullish"
        if m<signal-eps: return "bearish"
        return "neutral"
    def _bb(self,c,p=20):
        if len(c)<p: return 0.5
        w=c[-p:]; mn=float(np.mean(w)); sd=float(np.std(w))
        return 0.5 if sd==0 else (c[-1]-(mn-2*sd))/(4*sd)
    def _regime(self,c):
        if len(c)<40: return "ranging"
        cv=float(np.std(c[-40:])/np.mean(c[-40:]))
        ma10=float(np.mean(c[-10:])); ma40=float(np.mean(c[-40:]))
        if cv>0.03: return "volatile"
        return "trending_up" if ma10>ma40*1.005 else ("trending_down" if ma10<ma40*0.995 else "ranging")

```

## main.py
```python
#!/usr/bin/env python3
import asyncio,logging,signal,sys,random
from datetime import datetime,timezone
from config import Config
from bitget_client import BitgetClient
from data_engine import DataEngine
from agents import BullAgent,BearAgent,Judge
from memory import Memory
from rl_agent import RLAgent
from position_manager import PositionManager

logging.basicConfig(level=logging.INFO,format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("/opt/ensemble-agent/ensemble.log")])
log=logging.getLogger("main")

class Orchestrator:
    def __init__(self):
        self.cfg=Config(); self.bitget=BitgetClient(self.cfg)
        self.data=DataEngine(self.bitget); self.bull=BullAgent(self.cfg)
        self.bear=BearAgent(self.cfg); self.judge=Judge(self.cfg)
        self.memory=Memory(self.cfg)
        self.rl=RLAgent(self.cfg)
        self.positions=PositionManager(self.bitget,self.cfg,self.memory,self.judge,self.rl)
        self.running=True; self.symbols=[]; self._stop_event=asyncio.Event()
    async def _wait(self,timeout):
        try: await asyncio.wait_for(self._stop_event.wait(),timeout=timeout)
        except asyncio.TimeoutError: pass
    async def start(self):
        await self.bitget.start()
        log.info("=== Adversarial Trading Agent started ===")
        bull_keys=len(getattr(self.cfg,"GEMINI_API_KEYS",[]) or [])
        groq_keys=len(getattr(self.cfg,"GROQ_API_KEYS",[]) or [])
        log.info("Bull: race(Gemini x"+str(bull_keys)+", Groq x"+str(groq_keys)+") → Haiku fb | Bear: race(Groq x"+str(groq_keys)+", Gemini x"+str(bull_keys)+") → Haiku fb | Judge: Haiku (decide) + Groq Llama (exit/dir/reflect)")
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
            try: await self.bitget.close()
            except Exception as e: log.error("bitget close: "+str(e))
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
            if snapshot.regime in ("volatile","unknown"):
                log.info(symbol+" | regime BLOCK ("+snapshot.regime+")"); return
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

```

## memory.py
```python
import json,logging,os,uuid,threading
from dataclasses import dataclass,asdict,field
from typing import Optional
from datetime import datetime
log=logging.getLogger("memory")
_MEM_LOCK=threading.RLock()

@dataclass
class TradeMemory:
    id:str; symbol:str; side:str; entry_price:float; exit_price:Optional[float]
    pnl_pct:Optional[float]; regime:str; rsi_at_entry:float; funding_at_entry:float
    volume_ratio_at_entry:float; bull_confidence:int; bear_confidence:int
    judge_confidence:int; judge_reasoning:str; outcome:Optional[str]
    opened_at:str; closed_at:Optional[str]; lessons:Optional[str]
    orphan:bool=False

class Memory:
    def __init__(self,cfg):
        self.path=cfg.MEMORY_FILE; self.trades=[]; self._load()
    def _load(self):
        with _MEM_LOCK:
            if os.path.exists(self.path):
                try:
                    data=json.load(open(self.path))
                    self.trades=[]
                    valid_fields=set(TradeMemory.__dataclass_fields__.keys())
                    for t in data:
                        clean={k:v for k,v in t.items() if k in valid_fields}
                        self.trades.append(TradeMemory(**clean))
                    log.info("Memory loaded: "+str(len(self.trades))+" trades")
                except Exception as e: log.error("Memory load: "+str(e)); self.trades=[]
    def _save(self):
        with _MEM_LOCK:
            try:
                tmp=self.path+".tmp"
                with open(tmp,"w") as f:
                    json.dump([asdict(t) for t in self.trades],f,indent=2,ensure_ascii=False)
                    f.flush(); os.fsync(f.fileno())
                os.replace(tmp,self.path)
            except Exception as e: log.error("Memory save: "+str(e))
    def add_trade(self,trade):
        with _MEM_LOCK: self.trades.append(trade); self._save()
    def update_trade(self,tid,**kw):
        with _MEM_LOCK:
            for t in self.trades:
                if t.id==tid:
                    for k,v in kw.items(): setattr(t,k,v)
                    self._save(); return
    def get_similar(self,snapshot,n=5):
        closed=[t for t in self.trades if t.outcome in ("profit","loss") and not getattr(t,"orphan",False)]
        if not closed: return []
        def score(t):
            s=3.0 if t.regime==snapshot.regime else 0.0
            s-=abs(t.rsi_at_entry-snapshot.rsi_15m)/100
            if (t.funding_at_entry>0)==(snapshot.funding_rate>0): s+=1.0
            return s
        return sorted(closed,key=score,reverse=True)[:n]
    def format_similar_for_judge(self,similar):
        if not similar: return "Memory: insufficient closed-trade history yet — base your decision on current Bull/Bear signals."
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

```

## paper_trading.py
```python
"""
Paper Trading Engine for Ensemble Agent
Симулирует торговлю без реальных ордеров
"""
import json
import os
import time
import threading
import logging
from datetime import datetime

log = logging.getLogger(__name__)

PAPER_STATE_FILE = "/opt/ensemble-agent/paper_state.json"
_STATE_LOCK = threading.RLock()

def _load_state():
    with _STATE_LOCK:
        try:
            with open(PAPER_STATE_FILE) as f:
                return json.load(f)
        except:
            return {
                "balance": 1000.0,
                "positions": {},
                "trade_history": [],
                "total_pnl": 0.0
            }

def _save_state(state):
    with _STATE_LOCK:
        tmp = PAPER_STATE_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(state, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, PAPER_STATE_FILE)

def paper_open(symbol, side, price, qty, confidence, leverage=5):
    """Открыть виртуальную позицию"""
    with _STATE_LOCK:
        state = _load_state()
        if symbol in state["positions"]:
            log.warning(f"[PAPER] Дубликат отклонён: {symbol} уже открыт ({state['positions'][symbol]['side']} @ {state['positions'][symbol]['entry_price']})")
            return None
        notional = price * qty
        margin = notional / max(leverage, 1)
        if margin > state["balance"]:
            log.warning(f"[PAPER] Недостаточно баланса: нужно {margin:.2f} margin, есть {state['balance']:.2f}")
            return None
        state["balance"] -= margin
        trade_id = f"PAPER_{symbol}_{int(time.time())}"
        state["positions"][symbol] = {
            "id": trade_id,
            "symbol": symbol,
            "side": side,
            "entry_price": price,
            "qty": qty,
            "confidence": confidence,
            "opened_at": datetime.utcnow().isoformat(),
            "cost": margin,
            "notional": notional,
            "leverage": leverage
        }
        _save_state(state)
        log.info(f"[PAPER] ОТКРЫТА {side.upper()} {symbol} @ {price:.4f} qty={qty} notional={notional:.2f} margin={margin:.2f} x{leverage} | Баланс: {state['balance']:.2f}")
        return trade_id

def paper_close(symbol, current_price, reason="judge_exit"):
    """Закрыть виртуальную позицию"""
    with _STATE_LOCK:
        state = _load_state()
        pos = state["positions"].get(symbol)
        if not pos:
            return None
        entry = pos["entry_price"]
        qty = pos["qty"]
        side = pos["side"]
        if side == "long":
            pnl = (current_price - entry) / entry * 100
            pnl_usdt = (current_price - entry) * qty
        else:
            pnl = (entry - current_price) / entry * 100
            pnl_usdt = (entry - current_price) * qty
        state["balance"] += pos["cost"] + pnl_usdt
        state["total_pnl"] += pnl_usdt
        trade_record = {
            **pos,
            "exit_price": current_price,
            "pnl_pct": round(pnl, 2),
            "pnl_usdt": round(pnl_usdt, 2),
            "closed_at": datetime.utcnow().isoformat(),
            "reason": reason,
            "outcome": "profit" if pnl_usdt > 0 else "loss"
        }
        state["trade_history"].append(trade_record)
        del state["positions"][symbol]
        _save_state(state)
        emoji = "✅" if pnl_usdt > 0 else "❌"
        log.info(f"[PAPER] {emoji} ЗАКРЫТА {side.upper()} {symbol} @ {current_price:.4f} PnL: {pnl:.2f}% ({pnl_usdt:+.2f} USDT) | Баланс: {state['balance']:.2f}")
        return trade_record

def paper_get_positions():
    """Вернуть список открытых PAPER позиций"""
    state = _load_state()
    return list(state["positions"].values())

def paper_get_stats():
    """Статистика paper trading"""
    state = _load_state()
    history = state["trade_history"]
    wins = [t for t in history if t["outcome"] == "profit"]
    losses = [t for t in history if t["outcome"] == "loss"]
    return {
        "balance": round(state["balance"], 2),
        "total_pnl": round(state["total_pnl"], 2),
        "open_positions": len(state["positions"]),
        "total_trades": len(history),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round(len(wins)/len(history)*100, 1) if history else 0
    }

```

## position_manager.py
```python
import paper_trading
import asyncio,logging,uuid
from datetime import datetime
from typing import Optional
log=logging.getLogger("positions")

class PositionManager:
    def __init__(self,bitget,cfg,memory,judge,rl=None):
        self.bitget=bitget; self.cfg=cfg; self.memory=memory; self.judge=judge; self.rl=rl
        self.open_trades={}
        self._peak_pnl={}
        if getattr(cfg,"PAPER_MODE",False): self._restore_paper_state()
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
                    id=str(uuid.uuid4())[:8],symbol=symbol,side=p["side"],
                    entry_price=p["entry_price"],exit_price=None,pnl_pct=None,
                    regime="unknown",rsi_at_entry=0.0,funding_at_entry=0.0,
                    volume_ratio_at_entry=0.0,bull_confidence=0,bear_confidence=0,
                    judge_confidence=p.get("confidence",0),
                    judge_reasoning="restored from paper_state",outcome="open",
                    opened_at=p.get("opened_at",datetime.utcnow().isoformat()),
                    closed_at=None,lessons=None,orphan=True)
                self.memory.add_trade(t); self.open_trades[symbol]=t
            longs=sum(1 for t in self.open_trades.values() if t.side=="long")
            shorts=sum(1 for t in self.open_trades.values() if t.side=="short")
            log.info("Restored "+str(len(self.open_trades))+" positions from paper_state ("+str(longs)+"L/"+str(shorts)+"S)")
        except Exception as e:
            import traceback; log.error("Restore: "+str(e)); log.error(traceback.format_exc())
    async def open_position(self,symbol,decision,snapshot):
        from memory import TradeMemory
        if self.cfg.PAPER_MODE:
            ps=paper_trading._load_state()
            open_syms=set(ps["positions"].keys()) | set(self.open_trades.keys())
            open_sides=[p["side"] for p in ps["positions"].values()]+[t.side for s,t in self.open_trades.items() if s not in ps["positions"]]
        else:
            open_syms=set(self.open_trades.keys())
            open_sides=[t.side for t in self.open_trades.values()]
        if symbol in open_syms: log.info("Already in "+symbol); return None
        if len(open_syms)>=self.cfg.MAX_POSITIONS: log.info("Max positions reached ("+str(len(open_syms))+"/"+str(self.cfg.MAX_POSITIONS)+")"); return None
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
        if self.cfg.PAPER_MODE:
            balance=ps["balance"]
            size=balance*decision.position_size_pct
            price=snapshot.price
            qty=round(size/price,4) if price>0 else 0
            leverage=getattr(self.cfg,"LEVERAGE",5)
            log.info("[PAPER] Opening "+decision.action.upper()+" "+symbol+" notional=$"+str(round(size,1))+" conf="+str(decision.confidence)+"%")
            trade_id=paper_trading.paper_open(symbol,decision.action,price,qty,decision.confidence,leverage=leverage)
            if not trade_id: return None
        else:
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
        min_hold=getattr(self.cfg,"MIN_HOLD_SEC",7200)
        ask_interval=getattr(self.cfg,"JUDGE_EXIT_INTERVAL_SEC",3600)
        noise_band=getattr(self.cfg,"JUDGE_EXIT_NOISE_BAND_PCT",1.0)
        while True:
            if stop_event is not None and stop_event.is_set(): log.info("Position monitor stopped"); return
            try:
                import time
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
                            await self._finalize(trade,"closed_externally"); del self.open_trades[symbol]
                        continue
                    ep=next((p for p in ex_list if p["symbol"]==symbol),None)
                    if ep is None or ep.get("marketPrice") is None: continue
                    cp=float(ep["marketPrice"])
                    pnl=(cp-trade.entry_price)/trade.entry_price*100 if trade.side=="long" else (trade.entry_price-cp)/trade.entry_price*100
                    peak=self._peak_pnl.get(symbol,pnl)
                    if pnl>peak: peak=pnl
                    self._peak_pnl[symbol]=peak
                    if pnl<=emerg_pct:
                        log.warning("EMERGENCY STOP "+symbol+" "+trade.side+" PnL:"+str(round(pnl,2))+"%")
                        await self._close(symbol,trade,cp,pnl,"emergency_stop"); continue
                    if pnl<=sl_pct:
                        log.info("STOP-LOSS "+symbol+" "+trade.side+" PnL:"+str(round(pnl,2))+"%")
                        await self._close(symbol,trade,cp,pnl,"stop_loss"); continue
                    if pnl>=tp_pct:
                        log.info("TAKE-PROFIT "+symbol+" "+trade.side+" PnL:"+str(round(pnl,2))+"%")
                        await self._close(symbol,trade,cp,pnl,"take_profit"); continue
                    if peak>=trail_arm and pnl<=peak-trail_give:
                        log.info("TRAILING-STOP "+symbol+" "+trade.side+" peak:"+str(round(peak,2))+"% now:"+str(round(pnl,2))+"%")
                        await self._close(symbol,trade,cp,pnl,"trailing_stop"); continue
                    from datetime import datetime as _dt
                    try:
                        opened_dt=_dt.fromisoformat(trade.opened_at.replace("Z",""))
                        hold_sec=(_dt.utcnow()-opened_dt).total_seconds()
                    except Exception: hold_sec=1e9
                    t=last_check.get(symbol,0)
                    in_noise=abs(pnl)<noise_band and peak<trail_arm
                    if hold_sec>=min_hold and now-t>ask_interval and not in_noise:
                        last_check[symbol]=now
                        should_exit=await self.judge.ask_exit(trade,cp,pnl,peak_pnl=peak)
                        if should_exit:
                            await self._close(symbol,trade,cp,pnl,"judge_exit")
            except Exception as e:
                import traceback
                log.error("Monitor: "+str(e))
                log.error(traceback.format_exc())
            if stop_event is not None:
                try: await asyncio.wait_for(stop_event.wait(),timeout=30); log.info("Position monitor stopped"); return
                except asyncio.TimeoutError: pass
            else:
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
        if self.rl is not None:
            try: self.rl.learn(trade)
            except Exception as ex: log.error("RL.learn "+trade.symbol+": "+str(ex))

```

## rl_agent.py
```python
import json, os, math, logging
from dataclasses import dataclass, asdict
from typing import List, Optional

log = logging.getLogger("rl")

@dataclass
class RLWeights:
    bull_weight: float = 1.0
    bear_weight: float = 1.0
    judge_weight: float = 1.0
    conf_threshold: float = 65.0
    learning_rate: float = 0.05
    episodes: int = 0
    total_reward: float = 0.0

class RLAgent:
    """Simple Q-learning agent that adjusts Bull/Bear/Judge weights based on trade outcomes."""
    
    def __init__(self, cfg):
        self.cfg = cfg
        self.path = os.path.join(os.path.dirname(cfg.MEMORY_FILE), "rl_weights.json")
        self.weights = self._load()
    
    def _load(self):
        try:
            if os.path.exists(self.path):
                d = json.load(open(self.path))
                w = RLWeights(**d)
                log.info(f"RL weights loaded: bull={w.bull_weight:.3f} bear={w.bear_weight:.3f} judge={w.judge_weight:.3f} episodes={w.episodes}")
                return w
        except Exception as e:
            log.error(f"RL load error: {e}")
        return RLWeights()
    
    def _save(self):
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(asdict(self.weights), f, indent=2)
                f.flush(); os.fsync(f.fileno())
            os.replace(tmp, self.path)
        except Exception as e:
            log.error(f"RL save error: {e}")
    
    def get_adjusted_confidence(self, bull_conf: int, bear_conf: int, judge_conf: int, action: str, bull_side: str = "long", bear_side: str = "short") -> float:
        """Apply learned weights to compute final confidence score.

        Judge confidence is the baseline. Ally/opposition tilt it symmetrically:
          - ally agreement boosts score
          - opposition dampens it
        A 'flat' verdict from either side is treated as neutral.
        The tilt is bounded so RL can never invert Judge's decision."""
        if action not in ("long", "short"):
            return float(judge_conf)
        w = self.weights
        if action == "long":
            ally_conf = bull_conf if bull_side == "long" else 0
            opp_conf = bear_conf if bear_side == "short" else 0
            ally_w, opp_w = w.bull_weight, w.bear_weight
        else:
            ally_conf = bear_conf if bear_side == "short" else 0
            opp_conf = bull_conf if bull_side == "long" else 0
            ally_w, opp_w = w.bear_weight, w.bull_weight
        # net signal in [-1, +1] roughly; weights normalized around 1.0
        net = (ally_conf * ally_w - opp_conf * opp_w) / 100.0
        tilt_cap = 15.0  # max ±15 points of Judge confidence
        tilt = max(-tilt_cap, min(tilt_cap, net * tilt_cap))
        score = float(judge_conf) + tilt
        return max(0.0, min(100.0, score))
    
    def should_trade(self, adjusted_conf: float) -> bool:
        """Check if adjusted confidence meets RL threshold."""
        return adjusted_conf >= self.weights.conf_threshold
    
    def learn(self, trade) -> Optional[str]:
        """Update weights based on closed trade outcome. Returns log message."""
        if trade.outcome not in ("profit", "loss"):
            return None
        if trade.pnl_pct is None:
            return None
        
        w = self.weights
        lr = w.learning_rate
        reward = trade.pnl_pct  # positive = profit, negative = loss
        
        bull_signal = trade.bull_confidence / 100.0
        bear_signal = trade.bear_confidence / 100.0
        judge_signal = trade.judge_confidence / 100.0
        
        if trade.outcome == "profit":
            # Reinforce: increase weights of agents that were aligned with the winning trade
            if trade.side == "long":
                w.bull_weight = min(2.0, w.bull_weight + lr * bull_signal * abs(reward) / 10)
                w.bear_weight = max(0.2, w.bear_weight - lr * bear_signal * abs(reward) / 20)
            elif trade.side == "short":
                w.bear_weight = min(2.0, w.bear_weight + lr * bear_signal * abs(reward) / 10)
                w.bull_weight = max(0.2, w.bull_weight - lr * bull_signal * abs(reward) / 20)
            w.judge_weight = min(2.0, w.judge_weight + lr * judge_signal * abs(reward) / 15)
            # Tighten threshold slightly on wins
            w.conf_threshold = max(60.0, w.conf_threshold - lr * 0.5)
        else:
            # Punish: decrease weights of agents that led to loss
            if trade.side == "long":
                w.bull_weight = max(0.2, w.bull_weight - lr * bull_signal * abs(reward) / 10)
            elif trade.side == "short":
                w.bear_weight = max(0.2, w.bear_weight - lr * bear_signal * abs(reward) / 10)
            w.judge_weight = max(0.2, w.judge_weight - lr * judge_signal * abs(reward) / 20)
            # Raise threshold on losses
            w.conf_threshold = min(90.0, w.conf_threshold + lr * 1.0)
        
        # Normalize weights so they sum to 3.0
        total = w.bull_weight + w.bear_weight + w.judge_weight
        w.bull_weight = round(w.bull_weight / total * 3.0, 4)
        w.bear_weight = round(w.bear_weight / total * 3.0, 4)
        w.judge_weight = round(w.judge_weight / total * 3.0, 4)
        w.conf_threshold = round(w.conf_threshold, 2)
        
        w.episodes += 1
        w.total_reward += reward
        self._save()
        
        msg = f"RL learned from {trade.side} {trade.symbol}: {trade.outcome} {reward:.2f}% | weights bull={w.bull_weight:.3f} bear={w.bear_weight:.3f} judge={w.judge_weight:.3f} threshold={w.conf_threshold}"
        log.info(msg)
        return msg
    
    def learn_from_history(self, memory) -> int:
        """Batch learn from all closed trades in memory. Returns count learned."""
        closed = [t for t in memory.trades if t.outcome in ("profit", "loss") and not getattr(t, "orphan", False)]
        if not closed:
            log.info("RL: no closed trades to learn from")
            return 0
        count = 0
        for trade in closed:
            result = self.learn(trade)
            if result:
                count += 1
        log.info(f"RL batch learned from {count} trades")
        return count
    
    def get_stats(self) -> dict:
        w = self.weights
        return {
            "bull_weight": w.bull_weight,
            "bear_weight": w.bear_weight,
            "judge_weight": w.judge_weight,
            "conf_threshold": w.conf_threshold,
            "episodes": w.episodes,
            "total_reward": round(w.total_reward, 4),
            "avg_reward": round(w.total_reward / w.episodes, 4) if w.episodes > 0 else 0
        }

```

## .env
```
TELEGRAM_TOKEN=***
TELEGRAM_CHAT_ID=***
ANTHROPIC_API_KEY=***

# Groq (free inference: Llama / GPT-OSS / Qwen) — used by Bear agent, Haiku stays as fallback
GROQ_API_KEY=***
GROQ_API_KEY2=***
BITGET_API_KEY=***
BITGET_SECRET=***
BITGET_PASSPHRASE=***

# Gemini keys (round-robin order: broadest coverage first, narrowest last)
GEMINI_API_KEY=***
GEMINI_API_KEY2=***
GEMINI_API_KEY3=***
GEMINI_API_KEY4=***
GEMINI_API_KEY5=***
```

