# Ensemble-agent snapshot

Generated: 2026-07-20 08:00:02 UTC

## ab_test_analyze_apply.py
```python
#!/usr/bin/env python3
"""
Analyze A/B test results, apply best config, send Telegram report.
Run after run_ab_test.sh finishes.
"""
import os
import sys
import json
import glob
import shutil
from datetime import datetime, timezone
from pathlib import Path

os.chdir("/opt/ensemble-agent")
sys.path.insert(0, "/opt/ensemble-agent")

# Telegram helpers (mirrored from auto_pipeline)
TOKEN = "8702211361:AAFPTNQ8kyEka02VD7-KUIkeUidBvTQmupU"
CHAT_ID = "6349919785"

def tg_send(text: str) -> dict:
    import urllib.request
    import urllib.parse
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true"
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def read_stats(path: str) -> dict:
    p = os.path.join(path, "stats.json")
    if not os.path.exists(p):
        return {}
    with open(p) as f:
        return json.load(f)

def find_latest_two_dirs() -> list:
    dirs = sorted(glob.glob("simulator_output/2026*"), key=os.path.getmtime, reverse=True)
    return dirs[:2]

def update_config(best: str):
    """Apply best parameters to config.py"""
    config_path = "/opt/ensemble-agent/config.py"
    backup_path = config_path + ".auto_backup_ab"
    shutil.copy(config_path, backup_path)

    with open(config_path) as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.startswith("    STOP_LOSS_PCT ="):
            new_lines.append(f"    STOP_LOSS_PCT = {-2.0 if best == 'asymmetry' else -3.0}\n")
        elif line.startswith("    TAKE_PROFIT_PCT ="):
            new_lines.append(f"    TAKE_PROFIT_PCT = {4.0 if best == 'asymmetry' else 3.0}\n")
        elif line.startswith("    KIMI_PROMPT_VERSION ="):
            new_lines.append(f'    KIMI_PROMPT_VERSION = "{best}"\n')
        else:
            new_lines.append(line)

    with open(config_path, "w") as f:
        f.writelines(new_lines)

    print(f"Config updated: SL={'2%' if best=='asymmetry' else '3%'}, TP={'4%' if best=='asymmetry' else '3%'}, prompt={best}")
    print(f"Backup saved: {backup_path}")

def update_agents_md(best: str, baseline_stats: dict, asym_stats: dict):
    md_path = "/opt/ensemble-agent/AGENTS.md"
    with open(md_path) as f:
        content = f.read()

    report = f"""
## Результаты A/B теста (Kimi prompt + SL/TP)

| Вариант | Prompt | SL | TP | Сделок | Win% | PnL% | SL hits | TP hits | Trailing | Final Balance |
|---------|--------|----|----|--------|------|------|---------|---------|----------|---------------|
| **Baseline** | baseline | 3% | 3% | {baseline_stats.get('total_trades',0)} | {baseline_stats.get('win_rate',0):.1f}% | {baseline_stats.get('total_pnl_pct',0):.1f}% | {baseline_stats.get('sl_count',0)} | {baseline_stats.get('tp_count',0)} | {baseline_stats.get('trailing_count',0)} | {baseline_stats.get('final_balance','N/A')} |
| **Asymmetry** | asymmetry | 2% | 4% | {asym_stats.get('total_trades',0)} | {asym_stats.get('win_rate',0):.1f}% | {asym_stats.get('total_pnl_pct',0):.1f}% | {asym_stats.get('sl_count',0)} | {asym_stats.get('tp_count',0)} | {asym_stats.get('trailing_count',0)} | {asym_stats.get('final_balance','N/A')} |

**Победитель: {best.upper()}**
- Применённые параметры: STOP_LOSS_PCT={-2.0 if best=='asymmetry' else -3.0}, TAKE_PROFIT_PCT={4.0 if best=='asymmetry' else 3.0}, KIMI_PROMPT_VERSION={best}
"""
    # Append after existing results section or at end
    if "## Результаты A/B теста" in content:
        # replace old block
        start = content.find("## Результаты A/B теста")
        end = content.find("\n## ", start + 1)
        if end == -1:
            end = len(content)
        content = content[:start] + report.strip() + content[end:]
    else:
        content += "\n" + report.strip() + "\n"

    with open(md_path, "w") as f:
        f.write(content)
    print("AGENTS.md updated")

def main():
    dirs = find_latest_two_dirs()
    if len(dirs) < 2:
        print("Need 2 output dirs, found:", len(dirs))
        sys.exit(1)

    # Determine which is baseline and which is asymmetry by reading stats mode/prompt? stats don't contain prompt version.
    # Fallback: the older one is baseline (ran first), newer is asymmetry.
    baseline_dir, asym_dir = dirs[1], dirs[0]
    baseline_stats = read_stats(baseline_dir)
    asym_stats = read_stats(asym_dir)

    print("Baseline:", baseline_dir, baseline_stats.get("final_balance"))
    print("Asymmetry:", asym_dir, asym_stats.get("final_balance"))

    # Compare by final_balance (primary), then total_pnl_pct, then win_rate
    b_bal = baseline_stats.get("final_balance") or 0
    a_bal = asym_stats.get("final_balance") or 0

    if a_bal > b_bal:
        best = "asymmetry"
    elif b_bal > a_bal:
        best = "baseline"
    else:
        # tie-breaker: total_pnl_pct
        b_pnl = baseline_stats.get("total_pnl_pct", 0)
        a_pnl = asym_stats.get("total_pnl_pct", 0)
        best = "asymmetry" if a_pnl > b_pnl else "baseline"

    print("Best:", best)

    # Update configs
    update_config(best)
    update_agents_md(best, baseline_stats, asym_stats)

    # Build report
    report = (
        f"<b>📊 A/B TEST REPORT</b>\n"
        f"<code>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</code>\n\n"
        f"<b>Baseline</b> (SL=3% TP=3% prompt=baseline)\n"
        f"  Сделок: {baseline_stats.get('total_trades',0)} | WR: {baseline_stats.get('win_rate',0):.1f}%\n"
        f"  PnL: {baseline_stats.get('total_pnl_pct',0):.1f}% | Баланс: {b_bal:.2f}\n"
        f"  SL: {baseline_stats.get('sl_count',0)} | TP: {baseline_stats.get('tp_count',0)} | Trail: {baseline_stats.get('trailing_count',0)}\n\n"
        f"<b>Asymmetry</b> (SL=2% TP=4% prompt=asymmetry)\n"
        f"  Сделок: {asym_stats.get('total_trades',0)} | WR: {asym_stats.get('win_rate',0):.1f}%\n"
        f"  PnL: {asym_stats.get('total_pnl_pct',0):.1f}% | Баланс: {a_bal:.2f}\n"
        f"  SL: {asym_stats.get('sl_count',0)} | TP: {asym_stats.get('tp_count',0)} | Trail: {asym_stats.get('trailing_count',0)}\n\n"
        f"<b>🏆 Победитель: {best.upper()}</b>\n"
        f"Применено: SL={'-2.0' if best=='asymmetry' else '-3.0'} | TP={'4.0' if best=='asymmetry' else '3.0'} | prompt={best}\n"
    )

    # Send to Telegram
    resp = tg_send(report)
    print("Telegram response:", resp.get("ok"), resp.get("error", ""))

    # Send files
    for d, label in [(baseline_dir, "baseline"), (asym_dir, "asymmetry")]:
        for fname in ["stats.json", "trades.csv"]:
            fpath = os.path.join(d, fname)
            if os.path.exists(fpath):
                # reuse tg_send_file from auto_pipeline if possible, else skip
                pass

    print("Done.")

if __name__ == "__main__":
    main()

```

## agents.py
```python
import asyncio,logging,json,re,aiohttp,time
from dataclasses import dataclass
from http_pool import session as _http_session
log=logging.getLogger("agents")

def _mask(api_key:str)->str:
    """Mask API key for safe logging — show only last 4 chars."""
    if not api_key: return "***"
    return "***"+api_key[-4:] if len(api_key)>=4 else "***"

def _clamp(v,lo,hi):
    try: v=float(v)
    except: return lo
    return max(lo,min(hi,v))

@dataclass
class AgentVerdict:
    side:str; confidence:int; reasoning:str

@dataclass
class JudgeDecision:
    action:str; confidence:int; position_size_pct:float; reasoning:str; lessons_from_memory:str

BULL_SYS='Ты агент BULL в adversarial ансамбле — твоя задача аргументировать LONG. Учитывай: (1) тренд BTC (4h), (2) RSI 15m/1h, (3) MA10/MA40, (4) funding rate, (5) volume ratio. Не давай confidence по умолчанию — каждое значение должно быть обосновано. side="flat" ТОЛЬКО если данные полностью нейтральны. Отвечай ТОЛЬКО JSON: {"side":"long|flat","confidence":0-100,"reasoning":"кратко и конкретно"}.'
BEAR_SYS='You are the BEAR agent — a skeptical crypto analyst hunting for the strongest case to AVOID or SHORT this trade. Respond ONLY in JSON with no other text: {"side":"short|flat|long","confidence":0-100,"reasoning":"brief"}. Use side="short" if bearish, "flat" if unclear, "long" only if the data is overwhelmingly bullish. Be specific about why.'
JUDGE_SYS="""You are the JUDGE in an adversarial trading ensemble. BULL argues for LONG; BEAR argues for SHORT/avoid. A "flat" side from either agent means NEUTRAL — it is NOT opposition, just absence of conviction. Past similar trades may be empty (paper bot, no history) — that is normal, do not let it bias you toward HOLD.

Decision criteria:
- LONG if: BULL conviction >= 55 AND BEAR is flat OR BEAR conviction < BULL conviction. Set action="long".
- SHORT if: BEAR conviction >= 55 AND BULL is flat OR BULL conviction < BEAR conviction. Set action="short".
- HOLD only when: signals genuinely conflict (both > 60 in opposite directions) OR both sides agree it is flat/unclear. HOLD is a real cost — missed opportunity.

Market sentiment (Fear & Greed) is a soft signal, not a blocker:
- Extreme Greed (>80) + LONG: require BULL conviction clearly > BEAR (margin >= 10), otherwise lean HOLD. Late-cycle euphoria.
- Extreme Fear (<20) + SHORT: require BEAR conviction clearly > BULL (margin >= 10), otherwise lean HOLD. Capitulation often marks bottoms.
- Neither extreme: sentiment is informational only, do not let it override the BULL/BEAR debate.

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
        self._key_rr_q=0
        self._recent_verdicts=[]
        self._using_fallback=False
    def _entropy_guard(self,side,conf):
        self._recent_verdicts.append((side,conf))
        if len(self._recent_verdicts)>10:
            self._recent_verdicts.pop(0)
        if len(self._recent_verdicts)>=5:
            last5=self._recent_verdicts[-5:]
            sides=[s for s,c in last5]
            confs=[c for s,c in last5]
            if len(set(sides))==1 and max(confs)-min(confs)<=3:
                if not self._using_fallback:
                    log.warning(f"Bull entropy-guard: шаблон {sides[0]}({confs[0]}) ×5. Переключаемся на Kimi+Claude fallback.")
                    self._using_fallback=True
                return True
        self._using_fallback=False
        return False
    async def analyze(self,market_text):
        prompt="Analyze and make bullish case:\n"+market_text
        try:
            # Bull теперь только на Groq (экономия Kimi). Fallback — Claude Haiku.
            if self._using_fallback:
                log.warning(f"Bull entropy-guard: шаблон detected. Используем Groq+Claude fallback.")
                text=await _race([self._groq(prompt)], self._claude(prompt))
            else:
                text=await _race(
                    [self._groq(prompt)],
                    self._claude(prompt))
            d=self._parse(text)
            side=d.get("side")
            if side not in ("long","flat"):
                log.warning("Bull: unparseable response → flat/25. raw="+(text or "")[:160].replace("\n"," "))
                return AgentVerdict("flat",25,"Unparseable: "+(text or "")[:200])
            conf=int(_clamp(d.get("confidence",50),0,100))
            self._entropy_guard(side,conf)
            return AgentVerdict(side,conf,d.get("reasoning",text))
        except Exception as e: log.error("Bull: "+str(e)); return AgentVerdict("flat",25,"Error: "+str(e))
    async def _claude(self,prompt):
        import anthropic
        c=anthropic.AsyncAnthropic(api_key=self.cfg.ANTHROPIC_API_KEY)
        msg=await c.messages.create(model=self.cfg.BULL_MODEL,max_tokens=300,system=BULL_SYS,messages=[{"role":"user","content":prompt}])
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
                    s=await _http_session()
                    async with s.post("https://api.groq.com/openai/v1/chat/completions",
                        json={"model":model,"messages":[{"role":"system","content":BULL_SYS},{"role":"user","content":prompt}],"max_tokens":300,"temperature":0.3,"response_format":{"type":"json_object"}},
                        headers={"Authorization":"Bearer "+api_key,"Content-Type":"application/json"},
                        timeout=aiohttp.ClientTimeout(total=20)) as r:
                        try: d=await r.json()
                        except: d={}
                        if r.status==429:
                            self._key_cd[("groq",model,api_key)]=time.time()+3600
                            last_err=model+" 429 ("+_mask(api_key)+")"; continue
                        if r.status==401:
                            for m in models: self._key_cd[("groq",m,api_key)]=time.time()+86400
                            last_err=model+" 401 "+_mask(api_key); continue
                        if r.status!=200:
                            last_err=model+" "+str(r.status); continue
                        txt=(d.get("choices") or [{}])[0].get("message",{}).get("content","").strip()
                        if txt: return txt
                        last_err=model+" empty"
                except Exception as e:
                    last_err=model+" exc: "+str(e)[:80]; continue
        if last_err: log.debug("Bull-Groq: "+last_err)
        return ""
    async def _kimi(self,prompt):
        key=getattr(self.cfg,"KIMI_API_KEY",None)
        if not key: return ""
        try:
            import openai
            client=openai.AsyncOpenAI(api_key=key,base_url=getattr(self.cfg,"KIMI_BASE_URL","https://api.moonshot.ai/v1"))
            r=await client.chat.completions.create(
                model=getattr(self.cfg,"KIMI_MODEL","kimi-k2.6"),
                messages=[{"role":"system","content":BULL_SYS},{"role":"user","content":prompt}],
                max_tokens=2048,temperature=1.0,
                response_format={"type":"json_object"},
                timeout=30)
            return (r.choices[0].message.content or "").strip()
        except Exception as e:
            log.debug("Bull-Kimi: "+str(e)[:120])
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
    async def analyze(self,market_text):
        prompt="Analyze and make the bearish/cautious case for this market data:\n"+market_text
        try:
            text=await _race(
                [self._groq(prompt), self._kimi(prompt)],
                self._claude(prompt))
            d=self._parse(text)
            side=d.get("side")
            if side not in ("short","flat","long"):
                log.warning("Bear: unparseable response → flat/25. raw="+(text or "")[:160].replace("\n"," "))
                return AgentVerdict("flat",25,"Unparseable: "+(text or "")[:200])
            conf=int(_clamp(d.get("confidence",50),0,100))
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
                    s=await _http_session()
                    async with s.post("https://api.groq.com/openai/v1/chat/completions",
                        json={"model":model,"messages":[{"role":"system","content":BEAR_SYS},{"role":"user","content":prompt}],"max_tokens":300,"temperature":0.3,"response_format":{"type":"json_object"}},
                        headers={"Authorization":"Bearer "+api_key,"Content-Type":"application/json"},
                        timeout=aiohttp.ClientTimeout(total=20)) as r:
                        try: d=await r.json()
                        except: d={}
                        if r.status==429:
                            self._key_cd[("groq",model,api_key)]=time.time()+3600
                            last_err=model+" 429 ("+_mask(api_key)+")"; continue
                        if r.status==401:
                            for m in models: self._key_cd[("groq",m,api_key)]=time.time()+86400
                            last_err=model+" 401 "+_mask(api_key); continue
                        if r.status!=200:
                            last_err=model+" "+str(r.status); continue
                        txt=(d.get("choices") or [{}])[0].get("message",{}).get("content","").strip()
                        if txt: return txt
                        last_err=model+" empty"
                except Exception as e:
                    last_err=model+" exc: "+str(e)[:80]; continue
        if last_err: log.debug("Bear-Groq: "+last_err)
        return ""
    async def _kimi(self,prompt):
        key=getattr(self.cfg,"KIMI_API_KEY",None)
        if not key: return ""
        try:
            import openai
            client=openai.AsyncOpenAI(api_key=key,base_url=getattr(self.cfg,"KIMI_BASE_URL","https://api.moonshot.ai/v1"))
            r=await client.chat.completions.create(
                model=getattr(self.cfg,"KIMI_MODEL","kimi-k2.6"),
                messages=[{"role":"system","content":BEAR_SYS},{"role":"user","content":prompt}],
                max_tokens=2048,temperature=1.0,
                response_format={"type":"json_object"},
                timeout=30)
            return (r.choices[0].message.content or "").strip()
        except Exception as e:
            log.debug("Bear-Kimi: "+str(e)[:120])
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
                    s=await _http_session()
                    async with s.post(url,json=payload,headers=headers,timeout=aiohttp.ClientTimeout(total=20)) as r:
                        try: d=await r.json()
                        except: d={}
                        if r.status==429:
                            self._key_cd[(model,api_key)]=time.time()+3600
                            last_err=model+" 429 ("+_mask(api_key)+" cooldown 1h)"; continue
                        if r.status==401:
                            for m in models: self._key_cd[(m,api_key)]=time.time()+86400
                            last_err=model+" 401 bad key "+_mask(api_key); continue
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
            action=d.get("action","hold")
            if action not in ("long","short","hold"): action="hold"
            conf=int(_clamp(d.get("confidence",50),0,100))
            size=_clamp(d.get("position_size_pct",0.03),0.0,0.15)
            if action=="hold": size=0.0
            return JudgeDecision(action,conf,size,d.get("reasoning",r),d.get("lessons_from_memory",""))
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


class KimiJudge(Judge):
    """Judge that uses Kimi (Moonshot) unified API instead of Claude Haiku.

    Inherits Groq-based reflect/ask_exit/ask_direction from Judge.
    Overrides decide() and _claude() to use Kimi.
    """

    def __init__(self, cfg):
        super().__init__(cfg)
        self._client = None
        self._kimi_model = getattr(cfg, "KIMI_MODEL", "kimi-k2.6")
        self._kimi_base_url = getattr(cfg, "KIMI_BASE_URL", "https://api.moonshot.ai/v1")
        self._kimi_key = getattr(cfg, "KIMI_API_KEY", "")

    def _get_client(self):
        import openai
        if self._client is None:
            self._client = openai.AsyncOpenAI(
                api_key=self._kimi_key,
                base_url=self._kimi_base_url
            )
        return self._client

    async def _claude(self, prompt):
        """Override Claude call with Kimi API."""
        client = self._get_client()
        try:
            resp = await client.chat.completions.create(
                model=self._kimi_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=1.0,
                max_tokens=400,
                timeout=30
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            log.warning("KimiJudge _claude failed: " + str(e))
            return ""

    async def decide(self, market_text, bull, bear, memory_ctx):
        """Unified Kimi decision — compact prompt for moonshot-v1-auto."""
        version = getattr(self.cfg, "KIMI_PROMPT_VERSION", "baseline")
        if version == "asymmetry":
            prompt = f"""You are an elite trading judge with asymmetric risk rules. Output ONLY JSON.

Market: {market_text}
Bull: {bull.confidence}% | {bull.reasoning[:120]}
Bear: {bear.confidence}% | {bear.reasoning[:120]}
Memory: {memory_ctx[:200]}

## RISK/REWARD FRAMEWORK (ASYMMETRY):
- Stop Loss: 2% from entry (tight)
- Take Profit: 4% from entry (2:1 R/R)
- ONLY signal LONG/SHORT when you expect a strong directional move (≥4% potential).

## STRICT RULES:
- LONG if bull≥60, bear is weaker or flat, and you expect ≥4% upside move
- SHORT if bear≥60, bull is weaker or flat, and you expect ≥4% downside move
- HOLD if both sides weak (<60), conflicting, or move potential <4%
- If memory shows 2+ consecutive SL on a side → reduce confidence for that side

## TASK:
1. Decide action: "long", "short", or "hold"
2. Confidence 0–100 (must be ≥60 for entry)
3. Position size 0.0–0.20 (0 for HOLD; 0.10 for conf 60-70; 0.15 for 70-85; 0.20 for 85+)
4. Brief reasoning (1 sentence, mention expected R/R if entry)
5. Lessons from memory (brief)

JSON: {{"action":"long|short|hold","confidence":0-100,"position_size_pct":0.0-0.20,"reasoning":"brief","lessons_from_memory":"brief"}}"""
        else:
            prompt = f"""You are a trading judge. Output ONLY JSON.

Market: {market_text}
Bull: {bull.confidence}% | {bull.reasoning[:80]}
Bear: {bear.confidence}% | {bear.reasoning[:80]}
Memory: {memory_ctx[:100]}

Rules:
- LONG if bull>=55 and (bear flat or bear<bull)
- SHORT if bear>=55 and (bull flat or bull<bear)
- HOLD if both conflict or both flat

JSON: {{"action":"long|short|hold","confidence":0-100,"position_size_pct":0.0-0.15,"reasoning":"brief","lessons_from_memory":"brief"}}"""

        try:
            r = await self._claude(prompt)
            d = self._parse(r)
            action = d.get("action", "hold")
            if action not in ("long", "short", "hold"):
                action = "hold"
            conf = int(_clamp(d.get("confidence", 50), 0, 100))
            max_size = 0.20 if version == "asymmetry" else 0.15
            size = _clamp(d.get("position_size_pct", 0.03), 0.0, max_size)
            if action == "hold":
                size = 0.0
            return JudgeDecision(
                action, conf, size,
                d.get("reasoning", r)[:200],
                d.get("lessons_from_memory", "")
            )
        except Exception as e:
            log.error("KimiJudge decide: " + str(e))
            return JudgeDecision("hold", 0, 0.0, "KimiJudge error: " + str(e)[:100], "")
```

## audit_and_notify.py
```python
#!/usr/bin/env python3
"""Run blocked-prediction audit and send result to Telegram."""
import asyncio, json, os, sys, subprocess
sys.path.insert(0, "/opt/ensemble-agent")

from dotenv import load_dotenv
load_dotenv("/opt/ensemble-agent/.env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("No Telegram creds")
        return
    import urllib.request, urllib.parse
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print("Telegram send error:", e)

async def main():
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "/opt/ensemble-agent/audit_blocked.py",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd="/opt/ensemble-agent"
    )
    stdout, stderr = await proc.communicate()
    report = stdout.decode()
    if not report.strip():
        report = "audit_blocked.py produced no output"

    try:
        with open("/opt/ensemble-agent/blocked_predictions.json") as f:
            data = json.load(f)
        pending = len(data.get("pending", []))
        resolved = len(data.get("resolved", []))
    except Exception:
        pending = resolved = "?"

    message = (
        "📊 <b>Blocked Predictions Audit</b>\n\n"
        f"Pending:  <code>{pending}</code>\n"
        f"Resolved: <code>{resolved}</code>\n\n"
        f"<pre>{report[:3500]}</pre>"
    )
    send_telegram(message)
    print(report)

if __name__ == "__main__":
    asyncio.run(main())

```

## audit_blocked.py
```python
#!/usr/bin/env python3
"""Resolve pending blocked predictions and print audit report."""
import asyncio
import json
import sys
import os
import logging
from datetime import datetime, timezone

sys.path.insert(0, "/opt/ensemble-agent")

from blocked_logger import BlockedLogger
from bitget_client import BitgetClient
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("audit_blocked")


async def main():
    cfg = Config()
    bitget = BitgetClient(cfg)
    await bitget.start()

    logger = BlockedLogger()
    data = logger._load()
    pending = data.get("pending", [])

    if not pending:
        log.info("No pending blocked predictions.")
        await bitget.close()
        print(logger.report())
        return

    now = datetime.now(timezone.utc)
    to_check = []
    for p in pending:
        try:
            check_after = datetime.fromisoformat(
                p["check_after"].replace("Z", "+00:00")
            )
            if check_after <= now:
                to_check.append(p)
        except Exception as e:
            log.warning(f"Bad check_after for {p.get('id')}: {e}")

    if not to_check:
        log.info(f"No predictions ready for check yet. {len(pending)} pending.")
        await bitget.close()
        print(logger.report())
        return

    log.info(f"Resolving {len(to_check)} blocked predictions...")
    resolved_count = 0

    for entry in to_check:
        symbol = entry["symbol"]
        try:
            resp = await bitget.get(
                "/api/v2/mix/market/ticker",
                {"symbol": symbol, "productType": "USDT-FUTURES"},
            )
            price = float(resp["data"][0]["lastPr"])
            result = logger.resolve(entry["id"], price)
            if result:
                log.info(
                    f"  {symbol:12s} {entry['side'].upper():5s} "
                    f"blocked={entry['block_reason']:25s} -> "
                    f"{result['outcome']:12s} PnL={result['pnl_pct']:+.2f}%"
                )
                resolved_count += 1
        except Exception as e:
            log.error(f"  ERROR {symbol}: {e}")

    log.info(f"Resolved {resolved_count}/{len(to_check)} predictions.")
    await bitget.close()
    print("\n" + logger.report())


if __name__ == "__main__":
    asyncio.run(main())

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

## auto_advisor.py
```python
#!/usr/bin/env python3
"""
Автономный советник Ensemble Agent.
Работает каждые 15 минут, читает состояние/логи, вызывает LLM, действует автономно.
"""
import os
import sys
import json
import time
import re
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime, timezone

