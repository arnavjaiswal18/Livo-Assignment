"""
linear.py — Fetches recently changed Linear issues via the GraphQL API.
Flags blocked issues as urgent; done/in-progress as informational.
"""

import os
import sys
from datetime import datetime, timedelta

from .models import DigestItem
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

LINEAR_API = "https://api.linear.app/graphql"

QUERY = """
query RecentIssues($since: DateTime) {
  issues(
    filter: { updatedAt: { gt: $since } }
    orderBy: updatedAt
    first: 30
  ) {
    nodes {
      id
      title
      state { name type }
      team  { name }
      updatedAt
      url
      description
    }
  }
}
"""

# State types that map to urgent
URGENT_STATES = {"blocked", "cancelled"}
# State names that we surface (avoids surfacing trivial backlog noise)
SKIP_STATE_TYPES = {"backlog", "triage"}


def collect() -> list[DigestItem]:
    """Return DigestItems from Linear for the last 30 minutes."""
    if not config.LINEAR_API_KEY:
        print("[Linear] LINEAR_API_KEY not set — skipping.")
        return []

    try:
        import requests
    except ImportError:
        print("[Linear] requests not installed — skipping.")
        return []

    since = (datetime.utcnow() - timedelta(minutes=config.DIGEST_INTERVAL_MINS)).isoformat() + "Z"
    headers = {
        "Authorization": config.LINEAR_API_KEY,
        "Content-Type":  "application/json",
    }
    payload = {"query": QUERY, "variables": {"since": since}}

    try:
        resp = requests.post(LINEAR_API, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[Linear] API error: {e}")
        return []

    issues = data.get("data", {}).get("issues", {}).get("nodes", [])
    items  = []

    for issue in issues:
        state_type = (issue.get("state") or {}).get("type", "").lower()
        state_name = (issue.get("state") or {}).get("name", "Unknown")
        team_name  = (issue.get("team")  or {}).get("name", "")

        if state_type in SKIP_STATE_TYPES:
            continue

        is_blocked = "blocked" in state_name.lower() or state_type in URGENT_STATES
        level      = "urgent" if is_blocked else "info"

        body = (issue.get("description") or "")[:200].strip() or f"State changed to: {state_name}"
        ts   = datetime.fromisoformat(issue["updatedAt"].replace("Z", "+00:00")).replace(tzinfo=None)

        items.append(DigestItem(
            source="linear",
            level=level,
            title=f"[{state_name}] {issue['title']} — {team_name}",
            body=body,
            timestamp=ts,
            link=issue.get("url"),
        ))

    return items
