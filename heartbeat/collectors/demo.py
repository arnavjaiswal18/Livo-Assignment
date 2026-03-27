"""
demo.py — Realistic mock data used when DEMO_MODE=true.
No API keys required; lets the dashboard run out-of-the-box.
"""

from datetime import datetime, timedelta
from .models import DigestItem


def get_demo_items() -> list[DigestItem]:
    now = datetime.now()

    return [
        # ── URGENT ────────────────────────────────────────────────────────────
        DigestItem(
            source="gmail",
            level="urgent",
            title="Priya Mehta (Acme Corp) — Re: Q2 Proposal",
            body="Hi, just wanted to follow up on the proposal we discussed. Can we hop on a quick call today? Happy to move fast on this.",
            timestamp=now - timedelta(hours=3, minutes=12),
            link="https://mail.google.com",
        ),
        DigestItem(
            source="slack",
            level="urgent",
            title="DM from James (Horizon Tech) — Staging broken",
            body="Hey, the staging env we demoed yesterday is throwing 502s. Client is watching this. Need someone on it ASAP.",
            timestamp=now - timedelta(minutes=18),
            link="https://slack.com",
        ),
        DigestItem(
            source="linear",
            level="urgent",
            title="[Blocked] Integrate payment gateway — Horizon Tech",
            body="Blocked: waiting on Stripe test credentials from client. No progress possible until received.",
            timestamp=now - timedelta(minutes=45),
            link="https://linear.app",
        ),
        DigestItem(
            source="calendar",
            level="urgent",
            title="Sync call — Acme Corp leadership",
            body="30-min check-in with Priya Mehta & CEO. Zoom link in invite.",
            timestamp=now + timedelta(minutes=35),
            link="https://calendar.google.com",
        ),
        # ── INFORMATIONAL ─────────────────────────────────────────────────────
        DigestItem(
            source="linear",
            level="info",
            title="[Done] Design handoff — Acme Corp dashboard",
            body="Sarah completed the Figma handoff for the analytics dashboard. Dev can now start implementation.",
            timestamp=now - timedelta(minutes=22),
            link="https://linear.app",
        ),
        DigestItem(
            source="gmail",
            level="info",
            title="Marcus Webb (Orbit SaaS) — NDA signed",
            body="Please find the signed NDA attached. Looking forward to kicking things off next week.",
            timestamp=now - timedelta(hours=1, minutes=5),
            link="https://mail.google.com",
        ),
        DigestItem(
            source="slack",
            level="info",
            title="#general — Sprint planning reminder",
            body="Team reminder: sprint planning at 4pm today. Drop blockers in the thread before then.",
            timestamp=now - timedelta(minutes=10),
            link="https://slack.com",
        ),
        DigestItem(
            source="linear",
            level="info",
            title="[In Progress] Auth module — Orbit SaaS",
            body="Dev picked up the auth task. ETA end of day.",
            timestamp=now - timedelta(minutes=50),
            link="https://linear.app",
        ),
        DigestItem(
            source="calendar",
            level="info",
            title="Team standup",
            body="Daily standup — internal only, 15 min.",
            timestamp=now + timedelta(hours=1, minutes=45),
            link="https://calendar.google.com",
        ),
    ]
