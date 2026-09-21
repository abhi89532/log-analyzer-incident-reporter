from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    level: str
    component: str
    message: str
    line_number: int
    raw: str


@dataclass(frozen=True)
class Incident:
    level: str
    component: str
    message: str
    occurrences: int
    first_seen: datetime
    last_seen: datetime


@dataclass(frozen=True)
class AnalysisResult:
    source: str
    entries: list[LogEntry]
    incidents: list[Incident]
    severity_counts: dict[str, int]
    component_counts: dict[str, int]
    malformed_lines: int
    generated_at: datetime

    @property
    def total_entries(self) -> int:
        return len(self.entries)

    @property
    def primary_incident(self) -> Incident | None:
        return self.incidents[0] if self.incidents else None
