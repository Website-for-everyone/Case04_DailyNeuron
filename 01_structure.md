# АРХИТЕКТУРА И СПЕЦИФИКАЦИЯ: DAILY NEURON

> **Проект:** Daily Neuron (Case 04)  
> **Клиент / Заказчик:** Медиа-платформа и агрегатор ИИ-новостей «Daily Neuron»  
> **Чек проекта:** 175 000 ₽ | **Срок:** 15 дней (Дедлайн: 2026-11-26)  
> **Дедлайн MVP (80%):** 2026-11-22  
> **Тип договора:** Договор СМЗ с юр. лицом (Чек «Мой Налог», 6%)

---

## 🛠 Технологический стек
- **Frontend / UI:** Swiss Cyber-Editorial Layout, швейцарская типографика (Space Grotesk + JetBrains Mono), неоновый акцент (`#00F0FF`, `#CCFF00`), Hype-Meter индикаторы, переключатель режима чтения («10 секунд» vs «Техразбор»)
- **Backend & Logic:** Python 3.12, FastAPI, Uvicorn, Pydantic v2
- **Crawler & AI Engine:** Модуль парсинга GitHub Trending, HuggingFace и Arxiv feeds + AI-суммаризатор новостей в двух форматах
- **Telegram Bot:** Aiogram 3.31 (утренний дайджест, подписки по категориям: LLM, Video Gen, Open Source, Agents)
- **Хранилище:** JSON/SQLite база структурированных новостей
- **Уведомления:** Пересылка горячих трендов и метрик в Telegram `@Idrisov_prod`

---

## 🎨 Дизайн-система (Swiss Cyber-Editorial)
- **Палитра:**
  - Pitch Black Canvas: `#0A0A0C`
  - Paper White: `#F9F9FB`
  - Subdued Carbon: `#141418`
  - Border Grid: `#26262E`
  - Neon Cyan (LLM / Research): `#00F0FF`
  - Acid Lime (Agents / High Velocity): `#CCFF00`
  - Flame Orange (Hot Hype >90%): `#FF5500`
- **Типографика:** Строгая модульная сетка International Typographic Style, моноширинные теги, бегущая строка тикера.

---

## 🏛 Архитектурная схема
```
[ Источники: GitHub / HuggingFace / Arxiv ]
                   │
                   ▼
       [ Ingestion & AI Summarizer ]
                   │
                   ▼
         [ JSON / SQLite News DB ]
          │                    │
          ▼                    ▼
[ Swiss Web Editorial ]    [ Aiogram 3 Digest Bot ]
(10s vs Tech View)         (Subscriptions & Broadcast)
                               │
                               └──► [ Alert @Idrisov_prod ]
```

---

## 🔐 Переменные окружения (.env.example)
```env
BOT_TOKEN=8217851677:AAHN34TMuC1P4e6SppuazFN8BIiLHa_RyIc
ADMIN_CHAT_ID=1387913438
OWNER_HANDLE=@Idrisov_prod
WEB_PORT=8004
NEWS_DATA_PATH=data/news.json
CRAWLER_INTERVAL_HOURS=4
```

---

## 🔗 Ресурсы и ссылки
- **Web App:** `http://localhost:8004/`
- **Telegram Bot:** `@DailyNeuronBot`
- **GitHub:** `https://github.com/Website-for-everyone/Case04_DailyNeuron`
