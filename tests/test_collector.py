"""Black-box checks of the documented, isolated collector workflow.

The collector and its native exporter really run in child processes. A further
fresh Python process reads the retained CSV. Expected content is fixed from
the sample's requirements, never learned from a generated contract or report.
These are controlled local CLI/file checks, not host-agent or real-API tests.
"""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = PROJECT_ROOT / "examples" / "paginated_export" / "accept.py"
HELPER = PROJECT_ROOT / "scripts" / "acceptance.py"
EXPECTED_HEADER = ["id", "title", "notes"]
EXPECTED_ROWS = [
    ["r-001", "示例, Hello", "第一行\n第二行"],
    ["r-002", 'Quote "double"', "café ☕"],
    ["r-003", "雪 / snow", ""],
    ["r-004", "Emoji 🚀", "CRLF\r\nnext"],
    ["r-005", "最后一页", 'END, "边界"\n末尾'],
]


class CollectorCLITests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="acceptance-collector-test-")
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name).resolve()

    def collect(self, case, run_dir):
        return subprocess.run(
            [sys.executable, "-B", str(COLLECTOR), "--case", case,
             "--run-dir", str(run_dir)],
            cwd=self.workspace, text=True, capture_output=True,
            timeout=30, check=False,
        )

    def read_json(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def artifact_path(self, run_dir, reference):
        relative = Path(reference["path"])
        self.assertFalse(relative.is_absolute(), reference)
        self.assertNotIn("..", relative.parts, reference)
        artifact = run_dir / relative
        self.assertFalse(artifact.is_symlink(), str(artifact))
        self.assertTrue(artifact.is_file(), str(artifact))
        self.assertTrue(artifact.resolve().is_relative_to(run_dir.resolve()), reference)
        self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), reference["sha256"])
        return artifact

    def retained_materials(self, run_dir):
        contract_bytes = (run_dir / "contract.json").read_bytes()
        contract = json.loads(contract_bytes)
        run = self.read_json(run_dir / "run.json")
        self.assertEqual(run["contract_sha256"], hashlib.sha256(contract_bytes).hexdigest())
        self.artifact_path(run_dir, run["runtime"])
        self.artifact_path(run_dir, run["input"])
        self.assertEqual(run["runtime"]["sha256"], contract["target"]["sha256"])
        self.assertEqual(run["input"]["sha256"], contract["input_sha256"])
        self.assertEqual(run["execution_state"], "completed")
        self.assertEqual(run["cleanup"]["state"], "retained")
        self.assertEqual(run["retention"]["policy"], "until-owner-removes")
        self.assertEqual(len(run["attempts"]), 1)
        attempt = run["attempts"][0]
        record = self.read_json(self.artifact_path(run_dir, attempt["execution"]))
        self.assertEqual(record["schema_version"], "local-process/v1")
        self.assertEqual(record["run_id"], run["id"])
        self.assertEqual(record["attempt_id"], attempt["id"])
        self.assertEqual(record["target_sha256"], run["runtime"]["sha256"])
        self.assertEqual(record["input_sha256"], run["input"]["sha256"])
        self.assertIs(record["completed"], True)
        self.assertEqual(record["exit_code"], 0)
        self.assertTrue(record["argv"])
        csv_path = self.artifact_path(run_dir, record["output"])
        for observation in attempt["observations"]:
            self.assertEqual(observation["artifact"], record["output"])
            self.artifact_path(run_dir, observation["artifact"])
        return contract, run, record, csv_path

    def retained_report(self, run_dir):
        # The public interface promises JSON and Markdown reports, but does not
        # prescribe their basenames. Locate them by their delivered format.
        reports = []
        for candidate in run_dir.glob("*.json"):
            value = self.read_json(candidate)
            if isinstance(value, dict) and "business_verdict" in value:
                reports.append((candidate, value))
        self.assertEqual(len(reports), 1, "Expected one retained JSON report.")
        markdown = list(run_dir.glob("*.md"))
        self.assertEqual(len(markdown), 1, "Expected one retained Markdown report.")
        self.assertTrue(markdown[0].read_text(encoding="utf-8").strip())
        return reports[0][1]

    def read_csv_in_fresh_process(self, csv_path):
        reader = (
            "import csv,json,sys\n"
            "with open(sys.argv[1], encoding='utf-8', newline='') as stream:\n"
            "    rows = list(csv.reader(stream, strict=True))\n"
            "print(json.dumps(rows, ensure_ascii=False))\n"
        )
        process = subprocess.run(
            [sys.executable, "-B", "-c", reader, str(csv_path)],
            cwd=self.workspace, text=True, capture_output=True,
            timeout=10, check=False,
        )
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        return json.loads(process.stdout)

    def recheck_in_fresh_process(self, run_dir):
        process = subprocess.run(
            [sys.executable, "-B", str(HELPER),
             "--contract", str(run_dir / "contract.json"),
             "--run", str(run_dir / "run.json"),
             "--root", str(run_dir), "--format", "json"],
            cwd=self.workspace, text=True, capture_output=True,
            timeout=10, check=False,
        )
        try:
            report = json.loads(process.stdout)
        except ValueError as error:
            self.fail("Helper returned no JSON report: {!r} / {!r}: {}".format(
                process.stdout, process.stderr, error
            ))
        return process, report

    def directory_snapshot(self, root):
        return {
            str(path.relative_to(root)): (
                "directory" if path.is_dir() else hashlib.sha256(path.read_bytes()).hexdigest()
            )
            for path in root.rglob("*")
        }

    def assert_report(self, report, verdict, completion):
        self.assertEqual(report["business_verdict"], verdict, report)
        self.assertEqual(report["completion"], completion, report)
        self.assertEqual(report["cleanup"]["state"], "retained", report)
        self.assertTrue(report["limitations"], "The local/synthetic scope must remain explicit.")

    def test_healthy_collection_is_readable_by_another_process(self):
        run_dir = self.workspace / "healthy-run"
        process = self.collect("healthy", run_dir)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn(str(run_dir), process.stdout + process.stderr)
        contract, run, _, csv_path = self.retained_materials(run_dir)
        self.assertEqual(contract["scope"]["environment"], "isolated-local")
        self.assertEqual(contract["scope"]["upstream"], "synthetic-pages")
        self.assertTrue(contract["goals"])
        self.assertTrue(run["attempts"][0]["observations"])
        self.assertEqual(self.read_csv_in_fresh_process(csv_path), [EXPECTED_HEADER] + EXPECTED_ROWS)
        self.assert_report(self.retained_report(run_dir), "PASS", "complete")
        recheck, report = self.recheck_in_fresh_process(run_dir)
        self.assertEqual(recheck.returncode, 0, recheck.stdout + recheck.stderr)
        self.assert_report(report, "PASS", "complete")

    def test_final_page_defect_is_failed_despite_zero_exit_native_process(self):
        run_dir = self.workspace / "defective-run"
        process = self.collect("defect", run_dir)
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        self.assertIn(str(run_dir), process.stdout + process.stderr)
        _, _, record, csv_path = self.retained_materials(run_dir)
        self.assertEqual(record["exit_code"], 0, "This controlled defect must appear to execute successfully.")
        rows = self.read_csv_in_fresh_process(csv_path)
        self.assertEqual(rows, [EXPECTED_HEADER] + EXPECTED_ROWS[:4])
        self.assertNotIn("r-005", [row[0] for row in rows[1:]])
        report = self.retained_report(run_dir)
        self.assert_report(report, "FAIL", "complete")
        failures = [item for item in report["obligations"] if item["status"] == "FAIL"]
        self.assertTrue(failures, "The result must include a concrete content counterexample.")
        self.assertTrue(all(item["reasons"] for item in failures))
        recheck, report = self.recheck_in_fresh_process(run_dir)
        self.assertEqual(recheck.returncode, 1, recheck.stdout + recheck.stderr)
        self.assert_report(report, "FAIL", "complete")

    def test_withheld_observation_is_unknown_even_though_csv_really_exists(self):
        run_dir = self.workspace / "unobserved-run"
        process = self.collect("missing-observation", run_dir)
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        self.assertIn(str(run_dir), process.stdout + process.stderr)
        contract, run, _, csv_path = self.retained_materials(run_dir)
        # The gap is missing observation, not an exporter failure or missing file.
        self.assertEqual(self.read_csv_in_fresh_process(csv_path), [EXPECTED_HEADER] + EXPECTED_ROWS)
        required = {
            item["id"] for item in contract["obligations"]
            if item["required"] and item["applicable"]
        }
        observed = {
            observation["obligation_id"]
            for attempt in run["attempts"] for observation in attempt["observations"]
        }
        self.assertTrue(required - observed, "The demonstration must withhold a required observation.")
        report = self.retained_report(run_dir)
        self.assert_report(report, "UNVERIFIED", "partial")
        self.assertTrue(any(item["status"] == "UNVERIFIED" for item in report["obligations"]))
        self.assertFalse(any(item["status"] == "FAIL" for item in report["obligations"]))
        recheck, report = self.recheck_in_fresh_process(run_dir)
        self.assertEqual(recheck.returncode, 2, recheck.stdout + recheck.stderr)
        self.assert_report(report, "UNVERIFIED", "partial")

    def test_second_run_leaves_first_evidence_independent_and_recheckable(self):
        first_dir = self.workspace / "first-run"
        first_process = self.collect("healthy", first_dir)
        self.assertEqual(first_process.returncode, 0, first_process.stdout + first_process.stderr)
        _, first_run, _, first_csv = self.retained_materials(first_dir)
        first_snapshot = self.directory_snapshot(first_dir)

        second_dir = self.workspace / "second-run"
        second_process = self.collect("defect", second_dir)
        self.assertEqual(second_process.returncode, 1, second_process.stdout + second_process.stderr)
        _, second_run, _, second_csv = self.retained_materials(second_dir)
        self.assertNotEqual(first_run["id"], second_run["id"])
        self.assertNotEqual(first_csv.resolve(), second_csv.resolve())
        self.assertEqual(self.directory_snapshot(first_dir), first_snapshot)
        self.assertEqual(self.read_csv_in_fresh_process(first_csv), [EXPECTED_HEADER] + EXPECTED_ROWS)
        self.assertEqual(self.read_csv_in_fresh_process(second_csv), [EXPECTED_HEADER] + EXPECTED_ROWS[:4])

        recheck, report = self.recheck_in_fresh_process(first_dir)
        self.assertEqual(recheck.returncode, 0, recheck.stdout + recheck.stderr)
        self.assert_report(report, "PASS", "complete")
        self.assertEqual(self.directory_snapshot(first_dir), first_snapshot)
        self.assert_report(self.retained_report(second_dir), "FAIL", "complete")

    def test_a_completed_run_directory_cannot_be_reused_or_overwritten(self):
        run_dir = self.workspace / "existing-run"
        first = self.collect("healthy", run_dir)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        snapshot = self.directory_snapshot(run_dir)
        second = self.collect("defect", run_dir)
        self.assertEqual(second.returncode, 2, second.stdout + second.stderr)
        self.assertEqual(self.directory_snapshot(run_dir), snapshot)
        self.assertNotIn("Traceback", second.stdout + second.stderr)
        recheck, report = self.recheck_in_fresh_process(run_dir)
        self.assertEqual(recheck.returncode, 0, recheck.stdout + recheck.stderr)
        self.assert_report(report, "PASS", "complete")

    def test_existing_empty_and_nonempty_directories_are_refused_unchanged(self):
        for populated in (False, True):
            with self.subTest(populated=populated):
                run_dir = self.workspace / ("occupied" if populated else "empty")
                run_dir.mkdir()
                if populated:
                    (run_dir / "user-data.txt").write_bytes(b"do not overwrite or remove\n")
                snapshot = self.directory_snapshot(run_dir)
                process = self.collect("healthy", run_dir)
                self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
                self.assertEqual(self.directory_snapshot(run_dir), snapshot)
                self.assertNotIn("Traceback", process.stdout + process.stderr)

    def test_existing_file_at_run_path_is_not_replaced(self):
        run_dir = self.workspace / "occupied-file"
        run_dir.write_bytes(b"owned file, not a run directory\n")
        process = self.collect("healthy", run_dir)
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        self.assertTrue(run_dir.is_file())
        self.assertEqual(run_dir.read_bytes(), b"owned file, not a run directory\n")
        self.assertNotIn("Traceback", process.stdout + process.stderr)

    def test_run_path_symlinks_are_not_followed_or_replaced(self):
        for dangling in (False, True):
            with self.subTest(dangling=dangling):
                suffix = "dangling" if dangling else "existing"
                target = self.workspace / (suffix + "-target")
                link = self.workspace / (suffix + "-run-link")
                if not dangling:
                    target.mkdir()
                    (target / "sentinel.txt").write_bytes(b"keep\n")
                try:
                    link.symlink_to(target, target_is_directory=True)
                except (OSError, NotImplementedError) as error:
                    self.skipTest("Creating a symlink is unavailable: {}".format(error))
                before = self.directory_snapshot(target) if not dangling else None
                process = self.collect("healthy", link)
                self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
                self.assertTrue(link.is_symlink())
                if dangling:
                    self.assertFalse(target.exists(), "Collector must not create a dangling link's target.")
                else:
                    self.assertEqual(self.directory_snapshot(target), before)
                self.assertNotIn("Traceback", process.stdout + process.stderr)


if __name__ == "__main__":
    unittest.main()
