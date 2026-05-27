# Live status

Generated: 2026-05-27 14:00:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      983538  0.0  1.1 130828 45172 ?        Ssl  12:06   0:01 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root      983708  0.2  3.2 688068 126048 ?       Ssl  12:20   0:13 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
```

## Paper state
```json
{
  "balance": 984.0433557693924,
  "positions": {
    "LINKUSDT": {
      "id": "PAPER_LINKUSDT_1779855776",
      "symbol": "LINKUSDT",
      "side": "short",
      "entry_price": 9.35,
      "qty": 10.6952,
      "confidence": 72,
      "opened_at": "2026-05-27T04:22:56.413656",
      "cost": 20.000024,
      "notional": 100.00012,
      "leverage": 5
    }
  },
  "trade_history": [
    {
      "id": "PAPER_PEPEUSDT_1779855184",
      "symbol": "PEPEUSDT",
      "side": "short",
      "entry_price": 3.5176e-06,
      "qty": 28428473.9595,
      "confidence": 72,
      "opened_at": "2026-05-27T04:13:04.351442",
      "cost": 19.99999999998744,
      "notional": 99.9999999999372,
      "leverage": 5,
      "exit_price": 3.5026e-06,
      "pnl_pct": 2.13,
      "pnl_usdt": 0.43,
      "closed_at": "2026-05-27T04:58:57.087082",
      "reason": "breakeven_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_HYPEUSDT_1779855561",
      "symbol": "HYPEUSDT",
      "side": "short",
      "entry_price": 59.775,
      "qty": 1.6729,
      "confidence": 72,
      "opened_at": "2026-05-27T04:19:21.880839",
      "cost": 19.999519499999998,
      "notional": 99.9975975,
      "leverage": 5,
      "exit_price": 60.99,
      "pnl_pct": -10.16,
      "pnl_usdt": -2.03,
      "closed_at": "2026-05-27T05:27:01.127399",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_ONDOUSDT_1779863392",
      "symbol": "ONDOUSDT",
      "side": "short",
      "entry_price": 0.4105,
      "qty": 243.6054,
      "confidence": 72,
      "opened_at": "2026-05-27T06:29:52.857604",
      "cost": 20.00000334,
      "notional": 100.00001669999999,
      "leverage": 5,
      "exit_price": 0.3976,
      "pnl_pct": 15.71,
      "pnl_usdt": 3.14,
      "closed_at": "2026-05-27T10:01:19.768565",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_HYPEUSDT_1779870952",
      "symbol": "HYPEUSDT",
      "side": "short",
      "entry_price": 62.219,
      "qty": 1.6072,
      "confidence": 68,
      "opened_at": "2026-05-27T08:35:52.416653",
      "cost": 19.99967536,
      "notional": 99.9983768,
      "leverage": 5,
      "exit_price": 60.968,
      "pnl_pct": 10.05,
      "pnl_usdt": 2.01,
      "closed_at": "2026-05-27T13:55:06.261562",
      "reason": "trailing_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_TONUSDT_1779878581",
      "symbol": "TONUSDT",
      "side": "short",
      "entry_price": 1.8936,
      "qty": 52.8095,
      "confidence": 72,
      "opened_at": "2026-05-27T10:43:01.437431",
      "cost": 20.00001384,
      "notional": 100.0000692,
      "leverage": 5,
      "exit_price": 1.8842,
      "pnl_pct": 2.48,
      "pnl_usdt": 0.5,
      "closed_at": "2026-05-27T13:55:06.906522",
      "reason": "breakeven_stop",
      "outcome": "profit"
    }
  ],
  "total_pnl": 4.0433797693924705
}
```

## Ensemble log (last 30 lines)
```
2026-05-27 13:36:23,184 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 13:36:23,186 [INFO] main: BTCUSDT | Judge:HOLD conf=80% size=0.0%
2026-05-27 13:36:23,186 [INFO] main: BTCUSDT | RL adj=80.0%
2026-05-27 13:36:28,897 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 13:36:31,215 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 13:36:31,216 [INFO] main: PHAUSDT | Bull:flat(15%) Bear:short(70%)
2026-05-27 13:36:35,284 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 13:36:35,286 [INFO] main: PHAUSDT | Judge:SHORT conf=68% size=6.0%
2026-05-27 13:36:35,286 [INFO] main: PHAUSDT | RL adj=77.8%
2026-05-27 13:36:35,289 [INFO] main: PHAUSDT | Context score=-0.13 bias=0.12
2026-05-27 13:36:35,289 [INFO] main: PHAUSDT | regime BLOCK (volatile)
2026-05-27 13:36:41,656 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 13:36:42,011 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 13:36:42,013 [INFO] main: FILUSDT | Bull:long(62%) Bear:short(80%)
2026-05-27 13:36:47,719 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 13:36:47,720 [INFO] main: FILUSDT | Judge:HOLD conf=80% size=0.0%
2026-05-27 13:36:47,720 [INFO] main: FILUSDT | RL adj=80.0%
2026-05-27 13:36:49,723 [INFO] main: Next scan in 30min (weekday-active)
2026-05-27 13:55:06,261 [INFO] positions: TRAILING-STOP HYPEUSDT short peak:2.84% now:2.01%
2026-05-27 13:55:06,264 [INFO] paper_trading: [PAPER] ✅ ЗАКРЫТА SHORT HYPEUSDT @ 60.9680 PnL: 10.05% (+2.01 USDT) | Баланс: 963.55
2026-05-27 13:55:06,905 [INFO] positions: OK HYPEUSDT short PnL:2.01% reason:trailing_stop
2026-05-27 13:55:06,905 [INFO] positions: Lessons: Bearish technical confluence can still be muted by low volume and a ranging regime, so keep position size modest and use tight stops. Past similar short setups that flopped remind us to treat overbought RSI and bearish MACD as warnings, not guarantees. A small, well‑managed trade can capture modest upside even when the signal isn’t overwhelming.
2026-05-27 13:55:06,906 [INFO] rl: RL learned from short HYPEUSDT: profit 2.01% | weights bull=1.019 bear=0.937 judge=1.044 threshold=64.41
2026-05-27 13:55:06,906 [INFO] positions: BREAKEVEN_STOP TONUSDT short PnL:0.5%
2026-05-27 13:55:06,909 [INFO] paper_trading: [PAPER] ✅ ЗАКРЫТА SHORT TONUSDT @ 1.8842 PnL: 2.48% (+0.50 USDT) | Баланс: 984.04
2026-05-27 13:55:06,961 [WARNING] agents: Judge-Groq all failed: openai/gpt-oss-120b 429 (***7Czb cooldown 1h)
2026-05-27 13:55:09,499 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 13:55:09,501 [INFO] positions: OK TONUSDT short PnL:0.5% reason:breakeven_stop
2026-05-27 13:55:09,501 [INFO] positions: Lessons: The short captured a modest 0.5% gain in a trending_down regime where BEAR conviction (80%) clearly dominated BULL (72%), validating the directional bias despite RSI oversold conditions that could have triggered a false reversal. Conservative 0.06 sizing proved prudent—even strong bearish setups can fail or stall, so position sizing remains the primary risk lever when conviction margins are meaningful but not absolute. Memory: trending regimes with extreme sentiment (Fear 25) and negative funding favor continuation shorts, but always size for the scenario where the reversal happens anyway.
2026-05-27 13:55:09,501 [INFO] rl: RL learned from short TONUSDT: profit 0.50% | weights bull=1.017 bear=0.938 judge=1.045 threshold=64.38
```

## Disk
```
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           382M  896K  381M   1% /run
efivarfs        256K   39K  213K  16% /sys/firmware/efi/efivars
/dev/sda1        75G  8.4G   64G  12% /
tmpfs           1.9G     0  1.9G   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda15      253M  146K  252M   1% /boot/efi
tmpfs           382M   12K  382M   1% /run/user/0
```

## Memory
```
               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       888Mi       254Mi       4.8Mi       2.9Gi       2.9Gi
Swap:          2.0Gi       256Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
