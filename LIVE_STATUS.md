# Live status

Generated: 2026-05-30 20:30:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      999913  0.0  1.2 133404 48140 ?        Ssl  May28   0:22 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root     1046809  0.1  3.1 716516 122864 ?       Ssl  16:36   0:25 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
root     1046995  0.0  1.0  56068 42912 ?        Ss   16:53   0:02 /opt/ensemble-agent/venv/bin/python3 /opt/metla/dashboard_api.py
```

## Paper state
```json
{
  "balance": 963.6079719289435,
  "positions": {
    "SUIUSDT": {
      "id": "PAPER_SUIUSDT_1780156745",
      "symbol": "SUIUSDT",
      "side": "short",
      "entry_price": 0.9096,
      "qty": 109.9384,
      "confidence": 85,
      "opened_at": "2026-05-30T15:59:05.068308",
      "cost": 19.999993728,
      "notional": 99.99996863999999,
      "leverage": 5
    },
    "TAOUSDT": {
      "id": "PAPER_TAOUSDT_1780167442",
      "symbol": "TAOUSDT",
      "side": "short",
      "entry_price": 254.1,
      "qty": 0.3935,
      "confidence": 75,
      "opened_at": "2026-05-30T18:57:22.393102",
      "cost": 19.99767,
      "notional": 99.98835,
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
    },
    {
      "id": "PAPER_TAOUSDT_1780044588",
      "symbol": "TAOUSDT",
      "side": "short",
      "entry_price": 257.64,
      "qty": 0.3881,
      "confidence": 80,
      "opened_at": "2026-05-29T08:49:48.347952",
      "cost": 19.9980168,
      "notional": 99.990084,
      "leverage": 5,
      "exit_price": 249.63,
      "pnl_pct": 15.54,
      "pnl_usdt": 3.11,
      "closed_at": "2026-05-29T13:12:02.461268",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_SUIUSDT_1780044712",
      "symbol": "SUIUSDT",
      "side": "short",
      "entry_price": 0.9226,
      "qty": 108.3893,
      "confidence": 85,
      "opened_at": "2026-05-29T08:51:52.564110",
      "cost": 19.999993636,
      "notional": 99.99996818,
      "leverage": 5,
      "exit_price": 0.9048,
      "pnl_pct": 9.65,
      "pnl_usdt": 1.93,
      "closed_at": "2026-05-29T13:43:49.621322",
      "reason": "trailing_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_ETHUSDT_1779978101",
      "symbol": "ETHUSDT",
      "side": "short",
      "entry_price": 1993.68,
      "qty": 0.0502,
      "confidence": 75,
      "opened_at": "2026-05-28T14:21:41.194598",
      "cost": 20.0165472,
      "notional": 100.08273600000001,
      "leverage": 5,
      "exit_price": 1987.41,
      "pnl_pct": 1.57,
      "pnl_usdt": 0.31,
      "closed_at": "2026-05-29T14:21:44.323148",
      "reason": "max_hold",
      "outcome": "profit"
    },
    {
      "id": "PAPER_ONDOUSDT_1780065524",
      "symbol": "ONDOUSDT",
      "side": "short",
      "entry_price": 0.3596,
      "qty": 278.0868,
      "confidence": 80,
      "opened_at": "2026-05-29T14:38:44.852406",
      "cost": 20.000002656,
      "notional": 100.00001327999999,
      "leverage": 5,
      "exit_price": 0.3678,
      "pnl_pct": -11.4,
      "pnl_usdt": -2.28,
      "closed_at": "2026-05-29T15:10:30.347208",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_TAOUSDT_1780061245",
      "symbol": "TAOUSDT",
      "side": "short",
      "entry_price": 249.93,
      "qty": 0.4001,
      "confidence": 85,
      "opened_at": "2026-05-29T13:27:25.304836",
      "cost": 19.9993986,
      "notional": 99.996993,
      "leverage": 5,
      "exit_price": 258.46,
      "pnl_pct": -17.06,
      "pnl_usdt": -3.41,
      "closed_at": "2026-05-29T15:28:29.774061",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_ADAUSDT_1780063478",
      "symbol": "ADAUSDT",
      "side": "short",
      "entry_price": 0.2327,
      "qty": 429.7379,
      "confidence": 85,
      "opened_at": "2026-05-29T14:04:38.204190",
      "cost": 20.000001865999998,
      "notional": 100.00000933,
      "leverage": 5,
      "exit_price": 0.2375,
      "pnl_pct": -10.31,
      "pnl_usdt": -2.06,
      "closed_at": "2026-05-29T15:36:40.516651",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_ZECUSDT_1780067702",
      "symbol": "ZECUSDT",
      "side": "short",
      "entry_price": 535.41,
      "qty": 0.1868,
      "confidence": 75,
      "opened_at": "2026-05-29T15:15:02.185519",
      "cost": 20.002917599999996,
      "notional": 100.01458799999999,
      "leverage": 5,
      "exit_price": 546.72,
      "pnl_pct": -10.56,
      "pnl_usdt": -2.11,
      "closed_at": "2026-05-29T15:38:42.250323",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_TAOUSDT_1780080104",
      "symbol": "TAOUSDT",
      "side": "short",
      "entry_price": 254.62,
      "qty": 0.3927,
      "confidence": 78,
      "opened_at": "2026-05-29T18:41:44.883956",
      "cost": 19.9978548,
      "notional": 99.989274,
      "leverage": 5,
      "exit_price": 249.99,
      "pnl_pct": 9.09,
      "pnl_usdt": 1.82,
      "closed_at": "2026-05-29T19:31:23.674784",
      "reason": "trailing_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_ZECUSDT_1780084207",
      "symbol": "ZECUSDT",
      "side": "short",
      "entry_price": 533.48,
      "qty": 0.1874,
      "confidence": 75,
      "opened_at": "2026-05-29T19:50:07.605911",
      "cost": 19.9948304,
      "notional": 99.974152,
      "leverage": 5,
      "exit_price": 544.35,
      "pnl_pct": -10.19,
      "pnl_usdt": -2.04,
      "closed_at": "2026-05-29T20:25:16.349327",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_FILUSDT_1780078135",
      "symbol": "FILUSDT",
      "side": "short",
      "entry_price": 0.9771,
      "qty": 102.3437,
      "confidence": 75,
      "opened_at": "2026-05-29T18:08:55.982497",
      "cost": 20.000005854,
      "notional": 100.00002927,
      "leverage": 5,
      "exit_price": 0.9471,
      "pnl_pct": 15.35,
      "pnl_usdt": 3.07,
      "closed_at": "2026-05-29T22:07:19.547477",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_ADAUSDT_1780093926",
      "symbol": "ADAUSDT",
      "side": "short",
      "entry_price": 0.2332,
      "qty": 428.8165,
      "confidence": 70,
      "opened_at": "2026-05-29T22:32:06.926306",
      "cost": 20.00000156,
      "notional": 100.0000078,
      "leverage": 5,
      "exit_price": 0.2379,
      "pnl_pct": -10.08,
      "pnl_usdt": -2.02,
      "closed_at": "2026-05-30T02:02:11.759336",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_ONDOUSDT_1780112426",
      "symbol": "ONDOUSDT",
      "side": "short",
      "entry_price": 0.3486,
      "qty": 286.8617,
      "confidence": 80,
      "opened_at": "2026-05-30T03:40:26.107387",
      "cost": 19.999997724,
      "notional": 99.99998862,
      "leverage": 5,
      "exit_price": 0.347,
      "pnl_pct": 2.29,
      "pnl_usdt": 0.46,
      "closed_at": "2026-05-30T15:14:43.429212",
      "reason": "breakeven_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_DOGEUSDT_1780069731",
      "symbol": "DOGEUSDT",
      "side": "short",
      "entry_price": 0.10036,
      "qty": 996.4129,
      "confidence": 85,
      "opened_at": "2026-05-29T15:48:51.356094",
      "cost": 19.9999997288,
      "notional": 99.999998644,
      "leverage": 5,
      "exit_price": 0.10129,
      "pnl_pct": -4.63,
      "pnl_usdt": -0.93,
      "closed_at": "2026-05-30T15:49:00.294227",
      "reason": "max_hold",
      "outcome": "loss"
    },
    {
      "id": "PAPER_NEARUSDT_1780156673",
      "symbol": "NEARUSDT",
      "side": "short",
      "entry_price": 2.3384,
      "qty": 42.7643,
      "confidence": 80,
      "opened_at": "2026-05-30T15:57:53.753769",
      "cost": 20.000007824,
      "notional": 100.00003912,
      "leverage": 5,
      "exit_price": 2.3268,
      "pnl_pct": 2.48,
      "pnl_usdt": 0.5,
      "closed_at": "2026-05-30T18:41:17.333161",
      "reason": "breakeven_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_TRXUSDT_1780086329",
      "symbol": "TRXUSDT",
      "side": "short",
      "entry_price": 0.34357,
      "qty": 291.0615,
      "confidence": 80,
      "opened_at": "2026-05-29T20:25:29.985317",
      "cost": 19.999999911,
      "notional": 99.999999555,
      "leverage": 5,
      "exit_price": 0.34734,
      "pnl_pct": -5.49,
      "pnl_usdt": -1.1,
      "closed_at": "2026-05-30T20:25:56.257422",
      "reason": "max_hold",
      "outcome": "loss"
    }
  ],
  "total_pnl": 3.6056356569438064
}
```

## Ensemble log (last 30 lines)
```
2026-05-30 20:09:15,113 [INFO] main: IDUSDT | regime BLOCK (volatile)
2026-05-30 20:09:20,971 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-30 20:09:21,495 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-30 20:09:21,495 [INFO] main: ETHUSDT | Bull:flat(25%) Bear:short(70%)
2026-05-30 20:09:23,987 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-30 20:09:23,989 [INFO] main: ETHUSDT | Judge:SHORT conf=75% size=15.0%
2026-05-30 20:09:23,989 [INFO] main: ETHUSDT | RL adj=84.9%
2026-05-30 20:09:24,003 [INFO] main: ETHUSDT | Context score=-0.05 bias=0.05
2026-05-30 20:09:24,004 [INFO] main: ETHUSDT | gate PASS (Judge 75/70 RL 84.9/64.54 slack=±3)
2026-05-30 20:09:24,004 [INFO] positions: 2/3 rule: skip SHORT ETHUSDT (3/3 already short)
2026-05-30 20:09:30,126 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-30 20:09:30,945 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-30 20:09:30,947 [INFO] main: XRPUSDT | Bull:flat(35%) Bear:short(72%)
2026-05-30 20:09:33,054 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-30 20:09:33,055 [INFO] main: XRPUSDT | Judge:HOLD conf=65% size=0.0%
2026-05-30 20:09:33,055 [INFO] main: XRPUSDT | RL adj=65.0%
2026-05-30 20:09:39,752 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-30 20:09:40,001 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-30 20:09:40,003 [INFO] main: HBARUSDT | Bull:flat(15%) Bear:short(80%)
2026-05-30 20:09:42,112 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-30 20:09:42,113 [INFO] main: HBARUSDT | Judge:SHORT conf=80% size=15.0%
2026-05-30 20:09:42,113 [INFO] main: HBARUSDT | RL adj=91.3%
2026-05-30 20:09:42,126 [INFO] main: HBARUSDT | Context score=-0.05 bias=0.05
2026-05-30 20:09:42,126 [INFO] main: HBARUSDT | regime BLOCK (volatile)
2026-05-30 20:09:44,133 [INFO] main: Next scan in 30min (always-30min)
2026-05-30 20:25:56,256 [INFO] positions: MAX_HOLD TRXUSDT short hold:24.0h
2026-05-30 20:25:56,261 [INFO] paper_trading: [PAPER] ❌ ЗАКРЫТА SHORT TRXUSDT @ 0.3473 PnL: -5.49% (-1.10 USDT) | Баланс: 963.61
2026-05-30 20:25:56,589 [INFO] positions: LOSS TRXUSDT short PnL:-1.1% reason:max_hold
2026-05-30 20:25:56,589 [INFO] positions: Lessons: The trade was based on strong bear dominance and confirming indicators, expecting a 4% downside move. However, the trade only resulted in a 1.1% loss, failing to meet the expected downside potential. This suggests that the asymmetric risk rules may need to be reevaluated to better capture potential downsides in trending_down regimes.
2026-05-30 20:25:56,589 [INFO] rl: RL learned from short TRXUSDT: loss -1.10% | weights bull=0.994 bear=0.943 judge=1.064 threshold=64.59
```

## Disk
```
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           382M  896K  381M   1% /run
efivarfs        256K   39K  213K  16% /sys/firmware/efi/efivars
/dev/sda1        75G  8.6G   64G  12% /
tmpfs           1.9G     0  1.9G   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda15      253M  146K  252M   1% /boot/efi
tmpfs           382M   12K  382M   1% /run/user/0
```

## Memory
```
               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       866Mi       492Mi       4.8Mi       2.7Gi       2.9Gi
Swap:          2.0Gi       512Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
0 */4 * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/audit_blocked.py >> /opt/ensemble-agent/audit_blocked.log 2>&1
```
