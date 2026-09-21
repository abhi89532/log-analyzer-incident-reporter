import argparse
import sys
from datetime import date
from pathlib import Path

from log_reporter.analysis import analyze_entries, filter_entries
from log_reporter.parser import parse_log_file
from log_reporter.reports import generate_reports


LEVELS = ["INFO", "WARNING", "ERROR", "CRITICAL"]


def iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use YYYY-MM-DD format.") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze structured logs and generate incident reports."
    )
    parser.add_argument("log_file", help="Path to the .log or .txt input file")
    parser.add_argument("--level", choices=LEVELS, help="Include only one severity level")
    parser.add_argument("--keyword", help="Filter by a message or component keyword")
    parser.add_argument("--start-date", type=iso_date, help="First date to include (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=iso_date, help="Last date to include (YYYY-MM-DD)")
    parser.add_argument("--output-dir", default="reports", help="Directory for generated reports")
    parser.add_argument(
        "--format",
        dest="formats",
        action="append",
        choices=["markdown", "json", "csv", "all"],
        default=None,
        help="Output format; repeat for multiple formats (default: all)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log_path = Path(args.log_file)
    if not log_path.is_file():
        print(f"Error: log file not found: {log_path}", file=sys.stderr)
        return 2
    if args.start_date and args.end_date and args.start_date > args.end_date:
        print("Error: start date must not be after end date.", file=sys.stderr)
        return 2

    try:
        entries, malformed = parse_log_file(log_path)
    except (OSError, UnicodeError) as exc:
        print(f"Error: could not read {log_path}: {exc}", file=sys.stderr)
        return 2

    filtered = filter_entries(
        entries,
        level=args.level,
        keyword=args.keyword,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    result = analyze_entries(filtered, source=log_path, malformed_lines=malformed)
    paths = generate_reports(result, args.output_dir, args.formats or ["all"])

    print("Log analysis complete")
    print(f"Valid entries analyzed: {result.total_entries}")
    print(f"Malformed lines skipped: {result.malformed_lines}")
    print(f"Warnings: {result.severity_counts.get('WARNING', 0)}")
    print(f"Errors: {result.severity_counts.get('ERROR', 0)}")
    print(f"Critical events: {result.severity_counts.get('CRITICAL', 0)}")
    if result.primary_incident:
        print(
            "Primary incident: "
            f"[{result.primary_incident.level}] {result.primary_incident.component} - "
            f"{result.primary_incident.message} ({result.primary_incident.occurrences} occurrences)"
        )
    print("Generated reports:")
    for path in paths:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
