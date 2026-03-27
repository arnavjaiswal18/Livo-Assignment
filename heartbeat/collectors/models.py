"""
models.py — Shared data structures used across all modules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional

Source = Literal["gmail", "slack", "linear", "calendar", "demo"]
Level  = Literal["urgent", "info"]


@dataclass
class DigestItem:
    source:      Source
    level:       Level
    title:       str
    body:        str
    timestamp:   datetime
    link:        Optional[str] = None
    extra:       dict          = field(default_factory=dict)

    def age_minutes(self) -> int:
        return int((datetime.now() - self.timestamp).total_seconds() / 60)


@dataclass
class Digest:
    generated_at: datetime
    urgent:       list[DigestItem] = field(default_factory=list)
    info:         list[DigestItem] = field(default_factory=list)

    @property
    def all_items(self) -> list[DigestItem]:
        return self.urgent + self.info

    @property
    def urgent_count(self) -> int:
        return len(self.urgent)

    @property
    def info_count(self) -> int:
        return len(self.info)
