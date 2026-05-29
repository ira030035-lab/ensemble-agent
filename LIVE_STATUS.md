# Live status

Generated: 2026-05-29 12:20:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      996988  0.1  3.2 719348 126132 ?       Ssl  May28   1:57 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
root      999913  0.0  1.2 133340 47464 ?        Ssl  May28   0:12 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root     1023517  6.4  1.0  55624 42176 ?        Ss   12:19   0:00 /opt/ensemble-agent/venv/bin/python3 /opt/metla/dashboard_api.py
```

## Paper state
```json
{
  "balance": 948.3398129629438,
  "positions": {
    "ETHUSDT": {
      "id": "PAPER_ETHUSDT_1779978101",
      "symbol": "ETHUSDT",
      "side": "short",
      "entry_price": 1993.68,
      "qty": 0.0502,
      "confidence": 75,
      "opened_at": "2026-05-28T14:21:41.194598",
      "cost": 20.0165472,
      "notional": 100.08273600000001,
      "leverage": 5
    },
    "TAOUSDT": {
      "id": "PAPER_TAOUSDT_1780044588",
      "symbol": "TAOUSDT",
      "side": "short",
      "entry_price": 257.64,
      "qty": 0.3881,
      "confidence": 80,
      "opened_at": "2026-05-29T08:49:48.347952",
      "cost": 19.9980168,
      "notional": 99.990084,
      "leverage": 5
    },
    "SUIUSDT": {
      "id": "PAPER_SUIUSDT_1780044712",
      "symbol": "SUIUSDT",
      "side": "short",
      "entry_price": 0.9226,
      "qty": 108.3893,
      "confidence": 85,
      "opened_at": "2026-05-29T08:51:52.564110",
      "cost": 19.999993636,
      "notional": 99.99996818,
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
    },
    {
      "id": "PAPER_RENDERUSDT_1779890875",
      "symbol": "RENDERUSDT",
      "side": "short",
      "entry_price": 2.242,
      "qty": 44.603,
      "confidence": 72,
      "opened_at": "2026-05-27T14:07:55.691992",
      "cost": 19.9999852,
      "notional": 99.999926,
      "leverage": 5,
      "exit_price": 2.171,
      "pnl_pct": 15.83,
      "pnl_usdt": 3.17,
      "closed_at": "2026-05-27T17:14:09.873662",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_LINKUSDT_1779855776",
      "symbol": "LINKUSDT",
      "side": "short",
      "entry_price": 9.35,
      "qty": 10.6952,
      "confidence": 72,
      "opened_at": "2026-05-27T04:22:56.413656",
      "cost": 20.000024,
      "notional": 100.00012,
      "leverage": 5,
      "exit_price": 9.061,
      "pnl_pct": 15.45,
      "pnl_usdt": 3.09,
      "closed_at": "2026-05-28T01:28:11.489436",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_XRPUSDT_1779903758",
      "symbol": "XRPUSDT",
      "side": "short",
      "entry_price": 1.3226,
      "qty": 75.6086,
      "confidence": 68,
      "opened_at": "2026-05-27T17:42:38.950713",
      "cost": 19.999986872,
      "notional": 99.99993436,
      "leverage": 5,
      "exit_price": 1.2959,
      "pnl_pct": 10.09,
      "pnl_usdt": 2.02,
      "closed_at": "2026-05-28T03:24:32.577475",
      "reason": "trailing_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_SUIUSDT_1779935246",
      "symbol": "SUIUSDT",
      "side": "short",
      "entry_price": 0.951,
      "qty": 105.1525,
      "confidence": 72,
      "opened_at": "2026-05-28T02:27:26.184971",
      "cost": 20.0000055,
      "notional": 100.0000275,
      "leverage": 5,
      "exit_price": 0.9219,
      "pnl_pct": 15.3,
      "pnl_usdt": 3.06,
      "closed_at": "2026-05-28T03:58:12.937999",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_BTCUSDT_1779897462",
      "symbol": "BTCUSDT",
      "side": "short",
      "entry_price": 75267.1,
      "qty": 0.0013,
      "confidence": 68,
      "opened_at": "2026-05-27T15:57:42.344776",
      "cost": 19.569446,
      "notional": 97.84723,
      "leverage": 5,
      "exit_price": 72939.5,
      "pnl_pct": 15.46,
      "pnl_usdt": 3.03,
      "closed_at": "2026-05-28T04:02:46.579255",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_HYPEUSDT_1779942884",
      "symbol": "HYPEUSDT",
      "side": "short",
      "entry_price": 57.098,
      "qty": 1.7514,
      "confidence": 68,
      "opened_at": "2026-05-28T04:34:44.346818",
      "cost": 20.00028744,
      "notional": 100.0014372,
      "leverage": 5,
      "exit_price": 58.284,
      "pnl_pct": -10.39,
      "pnl_usdt": -2.08,
      "closed_at": "2026-05-28T07:38:23.613313",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_TAOUSDT_1779942831",
      "symbol": "TAOUSDT",
      "side": "short",
      "entry_price": 257.4,
      "qty": 0.3885,
      "confidence": 76,
      "opened_at": "2026-05-28T04:33:51.378934",
      "cost": 19.99998,
      "notional": 99.9999,
      "leverage": 5,
      "exit_price": 262.56,
      "pnl_pct": -10.02,
      "pnl_usdt": -2.0,
      "closed_at": "2026-05-28T09:25:36.434966",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_HYPEUSDT_1779961383",
      "symbol": "HYPEUSDT",
      "side": "short",
      "entry_price": 57.349,
      "qty": 1.7437,
      "confidence": 85,
      "opened_at": "2026-05-28T09:43:03.412095",
      "cost": 19.999890259999997,
      "notional": 99.99945129999999,
      "leverage": 5,
      "exit_price": 57.065,
      "pnl_pct": 2.48,
      "pnl_usdt": 0.5,
      "closed_at": "2026-05-28T12:45:27.361720",
      "reason": "breakeven_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_TRUMPUSDT_1779953933",
      "symbol": "TRUMPUSDT",
      "side": "short",
      "entry_price": 1.885,
      "qty": 53.0504,
      "confidence": 72,
      "opened_at": "2026-05-28T07:38:53.513650",
      "cost": 20.000000800000002,
      "notional": 100.000004,
      "leverage": 5,
      "exit_price": 1.876,
      "pnl_pct": 2.39,
      "pnl_usdt": 0.48,
      "closed_at": "2026-05-28T13:01:47.611023",
      "reason": "breakeven_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_TAOUSDT_1779973828",
      "symbol": "TAOUSDT",
      "side": "short",
      "entry_price": 258.92,
      "qty": 0.3862,
      "confidence": 85,
      "opened_at": "2026-05-28T13:10:28.351608",
      "cost": 19.998980800000002,
      "notional": 99.994904,
      "leverage": 5,
      "exit_price": 257.67,
      "pnl_pct": 2.41,
      "pnl_usdt": 0.48,
      "closed_at": "2026-05-28T14:14:48.506797",
      "reason": "breakeven_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_XRPUSDT_1779942822",
      "symbol": "XRPUSDT",
      "side": "short",
      "entry_price": 1.2763,
      "qty": 78.3515,
      "confidence": 76,
      "opened_at": "2026-05-28T04:33:42.931172",
      "cost": 20.00000389,
      "notional": 100.00001945,
      "leverage": 5,
      "exit_price": 1.3034,
      "pnl_pct": -10.62,
      "pnl_usdt": -2.12,
      "closed_at": "2026-05-28T14:17:21.882304",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_TRUMPUSDT_1779973736",
      "symbol": "TRUMPUSDT",
      "side": "short",
      "entry_price": 1.866,
      "qty": 53.5906,
      "confidence": 85,
      "opened_at": "2026-05-28T13:08:56.593539",
      "cost": 20.000011920000002,
      "notional": 100.00005960000001,
      "leverage": 5,
      "exit_price": 1.858,
      "pnl_pct": 2.14,
      "pnl_usdt": 0.43,
      "closed_at": "2026-05-28T14:18:53.365419",
      "reason": "breakeven_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_ADAUSDT_1779978240",
      "symbol": "ADAUSDT",
      "side": "short",
      "entry_price": 0.2323,
      "qty": 430.4778,
      "confidence": 85,
      "opened_at": "2026-05-28T14:24:00.849362",
      "cost": 19.999998588,
      "notional": 99.99999294,
      "leverage": 5,
      "exit_price": 0.2371,
      "pnl_pct": -10.33,
      "pnl_usdt": -2.07,
      "closed_at": "2026-05-28T18:13:11.807931",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_TONUSDT_1780007297",
      "symbol": "TONUSDT",
      "side": "short",
      "entry_price": 1.7614,
      "qty": 56.773,
      "confidence": 85,
      "opened_at": "2026-05-28T22:28:17.444503",
      "cost": 19.999992440000003,
      "notional": 99.99996220000001,
      "leverage": 5,
      "exit_price": 1.7979,
      "pnl_pct": -10.36,
      "pnl_usdt": -2.07,
      "closed_at": "2026-05-29T07:10:35.224172",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_XRPUSDT_1779995291",
      "symbol": "XRPUSDT",
      "side": "short",
      "entry_price": 1.3288,
      "qty": 75.2559,
      "confidence": 75,
      "opened_at": "2026-05-28T19:08:11.858357",
      "cost": 20.000007984,
      "notional": 100.00003991999999,
      "leverage": 5,
      "exit_price": 1.3222,
      "pnl_pct": 2.48,
      "pnl_usdt": 0.5,
      "closed_at": "2026-05-29T08:28:11.943930",
      "reason": "breakeven_stop",
      "outcome": "profit"
    }
  ],
  "total_pnl": 8.354370598943827
}
```

## Ensemble log (last 30 lines)
```
2026-05-29 12:19:18,767 [INFO] main: UBUSDT | regime BLOCK (volatile)
2026-05-29 12:19:24,913 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-29 12:19:25,718 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-29 12:19:25,719 [INFO] main: ZECUSDT | Bull:flat(15%) Bear:short(70%)
2026-05-29 12:19:28,214 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-29 12:19:28,215 [INFO] main: ZECUSDT | Judge:SHORT conf=85% size=15.0%
2026-05-29 12:19:28,215 [INFO] main: ZECUSDT | RL adj=95.0%
2026-05-29 12:19:28,225 [INFO] main: ZECUSDT | Context score=-0.06 bias=0.05
2026-05-29 12:19:28,226 [INFO] main: ZECUSDT | gate PASS (Judge 85/70 RL 95.0/64.39 slack=±3)
2026-05-29 12:19:28,226 [INFO] positions: Same-side cap: skip SHORT ZECUSDT (3/3 already short)
2026-05-29 12:19:34,203 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-29 12:19:35,754 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-29 12:19:35,755 [INFO] main: BILLUSDT | Bull:flat(25%) Bear:flat(40%)
2026-05-29 12:19:38,324 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-29 12:19:38,325 [INFO] main: BILLUSDT | Judge:HOLD conf=60% size=0.0%
2026-05-29 12:19:38,325 [INFO] main: BILLUSDT | RL adj=60.0%
2026-05-29 12:19:45,736 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-29 12:19:46,397 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-29 12:19:46,399 [INFO] main: BTCUSDT | Bull:flat(15%) Bear:short(75%)
2026-05-29 12:19:48,547 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-29 12:19:48,549 [INFO] main: BTCUSDT | Judge:HOLD conf=50% size=0.0%
2026-05-29 12:19:48,549 [INFO] main: BTCUSDT | RL adj=50.0%
2026-05-29 12:19:54,351 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-29 12:19:55,058 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-29 12:19:55,060 [INFO] main: NEARUSDT | Bull:flat(15%) Bear:short(70%)
2026-05-29 12:19:57,354 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-29 12:19:57,356 [INFO] main: NEARUSDT | Judge:SHORT conf=70% size=15.0%
2026-05-29 12:19:57,356 [INFO] main: NEARUSDT | RL adj=80.0%
2026-05-29 12:19:57,365 [INFO] main: NEARUSDT | Context score=-0.06 bias=0.05
2026-05-29 12:19:57,366 [INFO] main: NEARUSDT | regime BLOCK (short × trending_up × rsi1h=51.0; counter-trend guard)
```

## Disk
```
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           382M  912K  381M   1% /run
efivarfs        256K   39K  213K  16% /sys/firmware/efi/efivars
/dev/sda1        75G  8.5G   64G  12% /
tmpfs           1.9G     0  1.9G   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda15      253M  146K  252M   1% /boot/efi
tmpfs           382M   12K  382M   1% /run/user/0
```

## Memory
```
               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       1.1Gi       167Mi       4.8Mi       2.8Gi       2.7Gi
Swap:          2.0Gi       256Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
