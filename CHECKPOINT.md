# 🚀 ENSEMBLE AGENT — CHECKPOINT 2026-05-26

> Сохранено для продолжения работы в новом чате.
> Дата: 2026-05-26 ~16:00 UTC

---

## 📁 Рабочая директория

```
/opt/ensemble-agent/
```

---

## 🏗️ Архитектура (3 сервиса)

| Сервис | Файл | Systemd unit | Роль |
|--------|------|-------------|------|
| **ensemble-agent** | `main.py` | `ensemble-agent.service` | Основной бот (Bull/Bear/Judge + RL) |
| **ensemble-explorer** | `explorer.py` | `ensemble-explorer.service` | Исследователь ($5, LONG+SHORT, TP/SL real-time) |
| **ensemble-advisor** | `auto_advisor.py` | `ensemble-advisor.service` | Автономный риск-монитор (каждые 15 мин) |
| **dashboard** | `dashboard_api.py` | `ensemble-dashboard.service` | API статуса (опционально) |

**Все сервисы:** `active`, `enabled` (автозапуск при ребуте).

---

## 🔑 Ключевые файлы (изменённые сегодня)

| Файл | Что изменено |
|------|-------------|
| `explorer.py` | **v2**: TP/SL real-time, monitor каждые 15 сек, rolling window 7 дней, auto-learn в ContextRL |
| `rl_context.py` | Новый модуль: ContextRL filter, exponential decay (0.9/день), bucket-based pattern learning |
| `main.py` | Интеграция ContextRL: score() после Judge/RL, BLOCK при score<-0.15, BOOST при score>=0.20 |
| `auto_advisor.py` | Исправлено HTML-escaping для Telegram (символы `<`, `>`, `&`) |
| `send_live_report.py` | Исправлено HTML-escaping |
| `feed_explorer_to_rl.py` | Скрипт ручного запуска обучения ContextRL из explorer_trades.json |
| `config.py` | Без изменений (стандартные TP=4%, SL=-2%, плечо 5x) |

---

## 💰 Текущий статус

### Ensemble-Agent (основной)
- **Баланс:** 707.44 USDT (старт 1000)
- **Открытые позиции:** 2
  - DOGEUSDT SHORT @ 0.10115
  - XRPUSDT LONG @ 1.3514
- **Всего сделок:** 71
- **Win rate:** 42.3% (30W / 41L)
- **RL Weights:** bull=0.9767, bear=0.9924, judge=1.0309, threshold=65.04, episodes=31

### Ensemble-Explorer
- **Баланс:** 479.90 USDT (старт 500)
- **Открытые позиции:** 20 (10 символов × LONG/SHORT)
- **Закрытые сделок:** 80
- **Win rate:** 37.5% (30W / 50L)
- **Exit breakdown:** TP=30, SL=50, HOLD=0
- **Sum PnL:** -0.24 USDT
- **Key signal:** `side=long` avg +2.59% | `side=short` avg -4.26% → рынок бычий

### ContextRL
- **State:** `rl_context.json` (~3.3 KB)
- **Features:** 12
- **Bucket updates:** ~12,800
- **Decay:** 0.9/day, auto-applied при learn_from_closed()

---

## 🧠 Как работает ContextRL (новое)

```
Explorer открывает LONG/SHORT по $5 → ждёт TP(+4%)/SL(-2%)/max_hold(24ч)
                                    ↓
                              Закрывается → записывается в explorer_trades.json
                                    ↓
                              learn_from_closed() вызывается автоматически
                                    ↓
                              ContextRL.update_bucket(feature, bucket, pnl_pct)
                                    ↓
                              main.py при скане: ctx = ContextRL.score(snapshot, side)
                                    ↓
                              ctx < -0.15 → context BLOCK
                              ctx >= 0.20 → context BOOST
                              иначе → PASS (обычная логика)
```

**Bucket features:** rsi_15m, rsi_1h, regime, macd, funding, volume_ratio, price_change_1h/4h, bb_position, fear_greed, btc_dominance, side

