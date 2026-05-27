# Live status

Generated: 2026-05-27 12:30:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      983538  0.0  1.1 130844 45116 ?        Ssl  12:06   0:01 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root      983708  0.8  3.1 685776 123684 ?       Ssl  12:20   0:04 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
```

## Paper state
```json
{
  "balance": 941.5366500693924,
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
    },
    "TONUSDT": {
      "id": "PAPER_TONUSDT_1779878581",
      "symbol": "TONUSDT",
      "side": "short",
      "entry_price": 1.8936,
      "qty": 52.8095,
      "confidence": 72,
      "opened_at": "2026-05-27T10:43:01.437431",
      "cost": 20.00001384,
      "notional": 100.0000692,
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
    }
  ],
  "total_pnl": 1.5363632693924822
}
```

## Ensemble log (last 30 lines)
```
2026-05-27 12:24:59,369 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 12:24:59,370 [INFO] main: XRPUSDT | Bull:flat(25%) Bear:short(75%)
2026-05-27 12:25:03,746 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 12:25:03,748 [INFO] main: XRPUSDT | Judge:SHORT conf=72% size=6.0%
2026-05-27 12:25:03,748 [INFO] main: XRPUSDT | RL adj=82.5%
2026-05-27 12:25:03,751 [INFO] main: XRPUSDT | Context score=-0.14 bias=0.12
2026-05-27 12:25:03,752 [INFO] main: XRPUSDT | regime BLOCK (short × trending_down × rsi1h=56.1; late-entry guard)
2026-05-27 12:25:09,907 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 12:25:10,597 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 12:25:10,598 [INFO] main: BILLUSDT | Bull:flat(15%) Bear:short(80%)
2026-05-27 12:25:14,832 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 12:25:14,833 [INFO] main: BILLUSDT | Judge:SHORT conf=72% size=6.0%
2026-05-27 12:25:14,833 [INFO] main: BILLUSDT | RL adj=83.2%
2026-05-27 12:25:14,835 [INFO] main: BILLUSDT | Context score=-0.13 bias=0.12
2026-05-27 12:25:14,835 [INFO] main: BILLUSDT | regime BLOCK (volatile)
2026-05-27 12:25:20,848 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 12:25:21,392 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 12:25:21,394 [INFO] main: SKYAIUSDT | Bull:flat(15%) Bear:short(75%)
2026-05-27 12:25:25,625 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 12:25:25,626 [INFO] main: SKYAIUSDT | Judge:SHORT conf=68% size=6.0%
2026-05-27 12:25:25,626 [INFO] main: SKYAIUSDT | RL adj=78.5%
2026-05-27 12:25:25,628 [INFO] main: SKYAIUSDT | Context score=-0.13 bias=0.12
2026-05-27 12:25:25,628 [INFO] main: SKYAIUSDT | regime BLOCK (volatile)
2026-05-27 12:25:32,967 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 12:25:33,012 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 12:25:33,013 [INFO] main: FILUSDT | Bull:long(68%) Bear:short(70%)
2026-05-27 12:25:38,225 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 12:25:38,227 [INFO] main: FILUSDT | Judge:HOLD conf=70% size=0.0%
2026-05-27 12:25:38,227 [INFO] main: FILUSDT | RL adj=70.0%
2026-05-27 12:25:40,229 [INFO] main: Next scan in 30min (weekday-active)
```

## Disk
```
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           382M  904K  381M   1% /run
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
Mem:           3.7Gi       978Mi       165Mi       4.8Mi       2.9Gi       2.8Gi
Swap:          2.0Gi       256Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
