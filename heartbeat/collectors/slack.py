"""
slack.py — Collects recent DMs and starred-channel messages via Slack SDK.
Scoped to DMs + starred channels only (avoids noise from all channels).
"""

import os
import sys
from datetime import datetime, timedelta

from .models import DigestItem
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def _ts_to_dt(ts: str) -> datetime:
    return datetime.fromtimestamp(float(ts))


def collect() -> list[DigestItem]:
    """Return DigestItems from Slack for the last 30 minutes."""
    if not config.SLACK_BOT_TOKEN:
        print("[Slack] SLACK_BOT_TOKEN not set — skipping.")
        return []

    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
    except ImportError:
        print("[Slack] slack-sdk not installed — skipping.")
        return []

    client   = WebClient(token=config.SLACK_BOT_TOKEN)
    since_ts = str((datetime.now() - timedelta(minutes=config.DIGEST_INTERVAL_MINS)).timestamp())
    items    = []

    # ── DMs ───────────────────────────────────────────────────────────────────
    try:
        convs = client.conversations_list(types="im", limit=20)
        for ch in convs["channels"]:
            history = client.conversations_history(
                channel=ch["id"], oldest=since_ts, limit=10
            )
            for msg in history.get("messages", []):
                if msg.get("subtype"):
                    continue
                user_info = client.users_info(user=msg.get("user", ""))
                name = user_info["user"]["real_name"] if user_info["ok"] else "Unknown"
                ts   = _ts_to_dt(msg["ts"])
                items.append(DigestItem(
                    source="slack",
                    level="urgent",
                    title=f"DM from {name}",
                    body=msg.get("text", "")[:200],
                    timestamp=ts,
                    link=f"https://slack.com/app_redirect?channel={ch['id']}",
                ))
    except SlackApiError as e:
        print(f"[Slack] DM fetch error: {e.response['error']}")

    # ── Starred channels ──────────────────────────────────────────────────────
    try:
        starred = client.stars_list(limit=20)
        channel_ids = {
            item["channel"] for item in starred.get("items", [])
            if item.get("type") == "channel"
        }
        for cid in channel_ids:
            try:
                info    = client.conversations_info(channel=cid)
                ch_name = info["channel"]["name"]
                history = client.conversations_history(
                    channel=cid, oldest=since_ts, limit=5
                )
                for msg in history.get("messages", []):
                    if msg.get("subtype"):
                        continue
                    ts = _ts_to_dt(msg["ts"])
                    items.append(DigestItem(
                        source="slack",
                        level="info",
                        title=f"#{ch_name}",
                        body=msg.get("text", "")[:200],
                        timestamp=ts,
                        link=f"https://slack.com/app_redirect?channel={cid}",
                    ))
            except SlackApiError:
                pass
    except SlackApiError as e:
        print(f"[Slack] starred-channels error: {e.response['error']}")

    return items
