"""Native subprocess acceptance checks; no Skill, network, or third-party packages."""

import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


EXAMPLE = Path(__file__).resolve().parent
EXPORTER = EXAMPLE / "export.py"
FIXTURES = EXAMPLE / "fixtures"


class ExportAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="acceptance-export-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.output = self.directory / "result.csv"
        self.expected = json.loads((FIXTURES / "expected_records.json").read_text(encoding="utf-8"))

    def run_export(self, source=None, output=None, fault=None):
        command = [
            sys.executable, str(EXPORTER),
            "--source", str(source if source is not None else FIXTURES / "pages.json"),
            "--output", str(output if output is not None else self.output),
        ]
        if fault is not None:
            command.extend(["--fault", fault])
        return subprocess.run(command, cwd=self.directory, text=True, capture_output=True, timeout=10)

    def source_file(self, payload):
        source = self.directory / "input.json"
        with source.open("x", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=True)
        return source

    def read_records(self, output=None):
        with (output if output is not None else self.output).open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(reader.fieldnames, ["id", "title", "notes"])
            return list(reader)

    def assert_complete_export(self, output=None):
        # This independent expectation never reads exporter internals or source pages.
        self.assertEqual(self.read_records(output), self.expected)

    def assert_no_temporary_files(self):
        self.assertEqual(list(self.directory.glob(".export-*.tmp")), [])

    def test_healthy_export_preserves_all_pages_and_exact_csv_fields(self):
        source_before = (FIXTURES / "pages.json").read_bytes()
        result = self.run_export()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_complete_export()
        self.assertEqual(len(self.expected), 5)
        self.assertEqual(self.expected[-1]["id"], "r-005")
        self.assertEqual((FIXTURES / "pages.json").read_bytes(), source_before)
        self.assert_no_temporary_files()

    def test_fault_returns_zero_but_fails_the_same_completeness_check(self):
        result = self.run_export(fault="omit-final-page")
        self.assertEqual(result.returncode, 0, result.stderr)
        records = self.read_records()
        self.assertEqual(records, self.expected[:-1])
        with self.assertRaises(AssertionError):
            self.assert_complete_export()
        self.assert_no_temporary_files()

    def test_empty_page_collection_writes_a_header_only_csv(self):
        result = self.run_export(source=FIXTURES / "empty_pages.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read_records(), [])
        self.assertEqual(self.output.read_bytes(), b"id,title,notes\r\n")

    def test_empty_records_page_is_valid(self):
        source = self.source_file({"pages": [{"page": 1, "records": []}]})
        result = self.run_export(source=source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read_records(), [])

    def test_invalid_json_does_not_create_output(self):
        source = self.directory / "broken.json"
        with source.open("xb") as stream:
            stream.write(b'{"pages":')
        result = self.run_export(source=source)
        self.assertEqual(result.returncode, 2)
        self.assertIn("export: error:", result.stderr)
        self.assertFalse(self.output.exists())
        self.assert_no_temporary_files()

    def test_duplicate_json_keys_are_rejected(self):
        source = self.directory / "duplicate.json"
        with source.open("x", encoding="utf-8") as stream:
            stream.write('{"pages": [], "pages": []}')
        result = self.run_export(source=source)
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate JSON key", result.stderr)
        self.assertFalse(self.output.exists())

    def test_invalid_schema_is_rejected_without_publishing(self):
        valid = {"id": "one", "title": "title", "notes": "notes"}
        cases = [
            [], {}, {"pages": None},
            {"pages": [{"page": 2, "records": []}]},
            {"pages": [{"page": True, "records": []}]},
            {"pages": [{"page": 1, "records": {}}]},
            {"pages": [{"page": 1, "records": [{"id": "one"}]}]},
            {"pages": [{"page": 1, "records": [{"id": "one", "title": 3, "notes": ""}]}]},
            {"pages": [{"page": 1, "records": [{"id": "", "title": "", "notes": ""}]}]},
            {"pages": [{"page": 1, "records": [dict(valid, extra="unsupported")]}]},
            {"pages": [{"page": 1, "records": [valid]}, {"page": 2, "records": [valid]}]},
        ]
        for index, payload in enumerate(cases):
            with self.subTest(case=index):
                source = self.directory / "invalid-{}.json".format(index)
                with source.open("x", encoding="utf-8") as stream:
                    json.dump(payload, stream)
                result = self.run_export(source=source)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertFalse(self.output.exists())
                self.assert_no_temporary_files()

    def test_fault_does_not_hide_invalid_final_page(self):
        source = self.source_file({"pages": [
            {"page": 1, "records": []},
            {"page": 2, "records": [{"id": "incomplete"}]},
        ]})
        result = self.run_export(source=source, fault="omit-final-page")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.output.exists())

    def test_invalid_unicode_does_not_publish_a_partial_csv(self):
        source = self.source_file({"pages": [{"page": 1, "records": [
            {"id": "one", "title": "\ud800", "notes": ""}
        ]}]})
        for fault in (None, "omit-final-page"):
            with self.subTest(fault=fault):
                result = self.run_export(source=source, fault=fault)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(self.output.exists())
                self.assert_no_temporary_files()

    def test_missing_source_and_source_directory_fail(self):
        for source in (self.directory / "missing.json", self.directory):
            with self.subTest(source=source.name):
                result = self.run_export(source=source)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(self.output.exists())

    def test_source_at_two_mib_limit_is_accepted(self):
        source = self.directory / "at-limit.json"
        payload = b'{"pages": []}'
        with source.open("xb") as stream:
            stream.write(payload + b" " * (2 * 1024 * 1024 - len(payload)))
        result = self.run_export(source=source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read_records(), [])
        self.assert_no_temporary_files()

    def test_source_larger_than_two_mib_is_rejected_without_output(self):
        source = self.directory / "too-large.json"
        payload = b'{"pages": []}'
        with source.open("xb") as stream:
            stream.write(payload + b" " * (2 * 1024 * 1024 + 1 - len(payload)))
        result = self.run_export(source=source)
        self.assertEqual(result.returncode, 2)
        self.assertIn("2 MiB limit", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.output.exists())
        self.assert_no_temporary_files()

    def test_deeply_nested_json_fails_cleanly_without_output(self):
        source = self.directory / "nested.json"
        with source.open("xb") as stream:
            stream.write(b"[" * 2000 + b"0" + b"]" * 2000)
        result = self.run_export(source=source)
        self.assertEqual(result.returncode, 2)
        # Decoder recursion thresholds vary by Python version. Both a friendly
        # decoder rejection and the subsequent schema rejection meet the contract.
        self.assertIn("export: error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.output.exists())
        self.assert_no_temporary_files()

    def test_source_symlink_and_dangling_symlink_are_rejected(self):
        for exists in (True, False):
            with self.subTest(target_exists=exists):
                source = self.directory / ("source-link.json" if exists else "dangling-source.json")
                target = FIXTURES / "pages.json" if exists else self.directory / "absent.json"
                try:
                    source.symlink_to(target)
                except (NotImplementedError, OSError) as error:
                    self.skipTest("symlinks unavailable: {}".format(error))
                result = self.run_export(source=source)
                self.assertEqual(result.returncode, 2)
                self.assertIn("symlinks and special files are not allowed", result.stderr)
                self.assertTrue(source.is_symlink())
                self.assertFalse(self.output.exists())
                self.assert_no_temporary_files()

    @unittest.skipUnless(hasattr(os, "mkfifo"), "named pipes unavailable")
    def test_source_named_pipe_is_rejected_without_waiting_for_a_writer(self):
        source = self.directory / "source.fifo"
        os.mkfifo(source, 0o600)
        result = self.run_export(source=source)
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlinks and special files are not allowed", result.stderr)
        self.assertFalse(self.output.exists())
        self.assert_no_temporary_files()

    def test_missing_output_parent_is_not_created(self):
        output = self.directory / "missing" / "result.csv"
        result = self.run_export(output=output)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(output.parent.exists())

    def test_existing_file_is_never_overwritten(self):
        original = b"existing user data\x00\xff"
        with self.output.open("xb") as stream:
            stream.write(original)
        for fault in (None, "omit-final-page"):
            with self.subTest(fault=fault):
                result = self.run_export(fault=fault)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(self.output.read_bytes(), original)
                self.assert_no_temporary_files()

    def test_source_cannot_be_used_as_output(self):
        source = self.source_file({"pages": []})
        before = source.read_bytes()
        result = self.run_export(source=source, output=source)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(source.read_bytes(), before)

    def test_existing_output_directory_is_preserved(self):
        self.output.mkdir()
        result = self.run_export()
        self.assertEqual(result.returncode, 2)
        self.assertTrue(self.output.is_dir())
        self.assertEqual(list(self.output.iterdir()), [])

    def test_output_symlink_and_dangling_symlink_are_preserved(self):
        for existing_target in (True, False):
            with self.subTest(existing_target=existing_target):
                target = self.directory / ("target.txt" if existing_target else "absent.txt")
                if existing_target:
                    with target.open("x", encoding="utf-8") as stream:
                        stream.write("leave me alone")
                output = self.directory / ("linked.csv" if existing_target else "dangling.csv")
                try:
                    output.symlink_to(target)
                except (NotImplementedError, OSError) as error:
                    self.skipTest("symlinks unavailable: {}".format(error))
                result = self.run_export(output=output)
                self.assertEqual(result.returncode, 2)
                self.assertTrue(output.is_symlink())
                if existing_target:
                    self.assertEqual(target.read_text(encoding="utf-8"), "leave me alone")
                else:
                    self.assertFalse(target.exists())

    def test_concurrent_same_output_has_one_winner_and_a_complete_file(self):
        command = [sys.executable, str(EXPORTER), "--source", str(FIXTURES / "pages.json"),
                   "--output", str(self.output)]
        processes = [subprocess.Popen(command, cwd=self.directory, text=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        try:
            for process in processes:
                process.communicate(timeout=10)
            self.assertEqual(sorted(process.returncode for process in processes), [0, 2])
            self.assert_complete_export()
            self.assert_no_temporary_files()
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                    process.communicate()

    def test_unknown_fault_is_an_argument_error_without_output(self):
        result = self.run_export(fault="unknown-fault")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.output.exists())

    def test_missing_artifact_cannot_satisfy_the_completeness_check(self):
        with self.assertRaises(FileNotFoundError):
            self.assert_complete_export()


if __name__ == "__main__":
    unittest.main()
