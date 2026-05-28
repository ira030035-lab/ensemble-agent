# Live status

Generated: 2026-05-28 14:20:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      996988  0.1  3.1 718324 124328 ?       Ssl  07:37   0:30 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
root      999913  0.0  1.2 133048 47548 ?        Ssl  10:43   0:04 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root     1001083  0.0  1.1  55884 43648 ?        Ss   11:50   0:03 /opt/ensemble-agent/venv/bin/python3 /opt/metla/dashboard_api.py
```

## Paper state
```json
{
  "balance": 1011.9961895989438,
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
    }
  ],
  "total_pnl": 11.99618959894383
}
```

## Ensemble log (last 30 lines)
```
2026-05-28 13:50:23,119 [INFO] main: WLDUSDT | Bull:flat(15%) Bear:short(60%)
2026-05-28 13:50:26,247 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-28 13:50:26,247 [INFO] main: WLDUSDT | Judge:LONG conf=76% size=15.0%
2026-05-28 13:50:26,248 [INFO] main: WLDUSDT | RL adj=67.4%
2026-05-28 13:50:26,255 [INFO] main: WLDUSDT | Context score=-0.01 bias=0.1
2026-05-28 13:50:26,255 [INFO] main: WLDUSDT | regime BLOCK (volatile)
2026-05-28 13:50:34,424 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-28 13:50:34,887 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-28 13:50:34,889 [INFO] main: ENAUSDT | Bull:flat(5%) Bear:short(80%)
2026-05-28 13:50:37,458 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-28 13:50:37,459 [INFO] main: ENAUSDT | Judge:SHORT conf=80% size=15.0%
2026-05-28 13:50:37,460 [INFO] main: ENAUSDT | RL adj=91.5%
2026-05-28 13:50:37,467 [INFO] main: ENAUSDT | Context score=-0.11 bias=0.1
2026-05-28 13:50:37,467 [INFO] main: ENAUSDT | regime BLOCK (volatile)
2026-05-28 13:50:39,470 [INFO] main: Next scan in 30min (weekday-active)
2026-05-28 14:14:48,506 [INFO] positions: BREAKEVEN_STOP TAOUSDT short PnL:0.48%
2026-05-28 14:14:48,509 [INFO] paper_trading: [PAPER] ✅ ЗАКРЫТА SHORT TAOUSDT @ 257.6700 PnL: 2.41% (+0.48 USDT) | Баланс: 973.69
2026-05-28 14:14:48,848 [INFO] positions: OK TAOUSDT short PnL:0.48% reason:breakeven_stop
2026-05-28 14:14:48,849 [INFO] positions: Lessons: The trade was a breakeven outcome with a 0.48% profit, meeting the minimum expectation. The initial bearish conviction and expected downside were not fully realized, but the trade was managed to limit losses. The asymmetry framework's rules and strong bearish signals were not enough to generate significant profits in this instance.
2026-05-28 14:14:48,849 [INFO] rl: RL learned from short TAOUSDT: profit 0.48% | weights bull=0.986 bear=0.960 judge=1.053 threshold=64.3
2026-05-28 14:17:21,881 [INFO] positions: STOP_LOSS XRPUSDT short PnL:-2.12%
2026-05-28 14:17:21,885 [INFO] paper_trading: [PAPER] ❌ ЗАКРЫТА SHORT XRPUSDT @ 1.3034 PnL: -10.62% (-2.12 USDT) | Баланс: 991.57
2026-05-28 14:17:22,211 [INFO] positions: LOSS XRPUSDT short PnL:-2.12% reason:stop_loss
2026-05-28 14:17:22,211 [INFO] positions: Lessons: High conviction short trades in trending_down regimes with deeply oversold RSI can still result in losses if volume support is lacking. Conservative sizing is crucial in such setups to limit potential losses. The absence of volume support and continuation of bearish technicals can weaken a reversal thesis and lead to stop loss outcomes.
2026-05-28 14:17:22,212 [INFO] rl: RL learned from short XRPUSDT: loss -2.12% | weights bull=0.990 bear=0.956 judge=1.054 threshold=64.35
2026-05-28 14:18:53,365 [INFO] positions: BREAKEVEN_STOP TRUMPUSDT short PnL:0.43%
2026-05-28 14:18:53,367 [INFO] paper_trading: [PAPER] ✅ ЗАКРЫТА SHORT TRUMPUSDT @ 1.8580 PnL: 2.14% (+0.43 USDT) | Баланс: 1012.00
2026-05-28 14:18:54,211 [INFO] positions: OK TRUMPUSDT short PnL:0.43% reason:breakeven_stop
2026-05-28 14:18:54,211 [INFO] positions: Lessons: The trade was closed at breakeven due to a stop loss, resulting in a 0.43% profit. The initial reasoning was based on high bear conviction and a trending_down regime, which aligned with the potential for a downside move. The outcome suggests that the trade management was effective in limiting losses and securing a small gain.
2026-05-28 14:18:54,211 [INFO] rl: RL learned from short TRUMPUSDT: profit 0.43% | weights bull=0.989 bear=0.957 judge=1.054 threshold=64.32
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
Mem:           3.7Gi       824Mi       459Mi       4.8Mi       2.8Gi       2.9Gi
Swap:          2.0Gi       256Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
