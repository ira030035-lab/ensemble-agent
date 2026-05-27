# Live status

Generated: 2026-05-27 08:50:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      966808  0.0  1.1 131496 45740 ?        Ssl  May26   0:07 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root      977418  0.1  3.3 724548 129728 ?       Ssl  04:18   0:16 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
```

## Paper state
```json
{
  "balance": 938.3941509093924,
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
    },
    "ONDOUSDT": {
      "id": "PAPER_ONDOUSDT_1779863392",
      "symbol": "ONDOUSDT",
      "side": "short",
      "entry_price": 0.4105,
      "qty": 243.6054,
      "confidence": 72,
      "opened_at": "2026-05-27T06:29:52.857604",
      "cost": 20.00000334,
      "notional": 100.00001669999999,
      "leverage": 5
    },
    "HYPEUSDT": {
      "id": "PAPER_HYPEUSDT_1779870952",
      "symbol": "HYPEUSDT",
      "side": "short",
      "entry_price": 62.219,
      "qty": 1.6072,
      "confidence": 68,
      "opened_at": "2026-05-27T08:35:52.416653",
      "cost": 19.99967536,
      "notional": 99.9983768,
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
    }
  ],
  "total_pnl": -1.6061463906075097
}
```

## Ensemble log (last 30 lines)
```
2026-05-27 08:35:02,275 [INFO] main: SUIUSDT | RL adj=64.0%
2026-05-27 08:35:02,275 [INFO] main: SUIUSDT | Context score=-0.12
2026-05-27 08:35:11,288 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 08:35:14,331 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 08:35:14,332 [INFO] main: WLDUSDT | Bull:long(60%) Bear:short(75%)
2026-05-27 08:35:19,251 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 08:35:19,252 [INFO] main: WLDUSDT | Judge:HOLD conf=75% size=0.0%
2026-05-27 08:35:19,252 [INFO] main: WLDUSDT | RL adj=75.0%
2026-05-27 08:35:27,321 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 08:35:30,157 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 08:35:30,158 [INFO] main: ESPORTSUSDT | Bull:long(70%) Bear:short(80%)
2026-05-27 08:35:34,500 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 08:35:34,502 [INFO] main: ESPORTSUSDT | Judge:HOLD conf=75% size=0.0%
2026-05-27 08:35:34,502 [INFO] main: ESPORTSUSDT | RL adj=75.0%
2026-05-27 08:35:46,867 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 08:35:46,868 [INFO] main: HYPEUSDT | Bull:long(55%) Bear:short(68%)
2026-05-27 08:35:51,777 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 08:35:51,778 [INFO] main: HYPEUSDT | Judge:SHORT conf=68% size=8.0%
2026-05-27 08:35:51,778 [INFO] main: HYPEUSDT | RL adj=68.9%
2026-05-27 08:35:51,778 [INFO] main: HYPEUSDT | Context score=-0.12
2026-05-27 08:35:51,778 [INFO] main: HYPEUSDT | gate PASS (Judge 68/70 RL 68.9/64.46 slack=±3)
2026-05-27 08:35:52,416 [INFO] positions: [PAPER] Opening SHORT HYPEUSDT notional=$100.0 conf=68%
2026-05-27 08:35:52,418 [INFO] paper_trading: [PAPER] ОТКРЫТА SHORT HYPEUSDT @ 62.2190 qty=1.6072 notional=100.00 margin=20.00 x5 | Баланс: 938.39
2026-05-27 08:36:01,526 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 08:36:04,565 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 08:36:04,566 [INFO] main: VIRTUALUSDT | Bull:long(70%) Bear:short(75%)
2026-05-27 08:36:10,108 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 08:36:10,110 [INFO] main: VIRTUALUSDT | Judge:HOLD conf=72% size=0.0%
2026-05-27 08:36:10,110 [INFO] main: VIRTUALUSDT | RL adj=72.0%
2026-05-27 08:36:12,113 [INFO] main: Next scan in 60min (weekday-active)
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
Mem:           3.7Gi       777Mi       332Mi       4.8Mi       2.9Gi       3.0Gi
Swap:          2.0Gi       256Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
