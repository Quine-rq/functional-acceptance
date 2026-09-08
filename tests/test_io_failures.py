"""Controlled I/O failure probes, separate from black-box happy-path checks.

The collector lifecycle test uses public collect() and filesystem/process I/O
boundaries. Its real child is deliberately slow, not the export sample: this
proves owned-process cleanup, not export correctness. The material-budget test
uses the real helper CLI with synthetic process records, not native collection.
All fixtures are isolated and are removed by TemporaryDirectory.

The report-cleanup probe runs the real collector, exporter, and helper CLIs.
Only the helper's unlink boundary is faulted, after a complete report exists;
the wrapper never supplies an assessment or replaces a command's result.
"""

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COLLECTOR_PATH = PROJECT_ROOT / "examples" / "paginated_export" / "accept.py"
HELPER_PATH = PROJECT_ROOT / "scripts" / "acceptance.py"
FILE_LIMIT = 2 * 1024 * 1024
READ_LIMIT = 16 * 1024 * 1024


# These wrappers live only in the owned child interpreters; no startup files,
# environment changes, or fault hooks escape into unrelated Python processes.
REPORT_CLEANUP_FAILURE_CLI = r"""
import errno
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

sys.argv = sys.argv[1:]
destination = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()

def fail_published_temporary_cleanup(event, arguments):
    if event != 'os.remove':
        return
    candidate = Path(arguments[0]).resolve()
    if (candidate != destination and destination.is_file()
            and candidate.is_file() and os.path.samefile(candidate, destination)):
        # Observe real published bytes before the fault. Later report rewriting
        # must not turn this historical observation into a different result.
        observation = {
            'published_file': str(destination),
            'temporary_file': str(candidate),
            'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
        }
        sys.stderr.write('PUBLICATION_PROBE ' + json.dumps(observation) + '\n')
        raise PermissionError(errno.EACCES, 'controlled report temporary unlink failure')

# Older pathlib versions bind os.unlink during import. The public audit event
# observes the actual removal attempt regardless of that cached callable.
# Unmatched events proceed unchanged; this hook exists only in this child.
sys.addaudithook(fail_published_temporary_cleanup)
runpy.run_path(sys.argv[0], run_name='__main__')
"""

COLLECTOR_WITH_REPORT_CLEANUP_FAILURE_CLI = r"""
import runpy
import subprocess
import sys

fault_wrapper = sys.argv[1]
helper_path = sys.argv[2]
sys.argv = sys.argv[3:]
real_run = subprocess.run

def run_with_helper_io_fault(command, *args, **kwargs):
    if helper_path not in command:
        return real_run(command, *args, **kwargs)
    helper_index = command.index(helper_path)
    wrapped = [sys.executable, '-B', '-c', fault_wrapper, *command[helper_index:]]
    result = real_run(wrapped, *args, **kwargs)
    # The collector receives the actual helper result, unchanged. Forward only
    # the controlled boundary observations to this test's separate stderr pipe.
    for line in result.stderr.splitlines(keepends=True):
        if line.startswith(b'PUBLICATION_PROBE '):
            sys.stderr.buffer.write(line)
    return result

subprocess.run = run_with_helper_io_fault
runpy.run_path(sys.argv[0], run_name='__main__')
"""


