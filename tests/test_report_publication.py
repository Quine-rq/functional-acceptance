"""Report delivery checks through the real helper CLI and its output files.

The interruption probe wraps file-opening APIs to split a real disk write and
pause after its first fragment is flushed. The parent then kills that exact
child. This is a controlled filesystem-boundary probe, not a claim about native
exporter behavior or naturally occurring write timing. No helper functions or
business verdicts are mocked.
"""

import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import unittest

import test_acceptance as material_fixtures


HELPER = Path(__file__).resolve().parents[1] / "scripts" / "acceptance.py"
WRITE_LIMIT = 120

# Run the unchanged CLI with a controlled file-write boundary in this child.
# Cover the public opening APIs used by text, binary, and Path-based callers;
# the probe does not depend on an output filename or a helper function name.
INTERRUPTED_CLI = r"""
import builtins
import io
import os
import runpy
import signal
import sys

barrier = int(sys.argv[1])
limit = int(sys.argv[2])
sys.argv = sys.argv[3:]

class InterruptedWriter:
    def __init__(self, stream):
        self.stream = stream

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.stream.__exit__(*args)

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def write(self, content):
        fragment = content[:limit]
        self.stream.write(fragment)
        self.stream.flush()
        raw_fragment = fragment.encode("utf-8") if isinstance(fragment, str) else fragment
        os.write(barrier, b"partial-write-flushed\n" + raw_fragment)
        while True:
            signal.pause()

def intercept_open(real_open):
    def open_at_boundary(*args, **kwargs):
        stream = real_open(*args, **kwargs)
        return InterruptedWriter(stream) if stream.writable() else stream
    return open_at_boundary

builtins.open = intercept_open(builtins.open)
io.open = intercept_open(io.open)
os.fdopen = intercept_open(os.fdopen)
runpy.run_path(sys.argv[0], run_name="__main__")
"""

# Unlike the uncatchable-termination probe, this child injects a catchable disk
# error after real report bytes have been written. The CLI must own its cleanup.
DISK_FAILURE_CLI = r"""
import builtins
import errno
import io
import os
import runpy
import sys

failure = sys.argv[1]
sys.argv = sys.argv[2:]
report_written = False

class FailingWriter:
    def __init__(self, stream):
        self.stream = stream

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.stream.__exit__(*args)

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def write(self, content):
        global report_written
        fragment = content[:120]
        raw_fragment = fragment.encode("utf-8") if isinstance(fragment, str) else fragment
        if not raw_fragment.startswith(b"# Functional acceptance\n\nBusiness: PASS"):
            raise RuntimeError("The fault must target report bytes, not unrelated I/O.")
        report_written = True
        if failure != "write":
            return self.stream.write(content)
        self.stream.write(fragment)
        self.stream.flush()
        sys.stderr.write("controlled partial-report ENOSPC\n")
        raise OSError(errno.ENOSPC, "controlled partial report write failure")

    def flush(self):
        self.stream.flush()
        if failure == "flush" and report_written:
            sys.stderr.write("controlled report flush failure\n")
            raise OSError(errno.EIO, "controlled report flush failure")

def intercept_open(real_open):
    def open_at_boundary(*args, **kwargs):
        stream = real_open(*args, **kwargs)
        return FailingWriter(stream) if stream.writable() else stream
    return open_at_boundary

builtins.open = intercept_open(builtins.open)
io.open = intercept_open(io.open)
os.fdopen = intercept_open(os.fdopen)
if failure == "fsync":
    def failed_fsync(descriptor):
        if not report_written:
            raise RuntimeError("The sync fault must follow an actual report write.")
        sys.stderr.write("controlled report fsync failure\n")
        raise OSError(errno.EIO, "controlled report fsync failure")
    os.fsync = failed_fsync
runpy.run_path(sys.argv[0], run_name="__main__")
"""