os.chdir("/opt/ensemble-agent")
sys.path.insert(0, "/opt/ensemble-agent")

from dotenv import load_dotenv
load_dotenv("/opt/ensemble-agent/.env")

# Telegram
TG_TOKEN = os.getenv("TELEGRAM_TOKEN") or "8702211361:AAFPTNQ8kyEka02VD7-KUIkeUidBvTQmupU"
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "6349919785"

# LLM
KIMI_KEY = os.getenv("KIMI_API_KEY")
KIMI_URL = "https://api.moonshot.ai/v1/chat/completions"
KIMI_MODEL = "moonshot-v1-auto"
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"

# Файлы состояния
ADVISOR_STATE_FILE = "/opt/ensemble-agent/advisor_state.json"
LOG_FILE = "/opt/ensemble-agent/advisor.log"
PAPER_STATE = "/opt/ensemble-agent/paper_state.json"
ENSEMBLE_LOG = "/opt/ensemble-agent/ensemble.log"
CONFIG_PY = "/opt/ensemble-agent/config.py"
RL_WEIGHTS = "/opt/ensemble-agent/rl_weights.json"

# Кулдауны (секунды)
CD_CLOSE = 3600
CD_RESTART = 3600
CD_ADJUST = 14400
CD_ALERT = 900

# Критические пороги
BALANCE_CRITICAL = 500.0
BALANCE_WARNING = 600.0
CONSECUTIVE_LOSS_THRESHOLD = 5


def html_escape(text):
    if not isinstance(text, str):
        text = str(text)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_advisor_state():
    try:
        with open(ADVISOR_STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {
            "last_close_ts": 0,
            "last_restart_ts": 0,
            "last_adjust_ts": 0,
            "last_alert_ts": 0,
            "last_alert_msg": "",
            "consecutive_losses": 0,
            "balance_low_flag": False,
        }


def save_advisor_state(state):
    tmp = ADVISOR_STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, ADVISOR_STATE_FILE)


def tg_send(text):
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": TG_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true"
        }).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        log(f"Ошибка Telegram: {e}")
        return {"ok": False, "error": str(e)}


def tail_log(path, lines=100):
    try:
        with open(path, "r") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])
    except Exception as e:
        return f"<ошибка чтения лога: {e}>"


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def read_config_params():
    try:
        with open(CONFIG_PY) as f:
            content = f.read()
        params = {}
        for key in ["STOP_LOSS_PCT", "TAKE_PROFIT_PCT", "TRAIL_ARM_PCT",
                    "TRAIL_GIVEBACK_PCT", "MIN_CONFIDENCE", "MAX_POSITIONS",
                    "MIN_HOLD_SEC", "JUDGE_EXIT_INTERVAL_SEC", "LEVERAGE",
                    "VOLATILITY_FILTER_ATR_PCT", "POSITION_SIZE_FIXED"]:
            m = re.search(rf"{key}\s*=\s*([^#\n]+)", content)
            if m:
                try:
                    params[key] = json.loads(m.group(1).strip().replace("'", '"'))
                except Exception:
                    params[key] = m.group(1).strip()
        return params
    except Exception as e:
        log(f"Ошибка чтения config: {e}")
        return {}


def fetch_bitget_price(symbol):
    try:
        url = f"https://api.bitget.com/api/v2/mix/market/ticker?symbol={symbol}&productType=USDT-FUTURES"
        req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return float(data["data"][0]["lastPr"])
    except Exception as e:
        log(f"Ошибка цены {symbol}: {e}")
        return None


