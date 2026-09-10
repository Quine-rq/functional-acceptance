"""Development-only write-once invocation ledger behavior."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "evals" / "harness" / "run_once.py"


class InvocationLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="invocation-ledger-")
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.project.mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def invoke(self, run_root, code, *, timeout="2", limit="1024"):
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(RUNNER),
                "--run-root",
                str(run_root),
                "--run-id",
                "run-001",
                "--cwd",
                str(self.project),
                "--timeout-seconds",
                timeout,
                "--max-capture-bytes",
                limit,
                "--",
                sys.executable,
                "-c",
                code,
            ],
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_completed_command_has_write_once_correlated_record(self):
        run_root = self.root / "run"
        run_root.mkdir()
        result = self.invoke(run_root, "import sys; print('out'); print('err', file=sys.stderr)")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        attempt = run_root / "attempt-1"
        claim = json.loads((run_root / ".invocation-claim.json").read_text())
        intent = json.loads((attempt / "intent.json").read_text())
        handle = json.loads((attempt / "process-handle.json").read_text())
        execution = json.loads((attempt / "execution.json").read_text())

        self.assertEqual(claim["run_id"], "run-001")
        self.assertEqual(intent["argv"], [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"])
        resolved_project = str(self.project.resolve())
        self.assertEqual(intent["cwd"], resolved_project)
        self.assertEqual(execution["cwd"], resolved_project)
        self.assertEqual(handle["pid"], execution["pid"])
        self.assertTrue(execution["process_started"])
        self.assertTrue(execution["process_terminated"])
        self.assertEqual(execution["exit_code"], 0)
        self.assertFalse(execution["timed_out"])
        self.assertEqual((attempt / "stdout.bin").read_bytes(), b"out\n")
        self.assertEqual((attempt / "stderr.bin").read_bytes(), b"err\n")
        self.assertEqual(execution["stdout"]["total_bytes"], 4)
        self.assertEqual(execution["runner_sha256"], hashlib.sha256(RUNNER.read_bytes()).hexdigest())
        self.assertEqual(execution["stdout"]["sha256"], hashlib.sha256(b"out\n").hexdigest())
        self.assertEqual(execution["stderr"]["sha256"], hashlib.sha256(b"err\n").hexdigest())

    def test_nonzero_product_exit_is_recorded_and_returned(self):
        run_root = self.root / "run"
        run_root.mkdir()
        result = self.invoke(run_root, "import sys; sys.exit(7)")
        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        execution = json.loads((run_root / "attempt-1/execution.json").read_text())
        self.assertEqual(execution["exit_code"], 7)
        self.assertTrue(execution["process_started"])
        self.assertTrue(execution["process_terminated"])
        self.assertFalse(execution["timed_out"])
        self.assertIsNone(execution["observer_error"])

    def test_second_invocation_is_refused_before_product_start(self):
        run_root = self.root / "run"
        run_root.mkdir()
        marker = self.project / "marker"
        code = f"from pathlib import Path; p=Path({str(marker)!r}); p.write_text(p.read_text()+'x' if p.exists() else 'x')"
        first = self.invoke(run_root, code)
        original_claim = (run_root / ".invocation-claim.json").read_bytes()
        second = self.invoke(run_root, code)
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 125)
        self.assertEqual(marker.read_text(), "x")
        self.assertEqual((run_root / ".invocation-claim.json").read_bytes(), original_claim)

    def test_orphaned_claim_is_refused_without_guessing_or_retrying(self):
        run_root = self.root / "run"
        run_root.mkdir()
        original_claim = b'{"run_id":"crashed-before-attempt"}\n'
        (run_root / ".invocation-claim.json").write_bytes(original_claim)
        marker = self.project / "must-not-run"
        result = self.invoke(run_root, f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')")
        self.assertEqual(result.returncode, 125)
        self.assertFalse(marker.exists())
        self.assertEqual((run_root / ".invocation-claim.json").read_bytes(), original_claim)
        self.assertFalse((run_root / "attempt-1").exists())

    def test_concurrent_calls_start_exactly_one_product(self):
        run_root = self.root / "run"
        run_root.mkdir()
        marker = self.project / "marker"
        code = f"import time; from pathlib import Path; Path({str(marker)!r}).write_text('started'); time.sleep(.2)"
        command = [
            sys.executable, "-B", str(RUNNER), "--run-root", str(run_root),
            "--run-id", "run-001", "--cwd", str(self.project), "--", sys.executable, "-c", code,
        ]
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        for process in processes:
            process.communicate(timeout=10)
        self.assertEqual(sorted(process.returncode for process in processes), [0, 125])
        self.assertEqual(marker.read_text(), "started")

    def test_timeout_stops_owned_descendant_before_delayed_write(self):
        run_root = self.root / "run"
        run_root.mkdir()
        marker = self.project / "late-marker"
        child = f"import time; from pathlib import Path; time.sleep(.6); Path({str(marker)!r}).write_text('late')"
        code = f"import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',{child!r}]); time.sleep(10)"
        result = self.invoke(run_root, code, timeout="0.1")
        self.assertEqual(result.returncode, 124, result.stdout + result.stderr)
        execution = json.loads((run_root / "attempt-1/execution.json").read_text())
        self.assertTrue(execution["timed_out"])
        self.assertTrue(execution["process_terminated"])
        time.sleep(.8)
        self.assertFalse(marker.exists())

    def test_successful_parent_with_live_descendant_is_not_reported_clean(self):
        run_root = self.root / "run"
        run_root.mkdir()
        marker = self.project / "late-marker"
        child = f"import time; from pathlib import Path; time.sleep(.6); Path({str(marker)!r}).write_text('late')"
        code = f"import subprocess,sys; subprocess.Popen([sys.executable,'-c',{child!r}])"
        result = self.invoke(run_root, code)
        self.assertEqual(result.returncode, 125, result.stdout + result.stderr)
        execution = json.loads((run_root / "attempt-1/execution.json").read_text())
        self.assertEqual(execution["exit_code"], 0)
        self.assertTrue(execution["descendants_found_after_parent"])
        self.assertEqual(execution["closure_status"], "descendant_cleanup_required")
        self.assertEqual(execution["runner_exit_code"], 125)
        self.assertTrue(execution["process_terminated"])
        time.sleep(.8)
        self.assertFalse(marker.exists())

    def test_output_prefix_is_bounded_and_truncation_is_visible(self):
        run_root = self.root / "run"
        run_root.mkdir()
        result = self.invoke(run_root, "import sys; print('a'*100, end=''); print('b'*90, end='', file=sys.stderr)", limit="32")
        self.assertEqual(result.returncode, 0)
        execution = json.loads((run_root / "attempt-1/execution.json").read_text())
        self.assertEqual(len((run_root / "attempt-1/stdout.bin").read_bytes()), 32)
        self.assertEqual(execution["stdout"]["total_bytes"], 100)
        self.assertEqual(execution["stdout"]["retained_bytes"], 32)
        self.assertTrue(execution["stdout"]["truncated"])
        self.assertEqual(execution["stdout"]["sha256"], hashlib.sha256(b"a" * 100).hexdigest())
        self.assertEqual(execution["stderr"]["total_bytes"], 90)
        self.assertEqual(execution["stderr"]["sha256"], hashlib.sha256(b"b" * 90).hexdigest())

    def test_missing_command_records_observer_failure_without_process_claim(self):
        run_root = self.root / "run"
        run_root.mkdir()
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--run-root", str(run_root),
             "--run-id", "run-001", "--cwd", str(self.project), "--", "missing-command-for-eval"],
            text=True, capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 125)
        execution = json.loads((run_root / "attempt-1/execution.json").read_text())
        self.assertEqual(execution["cwd"], str(self.project.resolve()))
        self.assertFalse(execution["process_started"])
        self.assertFalse(execution["process_terminated"])
        self.assertIsNone(execution["pid"])
        self.assertEqual(execution["observer_error"]["type"], "FileNotFoundError")
        self.assertFalse((run_root / "attempt-1/process-handle.json").exists())

    def test_invalid_setup_fails_before_claiming_run(self):
        run_root = self.root / "run"
        run_root.mkdir()
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--run-root", str(run_root),
             "--run-id", "run-001", "--cwd", str(self.root / "missing"), "--", sys.executable, "-c", "pass"],
            text=True, capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 125)
        self.assertEqual(list(run_root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
