import re
from pathlib import Path

from .models import LogEntry


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\|\s*"
    r"(?P<level>INFO|WARNING|ERROR|CRITICAL)\s*\|\s*"
    r"(?P<component>[^|]+?)\s*\|\s*(?P<message>.+)$",
    re.IGNORECASE,
)


def parse_log_line(line: str, line_number: int = 1) -> LogEntry | None:
    """Parse one pipe-delimited log line, returning None when invalid."""
    from datetime import datetime

    raw = line.rstrip("\r\n")
    match = LOG_PATTERN.match(raw)
    if not match:
        return None

    try:
        timestamp = datetime.strptime(match.group("timestamp"), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

    return LogEntry(
        timestamp=timestamp,
        level=match.group("level").upper(),
        component=match.group("component").strip(),
        message=match.group("message").strip(),
        line_number=line_number,
        raw=raw,
    )


def parse_log_file(path: str | Path) -> tuple[list[LogEntry], int]:
    """Parse a UTF-8 log file and return valid entries and malformed count."""
    log_path = Path(path)
    entries: list[LogEntry] = []
    malformed = 0

    with log_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            entry = parse_log_line(line, line_number)
            if entry is None:
                malformed += 1
            else:
                entries.append(entry)

    return entries, malformed
