# Live status

Generated: 2026-05-27 04:20:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      966808  0.0  1.1 131496 45740 ?        Ssl  May26   0:06 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root      977418  2.5  2.8 559124 111304 ?       Ssl  04:18   0:01 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
```

## Paper state
```json
{
  "balance": 960.0004805000125,
  "positions": {
    "PEPEUSDT": {
      "id": "PAPER_PEPEUSDT_1779855184",
      "symbol": "PEPEUSDT",
      "side": "short",
      "entry_price": 3.5176e-06,
      "qty": 28428473.9595,
      "confidence": 72,
      "opened_at": "2026-05-27T04:13:04.351442",
      "cost": 19.99999999998744,
      "notional": 99.9999999999372,
      "leverage": 5
    },
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
    }
  },
  "trade_history": [],
  "total_pnl": 0.0
}
```

## Ensemble log (last 30 lines)
```
2026-05-27 04:19:08,658 [INFO] main: NEARUSDT | RL adj=72.0%
2026-05-27 04:19:17,555 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:19:17,557 [INFO] main: HYPEUSDT | Bull:long(50%) Bear:short(78%)
2026-05-27 04:19:21,313 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:19:21,314 [INFO] main: HYPEUSDT | Judge:SHORT conf=72% size=8.0%
2026-05-27 04:19:21,314 [INFO] main: HYPEUSDT | RL adj=75.1%
2026-05-27 04:19:21,314 [INFO] main: HYPEUSDT | Context score=-0.12
2026-05-27 04:19:21,602 [INFO] main: HYPEUSDT | gate PASS (Judge 72/70 RL 75.1/64.43 slack=±3)
2026-05-27 04:19:21,880 [INFO] positions: [PAPER] Opening SHORT HYPEUSDT notional=$100.0 conf=72%
2026-05-27 04:19:21,882 [INFO] paper_trading: [PAPER] ОТКРЫТА SHORT HYPEUSDT @ 59.7750 qty=1.6729 notional=100.00 margin=20.00 x5 | Баланс: 960.00
2026-05-27 04:19:32,166 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:19:32,167 [INFO] main: WLDUSDT | Bull:long(65%) Bear:short(82%)
2026-05-27 04:19:36,501 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:19:36,502 [INFO] main: WLDUSDT | Judge:HOLD conf=82% size=0.0%
2026-05-27 04:19:36,502 [INFO] main: WLDUSDT | RL adj=82.0%
2026-05-27 04:19:42,727 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:19:43,075 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:19:43,077 [INFO] main: ADAUSDT | Bull:long(60%) Bear:short(90%)
2026-05-27 04:19:46,346 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:19:46,347 [INFO] main: ADAUSDT | Judge:SHORT conf=72% size=8.0%
2026-05-27 04:19:46,348 [INFO] main: ADAUSDT | RL adj=75.3%
2026-05-27 04:19:46,348 [INFO] main: ADAUSDT | Context score=-0.11
2026-05-27 04:19:46,348 [INFO] main: ADAUSDT | gate PASS (Judge 72/70 RL 75.3/64.43 slack=±3)
2026-05-27 04:19:46,349 [INFO] positions: Correlation block: skip SHORT ADAUSDT (corr 0.97 >= 0.85 with PEPEUSDT short)
2026-05-27 04:19:53,463 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:19:53,920 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:19:53,922 [INFO] main: TONUSDT | Bull:long(60%) Bear:short(80%)
2026-05-27 04:19:58,707 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:19:58,709 [INFO] main: TONUSDT | Judge:HOLD conf=80% size=0.0%
2026-05-27 04:19:58,709 [INFO] main: TONUSDT | RL adj=80.0%
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
Mem:           3.7Gi       923Mi       222Mi       4.8Mi       2.9Gi       2.8Gi
Swap:          2.0Gi       256Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
