import csv
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from log_reporter.analysis import analyze_entries
from log_reporter.models import LogEntry
from log_reporter.reports import generate_reports


class ReportTests(unittest.TestCase):
    def test_generates_all_formats(self):
        entries = [
            LogEntry(
                timestamp=datetime(2026, 9, 21, 10, 0, 0),
                level="ERROR",
                component="Database",
                message="Connection timeout",
                line_number=1,
                raw="sample",
            )
        ]
        result = analyze_entries(
            entries,
            "sample.log",
            generated_at=datetime(2026, 9, 21, 11, 0, 0),
        )
        with tempfile.TemporaryDirectory() as directory:
            paths = generate_reports(result, directory, ["all"])
            self.assertEqual({path.suffix for path in paths}, {".md", ".json", ".csv"})
            payload = json.loads(next(path for path in paths if path.suffix == ".json").read_text())
            self.assertEqual(payload["total_entries"], 1)
            with next(path for path in paths if path.suffix == ".csv").open(newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(rows[0]["component"], "Database")
            markdown = next(path for path in paths if path.suffix == ".md").read_text()
            self.assertIn("# Incident Analysis Report", markdown)


if __name__ == "__main__":
    unittest.main()
