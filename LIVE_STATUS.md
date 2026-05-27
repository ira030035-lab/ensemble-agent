# Live status

Generated: 2026-05-27 04:10:01 UTC

## Services
```
ensemble-agent.service:     active
ensemble-dashboard.service: active
```

## Processes
```
root      966808  0.0  1.1 131496 45740 ?        Ssl  May26   0:06 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/dashboard_api.py
root      977247  1.3  3.0 606152 117476 ?       Ssl  04:06   0:02 /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/main.py
```

## Paper state
```json
{
  "balance": 1000.0,
  "positions": {},
  "trade_history": [],
  "total_pnl": 0.0
}

```

## Ensemble log (last 30 lines)
```
2026-05-27 04:08:31,614 [INFO] main: VIRTUALUSDT | Bull:long(60%) Bear:short(70%)
2026-05-27 04:08:36,423 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:08:36,424 [INFO] main: VIRTUALUSDT | Judge:HOLD conf=70% size=0.0%
2026-05-27 04:08:36,424 [INFO] main: VIRTUALUSDT | RL adj=70.0%
2026-05-27 04:08:43,106 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:08:45,231 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:08:45,232 [INFO] main: ONDOUSDT | Bull:long(60%) Bear:short(75%)
2026-05-27 04:08:49,276 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:08:49,278 [INFO] main: ONDOUSDT | Judge:HOLD conf=75% size=0.0%
2026-05-27 04:08:49,278 [INFO] main: ONDOUSDT | RL adj=75.0%
2026-05-27 04:08:56,455 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:08:57,891 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:08:57,893 [INFO] main: INJUSDT | Bull:long(65%) Bear:short(70%)
2026-05-27 04:09:01,757 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:09:01,759 [INFO] main: INJUSDT | Judge:HOLD conf=70% size=0.0%
2026-05-27 04:09:01,759 [INFO] main: INJUSDT | RL adj=70.0%
2026-05-27 04:09:09,034 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:09:09,738 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:09:09,740 [INFO] main: DOGEUSDT | Bull:long(55%) Bear:short(70%)
2026-05-27 04:09:13,646 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:09:13,647 [INFO] main: DOGEUSDT | Judge:HOLD conf=70% size=0.0%
2026-05-27 04:09:13,647 [INFO] main: DOGEUSDT | RL adj=70.0%
2026-05-27 04:09:20,554 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:09:21,277 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:09:21,278 [INFO] main: FETUSDT | Bull:long(60%) Bear:short(73%)
2026-05-27 04:09:25,539 [INFO] httpx: HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2026-05-27 04:09:25,540 [INFO] main: FETUSDT | Judge:HOLD conf=73% size=0.0%
2026-05-27 04:09:25,540 [INFO] main: FETUSDT | RL adj=73.0%
2026-05-27 04:09:31,959 [INFO] httpx: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-05-27 04:09:58,986 [INFO] openai._base_client: Retrying request to /chat/completions in 0.465580 seconds
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
Mem:           3.7Gi       928Mi       218Mi       4.8Mi       2.9Gi       2.8Gi
Swap:          2.0Gi       256Ki       2.0Gi
```

## Crontab
```
SHELL=/bin/bash
*/15 * * * * cd /opt/ensemble-agent && /opt/ensemble-agent/venv/bin/python3 /opt/ensemble-agent/send_live_report.py >> /opt/ensemble-agent/live_report.log 2>&1
0 * * * * /opt/ensemble-agent/snapshot.sh >> /opt/ensemble-agent/snapshot.log 2>&1
*/10 * * * * /opt/ensemble-agent/live_status.sh >> /opt/ensemble-agent/status.log 2>&1
```
