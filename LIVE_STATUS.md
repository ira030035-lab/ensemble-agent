# Live status

Generated: 2026-05-28 04:20:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      983538  0.0  1.1 131968 45880 ?        Ssl  May27   0:04 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root      983708  0.1  3.2 721860 128196 ?       Ssl  May27   1:26 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
```

## Paper state
```json
{
  "balance": 1016.3171964489437,
  "positions": {},
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
    }
  ],
  "total_pnl": 16.31719644894383
}
```

## Ensemble log (last 30 lines)
```
2026-05-28 02:33:08,954 [INFO] main: BILLUSDT | Judge:SHORT conf=68% size=6.0%
2026-05-28 02:33:08,954 [INFO] main: BILLUSDT | RL adj=69.3%
2026-05-28 02:33:08,960 [INFO] main: BILLUSDT | Context score=-0.12 bias=0.1
2026-05-28 02:33:08,960 [INFO] main: BILLUSDT | regime BLOCK (volatile)
2026-05-28 02:33:15,714 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-28 02:33:27,559 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-28 02:33:27,561 [INFO] main: DOGEUSDT | Bull:flat(15%) Bear:short(60%)
2026-05-28 02:33:32,051 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-28 02:33:32,052 [INFO] main: DOGEUSDT | Judge:SHORT conf=68% size=6.0%
2026-05-28 02:33:32,052 [INFO] main: DOGEUSDT | RL adj=76.5%
2026-05-28 02:33:32,056 [INFO] main: DOGEUSDT | Context score=-0.11 bias=0.1
2026-05-28 02:33:32,057 [INFO] main: DOGEUSDT | gate PASS (Judge 68/70 RL 76.5/64.38 slack=±3)
2026-05-28 02:33:32,057 [INFO] positions: Same-side cap: skip SHORT DOGEUSDT (3/3 already short)
2026-05-28 02:33:34,060 [INFO] main: Next scan in 120min (weekday-quiet)
2026-05-28 03:20:26,978 [INFO] main: Symbols: 30
2026-05-28 03:24:32,576 [INFO] positions: TRAILING-STOP XRPUSDT short peak:2.88% now:2.02%
2026-05-28 03:24:32,580 [INFO] paper_trading: [PAPER] ✅ ЗАКРЫТА SHORT XRPUSDT @ 1.2959 PnL: 10.09% (+2.02 USDT) | Баланс: 970.66
2026-05-28 03:24:32,961 [INFO] positions: OK XRPUSDT short PnL:2.02% reason:trailing_stop
2026-05-28 03:24:32,962 [INFO] positions: Lessons: The trade was successful with a 2.02% profit, validating the original bearish bias and analysis of confluent bearish signals. The ranging regime limited downside but did not negate the directional bias, and conservative position sizing was key to managing risk in low-volume conditions. This setup serves as a reminder to respect low-volume ranging conditions and the potential for false breakdowns, highlighting the importance of disciplined position sizing.
2026-05-28 03:24:32,962 [INFO] rl: RL learned from short XRPUSDT: profit 2.02% | weights bull=0.999 bear=0.953 judge=1.048 threshold=64.35
2026-05-28 03:58:12,937 [INFO] positions: TAKE-PROFIT SUIUSDT short PnL:3.06%
2026-05-28 03:58:12,940 [INFO] paper_trading: [PAPER] ✅ ЗАКРЫТА SHORT SUIUSDT @ 0.9219 PnL: 15.30% (+3.06 USDT) | Баланс: 993.72
2026-05-28 03:58:13,347 [INFO] positions: OK SUIUSDT short PnL:3.06% reason:take_profit
2026-05-28 03:58:13,348 [INFO] positions: Lessons: A strong bearish setup with high conviction and confluent signals can still yield modest gains with disciplined position sizing. The combination of a trending_down regime, low volume, and oversold RSI within a downtrend context proved sufficient to overcome bullish counter-signals. Conservative sizing at 0.06 allowed for a 3.06% gain, consistent with prior lessons that similar setups can yield 0.5-3.2% gains with proper risk management.
2026-05-28 03:58:13,348 [INFO] rl: RL learned from short SUIUSDT: profit 3.06% | weights bull=0.989 bear=0.960 judge=1.051 threshold=64.32
2026-05-28 04:02:46,578 [INFO] positions: TAKE-PROFIT BTCUSDT short PnL:3.09%
2026-05-28 04:02:46,581 [INFO] paper_trading: [PAPER] ✅ ЗАКРЫТА SHORT BTCUSDT @ 72939.5000 PnL: 15.46% (+3.03 USDT) | Баланс: 1016.32
2026-05-28 04:02:46,896 [INFO] positions: OK BTCUSDT short PnL:3.09% reason:take_profit
2026-05-28 04:02:46,896 [INFO] positions: Lessons: The trade was successful with a 3.09% profit, validating the bearish conviction and analysis of oversold conditions, supply dominance, and weak buying. The trending_down regime and oversold RSI proved to be a profitable short setup despite the MACD bullish counterpoint. Conservative sizing helped manage the risk of potential false reversals or brief bounces before the trend continuation.
2026-05-28 04:02:46,896 [INFO] rl: RL learned from short BTCUSDT: profit 3.09% | weights bull=0.982 bear=0.966 judge=1.052 threshold=64.29
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
Mem:           3.7Gi       788Mi       330Mi       4.8Mi       2.9Gi       3.0Gi
Swap:          2.0Gi       256Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
