"""
config.py — Central configuration loader.
All API credentials and thresholds are read from environment variables / .env file.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed — fall back to real env vars / defaults

# ── Gmail ─────────────────────────────────────────────────────────────────────
GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials/gmail_credentials.json")
GMAIL_TOKEN_FILE        = os.getenv("GMAIL_TOKEN_FILE",       "credentials/gmail_token.json")

# ── Slack ─────────────────────────────────────────────────────────────────────
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")   # xoxb-...

# ── Linear ────────────────────────────────────────────────────────────────────
LINEAR_API_KEY  = os.getenv("LINEAR_API_KEY", "")    # lin_api_...
LINEAR_TEAM_ID  = os.getenv("LINEAR_TEAM_ID", "")    # optional filter

# ── Google Calendar ───────────────────────────────────────────────────────────
GCAL_CREDENTIALS_FILE = os.getenv("GCAL_CREDENTIALS_FILE", "credentials/gcal_credentials.json")
GCAL_TOKEN_FILE       = os.getenv("GCAL_TOKEN_FILE",       "credentials/gcal_token.json")

# ── Digest thresholds ─────────────────────────────────────────────────────────
URGENT_REPLY_HOURS      = int(os.getenv("URGENT_REPLY_HOURS", 2))      # email unanswered > N hrs → urgent
UPCOMING_MEETING_MINS   = int(os.getenv("UPCOMING_MEETING_MINS", 120)) # meetings within N min → urgent
DIGEST_INTERVAL_MINS    = int(os.getenv("DIGEST_INTERVAL_MINS", 30))   # how often to refresh

# ── Dashboard ─────────────────────────────────────────────────────────────────
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "127.0.0.1")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 5050))

# ── Demo mode (runs with mock data, no API keys needed) ───────────────────────
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
