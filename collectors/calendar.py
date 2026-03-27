"""
calendar.py — Fetches upcoming Google Calendar events.
Events within UPCOMING_MEETING_MINS → urgent; further out → info.
"""

import os
import pickle
import sys
from datetime import datetime, timezone, timedelta
from typing import Optional

from .models import DigestItem
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _authenticate() -> Optional[object]:
    try:
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print("[Calendar] google-api packages not installed — skipping.")
        return None

    creds = None
    if os.path.exists(config.GCAL_TOKEN_FILE):
        with open(config.GCAL_TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(config.GCAL_CREDENTIALS_FILE):
                print("[Calendar] credentials file not found — skipping.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                config.GCAL_CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(config.GCAL_TOKEN_FILE), exist_ok=True)
        with open(config.GCAL_TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("calendar", "v3", credentials=creds)


def collect() -> list[DigestItem]:
    """Return upcoming calendar events as DigestItems."""
    service = _authenticate()
    if service is None:
        return []

    now     = datetime.now(timezone.utc)
    window  = now + timedelta(minutes=config.UPCOMING_MEETING_MINS)

    try:
        result = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=window.isoformat(),
            singleEvents=True,
            orderBy="startTime",
            maxResults=10,
        ).execute()
        events = result.get("items", [])
    except Exception as e:
        print(f"[Calendar] API error: {e}")
        return []

    items = []
    for event in events:
        start_raw = event["start"].get("dateTime") or event["start"].get("date")
        try:
            ts = datetime.fromisoformat(start_raw.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            ts = datetime.now()

        mins_until = (ts - datetime.now()).total_seconds() / 60
        level      = "urgent" if mins_until <= 30 else "info"

        description = event.get("description", "") or ""
        summary     = event.get("summary", "Untitled Event")
        body        = description[:200] if description else f"Starts in {int(mins_until)} min"
        link        = event.get("htmlLink")

        items.append(DigestItem(
            source="calendar",
            level=level,
            title=summary,
            body=body,
            timestamp=ts,
            link=link,
        ))

    return items
