# Live status

Generated: 2026-05-27 10:10:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      966808  0.0  1.1 131496 45740 ?        Ssl  May26   0:07 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root      977418  0.1  3.4 729172 134668 ?       Ssl  04:18   0:21 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
```

## Paper state
```json
{
  "balance": 961.5366639093924,
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
2026-05-27 09:41:58,680 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 09:42:00,371 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 09:42:00,373 [INFO] main: ESPORTSUSDT | Bull:long(60%) Bear:short(80%)
2026-05-27 09:42:05,053 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 09:42:05,054 [INFO] main: ESPORTSUSDT | Judge:HOLD conf=72% size=0.0%
2026-05-27 09:42:05,055 [INFO] main: ESPORTSUSDT | RL adj=72.0%
2026-05-27 09:42:12,457 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 09:42:13,748 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 09:42:13,750 [INFO] main: SUIUSDT | Bull:long(70%) Bear:short(75%)
2026-05-27 09:42:18,478 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 09:42:18,480 [INFO] main: SUIUSDT | Judge:HOLD conf=75% size=0.0%
2026-05-27 09:42:18,480 [INFO] main: SUIUSDT | RL adj=75.0%
2026-05-27 09:42:26,683 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 09:42:30,173 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 09:42:30,175 [INFO] main: XRPUSDT | Bull:long(60%) Bear:short(50%)
2026-05-27 09:42:35,801 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 09:42:35,802 [INFO] main: XRPUSDT | Judge:HOLD conf=60% size=0.0%
2026-05-27 09:42:35,802 [INFO] main: XRPUSDT | RL adj=60.0%
2026-05-27 09:42:43,983 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 09:42:47,875 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 09:42:47,877 [INFO] main: RENDERUSDT | Bull:long(75%) Bear:short(75%)
2026-05-27 09:42:52,291 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 09:42:52,293 [INFO] main: RENDERUSDT | Judge:HOLD conf=75% size=0.0%
2026-05-27 09:42:52,293 [INFO] main: RENDERUSDT | RL adj=75.0%
2026-05-27 09:42:54,295 [INFO] main: Next scan in 60min (weekday-active)
2026-05-27 10:01:19,768 [INFO] positions: TAKE-PROFIT ONDOUSDT short PnL:3.14%
2026-05-27 10:01:19,770 [INFO] paper_trading: [PAPER] ✅ ЗАКРЫТА SHORT ONDOUSDT @ 0.3976 PnL: 15.71% (+3.14 USDT) | Баланс: 961.54
2026-05-27 10:01:20,220 [INFO] positions: OK ONDOUSDT short PnL:3.14% reason:take_profit
2026-05-27 10:01:20,220 [INFO] positions: Lessons: A strong bearish conviction does not guarantee profit, as seen in the past similar trade HYPEUSDT short that resulted in a loss despite 72% judge confidence. Conservative position sizing, such as the 0.06 size used in this trade, can help mitigate potential losses. The combination of confluent bearish signals and a trending_down regime can still yield profitable trades, as demonstrated by the 3.14% gain in this ONDOUSDT short.
2026-05-27 10:01:20,220 [INFO] rl: RL learned from short ONDOUSDT: profit 3.14% | weights bull=1.024 bear=0.933 judge=1.043 threshold=64.43
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
Mem:           3.7Gi       783Mi       324Mi       4.8Mi       2.9Gi       3.0Gi
Swap:          2.0Gi       256Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
