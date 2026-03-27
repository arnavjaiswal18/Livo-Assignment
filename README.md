# 💓 Heartbeat

> A lightweight, 30-minute digest dashboard for non-technical founders — surfaces urgent client communications, project blockers, and upcoming meetings in one clean view.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?style=flat-square&logo=flask)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Demo Mode](https://img.shields.io/badge/Demo%20Mode-No%20API%20keys%20needed-orange?style=flat-square)

---
# Output 
![alt text](image.png)
## 🤔 What is Heartbeat?

Heartbeat is a background digest script that runs every **30 minutes** ⏱️ while your laptop is active. It pulls from Gmail, Slack, Linear, and Google Calendar, then presents a prioritised, two-column dashboard:

| 🔴 Needs Attention | 🔵 Just so you know |
|---|---|
| 📧 Unanswered client emails (>2h) | ✅ Completed Linear tasks |
| 💬 Incoming Slack DMs | 🖊️ NDA signed, docs received |
| 🚧 Issues blocked in Linear | 📢 Starred-channel updates |
| 📅 Meetings starting in ≤30 min | 🗓️ Meetings later today |

---

## 🗂️ Project Structure

```
heartbeat/
├── 🚀 main.py                  # Flask server + background scheduler
├── ⚙️  config.py                # Env-based config loader
├── 📦 requirements.txt          # Python dependencies
├── 🔑 .env.example              # API credential template
│
├── collectors/
│   ├── 🧱 models.py             # DigestItem + Digest dataclasses
│   ├── 🔮 demo.py               # Realistic mock data (no API keys needed)
│   ├── ✉️  gmail.py              # Gmail API v1 collector
│   ├── 💬 slack.py              # Slack SDK collector (DMs + starred channels)
│   ├── ◈  linear.py             # Linear GraphQL API collector
│   └── 📅 calendar.py           # Google Calendar API collector
│
└── processors/
    ├── 🧠 digest.py             # Aggregates + deduplicates collector output
    └── 🎨 renderer.py           # Renders Digest → self-contained HTML dashboard
```

---

## ⚡ Quick Start (Demo Mode — no API keys required)

```bash
# 1. Clone / navigate to the project
cd heartbeat

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install flask

# 4. Run (demo mode is on by default)
python main.py
```

🌐 The browser opens automatically at **http://127.0.0.1:5050** showing realistic mock data.

---

## 🔌 Running with Real Integrations

### 1️⃣ Copy the env template

```bash
cp .env.example .env
```

Set `DEMO_MODE=false` in `.env`, then fill in the credentials for whichever tools you use.

### 2️⃣ Install all dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure each integration

#### ✉️ Gmail
1. Go to [Google Cloud Console](https://console.cloud.google.com) → **APIs & Services** → **Credentials**
2. Create an **OAuth 2.0 Client ID** (Desktop app type)
3. Download the JSON and save it as `credentials/gmail_credentials.json`
4. On first run, a browser window opens for one-time OAuth login — token is cached automatically 🔒

#### 📅 Google Calendar
Reuses the same Google Cloud project as Gmail. Download a second OAuth credential or share the same file:
```env
GCAL_CREDENTIALS_FILE=credentials/gcal_credentials.json
```

#### 💬 Slack
1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From Scratch**
2. Under **OAuth & Permissions**, add these scopes:
   - `channels:history`, `im:history`, `stars:read`, `users:info`
3. Install to workspace → copy the **Bot User OAuth Token** (`xoxb-...`) 🤖
4. Set `SLACK_BOT_TOKEN=xoxb-your-token` in `.env`

#### ◈ Linear
1. Go to [Linear Settings](https://linear.app/settings/api) → **Personal API keys** → **Create key**
2. Set `LINEAR_API_KEY=lin_api_your-key` in `.env`

### 4️⃣ Start 🚀

```bash
python main.py
```

---

## ⚙️ Configuration Reference

All settings live in `.env` (copy from `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `DEMO_MODE` | `true` | 🔮 Use mock data instead of live APIs |
| `DIGEST_INTERVAL_MINS` | `30` | ⏱️ How often the digest refreshes |
| `URGENT_REPLY_HOURS` | `2` | 🔴 Email unanswered > N hours → Urgent |
| `UPCOMING_MEETING_MINS` | `120` | 📅 Show calendar events within this window |
| `DASHBOARD_HOST` | `127.0.0.1` | 🌐 Host to bind the Flask server |
| `DASHBOARD_PORT` | `5050` | 🔌 Port for the dashboard |

---

## 🧠 How Urgency is Decided

| Source | 🔴 Urgent if… | 🔵 Info if… |
|---|---|---|
| **✉️ Gmail** | Email in inbox, no reply sent, older than `URGENT_REPLY_HOURS` | All other inbox emails |
| **💬 Slack** | Any direct message (DM) | Messages in starred channels |
| **◈ Linear** | Issue state contains "blocked" or is Cancelled | In Progress, Done, or other active states |
| **📅 Calendar** | Event starts within 30 minutes | Event within `UPCOMING_MEETING_MINS` window |

---

## 🛣️ API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | 🖥️ The live HTML dashboard |
| `GET /api/digest` | 📊 Current digest as JSON (for CLI / notifications) |
| `GET /health` | 🩺 Health check — returns `{"status": "ok"}` |

**📄 Example JSON response from `/api/digest`:**
```json
{
  "generated_at": "2026-03-27T10:00:00",
  "urgent_count": 3,
  "info_count": 5,
  "urgent": [
    {
      "source": "gmail",
      "level": "urgent",
      "title": "Priya Mehta (Acme Corp) — Re: Q2 Proposal",
      "body": "Can we hop on a quick call today?",
      "timestamp": "2026-03-27T07:00:00",
      "link": "https://mail.google.com/...",
      "age_minutes": 180
    }
  ],
  "info": [...]
}
```

---

## 🖥️ CLI Options

```bash
python main.py --help

Options:
  --host        🌐 Host to bind (default: 127.0.0.1)
  --port        🔌 Port to listen on (default: 5050)
  --no-browser  🚫 Skip auto-opening the browser on startup
```

---

## 💡 Design Decisions

### 🔧 Why these tools?
- **✉️ Gmail API** — direct, scoped access to inbox without scraping; read-only OAuth scope keeps it safe 🔒
- **💬 Slack SDK** — official Python SDK; scoping to DMs + starred channels cuts 90% of noise 📉
- **◈ Linear GraphQL** — single query returns state + team + description; REST API is far more verbose
- **📅 Google Calendar** — same OAuth flow as Gmail, minimal extra setup ♻️

### 🚫 What was deliberately left out
- **📝 Notion / Confluence** — document updates are almost never time-sensitive over 30 min
- **📢 All Slack channels** — too noisy; starred channels are the right signal for leadership
- **📜 Email body content** — snippet (first 200 chars) is enough context without privacy concerns 🔏
- **🔔 Push notifications** — a browser tab auto-refreshing every 30 min is lower friction for a MacBook user than native notifications requiring OS-level permissions

### ⚖️ Urgency vs. Informational
The threshold is intentionally simple: **does this block revenue or a client relationship? 💰** Unanswered client emails and DMs do. Completed tasks and general channel messages don't. The 2-hour email threshold is configurable (`URGENT_REPLY_HOURS`) because different teams have different SLA norms.

---

## 📋 Requirements

- 🐍 Python **3.9+**
- 🌶️ Flask (required for all modes)
- 📦 All other dependencies are **optional** — the app gracefully skips any integration whose package isn't installed ✅

---

## 📄 License

MIT — free to use, modify, and distribute. 🎉
