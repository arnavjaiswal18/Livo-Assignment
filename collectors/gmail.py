"""
gmail.py — Collects unread/unanswered client email threads from the last 30 min.
Uses Google Gmail API v1 via OAuth2.
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import Optional

from .models import DigestItem
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _authenticate() -> Optional[object]:
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print("[Gmail] google-api packages not installed — skipping Gmail.")
        return None

    creds = None
    if os.path.exists(config.GMAIL_TOKEN_FILE):
        with open(config.GMAIL_TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(config.GMAIL_CREDENTIALS_FILE):
                print("[Gmail] credentials file not found — skipping Gmail collection.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                config.GMAIL_CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(config.GMAIL_TOKEN_FILE), exist_ok=True)
        with open(config.GMAIL_TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("gmail", "v1", credentials=creds)


def _parse_email(service, msg_id: str) -> Optional[DigestItem]:
    try:
        msg = service.users().messages().get(
            userId="me", id=msg_id, format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        subject = headers.get("Subject", "(no subject)")
        sender  = headers.get("From", "Unknown")
        date_ms = int(msg.get("internalDate", 0))
        ts      = datetime.fromtimestamp(date_ms / 1000)

        # Label check: no SENT label in thread → unanswered
        labels  = msg.get("labelIds", [])
        level   = "urgent" if "SENT" not in labels and \
                  (datetime.now() - ts).total_seconds() > config.URGENT_REPLY_HOURS * 3600 \
                  else "info"

        snippet = msg.get("snippet", "")[:200]
        return DigestItem(
            source="gmail",
            level=level,
            title=f"{sender} — {subject}",
            body=snippet,
            timestamp=ts,
            link=f"https://mail.google.com/mail/u/0/#inbox/{msg_id}",
        )
    except Exception as e:
        print(f"[Gmail] error parsing message {msg_id}: {e}")
        return None


def collect() -> list[DigestItem]:
    """Return DigestItems from Gmail for the last 30 minutes."""
    service = _authenticate()
    if service is None:
        return []

    since = int((datetime.now() - timedelta(minutes=config.DIGEST_INTERVAL_MINS)).timestamp())
    query = f"in:inbox after:{since} -category:promotions -category:social"

    try:
        result = service.users().messages().list(userId="me", q=query, maxResults=20).execute()
        messages = result.get("messages", [])
    except Exception as e:
        print(f"[Gmail] API error: {e}")
        return []

    items = []
    for m in messages:
        item = _parse_email(service, m["id"])
        if item:
            items.append(item)
    return items