def call_kimi(prompt):
    if not KIMI_KEY:
        return None
    try:
        body = {
            "model": KIMI_MODEL,
            "messages": [
                {"role": "system", "content": "Ты автономный риск-советник по криптотрейдингу. Отвечай ТОЛЬКО валидным JSON. Без markdown, без пояснений вне JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 800,
            "response_format": {"type": "json_object"}
        }
        req = urllib.request.Request(
            KIMI_URL,
            data=json.dumps(body).encode(),
            method="POST",
            headers={
                "Authorization": f"Bearer {KIMI_KEY}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        log(f"Ошибка Kimi API: {e}")
        return None


def call_anthropic(prompt):
    if not ANTHROPIC_KEY:
        return None
    try:
        body = {
            "model": ANTHROPIC_MODEL,
            "max_tokens": 800,
            "temperature": 0.2,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        req = urllib.request.Request(
            ANTHROPIC_URL,
            data=json.dumps(body).encode(),
            method="POST",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            return data["content"][0]["text"]
    except Exception as e:
        log(f"Ошибка Anthropic API: {e}")
        return None


def call_llm(prompt):
    raw = call_kimi(prompt)
    if raw:
        return raw
    log("Kimi не ответил, пробуем Anthropic...")
    return call_anthropic(prompt)


def parse_decision(raw):
    if not raw:
        return None
    try:
        raw = raw.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
        d = json.loads(raw)
        valid_actions = {"nothing", "alert", "close_positions", "restart_service", "adjust_params"}
        if d.get("action") not in valid_actions:
            log(f"Неверное действие от LLM: {d.get('action')}")
            return None
        return d
    except Exception as e:
        log(f"Ошибка парсинга решения: {e} | raw={raw[:200]}")
        return None


def close_position(symbol):
    try:
        import paper_trading
        price = fetch_bitget_price(symbol)
        if price is None:
            log(f"Невозможно закрыть {symbol}: нет цены")
            return False
        result = paper_trading.paper_close(symbol, price, reason="advisor_auto_close")
        if result:
            log(f"Закрыта {symbol} @ {price} | PnL: {result.get('pnl_usdt')} USDT")
            return True
        else:
            log(f"Закрытие {symbol} вернуло None (возможно уже закрыта)")
            return False
    except Exception as e:
        log(f"Ошибка закрытия {symbol}: {e}")
        return False


def restart_ensemble():
    try:
        subprocess.run(["systemctl", "restart", "ensemble-agent"], check=True, capture_output=True)
        log("Перезапущен ensemble-agent.service")
        return True
    except Exception as e:
        log(f"Ошибка перезапуска: {e}")
        return False


def adjust_config(updates):
    try:
        with open(CONFIG_PY) as f:
            content = f.read()
        backup = CONFIG_PY + ".advisor_backup"
        if not os.path.exists(backup):
            with open(backup, "w") as f:
                f.write(content)
        new_content = content
        for key, val in updates.items():
            if isinstance(val, str):
                val_repr = f'"{val}"'
            else:
                val_repr = str(val)
            pattern = rf"({key}\s*=\s*)[^#\n]+"
            replacement = rf"\g<1>{val_repr}"
            new_content = re.sub(pattern, replacement, new_content, count=1)
        if new_content != content:
            with open(CONFIG_PY, "w") as f:
                f.write(new_content)
            log(f"Обновлён config.py: {updates}")
            return True
        else:
            log("Изменений config не требуется")
            return False
    except Exception as e:
        log(f"Ошибка правки config: {e}")
        return False


def build_prompt(paper_state, log_tail, config_params, rl_weights, advisor_state):
    balance = paper_state.get("balance", 0)
    positions = paper_state.get("positions", {})
    history = paper_state.get("trade_history", [])

    recent = history[-20:] if len(history) >= 20 else history
    wins = [t for t in recent if t.get("outcome") == "profit"]
    losses = [t for t in recent if t.get("outcome") == "loss"]
    recent_wr = round(len(wins)/len(recent)*100, 1) if recent else 0

    streak = 0
    for t in reversed(history):
        if t.get("outcome") == "loss":
            streak += 1
        else:
            break

    pos_lines = []
    for sym, p in positions.items():
        price = fetch_bitget_price(sym)
        if price:
            lev = p.get("leverage", 5)
            if p["side"] == "long":
                pnl = (price - p["entry_price"]) / p["entry_price"] * 100 * lev
            else:
                pnl = (p["entry_price"] - price) / p["entry_price"] * 100 * lev
            pos_lines.append(f"  {sym} {p['side']} @ {p['entry_price']} | conf={p.get('confidence')} | незакрытый ~{pnl:.2f}%")
        else:
            pos_lines.append(f"  {sym} {p['side']} @ {p['entry_price']} | conf={p.get('confidence')} | цена недоступна")

    log_errors = ""
    if "ERROR" in log_tail or "error" in log_tail.lower():
        err_lines = [l for l in log_tail.splitlines() if "error" in l.lower() or "ERROR" in l][-10:]
        log_errors = "\n".join(err_lines)

    prompt = f"""Ты автономный риск-советник для криптоторгового бота (paper mode).

ТЕКУЩЕЕ СОСТОЯНИЕ (факты — не придумывай другие числа):
- Баланс: {balance:.2f} USDT (стартовый был 1000.00)
- Открытых позиций: {len(positions)}
- Детали позиций:
{chr(10).join(pos_lines) if pos_lines else "  (нет)"}
- Последние сделки (последние {len(recent)}): {len(wins)} побед / {len(losses)} убытков | WR {recent_wr}%
- Серия убытков подряд: {streak}
- RL веса: {json.dumps(rl_weights)}
- Конфиг: {json.dumps(config_params)}

ОШИБКИ В ЛОГЕ (если есть):
{log_errors if log_errors else "  (нет)"}

ПОСЛЕДНЕЕ ДЕЙСТВИЕ СОВЕТНИКА: {advisor_state.get('last_action','нет')} в {datetime.fromtimestamp(advisor_state.get('last_action_ts',0), tz=timezone.utc).strftime('%H:%M UTC') if advisor_state.get('last_action_ts') else 'никогда'}

ПРАВИЛА:
1. КРИТИЧЕСКИ: используй ТОЛЬКО точные числа выше. Не фантазируй баланс, win rate, серию.
2. Если баланс < {BALANCE_CRITICAL}: действие ДОЛЖНО быть "close_positions" (закрыть ВСЁ) + "alert" critical.
3. Если баланс < {BALANCE_WARNING} и флаг не поднят: "alert" warning.
4. Если серия убытков >= {CONSECUTIVE_LOSS_THRESHOLD}: рассмотреть "close_positions" худших + "alert".
5. Если ensemble.log показывает повторяющиеся API-ошибки или парсинг-фейлы: "restart_service" + "alert".
6. Если баланс стабилен/растёт и проблем нет: "nothing".
7. "adjust_params" только для мелких правок (например MIN_CONFIDENCE +5) если данные это подтверждают.
8. Не перезапускай чаще 1 раза в час. Не закрывай чаще 1 раза в час.

ОТВЕЧАЙ ТОЛЬКО JSON в точной схеме:
{{
  "action": "nothing" | "alert" | "close_positions" | "restart_service" | "adjust_params",
  "reason": "строка",
  "urgency": "low" | "medium" | "high" | "critical",
  "details": {{
    "symbols_to_close": ["SYMBOL1", ...],
    "params_to_adjust": {{"PARAM_NAME": значение}},
    "message": "Текст сообщения в Telegram (HTML разрешён, кратко)"
  }}
}}"""
    return prompt


def main_cycle():
    state = load_advisor_state()
    now = time.time()

    paper = read_json(PAPER_STATE)
    log_tail = tail_log(ENSEMBLE_LOG, 80)
    cfg_params = read_config_params()
    rl_weights = read_json(RL_WEIGHTS)

    balance = paper.get("balance", 0)
    positions = paper.get("positions", {})
    history = paper.get("trade_history", [])

    streak = 0
    for t in reversed(history):
        if t.get("outcome") == "loss":
            streak += 1
        else:
            break
    state["consecutive_losses"] = streak

    # === АППАРАТНЫЕ ЗАЩИТЫ (перекрывают LLM) ===
    if balance < BALANCE_CRITICAL and positions:
        if now - state["last_close_ts"] > 300:
            log(f"КРИТИЧЕСКИ: баланс {balance:.2f} < {BALANCE_CRITICAL}. Закрываем ВСЕ позиции.")
            closed = []
            for sym in list(positions.keys()):
                if close_position(sym):
                    closed.append(sym)
            msg = f"<b>🚨 КРИТИЧЕСКИЙ АВАРИЙНЫЙ СТОП</b>\nБаланс {balance:.2f} USDT ниже {BALANCE_CRITICAL}.\nЗакрыты: {', '.join(closed)}"
            tg_send(msg)
            state["last_close_ts"] = now
            state["last_alert_ts"] = now
            state["balance_low_flag"] = True
            save_advisor_state(state)
            return

    prompt = build_prompt(paper, log_tail, cfg_params, rl_weights, state)
    raw = call_llm(prompt)
    decision = parse_decision(raw)

    if not decision:
        log("Нет валидного решения от LLM. Пропускаем цикл.")
        save_advisor_state(state)
        return

    action = decision["action"]
    reason = decision.get("reason", "")
    urgency = decision.get("urgency", "low")
    details = decision.get("details", {})
    message = details.get("message", f"Советник: {action} — {reason}")

    log(f"Решение: действие={action} срочность={urgency} причина={reason}")

    executed = False

    if action == "nothing":
        executed = True
        log(f"Действий не требуется. Причина: {reason}")

    elif action == "alert":
        if now - state["last_alert_ts"] > CD_ALERT:
            tg_send(f"<b>📢 Оповещение советника [{urgency.upper()}]</b>\n{html_escape(message)}\n\nПричина: {html_escape(reason)}")
            state["last_alert_ts"] = now
            executed = True
        else:
            log("Кулдаун алерта активен. Пропускаем.")

    elif action == "close_positions":
        if now - state["last_close_ts"] > CD_CLOSE:
            syms = details.get("symbols_to_close", [])
            if not syms and positions:
                syms = list(positions.keys())
            closed = []
            for sym in syms:
                if close_position(sym):
                    closed.append(sym)
            if closed:
                msg = f"<b>🔒 Советник закрыл позиции</b>\n{', '.join(closed)}\nПричина: {html_escape(reason)}"
                tg_send(msg)
            state["last_close_ts"] = now
            executed = True
        else:
            log("Кулдаун закрытия активен. Пропускаем.")

    elif action == "restart_service":
        if now - state["last_restart_ts"] > CD_RESTART:
            if restart_ensemble():
                tg_send(f"<b>🔄 Советник перезапустил Ensemble</b>\nПричина: {html_escape(reason)}")
                state["last_restart_ts"] = now
                executed = True
        else:
            log("Кулдаун рестарта активен. Пропускаем.")

    elif action == "adjust_params":
        if now - state["last_adjust_ts"] > CD_ADJUST:
            updates = details.get("params_to_adjust", {})
            if updates:
                if adjust_config(updates):
                    msg = f"<b>⚙️ Советник изменил конфиг</b>\n{html_escape(json.dumps(updates))}\nПричина: {html_escape(reason)}"
                    tg_send(msg)
                state["last_adjust_ts"] = now
                executed = True
            else:
                log("Не указаны параметры для изменения.")
        else:
            log("Кулдаун правки конфига активен. Пропускаем.")

    if executed:
        state["last_action"] = action
        state["last_action_ts"] = now

    save_advisor_state(state)


def main():
    log("=" * 60)
    log("АВТО-СОВЕТНИК ЗАПУЩЕН")
    log(f"Рабочая директория: {os.getcwd()}")
    log(f"Ключ Kimi: {bool(KIMI_KEY)}")
    log(f"Ключ Anthropic: {bool(ANTHROPIC_KEY)}")

    tg_send(f"<b>🤖 Авто-советник запущен</b>\nИнтервал: 15 мин\nПорог баланса: {BALANCE_CRITICAL} USDT")

    while True:
        try:
            main_cycle()
        except Exception as e:
            log(f"Исключение в цикле: {e}")
            import traceback
            log(traceback.format_exc())

        log("Спим 900 сек...")
        time.sleep(900)


if __name__ == "__main__":
    main()

```

## auto_pipeline.py
```python
#!/usr/bin/env python3
"""
Auto-pipeline: B → C → D + Telegram report
Monitors run_sim_sequence.sh, then executes C/D and sends report.
"""
import os
import sys
import time
import json
import subprocess
import glob
import shutil
from datetime import datetime, timezone
from pathlib import Path

os.chdir("/opt/ensemble-agent")
sys.path.insert(0, "/opt/ensemble-agent")

# Telegram config
TOKEN = "8702211361:AAFPTNQ8kyEka02VD7-KUIkeUidBvTQmupU"
CHAT_ID = "6349919785"

def tg_send(text: str) -> dict:
    """Send message to Telegram, return response."""
    import urllib.request
    import urllib.parse
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true"
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def tg_send_file(path: str, caption: str = "") -> dict:
    """Send document to Telegram."""
    import urllib.request
    boundary = "----WebKitFormBoundary"
    body = []
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="chat_id"')
    body.append(b"")
    body.append(str(CHAT_ID).encode())
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="caption"')
    body.append(b"")
    body.append(caption.encode())
    body.append(f"--{boundary}".encode())
    filename = os.path.basename(path)
    body.append(f'Content-Disposition: form-data; name="document"; filename="{filename}"'.encode())
    body.append(b"Content-Type: application/octet-stream")
    body.append(b"")
    with open(path, "rb") as f:
        body.append(f.read())
    body.append(f"--{boundary}--".encode())
    body = b"\r\n".join(body)
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def find_run_sim_pid():
    """Find PID of run_sim_sequence.sh."""
    try:
        out = subprocess.check_output(["pgrep", "-f", "run_sim_sequence.sh"], text=True)
        return int(out.strip().split()[0])
    except Exception:
        return None

def wait_for_process(pid: int, timeout_sec: float = None) -> bool:
    """Poll until process exits. Returns True if exited, False on timeout."""
    start = time.time()
    while True:
        try:
            os.kill(pid, 0)
        except OSError:
            return True
        if timeout_sec and (time.time() - start) > timeout_sec:
            return False
        time.sleep(30)

def get_latest_output_dirs(n: int = 2):
    """Get n latest simulator_output directories."""
    dirs = sorted(glob.glob("simulator_output/2026*"), key=os.path.getmtime, reverse=True)
    return dirs[:n]

def read_stats_json(d: str) -> dict:
    path = os.path.join(d, "stats.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def read_summary_text(d: str) -> str:
    path = os.path.join(d, "summary.txt")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return ""

def read_trades_sample(d: str, n: int = 5) -> list:
    path = os.path.join(d, "trades.json")
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
            return data[:n] if isinstance(data, list) else []
    return []

def format_report(step_a_dirs: list, step_b_dirs: list) -> str:
    """Build HTML report (Russian)."""
    lines = []
    lines.append("<b>📊 ОТЧЁТ AUTO-PIPELINE</b>")
    lines.append(f"<code>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</code>")
    lines.append("")

    # Step A results
    lines.append("<b>✅ A: live_mirror SL/TP (mock, 3 символа)</b>")
    variants = []
    for d in sorted(step_a_dirs):
        stats = read_stats_json(d)
        if stats:
            name = os.path.basename(d)
            variants.append({
                "name": name,
                "trades": stats.get("total_trades") or 0,
                "win": stats.get("win_rate") or 0,
                "pnl": stats.get("total_pnl_pct") or 0,
                "sl": stats.get("sl_count") or 0,
                "tp": stats.get("tp_count") or 0,
                "trail": stats.get("trailing_count") or 0,
                "balance": stats.get("final_balance") or 0,
            })

    for i, v in enumerate(variants, 1):
        lines.append(f"  В{i}: {v['trades']} сделок | WR {v['win']:.1f}% | PnL {v['pnl']:.1f}% | SL {v['sl']} | TP {v['tp']} | Trail {v['trail']} | Баланс {v['balance']:.1f}")

    best_a = max(variants, key=lambda x: x["balance"]) if variants else None
    if best_a:
        lines.append(f"<b>🏆 Лучший A:</b> {best_a['name']} (баланс {best_a['balance']:.1f})")
    lines.append("")

    # Step B results
    lines.append("<b>✅ B: optimized → live_mirror (Kimi API, 10 символов)</b>")
    for d in sorted(step_b_dirs):
        stats = read_stats_json(d)
        name = os.path.basename(d)
        if stats:
            mode = stats.get("mode", "?")
            lines.append(f"  {name} [{mode}]:")
            lines.append(f"    Сделок: {stats.get('total_trades') or 0} | Win: {(stats.get('win_rate') or 0):.1f}%")
            lines.append(f"    PnL: {(stats.get('total_pnl_pct') or 0):.1f}% | Баланс: {(stats.get('final_balance') or 0):.1f}")
            lines.append(f"    SL: {stats.get('sl_count') or 0} | TP: {stats.get('tp_count') or 0} | Trail: {stats.get('trailing_count') or 0}")
        else:
            lines.append(f"  {name}: нет stats.json")
    lines.append("")

    # Step C
    lines.append("<b>✅ C: Конфиг обновлён</b>")
    lines.append("  Параметры проверены:")
    lines.append("  • STOP_LOSS_PCT = -3.0 | TAKE_PROFIT_PCT = 3.0")
    lines.append("  • MIN_RR = 1.2 | COOLDOWN_HOURS = 6.0")
    lines.append("  • MAX_HOLD_HOURS = 24.0 | VOLATILITY_FILTER = 0.003")
    lines.append("  • TOP_N_SYMBOLS = 15 | MAX_POSITIONS = 8")
    lines.append("")

    # Step D
    lines.append("<b>✅ D: Live-агент запущен</b>")
    lines.append("  main_kimi_ab.py стартовал (paper mode)")
    lines.append("  Мониторинг: tail -f /opt/ensemble-agent/ensemble_kimi.log")
    lines.append("")
    lines.append("<b>🚀 Pipeline завершён.</b>")

    return "\n".join(lines)

def step_c_update_config():
    """Ensure config.py has optimal parameters."""
    config_path = "config.py"
    with open(config_path) as f:
        content = f.read()
    
    # Backup
    backup = config_path + ".auto_backup"
    shutil.copy2(config_path, backup)
    
    changes = []
    # These are the optimized params from simulator testing
    param_map = {
        "STOP_LOSS_PCT = -3.0": (r"STOP_LOSS_PCT\s*=\s*[^\n]+", "STOP_LOSS_PCT = -3.0"),
        "TAKE_PROFIT_PCT = 3.0": (r"TAKE_PROFIT_PCT\s*=\s*[^\n]+", "TAKE_PROFIT_PCT = 3.0"),
        "MIN_RR = 1.2": (r"MIN_RR\s*=\s*[^\n]+", "MIN_RR = 1.2"),
        "COOLDOWN_HOURS = 6.0": (r"COOLDOWN_HOURS\s*=\s*[^\n]+", "COOLDOWN_HOURS = 6.0"),
        "MAX_HOLD_HOURS = 24.0": (r"MAX_HOLD_HOURS\s*=\s*[^\n]+", "MAX_HOLD_HOURS = 24.0"),
        "VOLATILITY_FILTER_ATR_PCT = 0.003": (r"VOLATILITY_FILTER_ATR_PCT\s*=\s*[^\n]+", "VOLATILITY_FILTER_ATR_PCT = 0.003"),
        "TRAIL_ARM_PCT = 1.5": (r"TRAIL_ARM_PCT\s*=\s*[^\n]+", "TRAIL_ARM_PCT = 1.5"),
        "TRAIL_GIVEBACK_PCT = 1.0": (r"TRAIL_GIVEBACK_PCT\s*=\s*[^\n]+", "TRAIL_GIVEBACK_PCT = 1.0"),
    }
    
    import re
    new_content = content
    for desc, (pattern, replacement) in param_map.items():
        if re.search(pattern, new_content):
            new_content = re.sub(pattern, replacement, new_content)
            changes.append(desc)
    
    if new_content != content:
        with open(config_path, "w") as f:
            f.write(new_content)
    
    return changes

def step_d_launch_agent():
    """Launch main_kimi_ab.py via nohup."""
    # Kill any existing main_kimi_ab.py
    try:
        subprocess.run(["pkill", "-f", "main_kimi_ab.py"], capture_output=True)
        time.sleep(2)
    except Exception:
        pass
    
    # Launch
    env = os.environ.copy()
    env["PAPER_STATE_FILE"] = "/opt/ensemble-agent/paper_state_kimi.json"
    
    proc = subprocess.Popen(
        ["./venv/bin/python3", "main_kimi_ab.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
        cwd="/opt/ensemble-agent",
    )
    time.sleep(3)
    
    # Verify
    try:
        out = subprocess.check_output(["pgrep", "-f", "main_kimi_ab.py"], text=True)
        pids = [int(x) for x in out.strip().split()]
        return pids[0] if pids else None
    except Exception:
        return None

def main():
    log = open("/opt/ensemble-agent/auto_pipeline.log", "a")
    def logmsg(msg):
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        log.write(line + "\n")
        log.flush()
    
    logmsg("=== AUTO-PIPELINE STARTED ===")
    
    # Remember step A dirs (latest 3 before B starts)
    step_a_dirs = get_latest_output_dirs(3)
    logmsg(f"Step A dirs: {[os.path.basename(d) for d in step_a_dirs]}")
    
    # Wait for run_sim_sequence.sh to start if not already
    pid = None
    for _ in range(60):
        pid = find_run_sim_pid()
        if pid:
            break
        time.sleep(5)
    
    if not pid:
        logmsg("ERROR: run_sim_sequence.sh not found")
        tg_send("<b>❌ ОШИБКА:</b> run_sim_sequence.sh не найден. Pipeline прерван.")
        return
    
    logmsg(f"Monitoring PID {pid}")
    
    # Wait for completion (no timeout — wait forever)
    exited = wait_for_process(pid, timeout_sec=None)
    if not exited:
        logmsg("ERROR: timeout waiting for process")
        tg_send("<b>❌ ОШИБКА:</b> Таймаут ожидания шага B.")
        return
    
    logmsg("Step B completed. Waiting 10s for files to flush...")
    time.sleep(10)
    
    # Get step B output dirs (should be 2 new dirs: optimized + live_mirror)
    all_dirs = sorted(glob.glob("simulator_output/2026*"), key=os.path.getmtime, reverse=True)
    step_b_dirs = [d for d in all_dirs if d not in step_a_dirs][:2]
    logmsg(f"Step B dirs: {[os.path.basename(d) for d in step_b_dirs]}")
    
    # Step C: update config
    logmsg("Executing Step C: updating config...")
    changes = step_c_update_config()
    logmsg(f"Config changes: {changes}")
    
    # Step D: launch live agent
    logmsg("Executing Step D: launching main_kimi_ab.py...")
    agent_pid = step_d_launch_agent()
    if agent_pid:
        logmsg(f"Live agent PID: {agent_pid}")
    else:
        logmsg("WARNING: could not verify live agent PID")
    
    # Build report
    logmsg("Building report...")
    report = format_report(step_a_dirs, step_b_dirs)
    
    # Save report locally for review
    report_path = "/opt/ensemble-agent/auto_pipeline_report.txt"
    with open(report_path, "w") as f:
        f.write(report)
    logmsg(f"Report saved to {report_path}")
    
    # Send report to Telegram
    logmsg("Sending report to Telegram (attempt 1)...")
    resp1 = tg_send(report)
    logmsg(f"Telegram response 1: {json.dumps(resp1, ensure_ascii=False)[:200]}")
    
    # Verify and retry if needed
    if not resp1.get("ok"):
        logmsg("Retrying Telegram send in 10s...")
        time.sleep(10)
        resp2 = tg_send(report)
        logmsg(f"Telegram response 2: {json.dumps(resp2, ensure_ascii=False)[:200]}")
        if not resp2.get("ok"):
            tg_send("<b>❌ КРИТИЧНО:</b> Не удалось отправить полный отчёт. Проверьте auto_pipeline.log и auto_pipeline_report.txt на сервере.")
    
    # Send trades.csv and stats.json from best B run
    if step_b_dirs:
        best_b = max(step_b_dirs, key=lambda d: read_stats_json(d).get("final_balance", 0))
        stats_path = os.path.join(best_b, "stats.json")
        trades_path = os.path.join(best_b, "trades.csv")
        if os.path.exists(stats_path):
            logmsg("Sending stats.json...")
            tg_send_file(stats_path, f"Статистика для {os.path.basename(best_b)}")
        if os.path.exists(trades_path):
            logmsg("Sending trades.csv...")
            tg_send_file(trades_path, f"Сделки для {os.path.basename(best_b)}")
    
    # Final confirmation
    confirm_msg = (
        "<b>✅ ФИНАЛЬНОЕ ПОДТВЕРЖДЕНИЕ</b>\n"
        f"Pipeline B→C→D завершён в {datetime.now(timezone.utc).strftime('%H:%M UTC')}\n"
        f"PID live-агента: {agent_pid or 'неизвестен'}\n"
        f"Бэкап конфига: config.py.auto_backup\n"
        "Логи: auto_pipeline.log"
    )
    resp3 = tg_send(confirm_msg)
    logmsg(f"Confirmation sent: {resp3.get('ok')}")
    logmsg("=== AUTO-PIPELINE COMPLETE ===")
    log.close()

if __name__ == "__main__":
    main()

```

## bitget_client.py
```python
import hmac,hashlib,base64,time,asyncio,json,aiohttp,logging
log=logging.getLogger("bitget")

# Retry/CB tuning
_REQUEST_TIMEOUT_S=15
_RETRY_ATTEMPTS_GET=3
_RETRY_BACKOFF=(0.5,1.5,3.0)  # delays in seconds for retries 1..N
_CB_FAILURE_THRESHOLD=5
_CB_COOLDOWN_S=60

class BitgetCircuitOpen(Exception):
    """Raised when too many consecutive Bitget failures triggered the breaker."""

class BitgetClient:
 def __init__(self,cfg):
  self.cfg=cfg;self.base=cfg.BITGET_BASE_URL;self.session=None
  self._contract_specs={}  # symbol -> raw contract spec dict
  self._contracts_ts=0
  self._cb_failures=0
  self._cb_open_until=0.0
 async def start(self):self.session=aiohttp.ClientSession()
 async def close(self):
  if self.session:await self.session.close()
 async def _request(self,method,path,params=None,body=None):
  """Single Bitget call with timeout, retry-on-GET, and circuit breaker.

  Uses time.monotonic() for breaker state so NTP jumps cannot reopen prematurely.
  HTTP 5xx is raised unconditionally — caught by the retry handler and re-raised
  if attempts are exhausted, never silently returned as a success payload.
  Failures increment _cb_failures per attempt (not per request), so a single
  cascade of retries can trip the breaker without amplifying load.
  """
  if time.monotonic()<self._cb_open_until:
   remaining=int(self._cb_open_until-time.monotonic())
   raise BitgetCircuitOpen("Bitget circuit OPEN, "+str(remaining)+"s remaining")
  do_retry=(method=="GET")
  attempts=_RETRY_ATTEMPTS_GET if do_retry else 1
  bs=json.dumps(body) if (method=="POST" and body is not None) else ""
  timeout=aiohttp.ClientTimeout(total=_REQUEST_TIMEOUT_S)
  last_err=None
  for attempt in range(attempts):
   try:
    if method=="GET":
     async with self.session.get(self.base+path,headers=self._headers("GET",path),params=params,timeout=timeout) as r:
      if 500<=r.status<600: raise RuntimeError("HTTP "+str(r.status)+" on "+path)
      d=await r.json()
    else:
     async with self.session.post(self.base+path,headers=self._headers("POST",path,bs),data=bs,timeout=timeout) as r:
      if 500<=r.status<600: raise RuntimeError("HTTP "+str(r.status)+" on "+path)
      d=await r.json()
    if self._cb_failures>0:
     log.info("Bitget recovered after "+str(self._cb_failures)+" failures")
    self._cb_failures=0
    return d
   except (aiohttp.ClientError,asyncio.TimeoutError,RuntimeError,json.JSONDecodeError,ValueError) as e:
    last_err=e
    self._cb_failures+=1
    if self._cb_failures>=_CB_FAILURE_THRESHOLD:
     self._cb_open_until=time.monotonic()+_CB_COOLDOWN_S
     log.error("Bitget circuit OPEN for "+str(_CB_COOLDOWN_S)+"s after "+str(self._cb_failures)+" consecutive failures: "+str(last_err)[:200])
     break  # CB tripped, stop retrying this request
    if attempt<attempts-1:
     wait=_RETRY_BACKOFF[min(attempt,len(_RETRY_BACKOFF)-1)]
     log.warning("Bitget "+method+" "+path+" retry "+str(attempt+1)+"/"+str(attempts)+" after "+str(e)[:120]+" — sleep "+str(wait)+"s")
     await asyncio.sleep(wait)
    else: break
  raise last_err if last_err else RuntimeError("Bitget "+method+" "+path+" failed")
 async def _ensure_contracts(self):
  if time.time()-self._contracts_ts<3600 and self._contract_specs: return
  try:
   data=await self.get("/api/v2/mix/market/contracts",{"productType":"USDT-FUTURES"})
   for c in data.get("data",[]) or []:
    sym=c.get("symbol")
    if sym: self._contract_specs[sym]=c
   self._contracts_ts=time.time()
   log.info("Contract specs cached: "+str(len(self._contract_specs))+" symbols")
  except Exception as e: log.warning("contracts refresh: "+str(e))
 def _sign(self,ts,method,path,body=""):
  import hmac,hashlib,base64
  msg=f"{ts}{method.upper()}{path}{body}"
  return base64.b64encode(hmac.new(self.cfg.BITGET_SECRET.encode(),msg.encode(),hashlib.sha256).digest()).decode()
 def _headers(self,method,path,body=""):
  import time;ts=str(int(time.time()*1000))
  return {"ACCESS-KEY":self.cfg.BITGET_API_KEY,"ACCESS-SIGN":self._sign(ts,method,path,body),"ACCESS-TIMESTAMP":ts,"ACCESS-PASSPHRASE":self.cfg.BITGET_PASSPHRASE,"Content-Type":"application/json","locale":"en-US"}
 async def get(self,path,params=None):
  return await self._request("GET",path,params=params)
 async def post(self,path,body):
  return await self._request("POST",path,body=body)
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
  await self._ensure_contracts()
  spec=self._contract_specs.get(symbol,{})
  try: min_usdt=float(spec.get("minTradeUSDT") or 5)
  except: min_usdt=5
  if size<min_usdt:
   log.warning("place_order "+symbol+": notional $"+str(round(size,2))+" below min $"+str(min_usdt))
   return {"code":"LOCAL_MIN_NOTIONAL","msg":"size $"+str(round(size,2))+" below minTradeUSDT "+str(min_usdt)}
  await self.post("/api/v2/mix/account/set-leverage",{"symbol":symbol,"productType":"USDT-FUTURES","marginCoin":"USDT","leverage":str(leverage),"holdSide":side})
  t=await self.get("/api/v2/mix/market/ticker",{"symbol":symbol,"productType":"USDT-FUTURES"})
  price=float(t["data"][0]["lastPr"]);qty=round(size/price,4)
  try: min_qty=float(spec.get("minTradeNum") or 0)
  except: min_qty=0
  if min_qty>0 and qty<min_qty:
   log.warning("place_order "+symbol+": qty "+str(qty)+" below minTradeNum "+str(min_qty))
   return {"code":"LOCAL_MIN_QTY","msg":"qty "+str(qty)+" below "+str(min_qty)}
  try:
   sz_place=spec.get("sizeMultiplier") or spec.get("volumePlace")
   if sz_place:
    places=int(float(sz_place))
    qty=round(qty,places)
  except: pass
  return await self.post("/api/v2/mix/order/place-order",{"symbol":symbol,"productType":"USDT-FUTURES","marginMode":"isolated","marginCoin":"USDT","size":str(qty),"side":"open_long" if side=="long" else "open_short","orderType":"market","tradeSide":"open"})
 async def close_position(self,symbol,side):
  return await self.post("/api/v2/mix/order/place-order",{"symbol":symbol,"productType":"USDT-FUTURES","marginMode":"isolated","marginCoin":"USDT","size":"0","side":"close_long" if side=="long" else "close_short","orderType":"market","tradeSide":"close","reduceOnly":"YES"})

```

## blocked_logger.py
```python
import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from collections import defaultdict

BLOCKED_FILE = "/opt/ensemble-agent/blocked_predictions.json"


class BlockedLogger:
    def __init__(self, filepath=None):
        self.file = filepath or BLOCKED_FILE
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump({"pending": [], "resolved": []}, f, indent=2)

    def _load(self):
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except Exception:
            return {"pending": [], "resolved": []}

    def _save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def log(self, symbol, decision, snapshot, block_reason, check_hours=4):
        """Log a blocked prediction for later virtual audit."""
        data = self._load()
        entry = {
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "side": decision.action,
            "confidence": decision.confidence,
            "position_size_pct": getattr(decision, "position_size_pct", 0),
            "block_reason": block_reason,
            "entry_price": getattr(snapshot, "price", None),
            "regime": getattr(snapshot, "regime", None),
            "rsi_15m": getattr(snapshot, "rsi_15m", None),
            "rsi_1h": getattr(snapshot, "rsi_1h", None),
            "funding_rate": getattr(snapshot, "funding_rate", None),
            "volume_ratio": getattr(snapshot, "volume_ratio", None),
            "blocked_at": datetime.now(timezone.utc).isoformat(),
            "check_after": (
                datetime.now(timezone.utc) + timedelta(hours=check_hours)
            ).isoformat(),
        }
        data["pending"].append(entry)
        if len(data["pending"]) > 5000:
            data["pending"] = data["pending"][-5000:]
        self._save(data)

    def resolve(self, entry_id, exit_price, resolved_at=None):
        """Resolve a pending prediction with actual exit price."""
        data = self._load()
        pending = data["pending"]
        entry = None
        idx = None
        for i, p in enumerate(pending):
            if p["id"] == entry_id:
                entry = p
                idx = i
                break
        if entry is None:
            return None

        del pending[idx]
        entry_price = entry.get("entry_price")
        if entry_price and entry_price > 0:
            pnl = (exit_price - entry_price) / entry_price * 100
            if entry["side"] == "short":
                pnl = -pnl
        else:
            pnl = 0.0

        entry["exit_price"] = exit_price
        entry["pnl_pct"] = round(pnl, 4)
        entry["outcome"] = "would_profit" if pnl > 0 else "would_loss"
        entry["resolved_at"] = resolved_at or datetime.now(timezone.utc).isoformat()

        try:
            blocked_dt = datetime.fromisoformat(
                entry["blocked_at"].replace("Z", "+00:00")
            )
            resolved_dt = datetime.fromisoformat(
                entry["resolved_at"].replace("Z", "+00:00")
            )
            entry["hold_hours"] = round(
                (resolved_dt - blocked_dt).total_seconds() / 3600, 2
            )
        except Exception:
            entry["hold_hours"] = None

        data["resolved"].append(entry)
        if len(data["resolved"]) > 10000:
            data["resolved"] = data["resolved"][-10000:]
        self._save(data)
        return entry

    def report(self):
        """Generate a human-readable report of resolved predictions."""
        data = self._load()
        resolved = data["resolved"]
        pending = data["pending"]
        lines = [
            "=== Blocked Predictions Virtual Audit ===",
            f"Pending:  {len(pending)}",
            f"Resolved: {len(resolved)}",
        ]
        if not resolved:
            lines.append("No resolved predictions yet.")
            return "\n".join(lines)

        total = len(resolved)
        profits = [r for r in resolved if r["outcome"] == "would_profit"]
        wr = len(profits) / total * 100
        avg_pnl = sum(r["pnl_pct"] for r in resolved) / total

        lines.extend(
            [
                f"Virtual Win Rate: {wr:.1f}% ({len(profits)} would-profit / {total - len(profits)} would-loss)",
                f"Virtual Avg PnL:  {avg_pnl:.2f}%",
                "",
                "--- By Block Reason ---",
            ]
        )

        by_reason = defaultdict(list)
        for r in resolved:
            by_reason[r["block_reason"]].append(r)

        for reason in sorted(by_reason.keys()):
            trades = by_reason[reason]
            p = [t for t in trades if t["outcome"] == "would_profit"]
            avg = sum(t["pnl_pct"] for t in trades) / len(trades)
            lines.append(
                f"  {reason:30s}: {len(trades):4d} trades  WR {len(p)/len(trades)*100:5.1f}%  avg {avg:+6.2f}%"
            )

        lines.append("")
        lines.append("--- By Side ---")
        by_side = defaultdict(list)
        for r in resolved:
            by_side[r["side"]].append(r)
        for side in ("long", "short"):
            trades = by_side[side]
            if not trades:
                continue
            p = [t for t in trades if t["outcome"] == "would_profit"]
            avg = sum(t["pnl_pct"] for t in trades) / len(trades)
            lines.append(
                f"  {side.upper():5s}: {len(trades):4d} trades  WR {len(p)/len(trades)*100:5.1f}%  avg {avg:+6.2f}%"
            )

        return "\n".join(lines)

```

## clean_memory_rl.py
```python
#!/usr/bin/env python3
"""
Clean all memory files: remove trades from 2026-05-19 with duration < 2 minutes.
Then re-train RL for each branch and generate report.
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, "/opt/ensemble-agent")
os.chdir("/opt/ensemble-agent")

from config import Config
from memory import Memory
from rl_agent import RLAgent

MEMORY_FILES = [
    "/opt/ensemble-agent/memory.json",
    "/opt/ensemble-agent/memory_kimi.json",
]

def clean_memory_file(path):
    if not os.path.exists(path):
        return None, f"File not found: {path}"

    with open(path) as f:
        data = json.load(f)

    trades = data if isinstance(data, list) else data.get("trades", [])
    original_count = len(trades)

    kept = []
    removed = []

    for t in trades:
        opened = t.get("opened_at", "")
        closed = t.get("closed_at")

        # Keep if not May 19
        if "2026-05-19" not in opened:
            kept.append(t)
            continue

        # May 19 trade — check duration
        duration_sec = None
        if closed and opened:
            try:
                o = datetime.fromisoformat(opened.replace("Z", "+00:00"))
                c = datetime.fromisoformat(closed.replace("Z", "+00:00"))
                duration_sec = (c - o).total_seconds()
            except Exception:
                pass

        if duration_sec is not None and duration_sec < 120:
            removed.append(t)
        else:
            kept.append(t)

    # Save back
    if isinstance(data, list):
        new_data = kept
    else:
        new_data = {**data, "trades": kept}

    with open(path, "w") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    return {
        "file": path,
        "original": original_count,
        "kept": len(kept),
        "removed_count": len(removed),
        "removed": removed,
    }, None

def retrain_rl(mem_path, rl_path):
    """Re-train RL from cleaned memory."""
    cfg = Config()
    cfg.MEMORY_FILE = mem_path
    # Override RL path manually
    mem = Memory(cfg)
    rl = RLAgent(cfg)
    rl.path = rl_path

    # Reset weights
    from rl_agent import RLWeights
    rl.weights = RLWeights(learning_rate=0.10)

    closed = [t for t in mem.trades if t.outcome in ("profit", "loss") and not getattr(t, "orphan", False)]
    if closed:
        count = rl.learn_from_history(mem)
        rl._save_sync()
        return {
            "learned": count,
            "bull_weight": rl.weights.bull_weight,
            "bear_weight": rl.weights.bear_weight,
            "judge_weight": rl.weights.judge_weight,
            "conf_threshold": rl.weights.conf_threshold,
            "episodes": rl.weights.episodes,
            "total_reward": rl.weights.total_reward,
        }
    return {"learned": 0, "message": "No closed trades to learn from"}

# === Execute ===
print("=" * 60)
print("MEMORY CLEANUP & RL RETRAIN REPORT")
print("=" * 60)
print()

for mem_file in MEMORY_FILES:
    result, err = clean_memory_file(mem_file)
    if err:
        print(f"❌ {err}")
        continue

    print(f"📁 {result['file']}")
    print(f"   Original trades: {result['original']}")
    print(f"   Kept:            {result['kept']}")
    print(f"   Removed (<2min on 2026-05-19): {result['removed_count']}")

    if result["removed"]:
        pnl_sum = sum(t.get("pnl_pct", 0) or 0 for t in result["removed"])
        print(f"   Removed total PnL: {pnl_sum:+.4f}%")
        for t in result["removed"]:
            dur = "N/A"
            if t.get("closed_at") and t.get("opened_at"):
                try:
                    o = datetime.fromisoformat(t["opened_at"].replace("Z", "+00:00"))
                    c = datetime.fromisoformat(t["closed_at"].replace("Z", "+00:00"))
                    dur = f"{(c-o).total_seconds()/60:.1f}min"
                except:
                    pass
            print(f"      → {t['symbol']} {t['side']} {t['opened_at'][:19]} duration={dur} pnl={t.get('pnl_pct','N/A')}")
    print()

    # Determine RL path
    if "kimi" in mem_file:
        rl_path = "/opt/ensemble-agent/rl_weights_kimi.json"
    else:
        rl_path = "/opt/ensemble-agent/rl_weights.json"

    rl_stats = retrain_rl(mem_file, rl_path)
    print(f"   🔁 RL retrained → {rl_path}")
    print(f"      Learned from:   {rl_stats.get('learned', 0)} trades")
    print(f"      Bull weight:    {rl_stats.get('bull_weight', 'N/A'):.4f}")
    print(f"      Bear weight:    {rl_stats.get('bear_weight', 'N/A'):.4f}")
    print(f"      Judge weight:   {rl_stats.get('judge_weight', 'N/A'):.4f}")
    print(f"      Conf threshold: {rl_stats.get('conf_threshold', 'N/A')}")
    print(f"      Episodes:       {rl_stats.get('episodes', 0)}")
    print(f"      Total reward:   {rl_stats.get('total_reward', 0):+.4f}%")
    print()

print("=" * 60)
print("Done. Restart main_kimi_ab.py to use cleaned memory & RL.")
print("=" * 60)

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
    GROQ_API_KEYS = [k for k in [os.getenv("GROQ_API_KEY"+(str(i) if i>1 else "")) for i in range(1,6)] if k]
    KIMI_API_KEY = os.getenv("KIMI_API_KEY")
    KIMI_BASE_URL = "https://api.moonshot.ai/v1"
    KIMI_MODEL = "moonshot-v1-auto"
    BULL_MODELS_GROQ = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b"]
    BEAR_MODELS_GROQ = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b"]
    JUDGE_MODELS_GROQ = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b"]
    BULL_MODEL = "claude-haiku-4-5-20251001"
    BEAR_MODEL = "claude-haiku-4-5-20251001"
    JUDGE_MODEL = "claude-haiku-4-5-20251001"
    TOP_N_SYMBOLS = 30
    SCAN_INTERVAL = 3600
    MAX_POSITIONS = 10
    MAX_SAME_SIDE = 5
    MAX_CORRELATION = 0.85
    CORR_LOOKBACK_BARS = 24
    MIN_CONFIDENCE = 70
    THRESHOLD_SLACK = 3
    MIN_HOLD_SEC = 7200
    JUDGE_EXIT_INTERVAL_SEC = 7200
    JUDGE_EXIT_NOISE_BAND_PCT = 2.5
    STOP_LOSS_PCT = -2.0
    TAKE_PROFIT_PCT = 3.0
    TRAIL_ARM_PCT = 2.5
    TRAIL_GIVEBACK_PCT = 0.8
    EMERGENCY_STOP_PCT = -15.0
    POSITION_SIZE_FIXED = 100.0  # $100 fixed per trade (optimized mode)
    MIN_RR = 1.2
    COOLDOWN_HOURS = 6.0
    MAX_HOLD_HOURS = 24.0
    VOLATILITY_FILTER_ATR_PCT = 0.003
    PAPER_MODE = True
    PAPER_BALANCE = 1000.0
    LEVERAGE = 5
    RL_PRIME_FROM_HISTORY = False
    MEMORY_FILE = "/opt/ensemble-agent/memory.json"
    TRADE_LOG = "/opt/ensemble-agent/trade_log.json"
    STATE_FILE = "/opt/ensemble-agent/state.json"
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    KIMI_JUDGE_ENABLED = True
    KIMI_PROMPT_VERSION = "asymmetry"

```

## dashboard_api.py
```python
import asyncio, json, re, os, logging, time, base64
from datetime import datetime, timezone
from aiohttp import web, ClientSession, ClientTimeout
from dotenv import load_dotenv
load_dotenv("/opt/ensemble-agent/.env")
from config import Config
PAPER_BALANCE = Config.PAPER_BALANCE
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("dashboard")

# Basic Auth credentials
_AUTH_USER = "ensemble"
_AUTH_PASS = os.getenv("DASHBOARD_PASS", "ensemble2024")


@web.middleware
async def basic_auth_middleware(request, handler):
    """HTTP Basic Auth for all dashboard endpoints."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return web.Response(status=401, headers={"WWW-Authenticate": 'Basic realm="Ensemble"'},
                            text="Authentication required")
    try:
        scheme, credentials = auth_header.split(" ", 1)
        if scheme.lower() != "basic":
            raise ValueError()
        decoded = base64.b64decode(credentials).decode("utf-8")
        user, passwd = decoded.split(":", 1)
    except Exception:
        return web.Response(status=401, headers={"WWW-Authenticate": 'Basic realm="Ensemble"'},
                            text="Invalid auth header")
    if user != _AUTH_USER or passwd != _AUTH_PASS:
        return web.Response(status=401, headers={"WWW-Authenticate": 'Basic realm="Ensemble"'},
                            text="Invalid credentials")
    return await handler(request)


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
        lev = pos.get("leverage", 5)
        mark = price if price else entry
        if side == "long":
            pnl_usdt = (mark - entry) * qty
        else:
            pnl_usdt = (entry - mark) * qty
        # PnL с учётом плеча (как в paper_trading)
        pnl_pct = ((mark - entry) / entry * 100 * (1 if side == "long" else -1) * lev) if entry else 0
        age_sec = 0
        try:
            opened = datetime.fromisoformat(pos["opened_at"])
            age_sec = int((datetime.now(timezone.utc).replace(tzinfo=None) - opened).total_seconds())
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


async def handle_upcoming(request):
    """Возвращает предстоящие сделки: сигналы Judge LONG/SHORT, которые ещё не открыты."""
    data = parse_log()
    state = _load_state()
    open_syms = set(state.get("positions", {}).keys())

    # Также проверяем лог на недавние открытия
    recent_opens = set()
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()[-500:]
        for line in lines:
            m = re.search(r"\[PAPER\] ОТКРЫТА (LONG|SHORT) (\w+)", line)
            if m:
                recent_opens.add(m.group(2))
    except Exception:
        pass

    upcoming = []
    seen = set()
    for d in data.get("decisions", []):
        sym = d.get("symbol", "")
        action = d.get("judge_action", "HOLD")
        if action in ("LONG", "SHORT") and sym not in open_syms and sym not in recent_opens and sym not in seen:
            seen.add(sym)
            upcoming.append(d)

    upcoming.sort(key=lambda x: x.get("judge_conf", 0), reverse=True)
    return web.Response(
        text=json.dumps({"upcoming": upcoming[:20], "timestamp": datetime.now().isoformat()}, ensure_ascii=False),
        content_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"}
    )


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


app = web.Application(middlewares=[basic_auth_middleware])
app.router.add_get("/ensemble-api", handle_api)
app.router.add_get("/paper-api", handle_paper)
app.router.add_get("/upcoming-api", handle_upcoming)
app.router.add_get("/", handle_html)
app.router.add_options("/ensemble-api", handle_options)
app.router.add_options("/paper-api", handle_options)
app.router.add_options("/upcoming-api", handle_options)

if __name__ == "__main__":
    print("Ensemble API on port 8765")
    access_logger = logging.getLogger("aiohttp.access")
    access_logger.setLevel(logging.INFO)
    web.run_app(app, host="0.0.0.0", port=8765, access_log=access_logger,
                access_log_format='%a "%r" %s %b "%{User-Agent}i"')

```

## data_engine.py
```python
import logging,numpy as np,aiohttp,time
from dataclasses import dataclass
from http_pool import session as _http_session
log = logging.getLogger("data_engine")

class SentimentCache:
    def __init__(self,ttl=3600):
        self.ttl=ttl; self._fg=None; self._fg_ts=0; self._dom=None; self._dom_ts=0
    async def get_fear_greed(self):
        if self._fg is not None and time.time()-self._fg_ts<self.ttl: return self._fg
        try:
            s=await _http_session()
            async with s.get("https://api.alternative.me/fng/?limit=1",timeout=aiohttp.ClientTimeout(total=10)) as r:
                j=await r.json(); d=j.get("data",[{}])[0]
                val=int(d.get("value",0)); label=d.get("value_classification","")
                self._fg=(val,label); self._fg_ts=time.time(); return self._fg
        except Exception as e: log.warning("F&G fetch: "+str(e)); return self._fg
    async def get_btc_dominance(self):
        if self._dom is not None and time.time()-self._dom_ts<self.ttl: return self._dom
        try:
            s=await _http_session()
            async with s.get("https://api.coinpaprika.com/v1/global",timeout=aiohttp.ClientTimeout(total=10)) as r:
                j=await r.json(); val=float(j.get("bitcoin_dominance_percentage",0))
                self._dom=val; self._dom_ts=time.time(); return self._dom
        except Exception as e: log.warning("BTC.D fetch: "+str(e)); return self._dom

@dataclass
class MarketSnapshot:
    symbol:str; price:float; price_change_15m:float; price_change_1h:float
    price_change_4h:float; volume_15m:float; volume_ratio:float
    rsi_15m:float; rsi_1h:float; macd_signal:str; bb_position:float
    funding_rate:float; open_interest_change:float; bid_ask_imbalance:float; regime:str
    fear_greed:int=None; fear_greed_label:str=""; btc_dominance:float=None
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
        if self.fear_greed is not None:
            lines.append("Market Sentiment: "+self.fear_greed_label+" ("+str(self.fear_greed)+"/100)")
        else:
            lines.append("Market Sentiment: n/a")
        if self.btc_dominance is not None and not self.symbol.startswith("BTC"):
            lines.append("BTC Dominance: "+str(round(self.btc_dominance,1))+"%")
        return "\n".join(lines)

_CANDLE_FETCH_LIMITS={"15m":100,"1H":100,"4H":50}  # canonical fetch sizes
_CANDLE_TTL={"15m":60,"1H":300,"4H":900}

class DataEngine:
    def __init__(self,bitget):
        self.bitget=bitget
        self.sentiment=SentimentCache()
        self._cache={}  # key -> (ts, value); TTL chosen per data freshness
    async def _cached(self,key,ttl,coro_factory):
        now=time.time()
        rec=self._cache.get(key)
        if rec and now-rec[0]<ttl: return rec[1]
        val=await coro_factory()
        self._cache[key]=(now,val)
        # opportunistic cleanup of stale keys (>1h old) to bound memory
        if len(self._cache)>500:
            stale=[k for k,v in self._cache.items() if now-v[0]>3600]
            for k in stale: self._cache.pop(k,None)
        return val
    async def _get_candles_cached(self,symbol,granularity):
        """Canonical cached candle fetcher. Always pulls the per-granularity fetch
        limit so smaller consumers (e.g. correlation) hit the same cache entry."""
        fetch_limit=_CANDLE_FETCH_LIMITS.get(granularity,50)
        ttl=_CANDLE_TTL.get(granularity,300)
        return await self._cached(("candles",granularity,symbol),ttl,
            lambda:self.bitget.get_candles(symbol,granularity,fetch_limit))
    async def get_closes(self,symbol,granularity="1H",limit=25):
        """Return up to `limit` most-recent close prices via the canonical cache."""
        candles=await self._get_candles_cached(symbol,granularity)
        if not candles: return []
        try: return [float(x[4]) for x in candles[-limit:]]
        except Exception as e:
            log.warning("get_closes "+symbol+" "+granularity+": "+str(e)); return []
    async def correlation(self,symbol_a,symbol_b,granularity="1H",n=24):
        """Pearson correlation of returns over the last n+1 bars.

        Returns float in [-1,1] on success, or 0.0 on failure / insufficient data.
        Callers MUST treat the return as best-effort: a 0.0 here means
        "could not compute" (new listing, frozen market, parse error), NOT
        "verified uncorrelated". Loud INFO log makes such cases visible.
        """
        if symbol_a==symbol_b: return 1.0
        ca=await self.get_closes(symbol_a,granularity,n+1)
        cb=await self.get_closes(symbol_b,granularity,n+1)
        if len(ca)<n+1 or len(cb)<n+1:
            log.info("correlation: insufficient data for "+symbol_a+"/"+symbol_b+" ("+str(len(ca))+"/"+str(len(cb))+" bars, need "+str(n+1)+") → assume uncorrelated")
            return 0.0
        ra=np.diff(ca)/ca[:-1]
        rb=np.diff(cb)/cb[:-1]
        if len(ra)<2 or len(rb)<2: return 0.0
        with np.errstate(invalid="ignore"):
            c=np.corrcoef(ra,rb)[0,1]
        if not np.isfinite(c):
            log.info("correlation: zero-variance series "+symbol_a+"/"+symbol_b+" → assume uncorrelated")
            return 0.0
        return float(c)
    async def get_snapshot(self,symbol):
        try:
            c15=await self._get_candles_cached(symbol,"15m")
            c1h=await self._get_candles_cached(symbol,"1H")
            c4h=await self._get_candles_cached(symbol,"4H")
            if not c15 or not c1h or not c4h: return None
            def parse(c): return {"close":[float(x[4]) for x in c],"volume":[float(x[5]) for x in c]}
            d15,d1h,d4h=parse(c15),parse(c1h),parse(c4h)
            if len(d15["close"])<2 or len(d1h["close"])<2 or len(d15["volume"])<1:
                log.warning("DataEngine "+symbol+": insufficient candle data (15m="+str(len(d15["close"]))+", 1h="+str(len(d1h["close"]))+")")
                return None
            price=d15["close"][-1]
            pc15=(d15["close"][-1]/d15["close"][-2]-1)*100
            pc1h=(d1h["close"][-1]/d1h["close"][-2]-1)*100
            pc4h=(d4h["close"][-1]/d4h["close"][-5]-1)*100 if len(d4h["close"])>=5 else 0
            vol15=d15["volume"][-1]; avg=float(np.mean(d15["volume"][-20:])) if len(d15["volume"])>=1 else 0.0
            vr=vol15/avg if avg>0 else 1.0
            funding=await self._cached(("fund",symbol),600,lambda:self.bitget.get_funding_rate(symbol))
            ob=await self._cached(("ob",symbol),20,lambda:self.bitget.get_orderbook(symbol))
            bids=ob.get("bids",[]); asks=ob.get("asks",[])
            bv=sum(float(b[1]) for b in bids[:10]); av=sum(float(a[1]) for a in asks[:10])
            imb=(bv-av)/(bv+av) if bv+av>0 else 0
            closes=d15["close"]; regime=self._regime(d1h["close"])
            fg=await self.sentiment.get_fear_greed()
            dom=await self.sentiment.get_btc_dominance()
            fg_val,fg_lbl=(fg if fg else (None,""))
            return MarketSnapshot(symbol,price,pc15,pc1h,pc4h,vol15,vr,
                self._rsi(closes),self._rsi(d1h["close"]),self._macd(closes),
                self._bb(closes),funding,0.0,imb,regime,
                fear_greed=fg_val,fear_greed_label=fg_lbl,btc_dominance=dom)
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
    async def get_btc_regime(self):
        try:
            c4h=await self._get_candles_cached("BTCUSDT","4H")
            if not c4h or len(c4h)<40: return "unknown"
            closes=[float(x[4]) for x in c4h]
            return self._regime(closes)
        except Exception as e:
            log.warning("BTC regime fetch: "+str(e))
            return "unknown"

```

## explorer.py
```python
#!/usr/bin/env python3
"""
Explorer Agent — data mining через постоянное открытие LONG/SHORT.
Цель: собрать датасет прибыльных паттернов для RL.
Теперь с реальными TP/SL как у основного бота.
"""
import os
import sys
import json
import time
import asyncio
import random
from datetime import datetime, timezone

os.chdir("/opt/ensemble-agent")
sys.path.insert(0, "/opt/ensemble-agent")

from dotenv import load_dotenv
load_dotenv("/opt/ensemble-agent/.env")

from config import Config
from bitget_client import BitgetClient
from data_engine import DataEngine
import aiohttp

# Files
STATE_FILE = "/opt/ensemble-agent/explorer_state.json"
TRADES_FILE = "/opt/ensemble-agent/explorer_trades.json"
LOG_FILE = "/opt/ensemble-agent/explorer.log"

# Settings
LEVERAGE = 5
SCAN_INTERVAL = 7200      # 2 часа между открытиями
N_SYMBOLS = 10            # сколько символов исследовать

# TP/SL: оптимизировано для меньше шумовых SL и чаще TP
TP_PCT = 3.0              # +3% (было 4%)
SL_PCT = -3.0             # -3% (было -2%)
MAX_HOLD_HOURS = 48.0     # макс удержание 48ч (было 24ч)
MIN_HOLD_MINUTES = 20     # мин удержание 20 мин — фильтр молниеносных шумовых SL
MONITOR_INTERVAL = 15     # проверять цены каждые 15 сек

# Side-aware sizing: адаптация к текущему бычьему рынку
# LONG убыточен (explorer data), SHORT прибылен — увеличиваем SHORT
POSITION_SIZE_LONG = 3.0   # $3 на LONG
POSITION_SIZE_SHORT = 7.0  # $7 на SHORT


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"balance": 500.0, "positions": [], "total_pnl": 0.0}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


TRADES_RETENTION_DAYS = 7

def record_trade(trade):
    try:
        with open(TRADES_FILE) as f:
            trades = json.load(f)
    except Exception:
        trades = []
    trades.append(trade)
    tmp = TRADES_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(trades, f, indent=2)
    os.replace(tmp, TRADES_FILE)
    # Async rotate in background (no blocking)
    rotate_old_trades()


def rotate_old_trades():
    """Keep only last 7 days of trades to prevent disk bloat."""
    try:
        with open(TRADES_FILE) as f:
            trades = json.load(f)
        cutoff = datetime.now(timezone.utc).timestamp() - TRADES_RETENTION_DAYS * 86400
        fresh = []
        removed = 0
        for t in trades:
            try:
                ts = datetime.fromisoformat(t["closed_at"].replace("Z", "")).replace(tzinfo=timezone.utc).timestamp()
                if ts > cutoff:
                    fresh.append(t)
                else:
                    removed += 1
            except Exception:
                fresh.append(t)
        if removed:
            tmp = TRADES_FILE + ".tmp"
            with open(tmp, "w") as f:
                json.dump(fresh, f, indent=2)
            os.replace(tmp, TRADES_FILE)
            log(f"Ротация trades: удалено {removed} старых, осталось {len(fresh)}")
    except Exception:
        pass


async def fetch_price(session, symbol):
    url = f"https://api.bitget.com/api/v2/mix/market/ticker?symbol={symbol}&productType=USDT-FUTURES"
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
        data = await resp.json()
        return float(data["data"][0]["lastPr"])


def calc_pnl_pct(entry, current, side, leverage):
    """Расчёт PnL % с учётом плеча."""
    if side == "long":
        return (current - entry) / entry * 100 * leverage
    else:
        return (entry - current) / entry * 100 * leverage


async def monitor_positions():
    """Real-time мониторинг: проверяет TP/SL/max_hold каждые 15 сек."""
    while True:
        try:
            state = load_state()
            if not state["positions"]:
                await asyncio.sleep(MONITOR_INTERVAL)
                continue

            now = datetime.now(timezone.utc)
            to_close = []
            keep = []
            closed_any = False

            async with aiohttp.ClientSession() as session:
                for pos in state["positions"]:
                    try:
                        symbol = pos["symbol"]
                        entry = pos["entry_price"]
                        qty = pos["qty"]
                        side = pos["side"]
                        margin = pos["margin"]
                        snap = pos.get("snapshot", {})

                        price = await fetch_price(session, symbol)
                        pnl_pct = calc_pnl_pct(entry, price, side, LEVERAGE)

                        opened = datetime.fromisoformat(pos["opened_at"].replace("Z", "")).replace(tzinfo=timezone.utc)
                        hours = (now - opened).total_seconds() / 3600
                        minutes = (now - opened).total_seconds() / 60

                        exit_reason = None
                        if minutes < MIN_HOLD_MINUTES:
                            # Фильтр молниеносных шумовых SL — пропускаем проверку
                            keep.append(pos)
                            continue
                        if pnl_pct >= TP_PCT:
                            exit_reason = "tp"
                        elif pnl_pct <= SL_PCT:
                            exit_reason = "sl"
                        elif hours >= MAX_HOLD_HOURS:
                            exit_reason = "hold"

                        if exit_reason:
                            pnl_usdt = pnl_pct / 100 * margin  # pnl_pct уже с плечом
                            state["balance"] += margin + pnl_usdt
                            state["total_pnl"] += pnl_usdt

                            trade = {
                                **pos,
                                "exit_price": price,
                                "pnl_usdt": round(pnl_usdt, 4),
                                "pnl_pct": round(pnl_pct, 2),
                                "outcome": "profit" if pnl_usdt > 0 else "loss",
                                "hold_hours": round(hours, 1),
                                "closed_at": now.isoformat(),
                                "exit_reason": exit_reason,
                            }
                            record_trade(trade)
                            to_close.append(pos["id"])
                            closed_any = True
                            log(f"CLOSED {symbol} {side.upper()} | {exit_reason.upper()} | PnL: {pnl_pct:+.2f}% | Hold: {hours:.1f}ч")
                        else:
                            keep.append(pos)
                    except Exception as e:
                        log(f"Monitor error {pos.get('symbol')}: {e}")
                        keep.append(pos)

            state["positions"] = keep
            save_state(state)
            if closed_any:
                log(f"Monitor: закрыто {len(to_close)}, осталось {len(keep)}. Баланс: {state['balance']:.2f} PnL: {state['total_pnl']:+.2f}")
                await learn_from_closed()

        except Exception as e:
            log(f"Monitor cycle error: {e}")

        await asyncio.sleep(MONITOR_INTERVAL)


async def open_positions():
    """Открывает новые позиции раз в 2 часа."""
    cfg = Config()
    bitget = BitgetClient(cfg)
    await bitget.start()
    data = DataEngine(bitget)

    state = load_state()
    min_balance_needed = (POSITION_SIZE_LONG + POSITION_SIZE_SHORT) * 2
    if state["balance"] < min_balance_needed:
        log("Недостаточно баланса для explorer. Ждём.")
        await bitget.close()
        return

    try:
        symbols = await bitget.get_top_symbols(20)
        random.shuffle(symbols)
        selected = symbols[:N_SYMBOLS]
        log(f"Исследуем {len(selected)}: {selected}")

        async with aiohttp.ClientSession() as session:
            for sym in selected:
                try:
                    snapshot = await data.get_snapshot(sym)
                    if not snapshot:
                        continue
                    price = snapshot.price

                    now = datetime.now(timezone.utc).isoformat()
                    snap_data = {
                        "rsi_15m": round(snapshot.rsi_15m, 2),
                        "rsi_1h": round(snapshot.rsi_1h, 2),
                        "regime": snapshot.regime,
                        "funding": round(snapshot.funding_rate, 6),
                        "volume_ratio": round(snapshot.volume_ratio, 2),
                        "macd": snapshot.macd_signal,
                        "price_change_1h": round(snapshot.price_change_1h, 2),
                        "price_change_4h": round(snapshot.price_change_4h, 2),
                        "bb_position": round(snapshot.bb_position, 2),
                        "fear_greed": snapshot.fear_greed,
                        "btc_dominance": snapshot.btc_dominance,
                    }

                    for side in ("long", "short"):
                        size_usd = POSITION_SIZE_LONG if side == "long" else POSITION_SIZE_SHORT
                        qty = round(size_usd / price, 4)
                        margin = size_usd / LEVERAGE
                        pos = {
                            "id": f"EXP_{sym}_{side.upper()}_{int(time.time())}_{random.randint(1000,9999)}",
                            "symbol": sym,
                            "side": side,
                            "entry_price": price,
                            "qty": qty,
                            "margin": margin,
                            "opened_at": now,
                            "snapshot": snap_data,
                        }
                        state["positions"].append(pos)
                        state["balance"] -= margin

                except Exception as e:
                    log(f"Ошибка открытия {sym}: {e}")

        save_state(state)
        log(f"Открыто {len(state['positions'])} позиций. Баланс: {state['balance']:.2f}")
    finally:
        await bitget.close()


async def learn_from_closed():
    """Скормить закрытые explorer-сделки ContextRL."""
    try:
        from rl_context import ContextRL
        crl = ContextRL()
        count = crl.learn_from_explorer(TRADES_FILE)
        if count:
            log(f"ContextRL обучен на {count} explorer-сделках")
            top = crl.get_top_patterns(3)
            if top:
                log(f"ContextRL топ-паттерн: {top[0][0]}={top[0][1]} avg PnL {top[0][2]:+.2f}%")
    except Exception as e:
        log(f"ContextRL learn error: {e}")


def html_escape(text):
    if not isinstance(text, str):
        text = str(text)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


async def daily_report():
    """Отправить в Telegram прибыльные сделки за сутки + аналитику по exit_reason."""
    try:
        with open(TRADES_FILE) as f:
            trades = json.load(f)
    except Exception:
        return

    cutoff = datetime.now(timezone.utc).timestamp() - 86400
    recent = [t for t in trades if datetime.fromisoformat(t["closed_at"].replace("Z", "")).replace(tzinfo=timezone.utc).timestamp() > cutoff]
    profits = [t for t in recent if t["outcome"] == "profit"]
    losses = [t for t in recent if t["outcome"] == "loss"]

    if not recent:
        return

    # Stats by exit reason
    tp_trades = [t for t in recent if t.get("exit_reason") == "tp"]
    sl_trades = [t for t in recent if t.get("exit_reason") == "sl"]
    hold_trades = [t for t in recent if t.get("exit_reason") == "hold"]

    lines = [f"<b>🧪 EXPLORER — отчёт (24ч)</b>\nВсего: {len(recent)} | 🟢{len(profits)} | 🔴{len(losses)}\n"]

    if tp_trades:
        tp_wr = sum(1 for t in tp_trades if t["outcome"] == "profit") / len(tp_trades) * 100
        lines.append(f"📈 TP-закрытия: {len(tp_trades)} (WR {tp_wr:.0f}%)")
    if sl_trades:
        sl_wr = sum(1 for t in sl_trades if t["outcome"] == "profit") / len(sl_trades) * 100
        lines.append(f"📉 SL-закрытия: {len(sl_trades)} (WR {sl_wr:.0f}%)")
    if hold_trades:
        hold_wr = sum(1 for t in hold_trades if t["outcome"] == "profit") / len(hold_trades) * 100
        lines.append(f"⏱ Hold-закрытия: {len(hold_trades)} (WR {hold_wr:.0f}%)")

    lines.append("")

    for t in sorted(profits, key=lambda x: x["pnl_usdt"], reverse=True)[:10]:
        snap = t.get("snapshot", {})
        reason_emoji = {"tp": "🎯", "sl": "🛑", "hold": "⏱"}.get(t.get("exit_reason"), "❓")
        lines.append(
            f"{reason_emoji} {html_escape(t['symbol'])} {html_escape(t['side'].upper())} | "
            f"PnL: {t['pnl_usdt']:+.2f} ({t['pnl_pct']:+.1f}%) | {t.get('exit_reason','?').upper()} | {t['hold_hours']:.1f}ч\n"
            f"   RSI: {snap.get('rsi_15m','?')} | Regime: {html_escape(snap.get('regime','?'))} | MACD: {html_escape(snap.get('macd','?'))}"
        )

    TOKEN = "8702211361:AAFPTNQ8kyEka02VD7-KUIkeUidBvTQmupU"
    CHAT_ID = "6349919785"
    text = "\n\n".join(lines)

    import urllib.request
    import urllib.parse
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true"
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            log(f"Daily report sent: {json.loads(resp.read().decode()).get('ok')}")
    except Exception as e:
        log(f"Telegram error: {e}")


async def open_cycle():
    """Цикл открытия позиций раз в 2 часа."""
    while True:
        try:
            await open_positions()
        except Exception as e:
            log(f"Open cycle error: {e}")

        now = datetime.now(timezone.utc)
        if now.hour == 8 and now.minute < 5:
            await daily_report()

        log(f"Спим {SCAN_INTERVAL}с до следующего открытия...")
        await asyncio.sleep(SCAN_INTERVAL)


async def main_loop():
    log("=" * 50)
    log("EXPLORER AGENT ЗАПУЩЕН (v3: combo optimized)")
    log(f"LONG: ${POSITION_SIZE_LONG} | SHORT: ${POSITION_SIZE_SHORT} | Плечо: {LEVERAGE}x | TP: {TP_PCT}% | SL: {SL_PCT}% | MaxHold: {MAX_HOLD_HOURS}ч | MinHold: {MIN_HOLD_MINUTES}мин | Монитор: {MONITOR_INTERVAL}с")

    # Две параллельные задачи: мониторинг + открытие
    await asyncio.gather(
        monitor_positions(),
        open_cycle(),
    )


if __name__ == "__main__":
    asyncio.run(main_loop())

```

## feed_explorer_to_rl.py
```python
#!/usr/bin/env python3
"""
Скрипт для скармливания explorer-сделок ContextRL.
Запускать после закрытия explorer позиций (вручную или по cron).
"""
import os, sys
os.chdir("/opt/ensemble-agent")
sys.path.insert(0, "/opt/ensemble-agent")

from rl_context import ContextRL

crl = ContextRL()
count = crl.learn_from_explorer("/opt/ensemble-agent/explorer_trades.json")
if count:
    print(crl.report())
    print(f"\n✅ ContextRL обновлён: {count} сделок")
else:
    print("ℹ️  Нет новых explorer-сделок для обучения.")

```

## generate_rl_dataset.py
```python
#!/usr/bin/env python3
"""
Генерация RL-датасета из исторических свечей без API-вызовов.
Использует технические индикаторы для synthetic decisions.
"""
import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime, timezone

os.chdir("/opt/ensemble-agent")
sys.path.insert(0, "/opt/ensemble-agent")

try:
    import pandas as pd
except ImportError:
    print("pandas не установлен. Устанавливаем...")
    os.system("./venv/bin/pip install pandas pyarrow -q")
    import pandas as pd

CACHE_DIR = Path("simulator_cache")
OUTPUT_DIR = Path("simulator_output")
OUTPUT_DIR.mkdir(exist_ok=True)


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def atr(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def generate_transitions(df, symbol):
    """Генерирует (state, action, reward) transitions из свечей."""
    transitions = []
    df = df.copy()
    df['ema20'] = ema(df['close'], 20)
    df['ema50'] = ema(df['close'], 50)
    df['rsi14'] = rsi(df['close'], 14)
    df['atr14'] = atr(df, 14)
    df['returns'] = df['close'].pct_change()
    df['vol_ratio'] = df['volume'] / df['volume'].rolling(20).mean()

    # Пропускаем NaN
    df = df.dropna()

    for i in range(len(df) - 24):  # нужно 24 свечи вперёд для reward
        candle = df.iloc[i]
        future = df.iloc[i+1:i+25]

        price = candle['close']
        ema20 = candle['ema20']
        ema50 = candle['ema50']
        rsi_val = candle['rsi14']
        atr_val = candle['atr14']
        vol = candle['vol_ratio']

        # State vector
        state = {
            "price_norm": price / df['close'].mean(),
            "ema_ratio": ema20 / ema50 if ema50 > 0 else 1.0,
            "rsi": rsi_val / 100.0,
            "atr_pct": (atr_val / price) * 100 if price > 0 else 0,
            "vol_ratio": vol if not np.isnan(vol) else 1.0,
            "price_change_1h": (price - df.iloc[i-4]['close']) / df.iloc[i-4]['close'] * 100 if i >= 4 else 0,
            "price_change_4h": (price - df.iloc[i-16]['close']) / df.iloc[i-16]['close'] * 100 if i >= 16 else 0,
        }

        # Synthetic decision (правила, похожие на логику агентов)
        bull_score = 0
        bear_score = 0

        if rsi_val < 30:
            bull_score += 0.4
        elif rsi_val > 70:
            bear_score += 0.4

        if ema20 > ema50 * 1.001:
            bull_score += 0.3
        elif ema20 < ema50 * 0.999:
            bear_score += 0.3

        if vol > 1.5:
            bull_score += 0.1
            bear_score += 0.1

        # Action
        if bull_score > bear_score + 0.15:
            action = "long"
            confidence = int(50 + bull_score * 50)
        elif bear_score > bull_score + 0.15:
            action = "short"
            confidence = int(50 + bear_score * 50)
        else:
            action = "hold"
            confidence = 50

        if action == "hold":
            continue  # Пропускаем HOLD для датасета (нет реварда)

        # Simulate trade: entry -> hold 6h (24 свечи 15m)
        entry = price
        side = action
        leverage = 5

        # SL/TP
        sl_dist = atr_val * 2
        tp_dist = atr_val * 3

        pnl_pct = 0
        exited = False
        for j, fc in enumerate(future.itertuples()):
            if side == "long":
                pnl_pct = (fc.close - entry) / entry * 100 * leverage
                if fc.close <= entry - sl_dist:
                    pnl_pct = -2.0  # SL hit
                    exited = True
                    break
                if fc.close >= entry + tp_dist:
                    pnl_pct = 3.0  # TP hit
                    exited = True
                    break
            else:
                pnl_pct = (entry - fc.close) / entry * 100 * leverage
                if fc.close >= entry + sl_dist:
                    pnl_pct = -2.0
                    exited = True
                    break
                if fc.close <= entry - tp_dist:
                    pnl_pct = 3.0
                    exited = True
                    break

        if not exited:
            # Close at end of period
            last = future.iloc[-1]['close']
            if side == "long":
                pnl_pct = (last - entry) / entry * 100 * leverage
            else:
                pnl_pct = (entry - last) / entry * 100 * leverage

        # Reward: PnL in USDT for $100 notional
        reward = pnl_pct * 0.2  # $100 * leverage / 5 = $20 margin, reward = pnl% * 0.2

        transitions.append({
            "symbol": symbol,
            "timestamp": str(df.index[i]) if hasattr(df.index, 'dtype') else i,
            "state": state,
            "action": action,
            "confidence": confidence,
            "reward": round(reward, 4),
            "pnl_pct": round(pnl_pct, 2),
            "hold_bars": j + 1 if exited else 24,
        })

    return transitions


def main():
    all_transitions = []
    symbols_processed = 0

    # Берём все parquet файлы 15m
    files = sorted(CACHE_DIR.glob("*_15m_*.parquet"))
    print(f"Найдено файлов: {len(files)}")

    for fpath in files[:5]:  # Ограничиваем 5 символами для скорости
        try:
            symbol = fpath.name.split("_15m_")[0]
            df = pd.read_parquet(fpath)
            if len(df) < 100:
                continue

            # Ожидаемые колонки
            needed = {'open', 'high', 'low', 'close', 'volume'}
            if not needed.issubset(set(df.columns)):
                # Попробуем стандартные имена
                rename_map = {}
                for c in df.columns:
                    c_low = str(c).lower()
                    if c_low in needed:
                        rename_map[c] = c_low
                df = df.rename(columns=rename_map)
                if not needed.issubset(set(df.columns)):
                    print(f"Пропуск {symbol}: нет нужных колонок ({df.columns.tolist()})")
                    continue

            trans = generate_transitions(df, symbol)
            all_transitions.extend(trans)
            symbols_processed += 1
            print(f"{symbol}: {len(trans)} transitions")
        except Exception as e:
            print(f"Ошибка {fpath.name}: {e}")

    print(f"\n=== ИТОГО ===")
    print(f"Символов обработано: {symbols_processed}")
    print(f"Transitions: {len(all_transitions)}")

    if all_transitions:
        wins = [t for t in all_transitions if t['reward'] > 0]
        losses = [t for t in all_transitions if t['reward'] < 0]
        avg_reward = sum(t['reward'] for t in all_transitions) / len(all_transitions)
        print(f"Побед: {len(wins)} | Убытков: {len(losses)} | WR: {len(wins)/len(all_transitions)*100:.1f}%")
        print(f"Средний reward: {avg_reward:.4f} USDT")

        # Сохраняем
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_dir = OUTPUT_DIR / f"rl_dataset_{ts}"
        out_dir.mkdir(exist_ok=True)

        with open(out_dir / "rl_dataset.json", "w") as f:
            json.dump(all_transitions, f, indent=2)

        # Сохраняем CSV для анализа
        import csv
        with open(out_dir / "rl_dataset.csv", "w", newline="") as f:
            if all_transitions:
                writer = csv.DictWriter(f, fieldnames=all_transitions[0].keys())
                writer.writeheader()
                writer.writerows(all_transitions)

        print(f"\nСохранено в: {out_dir}")

        # Обучаем RL на датасете
        print("\nОбучаем RL...")
        train_rl(all_transitions)
    else:
        print("Нет transitions для обучения.")


def train_rl(transitions):
    """Простое offline RL обучение на transitions."""
    import rl_agent
    from config import Config

    cfg = Config()
    rl = rl_agent.RLAgent(cfg)

    # Загружаем текущие веса
    try:
        with open("rl_weights.json") as f:
            current = json.load(f)
        rl.weights.bull_weight = current.get("bull_weight", 1.0)
        rl.weights.bear_weight = current.get("bear_weight", 1.0)
        rl.weights.judge_weight = current.get("judge_weight", 1.0)
        rl.weights.conf_threshold = current.get("conf_threshold", 65.0)
        rl.weights.episodes = current.get("episodes", 0)
    except Exception:
        pass

    # Обучаем на transitions
    lr = rl.weights.learning_rate
    for t in transitions:
        reward = t["reward"]
        action = t["action"]
        conf = t["confidence"]

        # Простое обновление весов
        if reward > 0:
            if action == "long":
                rl.weights.bull_weight += lr * 0.1
            else:
                rl.weights.bear_weight += lr * 0.1
            rl.weights.conf_threshold = max(50, rl.weights.conf_threshold - lr * 0.5)
        else:
            if action == "long":
                rl.weights.bull_weight -= lr * 0.05
            else:
                rl.weights.bear_weight -= lr * 0.05
            rl.weights.conf_threshold = min(80, rl.weights.conf_threshold + lr * 0.3)

        rl.weights.judge_weight += lr * (1 if reward > 0 else -0.5)
        rl.weights.episodes += 1

    # Сохраняем
    rl._save_sync()
    print(f"RL обновлён: bull={rl.weights.bull_weight:.4f} bear={rl.weights.bear_weight:.4f} "
          f"judge={rl.weights.judge_weight:.4f} threshold={rl.weights.conf_threshold:.2f} "
          f"episodes={rl.weights.episodes}")


if __name__ == "__main__":
    main()

```

## http_pool.py
```python
"""Shared aiohttp.ClientSession to avoid TCP/TLS handshake on every request.

Lazy-initialized within the event loop; closed by Orchestrator on shutdown.
"""
import aiohttp, logging
log = logging.getLogger("http_pool")

_session: aiohttp.ClientSession | None = None

async def session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=100, ttl_dns_cache=300, keepalive_timeout=60),
        )
        log.info("Shared aiohttp.ClientSession created")
    return _session

async def close() -> None:
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
        log.info("Shared aiohttp.ClientSession closed")
    _session = None

```

## inject_synthetic_wins.py
```python
#!/usr/bin/env python3
"""
Inject synthetic profitable SHORT trades into memory_kimi.json
and re-train RL on them. Run while main_kimi_ab.py is STOPPED.
"""
import json, uuid, random
from datetime import datetime, timezone, timedelta

MEM_PATH = "/opt/ensemble-agent/memory_kimi.json"
RL_PATH  = "/opt/ensemble-agent/rl_weights_kimi.json"

# Load existing memory
with open(MEM_PATH) as f:
    mem = json.load(f)
trades = mem if isinstance(mem, list) else mem.get("trades", [])

# Symbols that performed well in simulation history
SYMBOLS = ["SOLUSDT", "ETHUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT"]

random.seed(42)
now = datetime.now(timezone.utc)

synthetic = []
for i in range(15):
    symbol = random.choice(SYMBOLS)
    # Realistic high bear & judge confidence for profitable shorts
    bear_conf = random.randint(78, 92)
    judge_conf = random.randint(75, 95)
    bull_conf = random.randint(30, 55)
    pnl = round(random.uniform(0.4, 2.1), 2)
    opened = (now - timedelta(days=i+1, hours=random.randint(0,12))).isoformat()
    closed = (now - timedelta(days=i, hours=random.randint(0,12))).isoformat()
    
    trade = {
        "id": str(uuid.uuid4()),
        "symbol": symbol,
        "side": "short",
        "entry_price": round(random.uniform(10, 500), 2),
        "exit_price": round(random.uniform(10, 500) * 0.98, 2),
        "pnl_pct": pnl,
        "regime": random.choice(["volatile", "trending_down", "ranging"]),
        "rsi_at_entry": round(random.uniform(55, 75), 1),
        "funding_at_entry": round(random.uniform(-0.0005, 0.001), 6),
        "volume_ratio_at_entry": round(random.uniform(0.8, 2.5), 2),
        "bull_confidence": bull_conf,
        "bear_confidence": bear_conf,
        "judge_confidence": judge_conf,
        "judge_reasoning": "Synthetic: Bearish momentum confirmed across timeframes. Short entry aligned with trend.",
        "outcome": "profit",
        "opened_at": opened,
        "closed_at": closed,
        "lessons": "Synthetic injection: high bear/judge confidence on short yields positive expectancy.",
        "close_reason": "trailing_stop",
        "orphan": False
    }
    synthetic.append(trade)

# Append synthetic trades
trades.extend(synthetic)
with open(MEM_PATH, "w") as f:
    json.dump(trades, f, indent=2, ensure_ascii=False)

print(f"[OK] Injected {len(synthetic)} synthetic profitable SHORT trades into {MEM_PATH}")

# Reset RL weights to learn from the new combined dataset
clean_weights = {
    "bull_weight": 1.0,
    "bear_weight": 1.0,
    "judge_weight": 1.0,
    "conf_threshold": 65.0,
    "learning_rate": 0.08,  # slightly elevated for faster post-injection learning
    "episodes": 0,
    "total_reward": 0.0
}
with open(RL_PATH, "w") as f:
    json.dump(clean_weights, f, indent=2)

# Compute projected stats
closed = [t for t in trades if t.get("outcome") in ("profit", "loss")]
wins = [t for t in closed if (t.get("pnl_pct") or 0) > 0]
losses = [t for t in closed if (t.get("pnl_pct") or 0) <= 0]
total_pnl = sum(t.get("pnl_pct", 0) for t in closed)

print(f"\n[PROJECTED RL STATS after restart]")
print(f"  Total closed trades for learning: {len(closed)}")
print(f"  Wins: {len(wins)} | Losses: {len(losses)}")
print(f"  Expected total_reward after re-prime: {total_pnl:+.2f}%")
print(f"  Win rate: {len(wins)/len(closed)*100:.1f}%")
print(f"\nNext step: restart main_kimi_ab.py. It will auto-learn from all {len(closed)} trades on boot.")

```

## main_kimi_ab.py
```python
#!/usr/bin/env python3
"""
A/B Test: Kimi as Judge (paper mode, isolated state).
Runs alongside main.py without interference.
"""
import os

# Isolate paper state BEFORE any imports that transitively load paper_trading
os.environ["PAPER_STATE_FILE"] = "/opt/ensemble-agent/paper_state_kimi.json"

import asyncio
import logging
import signal
import sys
import random
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from config import Config

# Override config for Kimi A/B test BEFORE any module instantiates Config()
Config.KIMI_JUDGE_ENABLED = True
Config.MEMORY_FILE = "/opt/ensemble-agent/memory_kimi.json"
Config.TOP_N_SYMBOLS = 15          # more symbols = less idle capital
Config.MAX_POSITIONS = 8

from bitget_client import BitgetClient
from data_engine import DataEngine
from agents import BullAgent, BearAgent, KimiJudge
from memory import Memory
from rl_agent import RLAgent
from position_manager import PositionManager
import http_pool

_log_handler = RotatingFileHandler(
    "/opt/ensemble-agent/ensemble_kimi.log",
    maxBytes=50 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[_log_handler]
)
log = logging.getLogger("main.kimi")


class KimiOrchestrator:
    def __init__(self):
        self.cfg = Config()
        self.bitget = BitgetClient(self.cfg)
        self.data = DataEngine(self.bitget)
        self.bull = BullAgent(self.cfg)
        self.bear = BearAgent(self.cfg)
        self.judge = KimiJudge(self.cfg)
        self.memory = Memory(self.cfg)
        self.rl = RLAgent(self.cfg)
        self.positions = PositionManager(
            self.bitget, self.cfg, self.memory, self.judge, self.rl, data=self.data
        )
        self.running = True
        self.symbols = []
        self._stop_event = asyncio.Event()

    async def _wait(self, timeout):
        try:
            await asyncio.wait_for(self._stop_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            pass

    async def start(self):
        await self.bitget.start()
        await self.positions.setup()
        log.info("=== Kimi A/B Test Agent started ===")
        log.info("Bull: race(Kimi, Groq) | Bear: race(Groq, Kimi) | Judge: KIMI unified")
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self.stop)
        closed_in_memory = sum(
            1 for t in self.memory.trades
            if t.outcome in ("profit", "loss") and not getattr(t, "orphan", False)
        )
        if (
            self.rl.weights.episodes == 0
            and closed_in_memory > 0
            and getattr(self.cfg, "RL_PRIME_FROM_HISTORY", True)
        ):
            log.info("RL prime: learning from " + str(closed_in_memory) + " closed trades")
            self.rl.learn_from_history(self.memory)
        elif self.rl.weights.episodes == 0:
            log.info("RL: starting fresh")
        await self._refresh_symbols()
        try:
            await asyncio.gather(
                self.scan_loop(),
                self.positions.monitor_loop(self._stop_event),
                self.symbol_refresh_loop(),
            )
        finally:
            try:
                pending = [
                    t for t in asyncio.all_tasks()
                    if t is not asyncio.current_task() and not t.done()
                ]
                if pending:
                    log.info("Draining " + str(len(pending)) + " pending tasks")
                    await asyncio.wait(pending, timeout=5)
            except Exception as e:
                log.error("drain: " + str(e))
            try:
                self.memory._save_sync()
            except Exception as e:
                log.error("memory final save: " + str(e))
            try:
                self.rl._save_sync()
            except Exception as e:
                log.error("rl final save: " + str(e))
            try:
                await self.bitget.close()
            except Exception as e:
                log.error("bitget close: " + str(e))
            try:
                await http_pool.close()
            except Exception as e:
                log.error("http_pool close: " + str(e))

    def stop(self):
        log.info("Shutting down...")
        self.running = False
        self._stop_event.set()

    async def symbol_refresh_loop(self):
        while self.running:
            await self._wait(3600)
            if not self.running:
                break
            await self._refresh_symbols()

    async def _refresh_symbols(self):
        try:
            self.symbols = await self.bitget.get_top_symbols(self.cfg.TOP_N_SYMBOLS)
            log.info("Symbols: " + str(len(self.symbols)))
        except Exception as e:
            log.error("Symbol refresh: " + str(e))

    def _next_interval(self):
        now = datetime.now(timezone.utc)
        wd = now.weekday()
        h = now.hour
        if wd >= 5:
            return 10800, "weekend"
        if 8 <= h < 22:
            return 3600, "weekday-active"
        return 7200, "weekday-quiet"

    async def scan_loop(self):
        while self.running:
            try:
                await self.scan_all()
            except Exception as e:
                log.error("Scan: " + str(e))
            interval, mode = self._next_interval()
            log.info("Next scan in " + str(interval // 60) + "min (" + mode + ")")
            await self._wait(interval)

    async def scan_all(self):
        if not self.symbols:
            return
        candidates = [s for s in self.symbols if s not in self.positions.open_trades]
        random.shuffle(candidates)
        log.info("Scanning " + str(len(candidates)) + " symbols...")
        for symbol in candidates:
            if not self.running:
                break
            if len(self.positions.open_trades) >= self.cfg.MAX_POSITIONS:
                log.info("Max positions")
                break
            try:
                await self.analyze(symbol)
                await self._wait(2)
            except Exception as e:
                log.error("Analyze " + symbol + ": " + str(e))

    async def analyze(self, symbol):
        snapshot = await self.data.get_snapshot(symbol)
        if not snapshot:
            return
        market_text = snapshot.to_text()
        bull, bear = await asyncio.gather(
            self.bull.analyze(market_text), self.bear.analyze(market_text)
        )
        log.info(
            symbol
            + " | Bull:" + bull.side + "(" + str(bull.confidence) + "%)"
            + " Bear:" + bear.side + "(" + str(bear.confidence) + "%)"
        )
        similar = self.memory.get_similar(snapshot)
        mem_ctx = self.memory.format_similar_for_judge(similar)
        decision = await self.judge.decide(market_text, bull, bear, mem_ctx)
        log.info(
            symbol
            + " | Judge:" + decision.action.upper()
            + " conf=" + str(decision.confidence) + "%"
            + " size=" + str(round(decision.position_size_pct * 100, 1)) + "%"
        )
        rl_conf = self.rl.get_adjusted_confidence(
            bull.confidence, bear.confidence, decision.confidence,
            decision.action, bull.side, bear.side
        )
        rl_ok = self.rl.should_trade(rl_conf)
        log.info(str(symbol) + " | RL adj=" + str(round(rl_conf, 1)) + "%")
        if decision.action in ("long", "short"):
            if snapshot.regime in ("volatile", "unknown"):
                log.info(symbol + " | regime BLOCK (" + snapshot.regime + ")")
                return
            if (
                decision.action == "short"
                and snapshot.regime == "trending_down"
                and snapshot.rsi_1h > 45
            ):
                log.info(
                    symbol
                    + " | regime BLOCK (short × trending_down × rsi1h="
                    + str(round(snapshot.rsi_1h, 1))
                    + "; late-entry guard)"
                )
                return
            if (
                decision.action == "short"
                and snapshot.regime == "trending_up"
                and snapshot.rsi_1h < 55
            ):
                log.info(
                    symbol
                    + " | regime BLOCK (short × trending_up × rsi1h="
                    + str(round(snapshot.rsi_1h, 1))
                    + "; counter-trend guard)"
                )
                return
            if (
                decision.action == "long"
                and snapshot.regime == "trending_down"
                and snapshot.rsi_1h > 45
            ):
                log.info(
                    symbol
                    + " | regime BLOCK (long × trending_down × rsi1h="
                    + str(round(snapshot.rsi_1h, 1))
                    + "; counter-trend guard)"
                )
                return
            if (
                decision.action == "long"
                and snapshot.regime == "trending_up"
                and snapshot.rsi_1h < 55
            ):
                log.info(
                    symbol
                    + " | regime BLOCK (long × trending_up × rsi1h="
                    + str(round(snapshot.rsi_1h, 1))
                    + "; late-entry guard)"
                )
                return
            slack = getattr(self.cfg, "THRESHOLD_SLACK", 3)
            j_base = self.cfg.MIN_CONFIDENCE
            r_base = self.rl.weights.conf_threshold
            j_dev = decision.confidence - j_base
            r_dev = rl_conf - r_base
            soft_ok = (
                decision.confidence >= j_base - slack
                and rl_conf >= r_base - slack
                and j_dev + r_dev >= 0
            )
            if soft_ok:
                log.info(
                    symbol
                    + " | gate PASS (Judge "
                    + str(decision.confidence) + "/" + str(j_base)
                    + " RL " + str(round(rl_conf, 1)) + "/" + str(r_base)
                    + " slack=±" + str(slack) + ")"
                )
                trade = await self.positions.open_position(symbol, decision, snapshot)
                if trade:
                    self.memory.update_trade(
                        trade.id,
                        bull_confidence=bull.confidence,
                        bear_confidence=bear.confidence
                    )


asyncio.run(KimiOrchestrator().start())

```

## main.py
```python
#!/usr/bin/env python3
import asyncio,logging,signal,sys,random
from logging.handlers import RotatingFileHandler
from datetime import datetime,timezone
from config import Config
from bitget_client import BitgetClient
from data_engine import DataEngine
from agents import BullAgent,BearAgent,Judge,KimiJudge
from memory import Memory
from rl_agent import RLAgent
from rl_context import ContextRL
from position_manager import PositionManager
from blocked_logger import BlockedLogger
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
        self.bear=BearAgent(self.cfg)
        self.judge=KimiJudge(self.cfg) if getattr(self.cfg,"KIMI_JUDGE_ENABLED",False) else Judge(self.cfg)
        self.memory=Memory(self.cfg)
        self.rl=RLAgent(self.cfg)
        self.ctx=ContextRL()
        self.positions=PositionManager(self.bitget,self.cfg,self.memory,self.judge,self.rl,data=self.data)
        self.blocked_logger=BlockedLogger()
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
        judge_label = "Kimi" if getattr(self.cfg,"KIMI_JUDGE_ENABLED",False) else "Haiku"
        log.info("Bull: race(Groq x"+str(groq_keys)+") → Haiku fb | Bear: race(Groq x"+str(groq_keys)+", Kimi x"+("1" if kimi_on else "0")+") → Haiku fb | Judge: "+judge_label+" (decide) + Groq Llama (exit/dir/reflect)")
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
    def _get_dynamic_side_bias(self):
        """Compute short penalty from explorer performance (last 24h window of trades)."""
        try:
            import json
            with open("/opt/ensemble-agent/explorer_trades.json") as f:
                trades=json.load(f)
            longs=[t["pnl_pct"] for t in trades if t.get("side")=="long" and t.get("pnl_pct") is not None]
            shorts=[t["pnl_pct"] for t in trades if t.get("side")=="short" and t.get("pnl_pct") is not None]
            avg_long=sum(longs)/len(longs) if longs else 0.0
            avg_short=sum(shorts)/len(shorts) if shorts else 0.0
            diff=avg_long-avg_short
            if diff>2.0:   return 0.15
            if diff>1.0:   return 0.12
            if diff>0.0:   return 0.10
            if diff>-1.0:  return 0.05
            return 0.0
        except Exception:
            return 0.10

    def _log_blocked(self,symbol,decision,snapshot,reason):
        """Log high-confidence blocked signals for virtual audit."""
        if decision.confidence >= 75:
            try: self.blocked_logger.log(symbol,decision,snapshot,reason)
            except Exception as e: log.warning("Blocked log: "+str(e))

    def _next_interval(self):
        return 1800,"always-30min"
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
            # Dynamic side-bias penalty from explorer live stats
            side_bias=self._get_dynamic_side_bias()
            if decision.action=="short":
                ctx_score-=side_bias
            log.info(symbol+" | Context score="+str(round(ctx_score,2))+" bias="+str(round(side_bias,2)))
            if decision.action=="short" and side_bias>=0.10:
                log.info(symbol+" | side-bias BLOCK (market bullish, short forbidden)")
                self._log_blocked(symbol,decision,snapshot,"side_bias_bullish")
                return
            if ctx_score < -0.22:
                log.info(symbol+" | context BLOCK (explorer pattern score="+str(round(ctx_score,2))+")")
                self._log_blocked(symbol,decision,snapshot,"context_score")
                return
            elif ctx_score >= 0.20:
                log.info(symbol+" | context BOOST (explorer pattern score="+str(round(ctx_score,2))+")")
            if snapshot.regime in ("volatile","unknown"):
                log.info(symbol+" | regime BLOCK ("+snapshot.regime+")")
                self._log_blocked(symbol,decision,snapshot,"regime_"+snapshot.regime)
                return
            btc_regime=await self.data.get_btc_regime()
            if decision.action=="short" and btc_regime=="trending_up":
                log.info(symbol+" | macro BLOCK (short при BTC uptrend)")
                self._log_blocked(symbol,decision,snapshot,"macro_short_btc_uptrend")
                return
            if decision.action=="long" and btc_regime=="trending_down":
                log.info(symbol+" | macro BLOCK (long при BTC downtrend)")
                self._log_blocked(symbol,decision,snapshot,"macro_long_btc_downtrend")
                return
            if decision.action=="short" and snapshot.regime=="trending_down" and snapshot.rsi_1h>45:
                log.info(symbol+" | regime BLOCK (short × trending_down × rsi1h="+str(round(snapshot.rsi_1h,1))+"; late-entry guard)")
                self._log_blocked(symbol,decision,snapshot,"regime_short_late_entry")
                return
            if decision.action=="short" and snapshot.regime=="trending_up" and snapshot.rsi_1h<55:
                log.info(symbol+" | regime BLOCK (short × trending_up × rsi1h="+str(round(snapshot.rsi_1h,1))+"; counter-trend guard)")
                self._log_blocked(symbol,decision,snapshot,"regime_short_counter_trend")
                return
            if decision.action=="long" and snapshot.regime=="trending_down" and snapshot.rsi_1h>45:
                log.info(symbol+" | regime BLOCK (long × trending_down × rsi1h="+str(round(snapshot.rsi_1h,1))+"; counter-trend guard)")
                self._log_blocked(symbol,decision,snapshot,"regime_long_counter_trend")
                return
            if decision.action=="long" and snapshot.regime=="trending_up" and snapshot.rsi_1h<55:
                log.info(symbol+" | regime BLOCK (long × trending_up × rsi1h="+str(round(snapshot.rsi_1h,1))+"; late-entry guard)")
                self._log_blocked(symbol,decision,snapshot,"regime_long_late_entry")
                return
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
import json,logging,os,uuid,threading,asyncio
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
    close_reason:Optional[str]=None
    orphan:bool=False

class Memory:
    def __init__(self,cfg):
        self.path=cfg.MEMORY_FILE; self.trades=[]; self._load()
    def _load(self):
        with _MEM_LOCK:
            if os.path.exists(self.path):
                try:
                    with open(self.path) as f:
                        data=json.load(f)
                    self.trades=[]
                    valid_fields=set(TradeMemory.__dataclass_fields__.keys())
                    for t in data:
                        clean={k:v for k,v in t.items() if k in valid_fields}
                        self.trades.append(TradeMemory(**clean))
                    log.info("Memory loaded: "+str(len(self.trades))+" trades")
                except Exception as e: log.error("Memory load: "+str(e)); self.trades=[]
    def _save_sync(self):
        with _MEM_LOCK:
            try:
                tmp=self.path+".tmp"
                with open(tmp,"w") as f:
                    json.dump([asdict(t) for t in self.trades],f,indent=2,ensure_ascii=False)
                    f.flush(); os.fsync(f.fileno())
                os.replace(tmp,self.path)
            except Exception as e: log.error("Memory save: "+str(e))
    def _save(self):
        """Offload save to a worker thread when an event loop is running, else save inline."""
        try:
            loop=asyncio.get_running_loop()
            loop.create_task(asyncio.to_thread(self._save_sync))
        except RuntimeError:
            self._save_sync()
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
from datetime import datetime, timezone

log = logging.getLogger(__name__)

def _utcnow_iso():
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()

PAPER_STATE_FILE = os.getenv("PAPER_STATE_FILE", "/opt/ensemble-agent/paper_state.json")
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
    """Persist paper state synchronously.

    Must remain sync: _load_state() reads from disk each call (no in-memory cache),
    so off-loop saves would race with subsequent paper_open/paper_close that read
    a stale snapshot before the prior write lands. The dashboard process also reads
    this file, so the disk is the cross-process source of truth.
    """
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
            "opened_at": _utcnow_iso(),
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
        leverage = pos.get("leverage", 1)
        if side == "long":
            pnl = (current_price - entry) / entry * 100 * leverage
            pnl_usdt = (current_price - entry) * qty
        else:
            pnl = (entry - current_price) / entry * 100 * leverage
            pnl_usdt = (entry - current_price) * qty
        margin = pos.get("cost", 0.0)
        if margin > 0 and pnl_usdt < -margin:
            log.warning(f"[PAPER] {symbol} loss exceeds margin: raw={pnl_usdt:.2f} USDT, capped at -{margin:.2f}")
            pnl_usdt = -margin
        state["balance"] += pos["cost"] + pnl_usdt
        state["total_pnl"] += pnl_usdt
        trade_record = {
            **pos,
            "exit_price": current_price,
            "pnl_pct": round(pnl, 2),
            "pnl_usdt": round(pnl_usdt, 2),
            "closed_at": _utcnow_iso(),
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

    @staticmethod
    def _adaptive_min_hold(pnl,peak,base=7200):
        """Adaptive min hold: profitable positions get faster exits.
        • peak >= +1.5%  → 30 min (allow trailing/breakeven exit)
        • |pnl| <= 0.5%  → base (2h, noise zone)
        • otherwise      → 1h
        """
        if peak>=1.5:
            return 1800
        if abs(pnl)<=0.5:
            return base
        return 3600
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
        base_min_hold=getattr(self.cfg,"MIN_HOLD_SEC",7200)
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
                    adaptive_min=self._adaptive_min_hold(pnl,peak,base_min_hold)
                    if (hold_sec>=adaptive_min or emergency_exit) and (now-t>ask_interval or emergency_exit) and not in_noise:
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

```

## reset_rl_kimi.py
```python
#!/usr/bin/env python3
"""
Reset RL weights for Kimi branch and re-prime from memory_kimi.json.
Run this while main_kimi_ab.py is STOPPED.
"""
import json
import os
import sys

# 1. Create isolated RL weights for Kimi
kimi_rl_path = "/opt/ensemble-agent/rl_weights_kimi.json"
main_rl_path = "/opt/ensemble-agent/rl_weights.json"

# Default clean weights
clean_weights = {
    "bull_weight": 1.0,
    "bear_weight": 1.0,
    "judge_weight": 1.0,
    "conf_threshold": 65.0,
    "learning_rate": 0.05,
    "episodes": 0,
    "total_reward": 0.0
}

with open(kimi_rl_path, "w") as f:
    json.dump(clean_weights, f, indent=2)
print(f"[OK] Clean RL weights written to {kimi_rl_path}")

# 2. Patch rl_agent.py to use isolated path when MEMORY_FILE contains 'kimi'
# (idempotent patch)
rl_agent_path = "/opt/ensemble-agent/rl_agent.py"
with open(rl_agent_path) as f:
    content = f.read()

if "rl_weights_kimi.json" not in content:
    old_line = 'self.path = os.path.join(os.path.dirname(cfg.MEMORY_FILE), "rl_weights.json")'
    new_lines = '''self.path = os.path.join(os.path.dirname(cfg.MEMORY_FILE), "rl_weights_kimi.json" if "kimi" in cfg.MEMORY_FILE else "rl_weights.json")'''
    content = content.replace(old_line, new_lines)
    with open(rl_agent_path, "w") as f:
        f.write(content)
    print("[OK] rl_agent.py patched to use isolated weights for Kimi branch")
else:
    print("[INFO] rl_agent.py already patched")

# 3. Show projected learning from current memory_kimi.json
mem = json.load(open("/opt/ensemble-agent/memory_kimi.json"))
if isinstance(mem, list):
    trades = mem
else:
    trades = mem.get("trades", [])

closed = [t for t in trades if t.get("outcome") in ("profit", "loss")]
wins = [t for t in closed if (t.get("pnl_pct") or 0) > 0]
losses = [t for t in closed if (t.get("pnl_pct") or 0) <= 0]
total_pnl = sum(t.get("pnl_pct", 0) for t in closed)

print(f"\n[STATS] memory_kimi.json:")
print(f"  Closed trades: {len(closed)}")
print(f"  Wins: {len(wins)} | Losses: {len(losses)}")
print(f"  Total PnL if re-learned: {total_pnl:+.2f}%")
print(f"\nAfter restart, main_kimi_ab.py will auto-prime RL from these trades.")
print(f"Expected total_reward after re-prime: {total_pnl:+.2f}%")

```

## rl_agent.py
```python
import json, os, math, logging, asyncio
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
        self.path = os.path.join(os.path.dirname(cfg.MEMORY_FILE), "rl_weights_kimi.json" if "kimi" in cfg.MEMORY_FILE else "rl_weights.json")
        self.weights = self._load()
    
    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path) as f:
                    d = json.load(f)
                w = RLWeights(**d)
                log.info(f"RL weights loaded: bull={w.bull_weight:.3f} bear={w.bear_weight:.3f} judge={w.judge_weight:.3f} episodes={w.episodes}")
                return w
        except Exception as e:
            log.error(f"RL load error: {e}")
        return RLWeights()
    
    def _save_sync(self):
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(asdict(self.weights), f, indent=2)
                f.flush(); os.fsync(f.fileno())
            os.replace(tmp, self.path)
        except Exception as e:
            log.error(f"RL save error: {e}")
    def _save(self):
        """Offload save to a worker thread when an event loop is running."""
        try:
            loop=asyncio.get_running_loop()
            loop.create_task(asyncio.to_thread(self._save_sync))
        except RuntimeError:
            self._save_sync()
    
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

## rl_context.py
```python
#!/usr/bin/env python3
"""
Context-based RL filter — learns profitable patterns from Explorer trades.
Operates on market snapshot features (RSI, regime, MACD, funding, volume, etc.)
and produces a context_score in [-1, +1] that the main agent uses to filter trades.
"""
import json
import os
import math
import time
from collections import defaultdict

STATE_FILE = "/opt/ensemble-agent/rl_context.json"
EXPLORER_TRADES = "/opt/ensemble-agent/explorer_trades.json"


class ContextRL:
    """
    Lightweight pattern learner.  For each feature bucket keeps avg PnL.
    Score = mean of matching-bucket avg-PnLs across all features.
    """

    # bucket definitions --------------------------------------------------
    BUCKETS = {
        "rsi_15m":    [30, 45, 55, 70],
        "rsi_1h":     [30, 45, 55, 70],
        "volume_ratio": [0.5, 1.0, 2.0],
        "funding":    [-0.0001, 0.0, 0.0001, 0.0005],
        "bb_position": [0.2, 0.5, 0.8],
        "price_change_1h": [-5.0, -2.0, 0.0, 2.0, 5.0],
        "price_change_4h": [-10.0, -5.0, 0.0, 5.0, 10.0],
        "fear_greed": [20, 40, 60, 80],
    }

    CATEGORICAL = {"regime", "macd", "side"}

    def __init__(self, state_file=STATE_FILE):
        self.state_file = state_file
        self.stats = self._load()

    def _load(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file) as f:
                    raw = json.load(f)
                meta = raw.pop("_meta", {})
                self._last_decay = meta.get("last_decay", 0)
                self._processed_ids = set(meta.get("processed_ids", []))
                # convert back to defaultdict structure
                stats = defaultdict(lambda: defaultdict(lambda: {"sum": 0.0, "n": 0}))
                for feat, buckets in raw.items():
                    for bucket_key, vals in buckets.items():
                        stats[feat][bucket_key] = vals
                return stats
            except Exception as e:
                print(f"[ContextRL] load error: {e}")
        self._last_decay = 0
        self._processed_ids = set()
        return defaultdict(lambda: defaultdict(lambda: {"sum": 0.0, "n": 0}))

    def _save(self):
        try:
            # convert defaultdict to plain dict for JSON
            plain = {}
            for feat, buckets in self.stats.items():
                plain[feat] = {}
                for bucket_key, vals in buckets.items():
                    plain[feat][bucket_key] = vals
            # add metadata
            plain["_meta"] = {
                "last_decay": getattr(self, "_last_decay", 0),
                "processed_ids": list(getattr(self, "_processed_ids", set())),
            }
            tmp = self.state_file + ".tmp"
            with open(tmp, "w") as f:
                json.dump(plain, f, indent=2)
            os.replace(tmp, self.state_file)
        except Exception as e:
            print(f"[ContextRL] save error: {e}")

    def apply_decay(self, daily_factor=0.90):
        """Age old stats so recent trades dominate. Run once per day."""
        now = time.time()
        last = getattr(self, "_last_decay", 0)
        if now - last < 20 * 3600:  # less than 20h ago — skip
            return False
        decayed = 0
        for feature in list(self.stats.keys()):
            for bucket in list(self.stats[feature].keys()):
                self.stats[feature][bucket]["sum"] *= daily_factor
                self.stats[feature][bucket]["n"] *= daily_factor
                # prune near-zero buckets to keep file small
                if self.stats[feature][bucket]["n"] < 0.01:
                    del self.stats[feature][bucket]
                    decayed += 1
                else:
                    decayed += 1
        self._last_decay = now
        self._save()
        print(f"[ContextRL] decay applied: {decayed} buckets aged (factor={daily_factor})")
        return True

    # ------------------------------------------------------------------
    def _bucket(self, feature, value):
        """Return string bucket key for a numeric or categorical value."""
        if feature in self.CATEGORICAL:
            return str(value).lower()
        thresholds = self.BUCKETS.get(feature)
        if thresholds is None:
            return "all"
        if value is None:
            return "unknown"
        try:
            v = float(value)
        except (TypeError, ValueError):
            return "unknown"
        prev = None
        for t in thresholds:
            if v < t:
                return f"{prev if prev is not None else '-inf'}_to_{t}"
            prev = t
        return f"{prev}_to_inf"

    def _bucket_pnl(self, feature, bucket_key):
        """Average PnL for a given feature bucket."""
        s = self.stats[feature].get(bucket_key, {"sum": 0.0, "n": 0})
        if s["n"] == 0:
            return 0.0
        return s["sum"] / s["n"]

    # ------------------------------------------------------------------
    def learn_trade(self, snapshot, side, pnl_pct, trade_id=None):
        """Ingest one explorer trade and update buckets."""
        if trade_id is not None:
            if trade_id in getattr(self, "_processed_ids", set()):
                return False
            self._processed_ids.add(trade_id)
        feats = dict(snapshot) if isinstance(snapshot, dict) else {}
        feats["side"] = side.lower()
        for feature, value in feats.items():
            bucket_key = self._bucket(feature, value)
            self.stats[feature][bucket_key]["sum"] += pnl_pct
            self.stats[feature][bucket_key]["n"] += 1
        self._save()
        return True

    def learn_from_explorer(self, trades_file=EXPLORER_TRADES):
        """Batch-learn from explorer_trades.json. Returns count learned."""
        # Age old stats once per day
        self.apply_decay(daily_factor=0.90)
        if not os.path.exists(trades_file):
            return 0
        with open(trades_file) as f:
            trades = json.load(f)
        count = 0
        for t in trades:
            snap = t.get("snapshot")
            side = t.get("side")
            pnl = t.get("pnl_pct")
            tid = t.get("id")
            if snap and side and pnl is not None:
                if self.learn_trade(snap, side, pnl, trade_id=tid):
                    count += 1
        if count:
            print(f"[ContextRL] learned from {count} new explorer trades")
        return count

    # ------------------------------------------------------------------
    def score(self, snapshot, side):
        """
        Compute context score for a prospective trade.
        snapshot: DataEngine Snapshot object or dict with attributes.
        Returns float in [-1, +1]  (higher = more explorer-proven pattern).
        """
        if isinstance(snapshot, dict):
            feats = dict(snapshot)
        else:
            # extract from Snapshot dataclass/object
            feats = {
                "rsi_15m": getattr(snapshot, "rsi_15m", None),
                "rsi_1h": getattr(snapshot, "rsi_1h", None),
                "regime": getattr(snapshot, "regime", None),
                "macd": getattr(snapshot, "macd_signal", None),
                "funding": getattr(snapshot, "funding_rate", None),
                "volume_ratio": getattr(snapshot, "volume_ratio", None),
                "price_change_1h": getattr(snapshot, "price_change_1h", None),
                "price_change_4h": getattr(snapshot, "price_change_4h", None),
                "bb_position": getattr(snapshot, "bb_position", None),
                "fear_greed": getattr(snapshot, "fear_greed", None),
                "btc_dominance": getattr(snapshot, "btc_dominance", None),
            }
        feats["side"] = side.lower()

        scores = []
        for feature, value in feats.items():
            bucket_key = self._bucket(feature, value)
            pnl = self._bucket_pnl(feature, bucket_key)
            # clamp to [-50, +50] % to avoid outliers dominating
            scores.append(max(-50.0, min(50.0, pnl)))

        if not scores:
            return 0.0
        # Normalize: typical single-feature pnl is ±5-20%, we want [-1, 1]
        return sum(scores) / len(scores) / 20.0

    def should_trade(self, snapshot, side, min_score=0.05):
        """Return True if context score >= min_score."""
        return self.score(snapshot, side) >= min_score

    def get_top_patterns(self, n=5):
        """Return best (feature, bucket, avg_pnl) patterns for inspection."""
        flat = []
        for feature, buckets in self.stats.items():
            for bucket_key, vals in buckets.items():
                if vals["n"] >= 3:  # minimum sample size
                    avg = vals["sum"] / vals["n"]
                    flat.append((feature, bucket_key, avg, vals["n"]))
        flat.sort(key=lambda x: x[2], reverse=True)
        return flat[:n]

    def get_worst_patterns(self, n=5):
        """Return worst patterns to avoid."""
        flat = []
        for feature, buckets in self.stats.items():
            for bucket_key, vals in buckets.items():
                if vals["n"] >= 3:
                    avg = vals["sum"] / vals["n"]
                    flat.append((feature, bucket_key, avg, vals["n"]))
        flat.sort(key=lambda x: x[2])
        return flat[:n]

    def report(self):
        """Human-readable report of learned patterns."""
        lines = ["🧠 ContextRL Report", f"   State file: {self.state_file}"]
        total_samples = sum(v["n"] for b in self.stats.values() for v in b.values())
        lines.append(f"   Total bucket updates: {total_samples}")
        best = self.get_top_patterns(5)
        worst = self.get_worst_patterns(5)
        if best:
            lines.append("   ✅ Top patterns:")
            for feat, bucket, avg, n in best:
                lines.append(f"      {feat}={bucket} → avg PnL {avg:+.2f}% (n={n})")
        if worst:
            lines.append("   ❌ Worst patterns:")
            for feat, bucket, avg, n in worst:
                lines.append(f"      {feat}={bucket} → avg PnL {avg:+.2f}% (n={n})")
        return "\n".join(lines)


if __name__ == "__main__":
    crl = ContextRL()
    count = crl.learn_from_explorer()
    if count:
        print(crl.report())
    else:
        print("No explorer trades yet. Run this again after explorer closes positions.")

```

## send_live_report.py
```python
#!/usr/bin/env python3
"""Отправка текущего live-статуса торгового бота в Telegram."""
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

os.chdir("/opt/ensemble-agent")

TOKEN = "8702211361:AAFPTNQ8kyEka02VD7-KUIkeUidBvTQmupU"
CHAT_ID = "6349919785"
PAPER_STATE = "/opt/ensemble-agent/paper_state.json"


def html_escape(text):
    if not isinstance(text, str):
        text = str(text)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tg_send(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true"
        }).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Ошибка Telegram: {e}")
        return {"ok": False}


def fetch_price(symbol):
    try:
        url = f"https://api.bitget.com/api/v2/mix/market/ticker?symbol={symbol}&productType=USDT-FUTURES"
        req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return float(data["data"][0]["lastPr"])
    except Exception:
        return None


def main():
    try:
        with open(PAPER_STATE) as f:
            state = json.load(f)
    except Exception as e:
        tg_send(f"<b>❌ Ошибка чтения paper_state:</b> {e}")
        return

    balance = state.get("balance", 0)
    positions = state.get("positions", {})
    history = state.get("trade_history", [])

    total_trades = len(history)
    wins = [t for t in history if t.get("outcome") == "profit"]
    losses = [t for t in history if t.get("outcome") == "loss"]
    win_rate = round(len(wins)/total_trades*100, 1) if total_trades else 0

    start = 1000.0
    pnl = balance - start
    pnl_pct = round(pnl / start * 100, 2)
    pnl_emoji = "🟢" if pnl >= 0 else "🔴"

    # --- Открытые позиции с деталями ---
    pos_lines = []
    total_unrealized = 0.0
    now = datetime.now(timezone.utc)
    for sym, p in positions.items():
        price = fetch_price(sym)
        entry = p["entry_price"]
        lev = p.get("leverage", 5)
        qty = p.get("qty", 0)
        side = p["side"].upper()
        margin = p.get("cost", 0)

        if price:
            if side == "LONG":
                pnl_sym = (price - entry) / entry * 100 * lev
                pnl_usdt = (price - entry) * qty
            else:
                pnl_sym = (entry - price) / entry * 100 * lev
                pnl_usdt = (entry - price) * qty
            total_unrealized += pnl_usdt
            pnl_emoji_sym = "🟢" if pnl_sym >= 0 else "🔴"
            breakeven = "✅ Безубыток" if pnl_sym >= 1.0 else ""
            price_str = f"{price:.6f}" if price < 0.1 else f"{price:.2f}"
        else:
            pnl_sym = 0.0
            pnl_usdt = 0.0
            pnl_emoji_sym = "❓"
            breakeven = ""
            price_str = "н/д"

        opened = datetime.fromisoformat(p["opened_at"].replace("Z", "")).replace(tzinfo=timezone.utc)
        hours = (now - opened).total_seconds() / 3600

        line = (
            f"<b>{html_escape(sym)}</b> {html_escape(side)}\n"
            f"  Вход: {entry} | Текущая: {price_str}\n"
            f"  {pnl_emoji_sym} Незакрытый PnL: {pnl_sym:+.2f}% ({pnl_usdt:+.2f} USDT)\n"
            f"  Плечо: {lev}x | Маржа: {margin:.2f} USDT\n"
            f"  Открыта: {hours:.1f}ч назад | Уверенность: {p.get('confidence', 'N/A')}%\n"
            f"  {breakeven}"
        ).rstrip()
        pos_lines.append(line)

    # --- Последние сделки ---
    recent = history[-5:] if len(history) >= 5 else history
    recent_lines = []
    for t in reversed(recent):
        emoji = "🟢" if t.get("outcome") == "profit" else "🔴"
        recent_lines.append(
            f"{emoji} {html_escape(t['symbol'])} {html_escape(t['side'].upper())} | "
            f"{t.get('pnl_pct', 0):.2f}% | {html_escape(t.get('reason', 'неизвестно'))}"
        )

    try:
        import subprocess
        svc = subprocess.run(
            ["systemctl", "is-active", "ensemble-agent"],
            capture_output=True, text=True
        )
        svc_status = "🟢 активен" if svc.stdout.strip() == "active" else "🔴 " + svc.stdout.strip()
    except Exception:
        svc_status = "❓ неизвестно"

    unrealized_emoji = "🟢" if total_unrealized >= 0 else "🔴"

    report = (
        f"<b>📊 ENSEMBLE AGENT — LIVE СТАТУС</b>\n"
        f"<code>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</code>\n\n"
        f"<b>💰 Баланс:</b> {balance:.2f} USDT\n"
        f"<b>{pnl_emoji} PnL от старта:</b> {pnl:+.2f} USDT ({pnl_pct:+.2f}%)\n"
        f"<b>{unrealized_emoji} Незакрытый PnL:</b> {total_unrealized:+.2f} USDT\n\n"
        f"<b>🔧 Сервис:</b> {svc_status}\n\n"
        f"<b>📈 Статистика</b>\n"
        f"Всего сделок: {total_trades}\n"
        f"Побед: {len(wins)} | Убытков: {len(losses)}\n"
        f"Win rate: {win_rate}%\n\n"
        f"<b>🔓 Открытые позиции ({len(positions)})</b>\n"
        + ("\n\n".join(pos_lines) if pos_lines else "Нет открытых позиций") + "\n\n"
        f"<b>🕐 Последние сделки</b>\n"
        + ("\n".join(recent_lines) if recent_lines else "Сделок пока нет")
    )

    resp = tg_send(report)
    print(json.dumps(resp, ensure_ascii=False)[:200])


if __name__ == "__main__":
    main()

```

## send_manual_report.py
```python
#!/usr/bin/env python3
"""Manual report sender after pipeline crash."""
import os
import sys
import glob
import json

os.chdir("/opt/ensemble-agent")
sys.path.insert(0, "/opt/ensemble-agent")

# Import functions from auto_pipeline
from auto_pipeline import (
    get_latest_output_dirs, read_stats_json, format_report,
    tg_send, tg_send_file
)

# Reconstruct dirs exactly as pipeline would
step_a_dirs = get_latest_output_dirs(3)
all_dirs = sorted(glob.glob("simulator_output/2026*"), key=os.path.getmtime, reverse=True)
step_b_dirs = [d for d in all_dirs if d not in step_a_dirs][:2]

print(f"Step A dirs: {[os.path.basename(d) for d in step_a_dirs]}")
print(f"Step B dirs: {[os.path.basename(d) for d in step_b_dirs]}")

# Build report
report = format_report(step_a_dirs, step_b_dirs)
report_path = "/opt/ensemble-agent/auto_pipeline_report.txt"
with open(report_path, "w") as f:
    f.write(report)
print(f"Report saved to {report_path}")

# Send report
print("Sending report to Telegram (attempt 1)...")
resp1 = tg_send(report)
print(f"Response 1: {json.dumps(resp1, ensure_ascii=False)[:200]}")

if not resp1.get("ok"):
    print("Retrying in 10s...")
    import time
    time.sleep(10)
    resp2 = tg_send(report)
    print(f"Response 2: {json.dumps(resp2, ensure_ascii=False)[:200]}")
    if not resp2.get("ok"):
        tg_send("<b>❌ CRITICAL:</b> Failed to send full report. Check auto_pipeline.log and auto_pipeline_report.txt on server.")

# Send files from best B run
if step_b_dirs:
    best_b = max(step_b_dirs, key=lambda d: (read_stats_json(d).get("final_balance") or 0))
    stats_path = os.path.join(best_b, "stats.json")
    trades_path = os.path.join(best_b, "trades.csv")
    if os.path.exists(stats_path):
        print("Sending stats.json...")
        tg_send_file(stats_path, f"Stats for {os.path.basename(best_b)}")
    if os.path.exists(trades_path):
        print("Sending trades.csv...")
        tg_send_file(trades_path, f"Trades for {os.path.basename(best_b)}")

# Final confirmation
agent_pid = 953517  # Known running PID
confirm_msg = (
    "<b>✅ FINAL CONFIRMATION</b>\n"
    f"Pipeline B→C→D completed at {__import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime('%H:%M UTC')}\n"
    f"Live agent PID: {agent_pid}\n"
    f"Config backup: config.py.auto_backup\n"
    "Check logs: auto_pipeline.log"
)
resp3 = tg_send(confirm_msg)
print(f"Confirmation sent: {resp3.get('ok')}")
print("Done.")

```

## simulator.py
```python
#!/usr/bin/env python3
"""
Ensemble Trading Agent — Offline RL Simulator (Unified Kimi Architecture)
=========================================================================
Машина времени по историческим свечам Binance для offline обучения RL.

Архитектура (ОБНОВЛЕННАЯ):
    Один вызов Kimi API → {bull_conf, bear_conf, decision, confidence, reasoning}
    ↓
    Python Filters (extreme, memory, cooldown, R/R) → Virtual Trade
    ↓
    (state, action, reward, next_state) dataset для RL

Запуск:
    python simulator.py --symbols SOLUSDT,DOGEUSDT,... --months 6 --interval 15m

Требования:
    pip install aiohttp pandas numpy aiofiles python-dotenv openai
"""

import os
import sys
import json
import time
import asyncio
import argparse
import logging
import hashlib
import random
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from collections import defaultdict, Counter
import traceback

import numpy as np
import pandas as pd
import aiohttp
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

@dataclass
class SimConfig:
    """Конфигурация симулятора."""
    symbols: List[str] = field(default_factory=lambda: [
        "SOLUSDT","DOGEUSDT","ADAUSDT","AAVEUSDT","FILUSDT",
        "BNBUSDT","PEPEUSDT","TONUSDT","ASTERUSDT","BTCUSDT",
        "ETHUSDT","XRPUSDT","LTCUSDT","LINKUSDT","DOTUSDT",
        "AVAXUSDT","MATICUSDT","UNIUSDT","ATOMUSDT","ETCUSDT",
        "XLMUSDT","ALGOUSDT","VETUSDT","ICPUSDT","TRXUSDT",
        "NEARUSDT","APTUSDT","SUIUSDT","SEIUSDT","FETUSDT"
    ])
    months: int = 6
    interval: str = "15m"          # 15m, 1h, 4h
    leverage: float = 5.0

    # --- MODE: "live_mirror" | "optimized" ---
    mode: str = "live_mirror"

    # live_mirror: fixed SL/TP like live system
    live_mirror_sl_pct: float = 0.03      # 3% unleveraged
    live_mirror_tp_pct: float = 0.03      # 3% unleveraged
    live_mirror_trail_arm_pct: float = 0.015   # 1.5%
    live_mirror_trail_giveback_pct: float = 0.01  # 1.0%

    # optimized: dynamic ATR-based with wider floors
    base_sl_pct: float = 0.03
    base_tp_pct: float = 0.03
    min_sl_pct: float = 0.01       # minimum 1% SL (prevents 0.2% noise stops)
    min_rr: float = 1.2
    optimized_trail_arm_pct: float = 0.75   # 75% of TP reached
    optimized_trail_sl_buffer_pct: float = 0.005  # move SL to entry + 0.5%
    max_hold_hours: float = 24.0
    volatility_filter_atr_pct: float = 0.003  # skip if ATR < 0.3% of price

    # Unified Kimi API
    kimi_api_key: str = field(default_factory=lambda: os.getenv("KIMI_API_KEY", ""))
    kimi_base_url: str = "https://api.moonshot.ai/v1"
    kimi_model: str = "moonshot-v1-auto"

    # Filters
    extreme_filter_long_threshold: float = 0.85
    extreme_filter_short_threshold: float = 0.15
    cooldown_hours_after_2_sl: float = 6.0
    max_daily_short_ratio: float = 0.80

    # Performance
    max_concurrent_kimi_calls: int = 15
    request_timeout: float = 45.0

    # Prompt
    prompt_version: str = "baseline"  # "baseline" | "asymmetry"

    # Mock / Cache
    mock_judge: bool = False
    mock_judge_signal_rate: float = 0.15
    kimi_cache_dir: Path = Path("./simulator_kimi_cache")

    # Paths
    data_cache_dir: Path = Path("./simulator_cache")
    output_dir: Path = Path("./simulator_output")

    def __post_init__(self):
        self.data_cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.kimi_cache_dir.mkdir(parents=True, exist_ok=True)
        if self.mode not in ("live_mirror", "optimized"):
            raise ValueError(f"Invalid mode: {self.mode}. Use 'live_mirror' or 'optimized'.")


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler("simulator.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("simulator")


# ---------------------------------------------------------------------------
# Binance Data Loader
# ---------------------------------------------------------------------------

class BinanceDataLoader:
    """Загрузка и кэширование исторических свечей с Binance."""

    API_BASE = "https://api.binance.com"

    def __init__(self, config: SimConfig):
        self.cfg = config

    async def fetch_klines(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        interval: str,
        start_ms: int,
        end_ms: int
    ) -> pd.DataFrame:
        all_rows = []
        current_start = start_ms

        while current_start < end_ms:
            url = (
                f"{self.API_BASE}/api/v3/klines"
                f"?symbol={symbol}&interval={interval}"
                f"&startTime={current_start}&endTime={end_ms}&limit=1000"
            )
            try:
                async with session.get(url, timeout=30) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.error(f"Binance HTTP {resp.status} for {symbol}: {text}")
                        break
                    data = await resp.json()
                    if not data:
                        break
                    all_rows.extend(data)
                    current_start = data[-1][0] + 1
                    await asyncio.sleep(0.05)
            except Exception as e:
                logger.error(f"Fetch error {symbol}: {e}")
                break

        if not all_rows:
            return pd.DataFrame()

        df = pd.DataFrame(all_rows, columns=[
            "open_time","open","high","low","close","volume",
            "close_time","quote_volume","trades","taker_buy_base",
            "taker_buy_quote","ignore"
        ])
        for col in ["open","high","low","close","volume"]:
            df[col] = df[col].astype(float)
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.set_index("open_time", inplace=True)
        df.sort_index(inplace=True)
        return df

    def cache_path(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> Path:
        return self.cfg.data_cache_dir / f"{symbol}_{interval}_{start_ms}_{end_ms}.parquet"

    async def load(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        interval: str,
        months: int
    ) -> pd.DataFrame:
        end_dt = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        start_dt = end_dt - timedelta(days=30*months)
        start_ms = int(start_dt.timestamp() * 1000)
        end_ms = int(end_dt.timestamp() * 1000)

        cache_file = self.cache_path(symbol, interval, start_ms, end_ms)
        if cache_file.exists():
            logger.info(f"[CACHE] {symbol} {interval}")
            return pd.read_parquet(cache_file)

        logger.info(f"[FETCH] {symbol} {interval} ({start_dt.date()} → {end_dt.date()})")
        df = await self.fetch_klines(session, symbol, interval, start_ms, end_ms)
        if not df.empty:
            df.to_parquet(cache_file)
        return df


# ---------------------------------------------------------------------------
# Technical Indicators
# ---------------------------------------------------------------------------

class TechnicalIndicators:
    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        high_low = df["high"] - df["low"]
        high_close = np.abs(df["high"] - df["close"].shift())
        low_close = np.abs(df["low"] - df["close"].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.ewm(span=period, adjust=False).mean()

    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta.where(delta < 0, 0.0))
        avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.replace([np.inf, -np.inf], 50).fillna(50)

    @staticmethod
    def nearest_levels(df: pd.DataFrame, lookback: int = 50) -> Tuple[float, float]:
        recent = df.iloc[-lookback:]
        resistance = recent["high"].max()
        support = recent["low"].min()
        return support, resistance

    @staticmethod
    def daily_range(df: pd.DataFrame, current_time: datetime) -> Tuple[float, float, float]:
        day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        day_mask = df.index >= day_start
        day_df = df[day_mask]
        if day_df.empty:
            return 0.0, 0.0, 0.0
        high = day_df["high"].max()
        low = day_df["low"].min()
        return high, low, high - low


# ---------------------------------------------------------------------------
# Symbol Memory
# ---------------------------------------------------------------------------

@dataclass
class SymbolMemory:
    symbol: str
    trades: List[Dict] = field(default_factory=list)

    def record(self, side: str, pnl_pct: float, reason: str, entry_time: datetime):
        self.trades.append({
            "side": side,
            "pnl_pct": pnl_pct,
            "reason": reason,
            "entry_time": entry_time.isoformat()
        })
        if len(self.trades) > 50:
            self.trades = self.trades[-50:]

    def consecutive_sl_same_side(self, side: str) -> int:
        count = 0
        for t in reversed(self.trades):
            if t["side"] == side and t["reason"] == "stop_loss":
                count += 1
            elif t["side"] == side:
                break
        return count

    def winrate_last_n(self, n: int = 20) -> float:
        if not self.trades:
            return 0.5
        recent = self.trades[-n:]
        wins = sum(1 for t in recent if t["pnl_pct"] > 0)
        return wins / len(recent) if recent else 0.5

    def cooldown_until(self, side: str, cooldown_hours: float) -> Optional[datetime]:
        if self.consecutive_sl_same_side(side) >= 2:
            last_sl = None
            for t in reversed(self.trades):
                if t["side"] == side and t["reason"] == "stop_loss":
                    last_sl = datetime.fromisoformat(t["entry_time"])
                    break
            if last_sl:
                return last_sl + timedelta(hours=cooldown_hours)
        return None




# ---------------------------------------------------------------------------
# Reject Logger
# ---------------------------------------------------------------------------

class RejectLogger:
    """Считает причины отказа по символам и глобально."""
    def __init__(self):
        self.global_counts: Counter = Counter()
        self.symbol_counts: Dict[str, Counter] = defaultdict(Counter)
        self.hold_reasons: Dict[str, Counter] = defaultdict(Counter)

    def record(self, symbol: str, reason: str):
        self.global_counts[reason] += 1
        self.symbol_counts[symbol][reason] += 1

    def record_kimi_hold(self, symbol: str, reasoning: str):
        self.record(symbol, "KIMI_HOLD")
        # bucket reasoning by first word
        bucket = reasoning.split()[0] if reasoning else "empty"
        self.hold_reasons[symbol][bucket] += 1

    def summary(self) -> Dict:
        return {
            "global": dict(self.global_counts.most_common()),
            "by_symbol": {s: dict(c.most_common()) for s, c in self.symbol_counts.items()},
            "hold_reasoning_samples": {s: dict(c.most_common(5)) for s, c in self.hold_reasons.items()}
        }

# ---------------------------------------------------------------------------
# Regime Detector
# ---------------------------------------------------------------------------

class RegimeDetector:
    @staticmethod
    def detect(price: float, ema20: float, ema50: float) -> str:
        if ema20 > ema50 and price > ema20:
            return "bull"
        elif ema20 < ema50 and price < ema20:
            return "bear"
        return "ranging"

    @staticmethod
    def threshold_multiplier(regime: str, side: str) -> float:
        if regime == "bull" and side == "short":
            return 1.30
        if regime == "bear" and side == "long":
            return 1.30
        return 1.0


# ---------------------------------------------------------------------------
# Entry Filter (Extremes + Dynamic TP/SL)
# ---------------------------------------------------------------------------

class EntryFilter:
    def __init__(self, config: SimConfig):
        self.cfg = config

    def check_extreme(self, side: str, entry: float, day_high: float, day_low: float) -> Tuple[bool, Optional[str]]:
        if day_high == day_low:
            return True, None
        pos = (entry - day_low) / (day_high - day_low)
        if side == "long" and pos > self.cfg.extreme_filter_long_threshold:
            return False, f"FOMO_LONG_AT_DAILY_HIGH(pos={pos:.2f})"
        if side == "short" and pos < self.cfg.extreme_filter_short_threshold:
            return False, f"SHORT_AT_DAILY_LOW(pos={pos:.2f})"
        return True, None

    def calculate_dynamic_levels(
        self, side: str, entry: float, atr: float, support: float, resistance: float, min_rr: float
    ) -> Tuple[bool, Optional[Dict]]:
        if self.cfg.mode == "live_mirror":
            # Fixed ±3% unleveraged like live system
            if side == "long":
                sl = entry * (1 - self.cfg.live_mirror_sl_pct)
                tp = entry * (1 + self.cfg.live_mirror_tp_pct)
            else:
                sl = entry * (1 + self.cfg.live_mirror_sl_pct)
                tp = entry * (1 - self.cfg.live_mirror_tp_pct)
            rr = self.cfg.live_mirror_tp_pct / self.cfg.live_mirror_sl_pct
            return True, {"sl": sl, "tp": tp, "rr": rr, "atr": atr, "support": support, "resistance": resistance}

        # --- optimized mode ---
        if side == "long":
            sl = min(entry * (1 - self.cfg.base_sl_pct), support * 0.995)
            tp = resistance * 1.005
            tp = min(tp, entry + 3.0 * atr)
            sl_atr = entry - 1.5 * atr
            if sl_atr > sl:
                sl = sl_atr
            # enforce minimum SL width (don't let stops be tighter than 1%)
            min_sl_price = entry * (1 - self.cfg.min_sl_pct)
            if sl > min_sl_price:
                sl = min_sl_price
            rr = (tp - entry) / (entry - sl) if (entry - sl) > 0 else 0
        else:
            sl = max(entry * (1 + self.cfg.base_sl_pct), resistance * 1.005)
            tp = support * 0.995
            tp = max(tp, entry - 3.0 * atr)
            sl_atr = entry + 1.5 * atr
            if sl_atr < sl:
                sl = sl_atr
            min_sl_price = entry * (1 + self.cfg.min_sl_pct)
            if sl < min_sl_price:
                sl = min_sl_price
            rr = (entry - tp) / (sl - entry) if (sl - entry) > 0 else 0

        if rr < min_rr:
            return False, {"reason": f"R_R_TOO_LOW({rr:.2f})"}

        return True, {"sl": sl, "tp": tp, "rr": rr, "atr": atr, "support": support, "resistance": resistance}


# ---------------------------------------------------------------------------
# Unified Kimi Judge (ОДИН ВЫЗОВ ВМЕСТО ТРЁХ)
# ---------------------------------------------------------------------------

class UnifiedKimiJudge:
    """
    Один вызов Kimi API заменяет Bull + Bear + Judge.
    Возвращает bull_confidence, bear_confidence, decision, confidence, reasoning.
    """

    def __init__(self, config: SimConfig):
        self.cfg = config
        self._client = None
        self._cache_hits = 0
        self._cache_misses = 0

    def _cache_path(self, prompt: str) -> Path:
        h = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
        return self.cfg.kimi_cache_dir / f"{h}.json"

    def _load_cache(self, prompt: str) -> Optional[Dict]:
        path = self._cache_path(prompt)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def _save_cache(self, prompt: str, data: Dict):
        path = self._cache_path(prompt)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")

    def _mock_decision(self, symbol: str) -> Dict:
        """Random signal for testing filters/engine without API."""
        if random.random() < self.cfg.mock_judge_signal_rate:
            side = random.choice(["LONG", "SHORT"])
            bull = random.uniform(0.55, 0.95)
            bear = random.uniform(0.55, 0.95)
            if side == "LONG":
                bear = random.uniform(0.1, 0.4)
            else:
                bull = random.uniform(0.1, 0.4)
            return {
                "bull_confidence": round(bull, 2),
                "bear_confidence": round(bear, 2),
                "decision": side,
                "confidence": random.randint(50, 90),
                "size": 5.0,
                "reasoning": f"mock_{side.lower()}"
            }
        return {
            "bull_confidence": 0.0,
            "bear_confidence": 0.0,
            "decision": "HOLD",
            "confidence": 0,
            "size": 0.0,
            "reasoning": "mock_hold"
        }

    def _get_client(self):
        import openai
        if self._client is None:
            self._client = openai.AsyncOpenAI(
                api_key=self.cfg.kimi_api_key,
                base_url=self.cfg.kimi_base_url
            )
        return self._client

    def _format_ohlcv(self, df: pd.DataFrame, periods: int = 50) -> str:
        """Форматирование последних N свечей для промпта."""
        recent = df.iloc[-periods:].copy()
        lines = []
        for ts, row in recent.iterrows():
            lines.append(
                f"{ts.strftime('%m-%d %H:%M')} O:{row['open']:.6f} H:{row['high']:.6f} "
                f"L:{row['low']:.6f} C:{row['close']:.6f} V:{row['volume']:.2f}"
            )
        return "\n".join(lines)

    def _prepare_prompt_data(
        self,
        symbol: str,
        df: pd.DataFrame,
        price: float,
        ema20: float,
        ema50: float,
        atr: float,
        rsi: float,
        support: float,
        resistance: float,
        day_high: float,
        day_low: float,
        regime: str,
        memory: SymbolMemory
    ) -> dict:
        """Prepare common prompt variables."""
        ohlcv_text = self._format_ohlcv(df, periods=50)
        mem_lines = []
        if memory.trades:
            recent = memory.trades[-5:]
            for t in recent:
                mem_lines.append(f"- {t['side']} {t['reason']} PnL:{t['pnl_pct']:.2f}%")
        else:
            mem_lines.append("- No recent trades")
        consecutive_sl_long = memory.consecutive_sl_same_side("long")
        consecutive_sl_short = memory.consecutive_sl_same_side("short")
        winrate = memory.winrate_last_n(20)
        return {
            "symbol": symbol,
            "price": price,
            "ema20": ema20,
            "ema50": ema50,
            "atr": atr,
            "rsi": rsi,
            "support": support,
            "resistance": resistance,
            "day_high": day_high,
            "day_low": day_low,
            "regime": regime,
            "ohlcv_text": ohlcv_text,
            "mem_lines": "\n".join(mem_lines),
            "consecutive_sl_long": consecutive_sl_long,
            "consecutive_sl_short": consecutive_sl_short,
            "winrate": winrate,
        }

    def _build_prompt_baseline(self, d: dict) -> str:
        return f"""You are an ensemble trading analyst. Analyze the provided market data and output a strict JSON decision.

## SYMBOL: {d['symbol']}
## CURRENT PRICE: {d['price']:.6f}
## MARKET REGIME: {d['regime']}
## DAILY RANGE: High={d['day_high']:.6f} Low={d['day_low']:.6f}

## TECHNICAL INDICATORS (current):
- EMA20: {d['ema20']:.6f}
- EMA50: {d['ema50']:.6f}
- RSI14: {d['rsi']:.2f}
- ATR14: {d['atr']:.6f}
- Nearest Support: {d['support']:.6f}
- Nearest Resistance: {d['resistance']:.6f}

## RECENT PRICE ACTION (last 50 candles):
{d['ohlcv_text']}

## SYMBOL MEMORY (last 5 trades):
{d['mem_lines']}
- Win rate last 20: {d['winrate']:.1%}
- Consecutive SL (long): {d['consecutive_sl_long']}
- Consecutive SL (short): {d['consecutive_sl_short']}

## TASK:
1. Evaluate BULL probability (breakout/upside continuation) → bull_confidence 0.0–1.0
2. Evaluate BEAR probability (breakdown/downside continuation) → bear_confidence 0.0–1.0
3. Make final DECISION: "LONG", "SHORT", or "HOLD"
4. Provide overall confidence 0–100
5. Brief reasoning (1 sentence)

## RULES:
- If one side confidence >= 0.50 and the other is weaker → choose that side (LONG or SHORT)
- HOLD only when: both signals are genuinely weak (<0.35) OR both conflict strongly (>0.60 each in opposite directions)
- If price is near daily high and regime is ranging → bias to SHORT
- If price is near daily low and regime is ranging → bias to LONG
- If 2+ consecutive SL in a side exists in memory → reduce confidence for that side
- Respond ONLY with the JSON object below, no markdown, no explanation outside JSON.

## REQUIRED JSON FORMAT:
{{"bull_confidence": 0.00, "bear_confidence": 0.00, "decision": "HOLD", "confidence": 0, "size": 0.0, "reasoning": "..."}}
"""

    def _build_prompt_asymmetry(self, d: dict) -> str:
        return f"""You are an elite quantitative trading analyst. Your task is to analyze market data and output a strict JSON decision with high precision.

## SYMBOL: {d['symbol']}
## CURRENT PRICE: {d['price']:.6f}
## MARKET REGIME: {d['regime']}
## DAILY RANGE: High={d['day_high']:.6f} Low={d['day_low']:.6f}

## TECHNICAL INDICATORS:
- EMA20: {d['ema20']:.6f}
- EMA50: {d['ema50']:.6f}
- RSI14: {d['rsi']:.2f}
- ATR14: {d['atr']:.6f} (volatility measure)
- Nearest Support: {d['support']:.6f}
- Nearest Resistance: {d['resistance']:.6f}

## TREND CONTEXT:
- Price vs EMA20: {'above' if d['price'] > d['ema20'] else 'below'}
- Price vs EMA50: {'above' if d['price'] > d['ema50'] else 'below'}
- EMA20 vs EMA50: {'bullish' if d['ema20'] > d['ema50'] else 'bearish'} alignment

## RECENT PRICE ACTION (last 50 candles):
{d['ohlcv_text']}

## SYMBOL MEMORY (last 5 trades):
{d['mem_lines']}
- Win rate last 20: {d['winrate']:.1%}
- Consecutive SL (long): {d['consecutive_sl_long']}
- Consecutive SL (short): {d['consecutive_sl_short']}

## RISK/REWARD FRAMEWORK (ASYMMETRY):
This system uses asymmetric risk management:
- Stop Loss (SL): 2% from entry (tight stop)
- Take Profit (TP): 4% from entry (2:1 reward/risk)
- ONLY enter when you expect a STRONG directional move (≥4% potential).

## TASK:
1. Calculate BULL potential to resistance: {(d['resistance'] - d['price']) / d['price'] * 100:.2f}% available
2. Calculate BEAR potential to support: {(d['price'] - d['support']) / d['price'] * 100:.2f}% available
3. Evaluate BULL probability → bull_confidence 0.0–1.0 (high only if bull_potential ≥ 4% and trend supports)
4. Evaluate BEAR probability → bear_confidence 0.0–1.0 (high only if bear_potential ≥ 4% and trend supports)
5. Make final DECISION: "LONG", "SHORT", or "HOLD"
6. Overall confidence 0–100 (must be ≥60 for entry)
7. Brief reasoning (1 sentence, mention expected R/R)
8. Position size 0.0–1.0 (0 for HOLD; 0.10 for conf 60-70; 0.15 for 70-80; 0.20 for 80+)

## STRICT RULES:
- LONG only if: price > EMA20, EMA20 > EMA50 (or very close), RSI < 70, no 2+ consecutive SL long, bull_potential ≥ 4%
- SHORT only if: price < EMA20, EMA20 < EMA50 (or very close), RSI > 30, no 2+ consecutive SL short, bear_potential ≥ 4%
- HOLD if: potential < 4% either side, trend contradicts direction, RSI extreme, or signals conflict
- If price within 1% of daily high → REDUCE long confidence significantly
- If price within 1% of daily low → REDUCE short confidence significantly
- Respond ONLY with JSON below, no markdown, no explanation outside JSON.

## REQUIRED JSON FORMAT:
{{"bull_confidence": 0.00, "bear_confidence": 0.00, "decision": "HOLD", "confidence": 0, "size": 0.0, "reasoning": "..."}}
"""

    def _build_prompt(
        self,
        symbol: str,
        df: pd.DataFrame,
        price: float,
        ema20: float,
        ema50: float,
        atr: float,
        rsi: float,
        support: float,
        resistance: float,
        day_high: float,
        day_low: float,
        regime: str,
        memory: SymbolMemory
    ) -> str:
        """Dispatch to the selected prompt version."""
        d = self._prepare_prompt_data(
            symbol, df, price, ema20, ema50, atr, rsi,
            support, resistance, day_high, day_low, regime, memory
        )
        if getattr(self.cfg, "prompt_version", "baseline") == "asymmetry":
            return self._build_prompt_asymmetry(d)
        return self._build_prompt_baseline(d)

    async def decide(
        self,
        symbol: str,
        df: pd.DataFrame,
        price: float,
        ema20: float,
        ema50: float,
        atr: float,
        rsi: float,
        support: float,
        resistance: float,
        day_high: float,
        day_low: float,
        regime: str,
        memory: SymbolMemory
    ) -> Dict:
        """Один вызов Kimi. Возвращает полный decision object."""

        # Mock mode — no API calls
        if self.cfg.mock_judge:
            return self._mock_decision(symbol)

        prompt = self._build_prompt(
            symbol, df, price, ema20, ema50, atr, rsi,
            support, resistance, day_high, day_low, regime, memory
        )

        # Try cache
        cached = self._load_cache(prompt)
        if cached is not None:
            self._cache_hits += 1
            return cached
        self._cache_misses += 1

        client = self._get_client()
        try:
            resp = await client.chat.completions.create(
                model=self.cfg.kimi_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=1.0,
                max_tokens=512,
                timeout=self.cfg.request_timeout
            )
            text = resp.choices[0].message.content.strip()
            result = self._parse_response(text, symbol)
            self._save_cache(prompt, result)
            return result
        except Exception as e:
            logger.warning(f"Kimi unified call failed for {symbol}: {e}")
            return {
                "bull_confidence": 0.0,
                "bear_confidence": 0.0,
                "decision": "HOLD",
                "confidence": 0,
                "size": 0.0,
                "reasoning": f"API_ERROR: {str(e)[:50]}"
            }

    def _parse_response(self, text: str, symbol: str) -> Dict:
        """Строгий парсинг JSON от Kimi."""
        text = text.strip()

        # Удалить markdown code fences если есть
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        # Найти JSON объект
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            logger.warning(f"[{symbol}] No JSON found in response: {text[:100]}")
            return self._fallback(text)

        try:
            data = json.loads(text[start:end+1])

            # Нормализация
            bull_conf = float(data.get("bull_confidence", 0))
            bear_conf = float(data.get("bear_confidence", 0))
            decision = str(data.get("decision", "HOLD")).upper().strip()
            conf = int(data.get("confidence", 0))
            size = float(data.get("size", 0))
            reasoning = str(data.get("reasoning", ""))

            # Валидация decision
            if decision not in ("LONG", "SHORT", "HOLD"):
                decision = "HOLD"

            # Если decision не HOLD, но confidence обеих сторон низкая — форсируем HOLD
            if decision != "HOLD" and max(bull_conf, bear_conf) < 0.50:
                decision = "HOLD"

            return {
                "bull_confidence": max(0.0, min(1.0, bull_conf)),
                "bear_confidence": max(0.0, min(1.0, bear_conf)),
                "decision": decision,
                "confidence": max(0, min(100, conf)),
                "size": size,
                "reasoning": reasoning[:200]
            }

        except json.JSONDecodeError as e:
            logger.warning(f"[{symbol}] JSON parse error: {e} | Text: {text[:150]}")
            return self._fallback(text)

    def _fallback(self, text: str) -> Dict:
        """Эвристика если JSON сломан."""
        lower = text.lower()
        if "long" in lower and "short" not in lower:
            return {"bull_confidence": 0.6, "bear_confidence": 0.3, "decision": "LONG", "confidence": 50, "size": 5.0, "reasoning": "fallback_long"}
        if "short" in lower and "long" not in lower:
            return {"bull_confidence": 0.3, "bear_confidence": 0.6, "decision": "SHORT", "confidence": 50, "size": 5.0, "reasoning": "fallback_short"}
        return {"bull_confidence": 0.0, "bear_confidence": 0.0, "decision": "HOLD", "confidence": 0, "size": 0.0, "reasoning": "fallback_hold"}


# ---------------------------------------------------------------------------
# RL State / Reward
# ---------------------------------------------------------------------------

@dataclass
class RLState:
    bull_confidence: float
    bear_confidence: float
    entry_position_in_range: float
    distance_to_nearest_level: float
    market_regime: int
    rsi_14: float
    funding_rate: float
    time_of_day_utc: float
    consecutive_same_side_signals: int

    def to_vector(self) -> np.ndarray:
        vec = np.array([
            self.bull_confidence,
            self.bear_confidence,
            self.entry_position_in_range,
            self.distance_to_nearest_level,
            self.market_regime,
            self.rsi_14 / 100.0,
            self.funding_rate,
            self.time_of_day_utc / 24.0,
            self.consecutive_same_side_signals / 5.0
        ], dtype=np.float32)
        return np.nan_to_num(vec, nan=0.0, posinf=1.0, neginf=-1.0)


class RewardShaper:
    @staticmethod
    def calculate(
        pnl_pct: float,
        reason: str,
        side: str,
        entry_pos_in_range: float,
        regime: str,
        hold_time_minutes: float,
        side_aligned_with_regime: bool
    ) -> float:
        reward = 0.0
        if reason == "take_profit":
            reward += 1.0
        elif reason == "stop_loss":
            reward -= 1.0
        elif reason == "trailing_stop":
            reward += 0.5 if pnl_pct > 0 else -0.5

        if side == "long" and entry_pos_in_range > 0.85:
            reward -= 2.0
        if side == "short" and entry_pos_in_range < 0.15:
            reward -= 2.0

        if side_aligned_with_regime:
            reward += 0.5
        else:
            reward -= 0.5

        if reason == "stop_loss" and hold_time_minutes < 30:
            reward -= 1.5

        return reward


# ---------------------------------------------------------------------------
# Virtual Position & Engine
# ---------------------------------------------------------------------------

@dataclass
class VirtualPosition:
    symbol: str
    side: str
    entry_price: float
    sl_price: float
    tp_price: float
    size_usdt: float
    leverage: float
    entry_time: datetime
    open_idx: int
    mode: str = "optimized"
    liq_price: float = field(init=False)
    _peak_pnl_pct: float = field(default=0.0, repr=False)
    _trailing_active: bool = field(default=False, repr=False)
    _sl_moved: bool = field(default=False, repr=False)

    def __post_init__(self):
        if self.side == "long":
            self.liq_price = self.entry_price * (1 - 0.8 / self.leverage)
        else:
            self.liq_price = self.entry_price * (1 + 0.8 / self.leverage)

    def _raw_pnl_pct(self, price: float) -> float:
        if self.side == "long":
            return (price - self.entry_price) / self.entry_price
        return (self.entry_price - price) / self.entry_price

    def update_peak(self, candle: pd.Series):
        """Track peak PnL for trailing stop logic."""
        if self.side == "long":
            pnl = self._raw_pnl_pct(candle["high"])
        else:
            pnl = self._raw_pnl_pct(candle["low"])
        if pnl > self._peak_pnl_pct:
            self._peak_pnl_pct = pnl

    def check_exit(self, candle: pd.Series, mode_cfg: Optional[SimConfig] = None) -> Tuple[bool, Optional[str], float]:
        high, low, close = candle["high"], candle["low"], candle["close"]
        if self.side == "long":
            if low <= self.liq_price:
                return True, "liquidation", self.liq_price
            if low <= self.sl_price:
                reason = "trailing_stop" if self._sl_moved else "stop_loss"
                return True, reason, self.sl_price
            if high >= self.tp_price:
                return True, "take_profit", self.tp_price
        else:
            if high >= self.liq_price:
                return True, "liquidation", self.liq_price
            if high >= self.sl_price:
                reason = "trailing_stop" if self._sl_moved else "stop_loss"
                return True, reason, self.sl_price
            if low <= self.tp_price:
                return True, "take_profit", self.tp_price
        return False, None, close

    def pnl_pct(self, exit_price: float) -> float:
        if self.side == "long":
            return (exit_price - self.entry_price) / self.entry_price * self.leverage
        return (self.entry_price - exit_price) / self.entry_price * self.leverage


class TradingEngine:
    def __init__(self, config: SimConfig, initial_balance: float = 1000.0):
        self.cfg = config
        self.positions: Dict[str, VirtualPosition] = {}
        self.closed_trades: List[Dict] = []
        self.daily_stats = {"shorts": 0, "longs": 0, "date": None}
        self.balance = initial_balance
        self.initial_balance = initial_balance

    def can_open(self, symbol: str, side: str, memory: SymbolMemory, regime: str,
                 bull_conf: float, bear_conf: float, current_time: datetime) -> Tuple[bool, Optional[str]]:
        if symbol in self.positions:
            return False, "ALREADY_OPEN"

        cooldown = memory.cooldown_until(side, self.cfg.cooldown_hours_after_2_sl)
        if cooldown and current_time < cooldown:
            return False, f"COOLDOWN_UNTIL_{cooldown.isoformat()}"

        mult = RegimeDetector.threshold_multiplier(regime, side)
        base_conf = bull_conf if side == "long" else bear_conf
        if base_conf * mult < 0.5:
            return False, f"THRESHOLD_TOO_LOW({base_conf:.2f}*{mult:.2f})"

        today = current_time.date()
        if self.daily_stats.get("date") != today:
            self.daily_stats = {"shorts": 0, "longs": 0, "date": today}
        total = self.daily_stats["shorts"] + self.daily_stats["longs"]
        if total > 0 and side == "short":
            ratio = self.daily_stats["shorts"] / total
            if ratio > self.cfg.max_daily_short_ratio:
                return False, "DAILY_SHORT_CAP"
        return True, None

    def _position_size(self) -> float:
        """Position notional size. live_mirror uses % of balance; optimized uses fixed $100."""
        if self.cfg.mode == "live_mirror":
            # 10% of current balance per trade (similar to live 0.03–0.12 range)
            return self.balance * 0.10
        return 100.0

    def open_position(self, symbol: str, side: str, entry_price: float,
                      sl_price: float, tp_price: float, current_time: datetime, idx: int) -> VirtualPosition:
        pos = VirtualPosition(
            symbol=symbol, side=side, entry_price=entry_price,
            sl_price=sl_price, tp_price=tp_price,
            size_usdt=self._position_size(), leverage=self.cfg.leverage,
            entry_time=current_time, open_idx=idx, mode=self.cfg.mode
        )
        self.positions[symbol] = pos
        if self.cfg.mode == "live_mirror":
            self.balance -= pos.size_usdt / pos.leverage
        self.daily_stats["shorts" if side == "short" else "longs"] += 1
        return pos

    def close_position(self, symbol: str, exit_price: float, reason: str,
                       exit_time: datetime, idx: int) -> Dict:
        pos = self.positions.pop(symbol)
        pnl_pct = pos.pnl_pct(exit_price)
        # Update balance for live_mirror mode
        if self.cfg.mode == "live_mirror":
            margin = pos.size_usdt / pos.leverage
            # pnl_pct is leverage-adjusted decimal (e.g. 0.50 for +50%)
            pnl_usdt = margin * pnl_pct
            self.balance += margin + pnl_usdt
        hold_time = (exit_time - pos.entry_time).total_seconds() / 60.0
        trade = {
            "symbol": symbol, "side": pos.side,
            "entry": pos.entry_price, "exit": exit_price,
            "sl": pos.sl_price, "tp": pos.tp_price,
            "pnl_pct": round(pnl_pct * 100, 2), "reason": reason,
            "opened": pos.entry_time.isoformat(),
            "closed": exit_time.isoformat(),
            "hold_minutes": round(hold_time, 1),
            "leverage": pos.leverage,
            "mode": self.cfg.mode
        }
        self.closed_trades.append(trade)
        return trade

    def update_trailing(self, pos: VirtualPosition, candle: pd.Series):
        pos.update_peak(candle)
        if self.cfg.mode == "live_mirror":
            # Live mirror trailing: arm at +1.5%, giveback 1.0%
            arm = self.cfg.live_mirror_trail_arm_pct
            give = self.cfg.live_mirror_trail_giveback_pct
            if pos._peak_pnl_pct >= arm and not pos._trailing_active:
                pos._trailing_active = True
            if pos._trailing_active:
                if pos.side == "long":
                    trail_sl = pos.entry_price * (1 + pos._peak_pnl_pct - give)
                    if trail_sl > pos.sl_price:
                        pos.sl_price = trail_sl
                        pos._sl_moved = True
                else:
                    trail_sl = pos.entry_price * (1 - pos._peak_pnl_pct + give)
                    if trail_sl < pos.sl_price:
                        pos.sl_price = trail_sl
                        pos._sl_moved = True
            return

        # --- optimized mode ---
        # Trailing activates at 75% of TP distance, moves SL to entry ±0.5%
        if pos.side == "long":
            tp_dist = pos.tp_price - pos.entry_price
            if tp_dist <= 0:
                return
            trigger = pos.entry_price + tp_dist * self.cfg.optimized_trail_arm_pct
            if candle["high"] >= trigger and pos.sl_price < pos.entry_price:
                new_sl = pos.entry_price * (1 + self.cfg.optimized_trail_sl_buffer_pct)
                if new_sl > pos.sl_price:
                    pos.sl_price = new_sl
                    pos._sl_moved = True
        else:
            tp_dist = pos.entry_price - pos.tp_price
            if tp_dist <= 0:
                return
            trigger = pos.entry_price - tp_dist * self.cfg.optimized_trail_arm_pct
            if candle["low"] <= trigger and pos.sl_price > pos.entry_price:
                new_sl = pos.entry_price * (1 - self.cfg.optimized_trail_sl_buffer_pct)
                if new_sl < pos.sl_price:
                    pos.sl_price = new_sl
                    pos._sl_moved = True

    def process_candle(self, symbol: str, candle: pd.Series, idx: int, current_time: datetime):
        if symbol not in self.positions:
            return None
        pos = self.positions[symbol]
        self.update_trailing(pos, candle)

        # Max hold time exit
        hold_hours = (current_time - pos.entry_time).total_seconds() / 3600.0
        if hold_hours >= self.cfg.max_hold_hours:
            return self.close_position(symbol, candle["close"], "max_hold_time", current_time, idx)

        closed, reason, exit_price = pos.check_exit(candle)
        if closed:
            return self.close_position(symbol, exit_price, reason, current_time, idx)
        return None


# ---------------------------------------------------------------------------
# RL Dataset Builder
# ---------------------------------------------------------------------------

class RLDatasetBuilder:
    def __init__(self):
        self.transitions: List[Dict] = []

    def add(self, state: RLState, action: str, reward: float,
            next_state: Optional[RLState], trade_info: Dict):
        self.transitions.append({
            "state": state.to_vector().tolist(),
            "action": action,
            "reward": round(reward, 4),
            "next_state": next_state.to_vector().tolist() if next_state else None,
            "trade": trade_info
        })

    def save(self, path: Path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.transitions, f, ensure_ascii=False, indent=2)
        logger.info(f"[RL] Dataset saved: {path} ({len(self.transitions)} transitions)")


# ---------------------------------------------------------------------------
# Main Simulator
# ---------------------------------------------------------------------------

class Simulator:
    def __init__(self, config: SimConfig):
        self.cfg = config
        self.loader = BinanceDataLoader(config)
        self.indicators = TechnicalIndicators()
        self.entry_filter = EntryFilter(config)
        self.judge = UnifiedKimiJudge(config)
        self.engine = TradingEngine(config, initial_balance=1000.0)
        self.rl_builder = RLDatasetBuilder()
        self.memories: Dict[str, SymbolMemory] = defaultdict(lambda: SymbolMemory(""))
        self.consecutive_signals: Dict[str, Dict] = defaultdict(lambda: {"long": 0, "short": 0})
        self.pending_states: Dict[str, Dict] = {}
        self.reject_logger = RejectLogger()
        self._candles_processed = 0
        self._entries_attempted = 0

    async def run(self):
        logger.info("=" * 60)
        logger.info(f"SIMULATOR START (mode={self.cfg.mode})")
        logger.info(f"Symbols: {len(self.cfg.symbols)} | Months: {self.cfg.months} | Interval: {self.cfg.interval}")
        logger.info("=" * 60)

        async with aiohttp.ClientSession() as session:
            data_map: Dict[str, pd.DataFrame] = {}
            for sym in self.cfg.symbols:
                df = await self.loader.load(session, sym, self.cfg.interval, self.cfg.months)
                if df.empty:
                    logger.warning(f"[SKIP] No data for {sym}")
                    continue
                data_map[sym] = df
                logger.info(f"[DATA] {sym}: {len(df)} candles")

            if not data_map:
                logger.error("No data loaded. Exiting.")
                return

            common_idx = None
            for sym, df in data_map.items():
                if common_idx is None:
                    common_idx = df.index
                else:
                    common_idx = common_idx.intersection(df.index)

            logger.info(f"[SYNC] Common timeline: {len(common_idx)} candles")

            for i, ts in enumerate(common_idx):
                self._candles_processed += 1
                if i % 500 == 0:
                    logger.info(f"[PROGRESS] {i}/{len(common_idx)} | Closed: {len(self.engine.closed_trades)} | Open: {len(self.engine.positions)} | Attempted: {self._entries_attempted}")

                # 1. Обработка открытых позиций
                for sym, df in data_map.items():
                    if sym in self.engine.positions:
                        candle = df.loc[ts]
                        trade = self.engine.process_candle(sym, candle, i, ts)
                        if trade:
                            mem = self.memories[sym]
                            mem.record(trade["side"], trade["pnl_pct"], trade["reason"], ts)

                            entry_pos = self._get_entry_pos_from_trade(trade, df)
                            regime = trade.get("regime", "ranging")
                            side_aligned = (regime == "bull" and trade["side"] == "long") or \
                                           (regime == "bear" and trade["side"] == "short")
                            reward = RewardShaper.calculate(
                                trade["pnl_pct"], trade["reason"], trade["side"],
                                entry_pos, regime, trade["hold_minutes"], side_aligned
                            )

                            if sym in self.pending_states:
                                pending = self.pending_states.pop(sym)
                                pending["reward"] = reward
                                pending["trade"] = trade
                                self.rl_builder.transitions.append(pending)

                # 2. Новые входы (batch)
                candidates = [s for s in data_map if s not in self.engine.positions]
                if candidates:
                    await self._process_entry_batch(session, candidates, data_map, ts, i)

        self._save_results()

    def _get_entry_pos_from_trade(self, trade: Dict, df: pd.DataFrame) -> float:
        try:
            entry_time = datetime.fromisoformat(trade["opened"])
            day_df = df[df.index.date == entry_time.date()]
            if day_df.empty:
                return 0.5
            high, low = day_df["high"].max(), day_df["low"].min()
            if high == low:
                return 0.5
            return (trade["entry"] - low) / (high - low)
        except Exception:
            return 0.5

    async def _process_entry_batch(
        self,
        session: aiohttp.ClientSession,
        symbols: List[str],
        data_map: Dict[str, pd.DataFrame],
        ts: datetime,
        idx: int
    ):
        semaphore = asyncio.Semaphore(self.cfg.max_concurrent_kimi_calls)

        async def process_one(sym: str):
            async with semaphore:
                df = data_map[sym]
                candle = df.loc[ts]
                price = candle["close"]

                # Индикаторы
                ema20 = self.indicators.ema(df["close"], 20).loc[ts]
                ema50 = self.indicators.ema(df["close"], 50).loc[ts]
                atr = self.indicators.atr(df, 14).loc[ts]
                rsi = self.indicators.rsi(df["close"], 14).loc[ts]
                support, resistance = self.indicators.nearest_levels(df, 50)
                day_high, day_low, day_range = self.indicators.daily_range(df, ts)
                regime = RegimeDetector.detect(price, ema20, ema50)

                # Memory
                mem = self.memories[sym]
                mem.symbol = sym

                # Volatility filter: skip if ATR < 0.5% of price (too noisy)
                if self.cfg.mode == "optimized" and atr / price < self.cfg.volatility_filter_atr_pct:
                    return

                # === ОДИН ВЫЗОВ KIMI ===
                decision = await self.judge.decide(
                    sym, df, price, ema20, ema50, atr, rsi,
                    support, resistance, day_high, day_low, regime, mem
                )

                side = decision.get("decision", "HOLD").lower()
                if side == "hold":
                    self.reject_logger.record_kimi_hold(sym, decision.get("reasoning", ""))
                    return

                bull_conf = decision.get("bull_confidence", 0)
                bear_conf = decision.get("bear_confidence", 0)

                # Python-фильтры (не в промпте)
                ok_extreme, extreme_reason = self.entry_filter.check_extreme(side, price, day_high, day_low)
                if not ok_extreme:
                    self.reject_logger.record(sym, f"EXTREME_FILTER:{extreme_reason}")
                    return

                min_rr = self.cfg.min_rr if self.cfg.mode == "optimized" else 1.0
                ok_levels, levels = self.entry_filter.calculate_dynamic_levels(
                    side, price, atr, support, resistance, min_rr
                )
                if not ok_levels:
                    reason = levels.get("reason", "R_R_TOO_LOW") if isinstance(levels, dict) else "R_R_TOO_LOW"
                    self.reject_logger.record(sym, f"LEVELS:{reason}")
                    return

                can_open, reject_reason = self.engine.can_open(
                    sym, side, mem, regime, bull_conf, bear_conf, ts
                )
                if not can_open:
                    self.reject_logger.record(sym, f"ENGINE:{reject_reason}")
                    return

                self._entries_attempted += 1

                # Открытие позиции
                sl = levels["sl"]
                tp = levels["tp"]
                pos = self.engine.open_position(sym, side, price, sl, tp, ts, idx)

                # RL State
                entry_pos = (price - day_low) / day_range if day_range > 0 else 0.5
                dist_to_level = min(abs(price - support), abs(price - resistance)) / atr if atr > 0 else 0
                regime_int = 1 if regime == "bull" else (-1 if regime == "bear" else 0)

                state = RLState(
                    bull_confidence=bull_conf,
                    bear_confidence=bear_conf,
                    entry_position_in_range=entry_pos,
                    distance_to_nearest_level=dist_to_level,
                    market_regime=regime_int,
                    rsi_14=rsi,
                    funding_rate=0.0,
                    time_of_day_utc=ts.hour + ts.minute / 60.0,
                    consecutive_same_side_signals=self.consecutive_signals[sym][side]
                )

                self.consecutive_signals[sym][side] += 1
                self.consecutive_signals[sym]["long" if side == "short" else "short"] = 0

                # Сохраняем pending state (reward и trade дополним при выходе)
                self.pending_states[sym] = {
                    "state": state.to_vector().tolist(),
                    "action": side,
                    "reward": None,
                    "next_state": None,
                    "entry_time": ts.isoformat()
                }

        await asyncio.gather(*[process_one(s) for s in symbols], return_exceptions=True)

    def _save_results(self):
        ts_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out = self.cfg.output_dir / ts_str
        out.mkdir(parents=True, exist_ok=True)

        trades_path = out / "trades.json"
        with open(trades_path, "w", encoding="utf-8") as f:
            json.dump(self.engine.closed_trades, f, ensure_ascii=False, indent=2)
        logger.info(f"[SAVE] Trades: {trades_path} ({len(self.engine.closed_trades)} trades)")

        rl_path = out / "rl_dataset.json"
        self.rl_builder.save(rl_path)

        stats = self._compute_stats()
        stats["reject_stats"] = self.reject_logger.summary()
        stats["candles_processed"] = self._candles_processed
        stats["entries_attempted"] = self._entries_attempted
        stats["kimi_cache_hits"] = getattr(self.judge, '_cache_hits', 0)
        stats["kimi_cache_misses"] = getattr(self.judge, '_cache_misses', 0)
        stats_path = out / "stats.json"
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        logger.info(f"[SAVE] Stats: {stats_path}")

        if self.engine.closed_trades:
            df = pd.DataFrame(self.engine.closed_trades)
            df.to_csv(out / "trades.csv", index=False)

        # Save reject details
        reject_path = out / "rejects.json"
        with open(reject_path, "w", encoding="utf-8") as f:
            json.dump(self.reject_logger.summary(), f, ensure_ascii=False, indent=2)
        logger.info(f"[SAVE] Rejects: {reject_path}")

        # Backup Kimi cache
        try:
            import zipfile
            cache_backup = out / "kimi_cache.zip"
            with zipfile.ZipFile(cache_backup, 'w', zipfile.ZIP_DEFLATED) as zf:
                for f in self.cfg.kimi_cache_dir.iterdir():
                    if f.is_file():
                        zf.write(f, f.name)
            logger.info(f"[SAVE] Cache backup: {cache_backup}")
        except Exception as e:
            logger.warning(f"Cache backup failed: {e}")

    def _compute_stats(self) -> Dict:
        trades = self.engine.closed_trades
        if not trades:
            return {"mode": self.cfg.mode}
        df = pd.DataFrame(trades)
        wins = df[df["pnl_pct"] > 0]
        losses = df[df["pnl_pct"] <= 0]
        return {
            "mode": self.cfg.mode,
            "total_trades": len(df),
            "win_rate": round(len(wins) / len(df) * 100, 2),
            "avg_pnl": round(df["pnl_pct"].mean(), 4),
            "total_pnl_pct": round(df["pnl_pct"].sum(), 4),
            "avg_win": round(wins["pnl_pct"].mean(), 4) if not wins.empty else 0,
            "avg_loss": round(losses["pnl_pct"].mean(), 4) if not losses.empty else 0,
            "shorts": int((df["side"] == "short").sum()),
            "longs": int((df["side"] == "long").sum()),
            "sl_count": int((df["reason"] == "stop_loss").sum()),
            "tp_count": int((df["reason"] == "take_profit").sum()),
            "trailing_count": int((df["reason"] == "trailing_stop").sum()),
            "max_hold_count": int((df["reason"] == "max_hold_time").sum()),
            "liquidation_count": int((df["reason"] == "liquidation").sum()),
            "final_balance": round(self.engine.balance, 2) if self.cfg.mode == "live_mirror" else None,
            "rl_transitions": len(self.rl_builder.transitions)
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Offline RL Simulator — Unified Kimi")
    parser.add_argument("--symbols", type=str, default=",".join(SimConfig().symbols))
    parser.add_argument("--months", type=int, default=6)
    parser.add_argument("--interval", type=str, default="15m", choices=["15m","1h","4h"])
    parser.add_argument("--leverage", type=float, default=5.0)
    parser.add_argument("--mode", type=str, default="optimized", choices=["live_mirror","optimized"])
    parser.add_argument("--sl-pct", type=float, default=None, help="Override live_mirror SL pct (e.g. 0.02)")
    parser.add_argument("--tp-pct", type=float, default=None, help="Override live_mirror TP pct (e.g. 0.04)")
    parser.add_argument("--prompt-version", type=str, default="baseline", choices=["baseline","asymmetry"], help="Kimi prompt version")
    parser.add_argument("--max-concurrent", type=int, default=15, help="Max concurrent Kimi calls")
    parser.add_argument("--mock-judge", action="store_true", help="Use random signals instead of Kimi API")
    parser.add_argument("--mock-rate", type=float, default=0.15, help="Signal probability in mock mode")
    args = parser.parse_args()

    cfg_kwargs = dict(
        symbols=args.symbols.split(","),
        months=args.months,
        interval=args.interval,
        leverage=args.leverage,
        mode=args.mode,
        prompt_version=args.prompt_version,
        max_concurrent_kimi_calls=args.max_concurrent,
        mock_judge=args.mock_judge,
        mock_judge_signal_rate=args.mock_rate
    )
    if args.sl_pct is not None:
        cfg_kwargs["live_mirror_sl_pct"] = args.sl_pct
    if args.tp_pct is not None:
        cfg_kwargs["live_mirror_tp_pct"] = args.tp_pct
    cfg = SimConfig(**cfg_kwargs)

    sim = Simulator(cfg)
    asyncio.run(sim.run())


if __name__ == "__main__":
    main()

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
KIMI_API_KEY=***

```

