import tempfile
import unittest
from pathlib import Path

from log_reporter.parser import parse_log_file, parse_log_line


class ParserTests(unittest.TestCase):
    def test_parses_valid_line(self):
        entry = parse_log_line(
            "2026-09-21 10:15:44 | CRITICAL | DatabaseService | Pool exhausted",
            7,
        )
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, "CRITICAL")
        self.assertEqual(entry.component, "DatabaseService")
        self.assertEqual(entry.line_number, 7)

    def test_rejects_invalid_line(self):
        self.assertIsNone(parse_log_line("not a valid log entry"))

    def test_counts_malformed_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.log"
            path.write_text(
                "2026-09-21 10:00:00 | INFO | App | Started\ninvalid\n",
                encoding="utf-8",
            )
            entries, malformed = parse_log_file(path)
        self.assertEqual(len(entries), 1)
        self.assertEqual(malformed, 1)


if __name__ == "__main__":
    unittest.main()
