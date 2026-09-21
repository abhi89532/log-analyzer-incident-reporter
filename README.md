# Log Analyzer and Incident Report Generator

A command-line Python application that parses structured log files, detects repeated incidents, prioritizes critical failures, and generates professional Markdown, JSON, and CSV reports.

## Features

- Parses timestamped INFO, WARNING, ERROR, and CRITICAL entries
- Filters events by severity, keyword, and date range
- Counts malformed lines without stopping the analysis
- Groups repeated incidents by severity, component, and message
- Prioritizes incidents using severity and occurrence count
- Produces an executive summary and chronological event timeline
- Generates Markdown, JSON, and CSV reports
- Uses only the Python standard library
- Includes automated unit tests

## Expected log format

```text
YYYY-MM-DD HH:MM:SS | LEVEL | Component | Message
```

Example:

```text
2026-09-21 10:15:44 | CRITICAL | DatabaseService | Database connection pool exhausted
```

## Project structure

```text
log-analyzer-incident-reporter/
├── log_analyzer.py
├── log_reporter/
│   ├── __init__.py
│   ├── analysis.py
│   ├── models.py
│   ├── parser.py
│   └── reports.py
├── sample_logs/
│   └── application.log
├── tests/
│   ├── test_analysis.py
│   ├── test_parser.py
│   └── test_reports.py
├── .gitignore
├── LICENSE
└── README.md
```

## Requirements

- Python 3.10 or newer
- No third-party packages

## Run the analyzer

Analyze the included sample log and create every report format:

```bash
python log_analyzer.py sample_logs/application.log
```

Generated files are written to `reports/`.

## Filtering examples

Only critical entries:

```bash
python log_analyzer.py sample_logs/application.log --level CRITICAL
```

Entries containing a component or message keyword:

```bash
python log_analyzer.py sample_logs/application.log --keyword database
```

Entries within a date range:

```bash
python log_analyzer.py sample_logs/application.log --start-date 2026-09-20 --end-date 2026-09-21
```

Generate only Markdown and JSON:

```bash
python log_analyzer.py sample_logs/application.log --format markdown --format json
```

Display all options:

```bash
python log_analyzer.py --help
```

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Generated reports

- **Markdown:** Human-readable incident report for GitHub or documentation
- **JSON:** Structured output for another application or API
- **CSV:** Incident summary for Excel or spreadsheet analysis

The `reports/` directory is excluded from Git because reports may contain sensitive production information.

## Skills demonstrated

- Python programming
- Object-oriented data modeling
- Regular expressions
- File and datetime processing
- Command-line interface design
- JSON and CSV serialization
- Data aggregation and incident prioritization
- Automated testing
- Defensive error handling

## License

This project is available under the MIT License.
