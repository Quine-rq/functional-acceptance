"""Control integrity, not evidence that an agent follows the Skill."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

FIXTURE = Path(__file__).resolve().parents[1] / "evals/handoff/fixture.py"


class HandoffFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="handoff-control-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copyfile(FIXTURE, self.root / "delivery.py")
        (self.root / "state").mkdir()
        (self.root / "artifacts").mkdir()
        (self.root / "document.txt").write_text("交付\nA,B\n", encoding="utf-8")
        (self.root / "original.json").write_text('{"id":"original","tags":["keep"]}')
        self.configure("healthy")

    def configure(self, case):
        (self.root / "fixture.json").write_text(json.dumps({"case": case}))

    def command(self, name, marker="check-1"):
        return subprocess.run([sys.executable, "-B", str(self.root / "delivery.py"), name, marker],
                              cwd=self.root, capture_output=True, text=True, timeout=5)

    def test_uncertain_write_is_completed_once_and_repetition_duplicates(self):
        self.configure("uncertain-write")
        self.assertEqual(self.command("deliver").returncode, 124)
        status = json.loads(self.command("status").stdout)
        self.assertTrue(status["terminal"])
        self.assertEqual(len(status["deliveries"]), 1)
        self.assertEqual(json.loads(self.command("download").stdout)["body"], "交付\nA,B\n")
        self.command("deliver")
        self.assertEqual(len(json.loads(self.command("status").stdout)["deliveries"]), 2)
        self.assertEqual(self.command("download").returncode, 2)

    def test_observer_failure_does_not_break_independent_download_or_original(self):
        self.configure("observer-error")
        original = (self.root / "original.json").read_bytes()
        self.command("deliver")
        self.assertEqual(self.command("preview").returncode, 70)
        self.assertEqual(self.command("download").returncode, 0)
        self.assertEqual(self.command("audit").returncode, 0)
        self.assertEqual((self.root / "original.json").read_bytes(), original)

    def test_snapshot_precedes_action_and_is_not_an_agent_report(self):
        (self.root / "artifacts/plan.md").write_text("before")
        self.command("deliver")
        (self.root / "artifacts/plan.md").write_text("after")
        snapshot = json.loads(next((self.root / "state").glob("*-boundary.json")).read_text())
        self.assertEqual(snapshot["artifacts_before"], {"artifacts/plan.md": "before"})
        self.assertEqual(snapshot["command"], "deliver")

    def test_marker_cannot_be_a_path(self):
        self.assertEqual(self.command("deliver", "../other").returncode, 2)
        self.assertEqual(list((self.root / "state").iterdir()), [])

    def test_hard_kill_retains_delivery_and_stale_audit_without_completion(self):
        self.configure("hard-stop")
        self.command("deliver")
        self.assertEqual(self.command("audit").returncode, 2)
        self.command("download")
        process = subprocess.Popen([sys.executable, "-B", str(self.root / "delivery.py"), "audit", "check-1"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 3
            while not (self.root / "state/audit-active.json").exists() and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertTrue((self.root / "state/audit-active.json").is_file())
            process.kill()
            stdout, _ = process.communicate(timeout=3)
            self.assertNotEqual(process.returncode, 0)
            self.assertNotIn(b'consistent', stdout)
            self.assertEqual(len(json.loads(self.command("status").stdout)["deliveries"]), 1)
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=3)
