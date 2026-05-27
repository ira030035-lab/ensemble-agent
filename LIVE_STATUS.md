# Live status

Generated: 2026-05-27 17:00:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      983538  0.0  1.1 130976 45552 ?        Ssl  12:06   0:03 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root      983708  0.2  3.2 721860 127444 ?       Ssl  12:20   0:36 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
```

## Paper state
```json
{
  "balance": 942.3854480789438,
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
    "RENDERUSDT": {
      "id": "PAPER_RENDERUSDT_1779890875",
      "symbol": "RENDERUSDT",
      "side": "short",
      "entry_price": 2.242,
      "qty": 44.603,
      "confidence": 72,
      "opened_at": "2026-05-27T14:07:55.691992",
      "cost": 19.9999852,
      "notional": 99.999926,
      "leverage": 5
    },
    "BTCUSDT": {
      "id": "PAPER_BTCUSDT_1779897462",
      "symbol": "BTCUSDT",
      "side": "short",
      "entry_price": 75267.1,
      "qty": 0.0013,
      "confidence": 68,
      "opened_at": "2026-05-27T15:57:42.344776",
      "cost": 19.569446,
      "notional": 97.84723,
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
    },
    {
      "id": "PAPER_PEPEUSDT_1779890846",
      "symbol": "PEPEUSDT",
      "side": "short",
      "entry_price": 3.5241e-06,
      "qty": 28376039.2724,
      "confidence": 68,
      "opened_at": "2026-05-27T14:07:26.484925",
      "cost": 19.999999999972964,
      "notional": 99.99999999986483,
      "leverage": 5,
      "exit_price": 3.5977e-06,
      "pnl_pct": -10.44,
      "pnl_usdt": -2.09,
      "closed_at": "2026-05-27T15:31:16.865245",
      "reason": "stop_loss",
      "outcome": "loss"
    }
  ],
  "total_pnl": 1.9549032789438296
}
```

## Ensemble log (last 30 lines)
```
2026-05-27 16:35:35,135 [INFO] main: BILLUSDT | Bull:flat(25%) Bear:short(70%)
2026-05-27 16:35:39,613 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 16:35:39,613 [INFO] main: BILLUSDT | Judge:SHORT conf=68% size=6.0%
2026-05-27 16:35:39,613 [INFO] main: BILLUSDT | RL adj=77.8%
2026-05-27 16:35:39,615 [INFO] main: BILLUSDT | Context score=-0.12 bias=0.1
2026-05-27 16:35:39,615 [INFO] main: BILLUSDT | regime BLOCK (volatile)
2026-05-27 16:35:46,182 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 16:35:50,297 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 16:35:50,298 [INFO] main: SOLUSDT | Bull:flat(35%) Bear:short(70%)
2026-05-27 16:35:54,681 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 16:35:54,682 [INFO] main: SOLUSDT | Judge:SHORT conf=62% size=5.0%
2026-05-27 16:35:54,682 [INFO] main: SOLUSDT | RL adj=71.8%
2026-05-27 16:35:54,687 [INFO] main: SOLUSDT | Context score=-0.11 bias=0.1
2026-05-27 16:35:59,988 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 16:36:01,824 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 16:36:01,826 [INFO] main: BEATUSDT | Bull:flat(25%) Bear:short(75%)
2026-05-27 16:36:07,439 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 16:36:07,440 [INFO] main: BEATUSDT | Judge:SHORT conf=72% size=6.0%
2026-05-27 16:36:07,440 [INFO] main: BEATUSDT | RL adj=82.5%
2026-05-27 16:36:07,445 [INFO] main: BEATUSDT | Context score=-0.11 bias=0.1
2026-05-27 16:36:07,445 [INFO] main: BEATUSDT | regime BLOCK (volatile)
2026-05-27 16:36:12,982 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 16:36:14,592 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 16:36:14,594 [INFO] main: WLDUSDT | Bull:flat(15%) Bear:short(70%)
2026-05-27 16:36:20,265 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 16:36:20,267 [INFO] main: WLDUSDT | Judge:SHORT conf=68% size=6.0%
2026-05-27 16:36:20,267 [INFO] main: WLDUSDT | RL adj=77.8%
2026-05-27 16:36:20,271 [INFO] main: WLDUSDT | Context score=-0.11 bias=0.1
2026-05-27 16:36:20,271 [INFO] main: WLDUSDT | regime BLOCK (volatile)
2026-05-27 16:36:22,274 [INFO] main: Next scan in 30min (weekday-active)
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
Mem:           3.7Gi       796Mi       344Mi       4.8Mi       2.9Gi       2.9Gi
Swap:          2.0Gi       256Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
