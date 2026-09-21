from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

from .models import AnalysisResult, Incident, LogEntry


SEVERITY_ORDER = {"CRITICAL": 4, "ERROR": 3, "WARNING": 2, "INFO": 1}


def filter_entries(
    entries: list[LogEntry],
    level: str | None = None,
    keyword: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[LogEntry]:
    """Filter entries without modifying the original list."""
    normalized_level = level.upper() if level else None
    normalized_keyword = keyword.casefold() if keyword else None

    return [
        entry
        for entry in entries
        if (not normalized_level or entry.level == normalized_level)
        and (
            not normalized_keyword
            or normalized_keyword in entry.message.casefold()
            or normalized_keyword in entry.component.casefold()
        )
        and (not start_date or entry.timestamp.date() >= start_date)
        and (not end_date or entry.timestamp.date() <= end_date)
    ]


def analyze_entries(
    entries: list[LogEntry],
    source: str | Path,
    malformed_lines: int = 0,
    generated_at: datetime | None = None,
) -> AnalysisResult:
    """Aggregate severity, component, and repeated-incident statistics."""
    severity_counts = Counter(entry.level for entry in entries)
    component_counts = Counter(entry.component for entry in entries)
    grouped: dict[tuple[str, str, str], list[LogEntry]] = defaultdict(list)

    for entry in entries:
        if entry.level in {"WARNING", "ERROR", "CRITICAL"}:
            grouped[(entry.level, entry.component, entry.message)].append(entry)

    incidents = [
        Incident(
            level=level,
            component=component,
            message=message,
            occurrences=len(group),
            first_seen=min(item.timestamp for item in group),
            last_seen=max(item.timestamp for item in group),
        )
        for (level, component, message), group in grouped.items()
    ]
    incidents.sort(
        key=lambda item: (
            SEVERITY_ORDER[item.level],
            item.occurrences,
            item.last_seen,
        ),
        reverse=True,
    )

    return AnalysisResult(
        source=str(source),
        entries=sorted(entries, key=lambda item: item.timestamp),
        incidents=incidents,
        severity_counts=dict(severity_counts),
        component_counts=dict(component_counts),
        malformed_lines=malformed_lines,
        generated_at=generated_at or datetime.now(),
    )
