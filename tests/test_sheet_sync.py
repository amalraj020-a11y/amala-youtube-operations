import json
import shutil
import tempfile
import unittest
from pathlib import Path

import amala_youtube as app
import sheet_sync


class Reply:
    def __init__(self, data):
        self.data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self.data


class FakeSession:
    def __init__(self):
        self.rows = [sheet_sync.HEADERS[:]]
        self.actions = []
    def request(self, method, url, **kwargs):
        if method == "GET":
            return Reply({"values": self.rows})
        self.actions.append(method)
        if method == "POST":
            self.rows.extend(kwargs["json"]["values"])
        elif method == "PUT":
            self.rows[1] = kwargs["json"]["values"][0]
        return Reply({})


class SheetSyncTest(unittest.TestCase):
    def test_retry_updates_same_row(self):
        original_app_root, original_sync_root, original_queue = app.ROOT, sheet_sync.ROOT, sheet_sync.QUEUE
        temp_root = Path(__file__).parent / ".tmp"
        temp_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as directory:
            root = Path(directory)
            try:
                app.ROOT = sheet_sync.ROOT = root
                sheet_sync.QUEUE = root / "data" / "sheet-queue.jsonl"
                shutil.copy2(original_sync_root / "schedule.csv", root / "schedule.csv")
                app.record("2099-01-03", "research", "IN_PROGRESS")
                fake = FakeSession()
                self.assertEqual(sheet_sync.sync("dummy", fake), 1)
                app.record("2099-01-03", "research", "FAILED", "Test failure")
                self.assertEqual(sheet_sync.sync("dummy", fake), 1)
                self.assertEqual(len(fake.rows), 2)
                self.assertEqual(fake.rows[1][10], "FAILED")
                self.assertEqual(fake.actions, ["POST", "PUT"])
            finally:
                app.ROOT, sheet_sync.ROOT, sheet_sync.QUEUE = original_app_root, original_sync_root, original_queue


if __name__ == "__main__":
    unittest.main()