class ReportPublicationCLITests(unittest.TestCase):
    def setUp(self):
        # Composition reuses synthetic material without inheriting/discovering
        # the material suite's 43 test methods for a second time.
        self.material = material_fixtures.AcceptanceCLITests()
        self.material.setUp()
        self.addCleanup(self.material.doCleanups)
        self.output = self.material.workspace / "report.md"

    def helper_arguments(self, output_format="markdown"):
        return [str(HELPER), "--contract", str(self.material.contract_path),
                "--run", str(self.material.run_path), "--root", str(self.material.root),
                "--format", output_format, "--output", str(self.output)]

    def test_complete_report_is_available_after_a_successful_cli_run(self):
        for output_format, suffix in (("json", ".json"), ("markdown", ".md")):
            with self.subTest(output_format=output_format):
                self.output = self.material.workspace / ("complete-report" + suffix)
                result = subprocess.run(
                    [sys.executable, "-B", *self.helper_arguments(output_format)],
                    capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                content = self.output.read_text(encoding="utf-8")
                if output_format == "json":
                    report = json.loads(content)
                    self.assertEqual(report["business_verdict"], "PASS")
                    self.assertTrue(report["qualified_pass"])
                    self.assertEqual(report["completion"], "complete")
                    self.assertEqual(report["obligations"][0]["status"], "PASS")
                else:
                    self.assertIn("Business: PASS · Completion: complete", content)
                    self.assertIn("csv\\-complete: PASS", content)
                    self.assertIn("## Execution and retention", content)
                    self.assertIn("## Limits", content)
                    self.assertTrue(content.endswith("\n"))

    def test_killing_a_writer_mid_report_does_not_publish_a_partial_report(self):
        read_end, write_end = os.pipe()
        child = None
        try:
            child = subprocess.Popen(
                [sys.executable, "-B", "-c", INTERRUPTED_CLI, str(write_end),
                 str(WRITE_LIMIT), *self.helper_arguments()],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                pass_fds=(write_end,),
            )
            os.close(write_end)
            write_end = None
            ready, _, _ = select.select([read_end], [], [], 10)
            self.assertTrue(ready, "The real child must reach the controlled write boundary.")
            observed_write = os.read(read_end, 1024)
            self.assertTrue(
                observed_write.startswith(
                    b"partial-write-flushed\n# Functional acceptance\n\nBusiness: PASS"
                ),
                "The interrupted disk write must contain the actual report, not unrelated I/O: "
                + repr(observed_write),
            )
            self.assertIsNone(child.poll(), "The owned writer must still be active at the barrier.")
            child.kill()
            stdout, stderr = child.communicate(timeout=5)
            self.assertEqual(child.returncode, -signal.SIGKILL, (stdout, stderr))
            self.assertFalse(
                self.output.exists(),
                "A killed writer left a partial report under the final delivery name: "
                + (repr(self.output.read_bytes()) if self.output.exists() else ""),
            )
        finally:
            # Never act on a recorded/stale PID or a process name: only this
            # test's Popen handle is owned, and it is reaped before file cleanup.
            if child is not None:
                if child.poll() is None:
                    child.kill()
                child.communicate(timeout=5)
            os.close(read_end)
            if write_end is not None:
                os.close(write_end)

    def test_concurrent_report_delivery_has_one_winner_and_a_complete_report(self):
        self.output = self.material.workspace / "concurrent-report.json"
        command = [sys.executable, "-B", *self.helper_arguments("json")]
        children = []
        try:
            for _ in range(2):
                children.append(subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                ))
            results = [child.communicate(timeout=10) for child in children]
            self.assertEqual(sorted(child.returncode for child in children), [0, 2], results)
            report = json.loads(self.output.read_text(encoding="utf-8"))
            self.assertTrue(report["qualified_pass"])
            self.assertEqual(report["completion"], "complete")
            self.assertEqual(report["obligations"][0]["status"], "PASS")
            self.assertEqual(set(self.material.workspace.iterdir()), {self.material.root, self.output})
        finally:
            for child in children:
                if child.poll() is None:
                    child.kill()
                child.communicate(timeout=5)

    def test_partial_disk_write_failure_leaves_no_report_and_allows_a_fresh_delivery(self):
        unrelated = self.material.workspace / "existing-other-report.md"
        original = b"Existing owner file: retain every byte.\x00\xff\n"
        unrelated.write_bytes(original)
        failed = subprocess.run(
            [sys.executable, "-B", "-c", DISK_FAILURE_CLI, "write", *self.helper_arguments()],
            capture_output=True, text=True, timeout=10,
        )
        self.assertIn("controlled partial-report ENOSPC", failed.stderr)
        self.assertEqual(failed.returncode, 2, failed.stdout + failed.stderr)
        summary = json.loads(failed.stdout)
        self.assertEqual(summary["material_status"], "invalid")
        self.assertIsNot(summary.get("qualified_pass"), True)
        self.assertFalse(self.output.exists())
        self.assertEqual(unrelated.read_bytes(), original)
        self.assertEqual(set(self.material.workspace.iterdir()), {self.material.root, unrelated})

        # A new explicit invocation can deliver to the still-unused final name.
        recovered = subprocess.run(
            [sys.executable, "-B", *self.helper_arguments()],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
        content = self.output.read_text(encoding="utf-8")
        self.assertIn("Business: PASS · Completion: complete", content)
        self.assertIn("## Limits", content)
        self.assertEqual(unrelated.read_bytes(), original)
        self.assertEqual(set(self.material.workspace.iterdir()), {self.material.root, unrelated, self.output})

    def test_flush_and_sync_failures_leave_no_final_report_or_partial_artifacts(self):
        for failure in ("flush", "fsync"):
            with self.subTest(failure=failure):
                result = subprocess.run(
                    [sys.executable, "-B", "-c", DISK_FAILURE_CLI, failure, *self.helper_arguments()],
                    capture_output=True, text=True, timeout=10,
                )
                self.assertIn("controlled report " + failure + " failure", result.stderr)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                summary = json.loads(result.stdout)
                self.assertEqual(summary["material_status"], "invalid")
                self.assertIsNot(summary.get("qualified_pass"), True)
                self.assertFalse(self.output.exists())
                self.assertEqual(set(self.material.workspace.iterdir()), {self.material.root})


if __name__ == "__main__":
    unittest.main()
