import unittest
from datetime import date, datetime

from log_reporter.analysis import analyze_entries, filter_entries
from log_reporter.models import LogEntry


def entry(level, component, message, hour):
    return LogEntry(
        timestamp=datetime(2026, 9, 21, hour, 0, 0),
        level=level,
        component=component,
        message=message,
        line_number=hour,
        raw="sample",
    )


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            entry("INFO", "App", "Started", 8),
            entry("ERROR", "Database", "Timeout", 9),
            entry("ERROR", "Database", "Timeout", 10),
            entry("CRITICAL", "Payments", "Service unavailable", 11),
        ]

    def test_filters_by_level_and_keyword(self):
        filtered = filter_entries(self.entries, level="ERROR", keyword="database")
        self.assertEqual(len(filtered), 2)

    def test_filters_by_date(self):
        filtered = filter_entries(
            self.entries,
            start_date=date(2026, 9, 21),
            end_date=date(2026, 9, 21),
        )
        self.assertEqual(len(filtered), 4)

    def test_critical_incident_has_highest_priority(self):
        result = analyze_entries(
            self.entries,
            "sample.log",
            generated_at=datetime(2026, 9, 21, 12, 0, 0),
        )
        self.assertEqual(result.primary_incident.level, "CRITICAL")
        self.assertEqual(result.primary_incident.component, "Payments")
        self.assertEqual(result.severity_counts["ERROR"], 2)


if __name__ == "__main__":
    unittest.main()
