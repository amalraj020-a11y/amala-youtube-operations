import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import amala_youtube as app


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.temp_root = Path(__file__).parent / ".tmp"
        self.temp_root.mkdir(exist_ok=True)

    def test_failed_stage_preserves_completed_work_and_can_resume(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as directory:
            date = "2099-01-01"
            fixtures = Path(__file__).parent / "fixtures"
            def stage(name, *options):
                return subprocess.run([sys.executable, str(Path(app.__file__)), "stage", date, name, *options], capture_output=True, text=True, env={**os.environ, "AMALA_ROOT": directory})
            first = stage("research", "--research-file", str(fixtures / "research.md"))
            self.assertEqual(first.returncode, 0, first.stderr)
            failed = stage("script")
            self.assertEqual(failed.returncode, 1)
            progress = json.loads((Path(directory) / "youtube" / date / "progress.json").read_text(encoding="utf-8"))
            self.assertEqual(progress["stages"]["research"]["status"], "COMPLETED")
            self.assertEqual(progress["stages"]["script"]["retry_count"], 1)
            recovered = stage("script", "--script-file", str(fixtures / "script.md"), "--storyboard-file", str(fixtures / "storyboard.csv"))
            self.assertEqual(recovered.returncode, 0, recovered.stderr)
            skipped = stage("script")
            self.assertEqual(skipped.returncode, 0)
            self.assertIn("already completed", skipped.stdout)

    def test_technical_media_pipeline(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as directory:
            date = "2099-01-02"
            fixtures = Path(__file__).parent / "fixtures"
            wav = Path(directory) / "test-tone.wav"
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=6", str(wav)], check=True)
            def stage(name, *options):
                result = subprocess.run([sys.executable, str(Path(app.__file__)), "stage", date, name, *options], capture_output=True, text=True, env={**os.environ, "AMALA_ROOT": directory})
                self.assertEqual(result.returncode, 0, f"{name}: {result.stderr}")
            stage("research", "--research-file", str(fixtures / "research.md"))
            stage("script", "--script-file", str(fixtures / "script.md"), "--storyboard-file", str(fixtures / "storyboard.csv"))
            stage("voice", "--voice-file", str(wav))
            stage("graphics")
            stage("assemble")
            stage("qa")
            stage("metadata", "--title", "TECHNICAL TEST - DO NOT UPLOAD")
            output = Path(directory) / "youtube" / date
            info = app.probe(output / "draft.mp4")
            self.assertEqual({s["codec_type"] for s in info["streams"]}, {"video", "audio"})
            self.assertIn("PENDING HUMAN REVIEW", (output / "qa-checklist.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