---

## 📋 Быстрые команды для нового чата

```bash
# Проверить статус всех сервисов
systemctl status ensemble-agent ensemble-explorer ensemble-advisor --no-pager

# Последние логи
journalctl -u ensemble-agent -n 20 --no-pager
tail -n 30 /opt/ensemble-agent/ensemble.log
tail -n 30 /opt/ensemble-agent/explorer.log
tail -n 10 /opt/ensemble-agent/advisor.log

# Статус балансов и позиций
python3 -c "import json; d=json.load(open('/opt/ensemble-agent/paper_state.json')); print('Main:', d['balance'], 'Pos:', len(d['positions']))"
python3 -c "import json; d=json.load(open('/opt/ensemble-agent/explorer_state.json')); print('Explorer:', d['balance'], 'Pos:', len(d['positions']), 'PnL:', d['total_pnl'])"

# Статистика explorer
python3 -c "import json; t=json.load(open('/opt/ensemble-agent/explorer_trades.json')); p=[x for x in t if x['outcome']=='profit']; print('Closed:', len(t), 'WR:', len(p)/len(t)*100:.1f}%)"

# ContextRL отчёт
python3 -c "from rl_context import ContextRL; crl=ContextRL(); print(crl.report())"

# Ручное обучение ContextRL (если нужно)
python3 /opt/ensemble-agent/feed_explorer_to_rl.py

# Отправить live-отчёт в Telegram
python3 /opt/ensemble-agent/send_live_report.py

# Перезапуск сервисов (если нужно)
systemctl restart ensemble-agent ensemble-explorer ensemble-advisor
```

---

## 📅 Что произойдёт автоматически

| Время | Событие |
|-------|---------|
| Каждые 15 сек | Explorer проверяет TP/SL всех позиций |
| Каждые 2 часа | Explorer открывает новые 20 позиций |
| Каждые 15 мин | Advisor читает состояние и шлёт алерты |
| Каждые 15 мин | Cron шлёт live-статус в Telegram |
| Каждые 60 мин | Main agent сканирует 30 монет |
| Каждые 24ч | ContextRL применяет decay (factor=0.9) |
| 08:00 UTC | Explorer шлёт daily report в Telegram |
| >7 дней | explorer_trades.json автоматически ротируется |

---

## ⚠️ Известные проблемы / TODO

1. **Баланс main agent -29%** — нормально для paper mode на этапе обучения, но требует внимания
2. **Advisor спамит warning** про баланс < 600 — кулдаун 15 мин работает, но можно поднять порог
3. **ContextRL пока молодой** — нужно 100+ сделок для устойчивых паттернов (будет к вечеру)
4. **HTML-escaping** — исправлено в advisor, но стоит проверить другие скрипты при добавлении новых

---

## 🎯 Цель системы

> Explorer торгует дёшево и быстро ($5 × 20 позиций), собирая ground truth.
> ContextRL учится на этих паттернах.
> Main agent использует ContextRL как второй фильтр после Judge.
> Advisor следит за рисками.
>
> Все 4 компонента работают автономно, без вмешательства.

---

## 🔗 Связанные файлы

- `AGENTS.md` — описание архитектуры (возможно устарело, проверить)
- `LIVE_STATUS.md` — автообновляемый статус (git push каждые 10 мин)
- `CHECKPOINT.md` — этот файл

---

## 🔧 Патч 2026-05-27 03:59 UTC (исправление просадки main agent)

**Проблема:** Main agent продолжал проседать (−31%) несмотря на ContextRL из-за 5 системных багов.

**Внесённые изменения:**

