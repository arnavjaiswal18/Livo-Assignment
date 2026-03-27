"""
digest.py — Aggregates all collector outputs into a single Digest object.
Handles deduplication, sorting, and urgency classification.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from collectors.models import Digest, DigestItem

# Collectors
from collectors import demo as demo_collector
from collectors import gmail as gmail_collector
from collectors import slack as slack_collector
from collectors import linear as linear_collector
from collectors import calendar as calendar_collector


def _deduplicate(items: list[DigestItem]) -> list[DigestItem]:
    """Remove near-duplicate items by title similarity (exact match on title)."""
    seen = set()
    unique = []
    for item in items:
        key = (item.source, item.title.lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def _sort_items(items: list[DigestItem]) -> list[DigestItem]:
    """Sort by: urgent first, then most recent first."""
    return sorted(items, key=lambda i: (0 if i.level == "urgent" else 1, -i.timestamp.timestamp()))


def build_digest() -> Digest:
    """
    Runs all collectors (or demo data) and assembles a Digest.
    Returns a Digest with .urgent and .info lists.
    """
    raw_items: list[DigestItem] = []

    if config.DEMO_MODE:
        raw_items = demo_collector.get_demo_items()
    else:
        collectors = [
            ("Gmail",    gmail_collector.collect),
            ("Slack",    slack_collector.collect),
            ("Linear",   linear_collector.collect),
            ("Calendar", calendar_collector.collect),
        ]
        for name, fn in collectors:
            try:
                items = fn()
                raw_items.extend(items)
                print(f"[Digest] {name}: {len(items)} item(s) collected.")
            except Exception as e:
                print(f"[Digest] {name} collector failed: {e}")

    raw_items = _deduplicate(raw_items)

    urgent = _sort_items([i for i in raw_items if i.level == "urgent"])
    info   = _sort_items([i for i in raw_items if i.level == "info"])

    return Digest(
        generated_at=datetime.now(),
        urgent=urgent,
        info=info,
    )
