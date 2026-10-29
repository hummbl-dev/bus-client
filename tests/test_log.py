import unittest
import tempfile
import os

from bus_client.log import append_row, read_rows, search, status, tail


class TestAppendRead(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "log.tsv")

    def test_round_trip(self):
        append_row(self.path, "a", "b", "STATUS", "hello world", timestamp="2026-01-01T00:00:00Z")
        rows = read_rows(self.path)
        self.assertEqual(rows, [("2026-01-01T00:00:00Z", "a", "b", "STATUS", "hello world")])

    def test_message_escaping(self):
        msg = "line1\nline2\twith tab"
        append_row(self.path, "a", "b", "STATUS", msg, timestamp="2026-01-01T00:00:00Z")
        self.assertEqual(read_rows(self.path)[0][4], msg)

    def test_tail(self):
        for i in range(10):
            append_row(self.path, "a", "b", "STATUS", f"m{i}", timestamp=f"2026-01-01T00:00:{i:02d}Z")
        self.assertEqual(len(tail(self.path, 3)), 3)
        self.assertEqual(tail(self.path, 3)[-1][4], "m9")

    def test_search_case_insensitive(self):
        append_row(self.path, "a", "b", "STATUS", "Hello World", timestamp="2026-01-01T00:00:00Z")
        self.assertEqual(len(search(self.path, "hello")), 1)
        self.assertEqual(len(search(self.path, "missing")), 0)

    def test_status(self):
        append_row(self.path, "a", "b", "STATUS", "x", timestamp="2026-01-01T00:00:00Z")
        s = status(self.path)
        self.assertEqual(s["lines"], 1)
        self.assertEqual(s["last_timestamp"], "2026-01-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