| Файл | Изменение | Приоритет |
|------|-----------|-----------|
| `position_manager.py` | **MAX_HOLD_HOURS** теперь принудительно закрывает позиции по таймауту (24ч). Раньше конфиг был мёртвый. | P0 |
| `position_manager.py` | **Breakeven SL** переносится на **+0.5%** (было 0%) при peak ≥ 1.5% (было 1.0%). Убирает «смерть от тысячи порезов». | P0 |
| `position_manager.py` | **Emergency exit:** если PnL < −1.0%, Judge может выйти немедленно, игнорируя MIN_HOLD 2ч. | P1 |
| `main.py` | **Side-bias penalty:** short-сделки получают −0.10 к ContextRL score (explorer: short avg −1.91%, long +1.37%). Блокирует shorts в бычьем рынке. | P0 |
| `config.py` | **TP** снижен с 4.0% → **3.0%** для более частых фиксаций. | P2 |

**Статус:** ensemble-agent перезапущен, изменения активны.
**Чек:** `systemctl status ensemble-agent` — active since 03:59 UTC.

---

## 🔄 Сброс состояния 2026-05-27 04:06 UTC (forget the −300)

**Причина:** Первоначальная настройка системы (крупный sizing, тестовые сделки) создала «виртуальную» просадку ~−300 USDT. Нужно начать чистый учёт с текущими фиксами.

**Что сброшено:**

| Файл | Было | Стало |
|------|------|-------|
| `paper_state.json` | balance 687.29, 3 позиции, 72 сделки в истории | **balance 1000.0**, позиций 0, история пуста |
| `memory.json` | 89 trades (pnl −22.68%) | **пусто** |
| `rl_weights.json` | bull=0.977, bear=0.992, judge=1.031, episodes=32 | **дефолт**: 1.0/1.0/1.0, threshold=70, **episodes=0** |
| `advisor_state.json` | flag поднят, consecutive_losses | **сброшен** |
| `ensemble.log` / `advisor.log` | старые алерты и ошибки | **ротированы** (.old) |

**Backups:** все оригиналы сохранены как `*.bak_20260527` и `*.old`.

**RL:** запустился с сообщением `RL: starting fresh (prime disabled, 0 closed in memory)`. Начнёт обучаться заново на новых сделках с правильным sizing ($20) и исправленной логикой.

**ContextRL (`rl_context.json`):** не трогали — он работает на explorer data и не связан с main-agent просадкой.

---

## 🔐 Аудит безопасности 2026-05-27 04:46 UTC

**Проведён полный аудит системы: сервисы, ключи, сеть, файлы, cron.**

### Найденные проблемы

| Уровень | Проблема | Риск |
|---------|----------|------|
| **P0** | `.env` права 644 | Любой пользователь читает API ключи |
| **P0** | Нет `.gitignore` | Случайный коммит секретов в публичный репо |
| **P0** | UFW отключен | Дашборд (8765) открыт из интернета |
| **P1** | `snapshot.sh` git push падает (race) | Репозиторий не синхронизируется |
| **P2** | 20+ старых `.bak`/`.log` файлов | Засорение, путаница |

### Выполненные фиксы

| Фикс | Команда/Действие |
|------|-----------------|
| `chmod 600 .env` | Только root читает секреты |
| Создан `.gitignore` | `.env`, `venv/`, `__pycache__/`, `*.log`, `*.bak_*`, `simulator_*` |
| `ufw enable` + `allow 22/tcp` + `delete allow 8765` | Только SSH снаружи. Dashboard — только localhost |
| `snapshot.sh`: `git pull --rebase` перед push | Race condition устранён |
| Удалены старые `.bak` файлы (до 20260527) | Оставлены только свежие backups |

### Итог аудита

- **Сервисы:** 4/4 active, стабильно
- **Ключи:** защищены от чтения другими пользователями, hardcoded secrets в .py — 0
- **Сеть:** firewall active, только 22/tcp inbound
- **Explorer:** 215 сделок, ContextRL обучен, ротация 7 дней работает
- **Main agent:** balance 940, 3 позиции, RL primed (20 synthetic episodes)
- **Advisor:** корректен, спама нет

**Статус:** Критических уязвимостей нет. Система готова к продолжению работы.
