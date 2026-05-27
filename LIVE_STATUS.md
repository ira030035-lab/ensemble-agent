# Live status

Generated: 2026-05-27 05:20:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      966808  0.0  1.1 131496 45740 ?        Ssl  May26   0:07 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root      977418  0.1  3.1 718372 124300 ?       Ssl  04:18   0:05 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
```

## Paper state
```json
{
  "balance": 960.4268836093923,
  "positions": {
    "HYPEUSDT": {
      "id": "PAPER_HYPEUSDT_1779855561",
      "symbol": "HYPEUSDT",
      "side": "short",
      "entry_price": 59.775,
      "qty": 1.6729,
      "confidence": 72,
      "opened_at": "2026-05-27T04:19:21.880839",
      "cost": 19.999519499999998,
      "notional": 99.9975975,
      "leverage": 5
    },
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
    }
  ],
  "total_pnl": 0.4264271093924959
}
```

## Ensemble log (last 30 lines)
```
2026-05-27 04:24:09,831 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:24:09,831 [INFO] main: SOLUSDT | Bull:long(45%) Bear:short(80%)
2026-05-27 04:24:18,424 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:24:18,426 [INFO] main: SOLUSDT | Judge:HOLD conf=80% size=0.0%
2026-05-27 04:24:18,426 [INFO] main: SOLUSDT | RL adj=80.0%
2026-05-27 04:24:24,091 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:24:26,016 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:24:26,017 [INFO] main: GRASSUSDT | Bull:long(60%) Bear:short(80%)
2026-05-27 04:24:30,035 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:24:30,037 [INFO] main: GRASSUSDT | Judge:HOLD conf=80% size=0.0%
2026-05-27 04:24:30,037 [INFO] main: GRASSUSDT | RL adj=80.0%
2026-05-27 04:24:37,219 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:24:38,404 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:24:38,405 [INFO] main: DOGEUSDT | Bull:long(60%) Bear:short(80%)
2026-05-27 04:24:44,528 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:24:44,530 [INFO] main: DOGEUSDT | Judge:HOLD conf=80% size=0.0%
2026-05-27 04:24:44,530 [INFO] main: DOGEUSDT | RL adj=80.0%
2026-05-27 04:24:50,488 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:24:51,328 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:24:51,330 [INFO] main: BILLUSDT | Bull:long(55%) Bear:short(80%)
2026-05-27 04:24:55,396 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:24:55,397 [INFO] main: BILLUSDT | Judge:HOLD conf=80% size=0.0%
2026-05-27 04:24:55,398 [INFO] main: BILLUSDT | RL adj=80.0%
2026-05-27 04:24:57,400 [INFO] main: Next scan in 120min (weekday-quiet)
2026-05-27 04:58:57,086 [INFO] positions: BREAKEVEN_STOP PEPEUSDT short PnL:0.43%
2026-05-27 04:58:57,089 [INFO] paper_trading: [PAPER] ✅ ЗАКРЫТА SHORT PEPEUSDT @ 0.0000 PnL: 2.13% (+0.43 USDT) | Баланс: 960.43
2026-05-27 04:58:57,386 [INFO] positions: OK PEPEUSDT short PnL:0.43% reason:breakeven_stop
2026-05-27 04:58:57,387 [INFO] positions: Lessons: The PEPEUSDT short trade resulted in a small profit of 0.43% due to a breakeven stop. The original reasoning for the trade was not explicitly stated as it was restored from a paper state. This trade can be considered a neutral outcome with minimal impact on overall performance.
2026-05-27 04:58:57,387 [INFO] rl: RL learned from short PEPEUSDT: profit 0.43% | weights bull=1.030 bear=0.929 judge=1.040 threshold=64.41
2026-05-27 05:18:51,580 [INFO] main: Symbols: 30
```

## Disk
```
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           382M  888K  381M   1% /run
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
Mem:           3.7Gi       768Mi       440Mi       4.8Mi       2.8Gi       3.0Gi
Swap:          2.0Gi       256Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