def load_collector():
    specification = importlib.util.spec_from_file_location("collector_io_review", COLLECTOR_PATH)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def encoded(value):
    return (json.dumps(value, ensure_ascii=False) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


class ControlledIOFailureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="acceptance-io-failure-")
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name).resolve()

    def write_artifact(self, name, data):
        with (self.workspace / name).open("xb") as stream:
            stream.write(data)
        return {"path": name, "sha256": digest(data)}

    def test_evidence_write_failure_after_start_reaps_the_owned_child(self):
        collector = load_collector()
        real_popen = subprocess.Popen
        real_open = Path.open
        children = []
        run_directory = self.workspace / "failed-run"

        def slow_owned_child(command, **kwargs):
            child = real_popen([sys.executable, "-B", "-c", "import time; time.sleep(30)"], **kwargs)
            children.append(child)
            return child

        def unavailable_handle(path, *args, **kwargs):
            if path.name == "process-handle.json":
                raise OSError("injected process-handle persistence failure")
            return real_open(path, *args, **kwargs)

        try:
            with mock.patch.object(subprocess, "Popen", side_effect=slow_owned_child), \
                    mock.patch.object(Path, "open", new=unavailable_handle):
                with self.assertRaises(OSError):
                    collector.collect("healthy", run_directory)
            self.assertTrue(children, "The injected write failure must occur after a real child starts.")
            self.assertTrue(all(child.poll() is not None for child in children),
                            "Returning an error does not release ownership of an active child.")
            self.assertFalse((run_directory / "run.json").exists(), "An incomplete run must not be finalized.")
            pending = json.loads((run_directory / "run.pending.json").read_text(encoding="utf-8"))
            self.assertEqual(pending["execution_state"], "unknown")
            self.assertEqual(pending["cleanup"]["state"], "unknown")
        finally:
            # This also prevents a regressed implementation from leaking a test
            # process. Only exact children created by this test are ever touched.
            for child in children:
                if child.poll() is None:
                    child.terminate()
                try:
                    child.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.communicate(timeout=5)

    def test_cumulative_read_budget_stops_before_reading_remaining_large_records(self):
        runtime = self.write_artifact("native.py", b"# Synthetic process evidence; never executed.\n")
        source = self.write_artifact("input.json", b"{}\n")
        output = self.write_artifact("output.csv", b"value\r\nok\r\n")
        contract = {
            "schema_version": "m1", "journey": "Retain the independently specified value.",
            "target": {"id": "resource-budget-fixture", "sha256": runtime["sha256"]},
            "input_sha256": source["sha256"],
            "goals": [{"id": "value-goal", "text": "The value is exactly ok.",
                       "source": "independent literal requirement", "obligations": ["value"],
                       "gap": None, "exclusion": None}],
            "obligations": [{"id": "value", "expected": "One literal ok row.", "required": True,
                             "applicable": True, "exclusion": None, "mapping": "csv-exact/v1",
                             "columns": ["value"], "rows": [["ok"]]}],
            "scope": {"environment": "isolated-local", "upstream": "synthetic",
                      "claim": "Material resource-budget check, not native execution."},
        }
        contract_bytes = encoded(contract)
        self.write_artifact("contract.json", contract_bytes)
        manifest = {
            "schema_version": "m1", "id": "bounded-material-run", "contract_sha256": digest(contract_bytes),
            "runtime": runtime, "input": source, "tool": {"name": "synthetic-process-record", "version": "1"},
            "attempts": [], "execution_state": "completed",
            "cleanup": {"state": "retained", "details": "Only isolated synthetic material exists."},
            "retention": {"policy": "until-owner-removes", "details": "Temporary test-owned directory."},
        }
        record_sizes = []
        for number in range(10):
            attempt_id = "attempt-" + str(number)
            record = {
                "schema_version": "local-process/v1", "run_id": manifest["id"], "attempt_id": attempt_id,
                "target_sha256": runtime["sha256"], "input_sha256": source["sha256"],
                "argv": ["synthetic-not-executed"], "completed": True, "exit_code": 0,
                "output": output, "stdout": "x" * 1_900_000, "stderr": "",
            }
            record_bytes = encoded(record)
            record_sizes.append(len(record_bytes))
            reference = self.write_artifact(attempt_id + ".json", record_bytes)
            manifest["attempts"].append({"id": attempt_id, "execution": reference,
                                         "observations": [{"obligation_id": "value", "artifact": output}]})
        self.assertTrue(all(size < FILE_LIMIT for size in record_sizes), "Each individual file must be permitted.")
        self.assertGreater(sum(record_sizes), READ_LIMIT, "Only the cumulative limit should trigger.")
        self.write_artifact("run.json", encoded(manifest))
        result = subprocess.run(
            [sys.executable, "-B", str(HELPER_PATH), "--contract", str(self.workspace / "contract.json"),
             "--run", str(self.workspace / "run.json"), "--root", str(self.workspace)],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["business_verdict"], "UNVERIFIED", report)
        self.assertFalse(report["qualified_pass"], report)
        usage = report["material_usage"]
        self.assertGreater(usage["bytes_read"], 0)
        self.assertLessEqual(usage["bytes_read"], READ_LIMIT, "Reporting a budget gap after overspending is insufficient.")
        self.assertTrue(any("budget" in attempt["reason"] for attempt in report["obligations"][0]["attempts"]), report)

    def test_later_report_recheck_losing_evidence_cannot_deliver_the_earlier_pass(self):
        collector = load_collector()
        real_run = subprocess.run
        run_directory = self.workspace / "reports-disagree"
        helper_codes = []
        evidence_moved = []

        def evidence_disappears_before_markdown(command, **kwargs):
            if command[command.index("--format") + 1] == "markdown":
                manifest = json.loads((run_directory / "run.json").read_text(encoding="utf-8"))
                reference = manifest["attempts"][0]["observations"][0]["artifact"]
                original = run_directory / reference["path"]
                retained = run_directory / "review-retained-output.csv"
                original.rename(retained)
                evidence_moved.append((original, retained))
            result = real_run(command, **kwargs)
            helper_codes.append(result.returncode)
            return result

        captured = io.StringIO()
        with contextlib.redirect_stdout(captured), \
                mock.patch.object(subprocess, "run", side_effect=evidence_disappears_before_markdown):
            result = collector.main(["--case", "healthy", "--run-dir", str(run_directory)])
        self.assertEqual(helper_codes, [0, 2], "Both helper processes must actually run and observe the change.")
        self.assertEqual(result, 2, "A known later evidence gap invalidates the current qualified delivery.")
        summary = json.loads(captured.getvalue())
        self.assertEqual(summary["status"], "incomplete", summary)
        self.assertIsNot(summary.get("qualified_pass"), True, summary)
        self.assertTrue(evidence_moved)
        self.assertTrue(all(not original.exists() and retained.is_file() for original, retained in evidence_moved))
        # Historic reports are retained, not rewritten to pretend they agreed.
        earlier = json.loads((run_directory / "report.json").read_text(encoding="utf-8"))
        later = (run_directory / "report.md").read_text(encoding="utf-8")
        self.assertTrue(earlier["qualified_pass"])
        self.assertIn("Business: UNVERIFIED", later)

    def test_published_report_cleanup_failure_remains_an_incomplete_handoff(self):
        for case, expected_verdict in (("healthy", "PASS"), ("defect", "FAIL")):
            with self.subTest(case=case):
                run_directory = self.workspace / (case + "-report-cleanup")
                result = subprocess.run(
                    [sys.executable, "-B", "-c", COLLECTOR_WITH_REPORT_CLEANUP_FAILURE_CLI,
                     REPORT_CLEANUP_FAILURE_CLI, str(HELPER_PATH), str(COLLECTOR_PATH),
                     "--case", case, "--run-dir", str(run_directory)],
                    capture_output=True, text=True, timeout=30,
                )
                observations = [
                    json.loads(line.removeprefix("PUBLICATION_PROBE "))
                    for line in result.stderr.splitlines()
                    if line.startswith("PUBLICATION_PROBE ")
                ]
                self.assertEqual(
                    {Path(item["published_file"]).name for item in observations},
                    {"report.json", "report.md"},
                    "Both real helper formats must publish before their cleanup fails: "
                    + result.stdout + result.stderr,
                )
                for observation in observations:
                    published = Path(observation["published_file"])
                    temporary = Path(observation["temporary_file"])
                    self.assertEqual(published.parent, run_directory)
                    self.assertEqual(temporary.parent, run_directory)
                    self.assertEqual(digest(published.read_bytes()), observation["sha256"],
                                     "Published historical reports must not be rewritten after the failure.")
                    self.assertTrue(temporary.is_file(), "The controlled cleanup fault must leave a real residual.")
                    self.assertEqual(temporary.read_bytes(), published.read_bytes())

                report = json.loads((run_directory / "report.json").read_text(encoding="utf-8"))
                markdown_report = (run_directory / "report.md").read_text(encoding="utf-8")
                self.assertEqual(report["business_verdict"], expected_verdict)
                self.assertIn("Business: " + expected_verdict, markdown_report)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                summary = json.loads(result.stdout)
                self.assertIsNot(summary.get("qualified_pass"), True, summary)
                self.assertNotEqual(summary.get("completion"), "complete", summary)
                self.assertEqual(summary.get("run_directory"), str(run_directory), summary)
                # Cleanup ownership may be expressed in any field or message;
                # do not freeze an error sentence or a new response structure.
                self.assertRegex(
                    json.dumps(summary, ensure_ascii=False),
                    r"(?i)(cleanup|temporary|residu|清理|临时|残留)",
                    "The handoff must disclose the remaining report-cleanup responsibility.",
                )


if __name__ == "__main__":
    unittest.main()
