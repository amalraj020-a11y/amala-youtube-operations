import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "hourly_cloud.py"
SPEC = importlib.util.spec_from_file_location("hourly_cloud", SCRIPT)
hourly = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hourly)


class HourlyCloudTest(unittest.TestCase):
    def test_non_openai_default_and_stable_topic(self):
        self.assertFalse(hourly.MODEL.startswith("openai/"))
        self.assertEqual(hourly.topic_for("2030-01-01T05"), hourly.topic_for("2030-01-01T05"))

    def test_reviewed_fixture_passes_validation(self):
        import json
        fixture = Path(__file__).parent / "fixtures" / "hourly-content.json"
        content = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertEqual(hourly.validate_content(content)["title"], content["title"])


if __name__ == "__main__":
    unittest.main()
