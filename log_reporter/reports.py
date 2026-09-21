import csv
import json
from pathlib import Path

from .models import AnalysisResult, Incident, LogEntry


def _timestamp(value) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _incident_dict(incident: Incident) -> dict:
    return {
        "level": incident.level,
        "component": incident.component,
        "message": incident.message,
        "occurrences": incident.occurrences,
        "first_seen": _timestamp(incident.first_seen),
        "last_seen": _timestamp(incident.last_seen),
    }


def _entry_dict(entry: LogEntry) -> dict:
    return {
        "timestamp": _timestamp(entry.timestamp),
        "level": entry.level,
        "component": entry.component,
        "message": entry.message,
        "line_number": entry.line_number,
    }


def write_markdown(result: AnalysisResult, destination: str | Path) -> Path:
    path = Path(destination)
    primary = result.primary_incident
    lines = [
        "# Incident Analysis Report",
        "",
        f"- **Generated:** {_timestamp(result.generated_at)}",
        f"- **Source:** `{result.source}`",
        f"- **Valid entries analyzed:** {result.total_entries}",
        f"- **Malformed lines skipped:** {result.malformed_lines}",
        "",
        "## Executive Summary",
        "",
        (
            f"The analyzer processed {result.total_entries} valid entries and detected "
            f"{result.severity_counts.get('WARNING', 0)} warnings, "
            f"{result.severity_counts.get('ERROR', 0)} errors, and "
            f"{result.severity_counts.get('CRITICAL', 0)} critical events."
        ),
        "",
        "## Severity Breakdown",
        "",
        "| Severity | Count |",
        "|---|---:|",
    ]
    for level in ("INFO", "WARNING", "ERROR", "CRITICAL"):
        lines.append(f"| {level} | {result.severity_counts.get(level, 0)} |")

    lines.extend(["", "## Primary Incident", ""])
    if primary:
        lines.extend(
            [
                f"- **Priority:** {primary.level}",
                f"- **Component:** {primary.component}",
                f"- **Occurrences:** {primary.occurrences}",
                f"- **First detected:** {_timestamp(primary.first_seen)}",
                f"- **Last detected:** {_timestamp(primary.last_seen)}",
                f"- **Message:** {primary.message}",
                "",
                f"**Recommended action:** Investigate `{primary.component}` first because it contains the highest-priority repeated incident.",
            ]
        )
    else:
        lines.append("No warning, error, or critical incident was detected.")

    lines.extend(
        [
            "",
            "## Incident Groups",
            "",
            "| Severity | Component | Occurrences | First seen | Last seen | Message |",
            "|---|---|---:|---|---|---|",
        ]
    )
    if result.incidents:
        for incident in result.incidents:
            safe_message = incident.message.replace("|", "\\|")
            lines.append(
                f"| {incident.level} | {incident.component} | {incident.occurrences} | "
                f"{_timestamp(incident.first_seen)} | {_timestamp(incident.last_seen)} | {safe_message} |"
            )
    else:
        lines.append("| - | - | 0 | - | - | No incidents |")

    lines.extend(["", "## Event Timeline", ""])
    relevant_entries = [entry for entry in result.entries if entry.level != "INFO"]
    if relevant_entries:
        for entry in relevant_entries:
            lines.append(
                f"- `{_timestamp(entry.timestamp)}` **{entry.level}** "
                f"`{entry.component}` - {entry.message}"
            )
    else:
        lines.append("No warning, error, or critical events to display.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_json(result: AnalysisResult, destination: str | Path) -> Path:
    path = Path(destination)
    payload = {
        "generated_at": _timestamp(result.generated_at),
        "source": result.source,
        "total_entries": result.total_entries,
        "malformed_lines": result.malformed_lines,
        "severity_counts": result.severity_counts,
        "component_counts": result.component_counts,
        "primary_incident": _incident_dict(result.primary_incident) if result.primary_incident else None,
        "incidents": [_incident_dict(item) for item in result.incidents],
        "entries": [_entry_dict(item) for item in result.entries],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_csv(result: AnalysisResult, destination: str | Path) -> Path:
    path = Path(destination)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["level", "component", "message", "occurrences", "first_seen", "last_seen"],
        )
        writer.writeheader()
        writer.writerows(_incident_dict(item) for item in result.incidents)
    return path


def generate_reports(
    result: AnalysisResult,
    output_dir: str | Path,
    formats: list[str],
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    stem = f"{Path(result.source).stem}-incident-report"
    writers = {
        "markdown": (write_markdown, directory / f"{stem}.md"),
        "json": (write_json, directory / f"{stem}.json"),
        "csv": (write_csv, directory / f"{stem}.csv"),
    }
    selected = list(writers) if "all" in formats else formats
    return [writers[name][0](result, writers[name][1]) for name in selected]
