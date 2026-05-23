# Live status

Generated: 2026-05-23 18:40:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      812670  0.0  1.2 209160 50560 ?        Ssl  May19   0:51 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root      907965  0.0  2.2 648304 86716 ?        Ssl  09:56   0:17 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
```

## Paper state
```json
{
  "balance": 733.6233747156951,
  "positions": {
    "BTCUSDT": {
      "id": "PAPER_BTCUSDT_1779497565",
      "symbol": "BTCUSDT",
      "side": "short",
      "entry_price": 75334.7,
      "qty": 0.0006,
      "confidence": 72,
      "opened_at": "2026-05-23T00:52:45.625592",
      "cost": 9.040163999999999,
      "notional": 45.20081999999999,
      "leverage": 5
    },
    "AAVEUSDT": {
      "id": "PAPER_AAVEUSDT_1779552292",
      "symbol": "AAVEUSDT",
      "side": "short",
      "entry_price": 85.4,
      "qty": 0.5143,
      "confidence": 72,
      "opened_at": "2026-05-23T16:04:52.629043",
      "cost": 8.784244,
      "notional": 43.92122,
      "leverage": 5
    }
  },
  "trade_history": [
    {
      "id": "PAPER_BZUSDT_1779195495",
      "symbol": "BZUSDT",
      "side": "short",
      "entry_price": 106.17,
      "qty": 0.7535,
      "confidence": 72,
      "opened_at": "2026-05-19T12:58:15.166276",
      "cost": 79.999095,
      "exit_price": 106.17,
      "pnl_pct": 0.0,
      "pnl_usdt": 0.0,
      "closed_at": "2026-05-19T16:13:35.906414",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_XAGUSDT_1779195506",
      "symbol": "XAGUSDT",
      "side": "short",
      "entry_price": 76.21,
      "qty": 1.0865,
      "confidence": 72,
      "opened_at": "2026-05-19T12:58:26.507689",
      "cost": 82.80216499999999,
      "exit_price": 76.21,
      "pnl_pct": 0.0,
      "pnl_usdt": 0.0,
      "closed_at": "2026-05-19T16:13:46.517759",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_CBRSUSDT_1779195552",
      "symbol": "CBRSUSDT",
      "side": "short",
      "entry_price": 290.99,
      "qty": 0.2589,
      "confidence": 72,
      "opened_at": "2026-05-19T12:59:12.713374",
      "cost": 75.33731100000001,
      "exit_price": 290.99,
      "pnl_pct": 0.0,
      "pnl_usdt": 0.0,
      "closed_at": "2026-05-19T16:13:50.732028",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_ZECUSDT_1779203250",
      "symbol": "ZECUSDT",
      "side": "short",
      "entry_price": 557.89,
      "qty": 0.0563,
      "confidence": 71,
      "opened_at": "2026-05-19T15:07:30.386682",
      "cost": 31.409207000000002,
      "exit_price": 557.89,
      "pnl_pct": 0.0,
      "pnl_usdt": 0.0,
      "closed_at": "2026-05-19T16:13:56.579908",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_FIDAUSDT_1779199370",
      "symbol": "FIDAUSDT",
      "side": "short",
      "entry_price": 0.02024,
      "qty": 1815.854,
      "confidence": 68,
      "opened_at": "2026-05-19T14:02:50.937804",
      "cost": 36.75288496,
      "exit_price": 0.02024,
      "pnl_pct": 0.0,
      "pnl_usdt": 0.0,
      "closed_at": "2026-05-19T16:14:01.677998",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_ONDOUSDT_1779199436",
      "symbol": "ONDOUSDT",
      "side": "short",
      "entry_price": 0.3695,
      "qty": 87.8886,
      "confidence": 68,
      "opened_at": "2026-05-19T14:03:56.477656",
      "cost": 32.474837699999995,
      "exit_price": 0.3695,
      "pnl_pct": 0.0,
      "pnl_usdt": 0.0,
      "closed_at": "2026-05-19T16:14:10.020901",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_BCHUSDT_1779199458",
      "symbol": "BCHUSDT",
      "side": "short",
      "entry_price": 381.05,
      "qty": 0.0668,
      "confidence": 68,
      "opened_at": "2026-05-19T14:04:18.466425",
      "cost": 25.45414,
      "exit_price": 381.05,
      "pnl_pct": 0.0,
      "pnl_usdt": 0.0,
      "closed_at": "2026-05-19T16:14:14.033406",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_LINKUSDT_1779203347",
      "symbol": "LINKUSDT",
      "side": "short",
      "entry_price": 9.488,
      "qty": 2.2821,
      "confidence": 68,
      "opened_at": "2026-05-19T15:09:07.803260",
      "cost": 21.652564799999997,
      "exit_price": 9.488,
      "pnl_pct": 0.0,
      "pnl_usdt": 0.0,
      "closed_at": "2026-05-19T16:14:17.992542",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_LABUSDT_1779199582",
      "symbol": "LABUSDT",
      "side": "short",
      "entry_price": 4.34692,
      "qty": 5.7701,
      "confidence": 68,
      "opened_at": "2026-05-19T14:06:22.592697",
      "cost": 25.082163092000002,
      "exit_price": 4.34692,
      "pnl_pct": 0.0,
      "pnl_usdt": 0.0,
      "closed_at": "2026-05-19T16:14:22.197132",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_BSBUSDT_1779203363",
      "symbol": "BSBUSDT",
      "side": "short",
      "entry_price": 0.67425,
      "qty": 34.1327,
      "confidence": 68,
      "opened_at": "2026-05-19T15:09:23.563927",
      "cost": 23.013972975,
      "exit_price": 0.78258,
      "pnl_pct": -16.07,
      "pnl_usdt": -3.7,
      "closed_at": "2026-05-19T16:17:12.432614",
      "reason": "emergency_stop_-15%",
      "outcome": "loss"
    },
    {
      "id": "PAPER_TONUSDT_1779203374",
      "symbol": "TONUSDT",
      "side": "short",
      "entry_price": 1.9667,
      "qty": 9.42,
      "confidence": 68,
      "opened_at": "2026-05-19T15:09:34.774633",
      "cost": 18.526314,
      "exit_price": 2.0066,
      "pnl_pct": -2.03,
      "pnl_usdt": -0.38,
      "closed_at": "2026-05-19T16:17:19.177654",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_XRPUSDT_1779203324",
      "symbol": "XRPUSDT",
      "side": "short",
      "entry_price": 1.3681,
      "qty": 18.4989,
      "confidence": 68,
      "opened_at": "2026-05-19T15:08:44.548359",
      "cost": 25.30834509,
      "exit_price": 1.3636,
      "pnl_pct": 0.33,
      "pnl_usdt": 0.08,
      "closed_at": "2026-05-19T16:17:27.034975",
      "reason": "judge_exit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_MUUSDT_1779203336",
      "symbol": "MUUSDT",
      "side": "short",
      "entry_price": 679.59,
      "qty": 0.0396,
      "confidence": 72,
      "opened_at": "2026-05-19T15:08:56.631155",
      "cost": 26.911764000000005,
      "exit_price": 713.03,
      "pnl_pct": -4.92,
      "pnl_usdt": -1.32,
      "closed_at": "2026-05-19T16:32:43.248594",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_INJUSDT_1779211451",
      "symbol": "INJUSDT",
      "side": "short",
      "entry_price": 5.028,
      "qty": 8.8967,
      "confidence": 72,
      "opened_at": "2026-05-19T17:24:11.678153",
      "cost": 44.732607599999994,
      "exit_price": 5.042,
      "pnl_pct": -0.28,
      "pnl_usdt": -0.12,
      "closed_at": "2026-05-19T17:24:22.169836",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_CRCLUSDT_1779211491",
      "symbol": "CRCLUSDT",
      "side": "long",
      "entry_price": 113.9,
      "qty": 0.5236,
      "confidence": 68,
      "opened_at": "2026-05-19T17:24:51.220342",
      "cost": 59.63804,
      "exit_price": 114.03,
      "pnl_pct": 0.11,
      "pnl_usdt": 0.07,
      "closed_at": "2026-05-19T17:24:59.503287",
      "reason": "judge_exit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_XAUTUSDT_1779211528",
      "symbol": "XAUTUSDT",
      "side": "short",
      "entry_price": 4505.19,
      "qty": 0.0099,
      "confidence": 68,
      "opened_at": "2026-05-19T17:25:28.335487",
      "cost": 44.601380999999996,
      "exit_price": 4504.7,
      "pnl_pct": 0.01,
      "pnl_usdt": 0.0,
      "closed_at": "2026-05-19T17:25:35.278753",
      "reason": "judge_exit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_HYPEUSDT_1779211591",
      "symbol": "HYPEUSDT",
      "side": "long",
      "entry_price": 48.686,
      "qty": 1.225,
      "confidence": 68,
      "opened_at": "2026-05-19T17:26:31.193556",
      "cost": 59.640350000000005,
      "exit_price": 48.655,
      "pnl_pct": -0.06,
      "pnl_usdt": -0.04,
      "closed_at": "2026-05-19T17:26:41.115213",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_CLUSDT_1779215679",
      "symbol": "CLUSDT",
      "side": "long",
      "entry_price": 104.283,
      "qty": 0.4914,
      "confidence": 68,
      "opened_at": "2026-05-19T18:34:39.490531",
      "cost": 51.2446662,
      "exit_price": 104.272,
      "pnl_pct": -0.01,
      "pnl_usdt": -0.01,
      "closed_at": "2026-05-19T18:34:51.900317",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_NEARUSDT_1779215463",
      "symbol": "NEARUSDT",
      "side": "long",
      "entry_price": 1.6575,
      "qty": 38.0471,
      "confidence": 72,
      "opened_at": "2026-05-19T18:31:03.165803",
      "cost": 63.06306825,
      "exit_price": 1.6556,
      "pnl_pct": -0.11,
      "pnl_usdt": -0.07,
      "closed_at": "2026-05-19T18:46:27.106191",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_SNDKUSDT_1779219374",
      "symbol": "SNDKUSDT",
      "side": "long",
      "entry_price": 1372.32,
      "qty": 0.0415,
      "confidence": 72,
      "opened_at": "2026-05-19T19:36:14.197617",
      "cost": 56.95128,
      "exit_price": 1372.32,
      "pnl_pct": 0.0,
      "pnl_usdt": 0.0,
      "closed_at": "2026-05-19T19:36:31.559106",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_BZUSDT_1779219428",
      "symbol": "BZUSDT",
      "side": "long",
      "entry_price": 106.85,
      "qty": 0.4735,
      "confidence": 68,
      "opened_at": "2026-05-19T19:37:08.326745",
      "cost": 50.593475,
      "exit_price": 106.68,
      "pnl_pct": -0.16,
      "pnl_usdt": -0.08,
      "closed_at": "2026-05-19T20:23:13.113908",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_MUUSDT_1779211630",
      "symbol": "MUUSDT",
      "side": "short",
      "entry_price": 720.7,
      "qty": 0.0621,
      "confidence": 72,
      "opened_at": "2026-05-19T17:27:10.924445",
      "cost": 44.75547,
      "exit_price": 701.0,
      "pnl_pct": 2.73,
      "pnl_usdt": 1.22,
      "closed_at": "2026-05-19T20:44:28.080090",
      "reason": "judge_exit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_XAGUSDT_1779215531",
      "symbol": "XAGUSDT",
      "side": "short",
      "entry_price": 74.3,
      "qty": 0.4034,
      "confidence": 68,
      "opened_at": "2026-05-19T18:32:11.883526",
      "cost": 29.97262,
      "exit_price": 73.98,
      "pnl_pct": 0.43,
      "pnl_usdt": 0.13,
      "closed_at": "2026-05-19T21:25:04.333581",
      "reason": "judge_exit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_BCHUSDT_1779226176",
      "symbol": "BCHUSDT",
      "side": "short",
      "entry_price": 368.82,
      "qty": 0.106,
      "confidence": 68,
      "opened_at": "2026-05-19T21:29:36.960227",
      "cost": 39.094919999999995,
      "exit_price": 369.53,
      "pnl_pct": -0.19,
      "pnl_usdt": -0.08,
      "closed_at": "2026-05-19T21:45:00.825591",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_RAVEUSDT_1779226342",
      "symbol": "RAVEUSDT",
      "side": "long",
      "entry_price": 0.60075,
      "qty": 77.5029,
      "confidence": 68,
      "opened_at": "2026-05-19T21:32:22.459107",
      "cost": 46.559867175,
      "exit_price": 0.59882,
      "pnl_pct": -0.32,
      "pnl_usdt": -0.15,
      "closed_at": "2026-05-19T21:47:43.238190",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_LINKUSDT_1779226065",
      "symbol": "LINKUSDT",
      "side": "long",
      "entry_price": 9.473,
      "qty": 5.9824,
      "confidence": 72,
      "opened_at": "2026-05-19T21:27:45.235821",
      "cost": 56.671275200000004,
      "exit_price": 9.466,
      "pnl_pct": -0.07,
      "pnl_usdt": -0.04,
      "closed_at": "2026-05-19T21:58:45.113016",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_DOGEUSDT_1779226331",
      "symbol": "DOGEUSDT",
      "side": "short",
      "entry_price": 0.10357,
      "qty": 295.7562,
      "confidence": 68,
      "opened_at": "2026-05-19T21:32:11.026958",
      "cost": 30.631469633999995,
      "exit_price": 0.10321,
      "pnl_pct": 0.35,
      "pnl_usdt": 0.11,
      "closed_at": "2026-05-19T22:02:28.177803",
      "reason": "judge_exit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_CHZUSDT_1779227898",
      "symbol": "CHZUSDT",
      "side": "short",
      "entry_price": 0.04704,
      "qty": 659.9363,
      "confidence": 68,
      "opened_at": "2026-05-19T21:58:18.226493",
      "cost": 31.043403551999997,
      "exit_price": 0.04686,
      "pnl_pct": 0.38,
      "pnl_usdt": 0.12,
      "closed_at": "2026-05-19T22:28:49.708349",
      "reason": "judge_exit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_TONUSDT_1779227913",
      "symbol": "TONUSDT",
      "side": "long",
      "entry_price": 1.9914,
      "qty": 23.6949,
      "confidence": 68,
      "opened_at": "2026-05-19T21:58:33.446041",
      "cost": 47.186023860000006,
      "exit_price": 1.9787,
      "pnl_pct": -0.64,
      "pnl_usdt": -0.3,
      "closed_at": "2026-05-19T22:28:55.017231",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_SUIUSDT_1779239152",
      "symbol": "SUIUSDT",
      "side": "long",
      "entry_price": 1.035,
      "qty": 41.0466,
      "confidence": 68,
      "opened_at": "2026-05-20T01:05:52.979894",
      "cost": 42.483230999999996,
      "exit_price": 1.0346,
      "pnl_pct": -0.04,
      "pnl_usdt": -0.02,
      "closed_at": "2026-05-20T01:36:09.789064",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_GOATUSDT_1779239296",
      "symbol": "GOATUSDT",
      "side": "short",
      "entry_price": 0.01791,
      "qty": 2229.7154,
      "confidence": 68,
      "opened_at": "2026-05-20T01:08:16.601589",
      "cost": 39.934202813999995,
      "exit_price": 0.018,
      "pnl_pct": -0.5,
      "pnl_usdt": -0.2,
      "closed_at": "2026-05-20T01:38:48.498020",
      "reason": "judge_exit",
      "outcome": "loss"
    },
    {
      "id": "PAPER_XRPUSDT_1779239442",
      "symbol": "XRPUSDT",
      "side": "short",
      "entry_price": 1.3567,
      "qty": 27.6687,
      "confidence": 68,
      "opened_at": "2026-05-20T01:10:42.560809",
      "cost": 37.53812529,
      "exit_price": 1.3488,
      "pnl_pct": 0.58,
      "pnl_usdt": 0.22,
      "closed_at": "2026-05-20T01:40:56.588958",
      "reason": "judge_exit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_XAUUSDT_1779215505",
      "symbol": "XAUUSDT",
      "side": "short",
      "entry_price": 4500.47,
      "qty": 0.0085,
      "confidence": 68,
      "opened_at": "2026-05-19T18:31:45.975311",
      "cost": 38.253995,
      "exit_price": 4481.23,
      "pnl_pct": 0.43,
      "pnl_usdt": 0.16,
      "closed_at": "2026-05-20T07:23:27.620613",
      "reason": "manual_audit_close",
      "outcome": "profit"
    },
    {
      "id": "PAPER_HYPEUSDT_1779272131",
      "symbol": "HYPEUSDT",
      "side": "short",
      "entry_price": 49.075,
      "qty": 0.9108,
      "confidence": 68,
      "opened_at": "2026-05-20T10:15:31.044487",
      "cost": 44.69751000000001,
      "exit_price": 50.613,
      "pnl_pct": -3.13,
      "pnl_usdt": -1.4,
      "closed_at": "2026-05-20T13:22:00.093784",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_ZECUSDT_1779261950",
      "symbol": "ZECUSDT",
      "side": "long",
      "entry_price": 590.98,
      "qty": 0.1137,
      "confidence": 72,
      "opened_at": "2026-05-20T07:25:50.987043",
      "cost": 67.19442599999999,
      "exit_price": 614.99,
      "pnl_pct": 4.06,
      "pnl_usdt": 2.73,
      "closed_at": "2026-05-20T14:17:01.569976",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_TONUSDT_1779264431",
      "symbol": "TONUSDT",
      "side": "short",
      "entry_price": 1.9532,
      "qty": 20.8666,
      "confidence": 72,
      "opened_at": "2026-05-20T08:07:11.906256",
      "cost": 40.75664312,
      "exit_price": 2.0163,
      "pnl_pct": -3.23,
      "pnl_usdt": -1.32,
      "closed_at": "2026-05-20T14:33:52.764054",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_HYPEUSDT_1779283931",
      "symbol": "HYPEUSDT",
      "side": "short",
      "entry_price": 50.534,
      "qty": 0.8825,
      "confidence": 72,
      "opened_at": "2026-05-20T13:32:11.020930",
      "cost": 44.596255,
      "exit_price": 52.18,
      "pnl_pct": -3.26,
      "pnl_usdt": -1.45,
      "closed_at": "2026-05-20T17:15:11.923507",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_PENGUUSDT_1779299656",
      "symbol": "PENGUUSDT",
      "side": "short",
      "entry_price": 0.009525,
      "qty": 6257.4878,
      "confidence": 78,
      "opened_at": "2026-05-20T17:54:16.607386",
      "cost": 59.602571295000004,
      "exit_price": 0.009221,
      "pnl_pct": 3.19,
      "pnl_usdt": 1.9,
      "closed_at": "2026-05-20T18:46:17.198085",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_PENGUUSDT_1779430529",
      "symbol": "PENGUUSDT",
      "side": "long",
      "entry_price": 0.009608,
      "qty": 6170.5085,
      "confidence": 72,
      "opened_at": "2026-05-22T06:15:29.774286",
      "cost": 11.8572491336,
      "notional": 59.286245668,
      "leverage": 5,
      "exit_price": 0.009788,
      "pnl_pct": 1.87,
      "pnl_usdt": 1.11,
      "closed_at": "2026-05-22T07:59:17.536654",
      "reason": "trailing_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_TAOUSDT_1779429563",
      "symbol": "TAOUSDT",
      "side": "long",
      "entry_price": 282.79,
      "qty": 0.1701,
      "confidence": 68,
      "opened_at": "2026-05-22T05:59:23.053840",
      "cost": 9.620515800000002,
      "notional": 48.102579000000006,
      "leverage": 5,
      "exit_price": 291.56,
      "pnl_pct": 3.1,
      "pnl_usdt": 1.49,
      "closed_at": "2026-05-22T11:55:53.834457",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_ASTERUSDT_1779429829",
      "symbol": "ASTERUSDT",
      "side": "short",
      "entry_price": 0.6908,
      "qty": 49.0437,
      "confidence": 72,
      "opened_at": "2026-05-22T06:03:49.621406",
      "cost": 6.7758775920000005,
      "notional": 33.87938796,
      "leverage": 5,
      "exit_price": 0.6682,
      "pnl_pct": 3.27,
      "pnl_usdt": 1.11,
      "closed_at": "2026-05-22T18:45:33.610179",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_ADAUSDT_1779453213",
      "symbol": "ADAUSDT",
      "side": "long",
      "entry_price": 0.2522,
      "qty": 239.4382,
      "confidence": 72,
      "opened_at": "2026-05-22T12:33:33.595113",
      "cost": 12.077262807999999,
      "notional": 60.386314039999995,
      "leverage": 5,
      "exit_price": 0.2445,
      "pnl_pct": -3.05,
      "pnl_usdt": -1.84,
      "closed_at": "2026-05-22T18:45:33.994955",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_DOGEUSDT_1779453249",
      "symbol": "DOGEUSDT",
      "side": "long",
      "entry_price": 0.10636,
      "qty": 495.5861,
      "confidence": 72,
      "opened_at": "2026-05-22T12:34:09.195141",
      "cost": 10.542107519199998,
      "notional": 52.710537595999995,
      "leverage": 5,
      "exit_price": 0.10298,
      "pnl_pct": -3.18,
      "pnl_usdt": -1.68,
      "closed_at": "2026-05-22T19:30:54.131442",
      "reason": "stop_loss",
      "outcome": "loss"
    },
    {
      "id": "PAPER_SOLUSDT_1779429946",
      "symbol": "SOLUSDT",
      "side": "short",
      "entry_price": 86.773,
      "qty": 0.6958,
      "confidence": 72,
      "opened_at": "2026-05-22T06:05:46.091766",
      "cost": 12.075330679999999,
      "notional": 60.376653399999995,
      "leverage": 5,
      "exit_price": 84.093,
      "pnl_pct": 3.09,
      "pnl_usdt": 1.86,
      "closed_at": "2026-05-22T19:41:09.750327",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_TONUSDT_1779478588",
      "symbol": "TONUSDT",
      "side": "short",
      "entry_price": 1.9003,
      "qty": 28.4302,
      "confidence": 78,
      "opened_at": "2026-05-22T19:36:28.136595",
      "cost": 10.805181812,
      "notional": 54.025909060000004,
      "leverage": 5,
      "exit_price": 1.8857,
      "pnl_pct": 0.77,
      "pnl_usdt": 0.42,
      "closed_at": "2026-05-22T22:53:32.262714",
      "reason": "trailing_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_PEPEUSDT_1779486338",
      "symbol": "PEPEUSDT",
      "side": "short",
      "entry_price": 3.683e-06,
      "qty": 11052828.4331,
      "confidence": 72,
      "opened_at": "2026-05-22T21:45:38.441448",
      "cost": 8.141513423821461,
      "notional": 40.7075671191073,
      "leverage": 5,
      "exit_price": 3.5721e-06,
      "pnl_pct": 3.01,
      "pnl_usdt": 1.23,
      "closed_at": "2026-05-22T23:48:05.066455",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_PEPEUSDT_1779497664",
      "symbol": "PEPEUSDT",
      "side": "short",
      "entry_price": 3.607e-06,
      "qty": 17013550.8304,
      "confidence": 78,
      "opened_at": "2026-05-23T00:54:24.256401",
      "cost": 12.27357556905056,
      "notional": 61.367877845252806,
      "leverage": 5,
      "exit_price": 3.4983e-06,
      "pnl_pct": 3.01,
      "pnl_usdt": 1.85,
      "closed_at": "2026-05-23T07:50:27.634617",
      "reason": "take_profit",
      "outcome": "profit"
    },
    {
      "id": "PAPER_BNBUSDT_1779330658",
      "symbol": "BNBUSDT",
      "side": "short",
      "entry_price": 654.18,
      "qty": 0.0913,
      "confidence": 76,
      "opened_at": "2026-05-21T02:30:58.052787",
      "cost": 59.726634,
      "exit_price": 644.83,
      "pnl_pct": 1.43,
      "pnl_usdt": 0.85,
      "closed_at": "2026-05-23T14:35:31.037978",
      "reason": "trailing_stop",
      "outcome": "profit"
    },
    {
      "id": "PAPER_FILUSDT_1779530186",
      "symbol": "FILUSDT",
      "side": "short",
      "entry_price": 0.9292,
      "qty": 66.2229,
      "confidence": 82,
      "opened_at": "2026-05-23T09:56:26.918762",
      "cost": 12.306863736,
      "notional": 61.53431868,
      "leverage": 5,
      "exit_price": 0.9577,
      "pnl_pct": -3.07,
      "pnl_usdt": -1.89,
      "closed_at": "2026-05-23T16:35:44.717276",
      "reason": "stop_loss",
      "outcome": "loss"
    }
  ],
  "total_pnl": 0.5883591536952666
}
```

## Ensemble log (last 30 lines)
```
2026-05-23 16:08:06,016 [INFO] main: BEATUSDT | Judge:HOLD conf=72% size=0.0%
2026-05-23 16:08:06,016 [INFO] main: BEATUSDT | RL adj=72.0%
2026-05-23 16:08:09,712 [INFO] main: NEARUSDT | Bull:long(80%) Bear:short(80%)
2026-05-23 16:08:15,333 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-23 16:08:15,335 [INFO] main: NEARUSDT | Judge:HOLD conf=80% size=0.0%
2026-05-23 16:08:15,335 [INFO] main: NEARUSDT | RL adj=80.0%
2026-05-23 16:08:19,021 [INFO] main: BCHUSDT | Bull:long(60%) Bear:short(80%)
2026-05-23 16:08:24,366 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-23 16:08:24,368 [INFO] main: BCHUSDT | Judge:HOLD conf=80% size=0.0%
2026-05-23 16:08:24,368 [INFO] main: BCHUSDT | RL adj=80.0%
2026-05-23 16:08:28,234 [INFO] main: INJUSDT | Bull:long(60%) Bear:short(80%)
2026-05-23 16:08:33,121 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-23 16:08:33,123 [INFO] main: INJUSDT | Judge:HOLD conf=80% size=0.0%
2026-05-23 16:08:33,123 [INFO] main: INJUSDT | RL adj=80.0%
2026-05-23 16:08:36,898 [INFO] main: DOGEUSDT | Bull:long(55%) Bear:short(80%)
2026-05-23 16:08:42,761 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-23 16:08:42,763 [INFO] main: DOGEUSDT | Judge:HOLD conf=80% size=0.0%
2026-05-23 16:08:42,763 [INFO] main: DOGEUSDT | RL adj=80.0%
2026-05-23 16:08:46,522 [INFO] main: ONDOUSDT | Bull:long(65%) Bear:short(70%)
2026-05-23 16:08:51,948 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-23 16:08:51,950 [INFO] main: ONDOUSDT | Judge:HOLD conf=70% size=0.0%
2026-05-23 16:08:51,950 [INFO] main: ONDOUSDT | RL adj=70.0%
2026-05-23 16:08:53,952 [INFO] main: Next scan in 180min (weekend)
2026-05-23 16:35:44,716 [INFO] positions: STOP-LOSS FILUSDT short PnL:-3.07%
2026-05-23 16:35:44,721 [INFO] paper_trading: [PAPER] ❌ ЗАКРЫТА SHORT FILUSDT @ 0.9577 PnL: -3.07% (-1.89 USDT) | Баланс: 733.62
2026-05-23 16:35:45,114 [INFO] positions: LOSS FILUSDT short PnL:-3.07% reason:stop_loss
2026-05-23 16:35:45,114 [INFO] positions: Lessons: The trade was closed at a loss due to hitting the stop loss, resulting in a -3.07% PnL. This outcome contrasts with past profitable trades in similar setups, highlighting the importance of patience and not exiting prematurely. The key takeaway is to hold through the trend and avoid exiting on minor reversals, as evidenced by past breakeven trades that would have been profitable with more patience.
2026-05-23 16:35:45,115 [INFO] rl: RL learned from short FILUSDT: loss -3.07% | weights bull=0.966 bear=1.020 judge=1.013 threshold=64.91
2026-05-23 16:56:25,300 [INFO] main: Symbols: 30
2026-05-23 17:56:25,987 [INFO] main: Symbols: 30
```

## Disk
```
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           382M  872K  381M   1% /run
efivarfs        256K   39K  213K  16% /sys/firmware/efi/efivars
/dev/sda1        75G  5.7G   67G   8% /
tmpfs           1.9G     0  1.9G   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda15      253M  146K  252M   1% /boot/efi
tmpfs           382M   12K  382M   1% /run/user/0
```

## Memory
```
               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       606Mi       1.1Gi       4.8Mi       2.3Gi       3.1Gi
Swap:             0B          0B          0B
```

## Crontab
```
SHELL=/bin/bash
@reboot nohup /opt/trading-agent/venv/bin/python -u /opt/trading-agent/main.py >> /opt/trading-agent/bot.log 2>&1 &
0 0 * * * /opt/trading-agent/backup.sh >> /opt/trading-agent/backup.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
