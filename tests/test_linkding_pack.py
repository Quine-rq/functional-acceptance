"""Native pack error/report contracts; real browser checks are a separate gate."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

PACK = Path(__file__).resolve().parents[1] / 'examples/linkding'
spec = importlib.util.spec_from_file_location('linkding_support', PACK / 'support.py')
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)


class VerdictTests(unittest.TestCase):
    def test_healthy_requires_complete_evidence_and_cleanup(self):
        self.assertTrue(support.classify({'save': 'PASS'}, None, False)['qualified_pass'])
        self.assertFalse(support.classify({'save': 'PASS'}, None, True)['qualified_pass'])

    def test_business_failure_survives_unknown_checks_and_cleanup(self):
        result = support.classify({'save': 'FAIL', 'delete': 'UNVERIFIED'}, 'business', True)
        self.assertEqual((result['business_verdict'], result['exit_code'], result['completion']), ('FAIL', 1, 'partial'))

    def test_environment_and_harness_errors_are_not_product_failures(self):
        for obstacle in ('environment', 'harness-or-observation', 'interrupted', 'evidence-delivery'):
            with self.subTest(obstacle=obstacle):
                result = support.classify({'save': 'PASS'}, obstacle, False)
                self.assertEqual(result['business_verdict'], 'UNVERIFIED')
                self.assertEqual(result['exit_code'], 2)

    def test_missing_observation_and_empty_suite_never_pass(self):
        for checks in ({}, {'save': 'PASS', 'restart': 'UNVERIFIED'}):
            self.assertEqual(support.classify(checks, None, False)['business_verdict'], 'UNVERIFIED')

    def test_failed_known_control_is_not_a_qualified_pass(self):
        result = support.classify({'notes': 'FAIL'}, None, False)
        self.assertEqual(result['exit_code'], 1)
        self.assertFalse(result['qualified_pass'])

    def test_unknown_status_cannot_silently_pass(self):
        result = support.classify({'notes': 'PAAS'}, None, False)
        self.assertEqual(result['exit_code'], 2)
        self.assertEqual(result['obstacle_kind'], 'invalid-check-status')


class SafetyTests(unittest.TestCase):
    def test_signal_request_does_not_throw_inside_a_browser_operation(self):
        stopping = support.StopRequest()
        stopping.checkpoint()
        stopping.request(15, None)  # Signal callback itself must only set state.
        self.assertTrue(stopping.requested)
        with self.assertRaises(support.ExecutionInterrupted):
            stopping.checkpoint()  # Throw only at an explicit caller boundary.

    def test_login_and_debug_404_or_500_are_not_captured(self):
        for url, debug in (('http://127.0.0.1/login/', False),
                           ('http://127.0.0.1/bookmarks/1/edit', True)):
            page = Mock(url=url)
            page.locator.return_value.count.return_value = int(debug)
            self.assertFalse(support.capture_allowed(page))
        page = Mock(url='http://127.0.0.1/bookmarks/')
        page.locator.return_value.count.return_value = 0
        self.assertTrue(support.capture_allowed(page))
        self.assertIn('body > #explanation', page.locator.call_args.args[0])

    def test_pack_snapshot_keeps_executable_bytes_and_refuses_replacement(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'source'; source.mkdir()
            (source / 'server.py').write_text('print("first")')
            (source / 'private.json').write_text('not copied')
            expected = support.snapshot_pack(source, root / 'snapshot')
            (source / 'server.py').write_text('print("second")')
            self.assertEqual(support.inventory(root / 'snapshot'), expected)
            self.assertNotEqual(support.inventory(source), expected)
            self.assertFalse((root / 'snapshot/private.json').exists())
            with self.assertRaises(FileExistsError):
                support.snapshot_pack(source, root / 'snapshot')

    def test_wrong_pin_and_tracked_changes_are_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / 'manage.py').touch()
            for answers in (['wrong-pin', ''], [support.PIN, 'bookmarks/models.py']):
                with patch.object(support.subprocess, 'check_output', side_effect=answers):
                    with self.assertRaises(ValueError):
                        support.validate_project(temp)

    def test_credentials_reject_symlink_permissions_and_bad_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state = root / '.acceptance-study'; state.mkdir(mode=0o700)
            (state / 'artifacts').mkdir()
            (state / 'db.sqlite3').touch()
            private = state / 'private.json'
            valid = {'django_secret': 'd' * 30, 'users': {'fa_alice': 'a' * 30, 'fa_bob': 'b' * 30}}
            private.write_text(json.dumps(valid)); private.chmod(0o600)
            self.assertEqual(support.load_credentials(root), valid)
            private.chmod(0o644)
            with self.assertRaises(ValueError): support.load_credentials(root)
            private.chmod(0o600)
            for invalid in ([], {'django_secret': 'd' * 30, 'users': []}, {'unexpected': 1}):
                private.write_text(json.dumps(invalid))
                with self.assertRaises(ValueError): support.load_credentials(root)
            private.unlink(); private.symlink_to(state / 'db.sqlite3')
            with self.assertRaises(ValueError): support.load_credentials(root)

    def test_reviewed_unicode_extension_preserves_original_contract(self):
        original = support.initial_notes('example', 'healthy')
        extended = support.initial_notes('example', 'unicode-notes')
        self.assertTrue(extended.startswith(original + '\n'))
        self.assertIn('🧭', extended)
        self.assertIn('"quoted"', extended)


class IOTests(unittest.TestCase):
    def test_private_exception_retains_locator_and_redacts_known_secrets(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'obstacle.private.txt'
            support.private_exception(path, TimeoutError('Confirm button: synthetic-secret'), ['synthetic-secret'])
            self.assertIn('Confirm button', path.read_text())
            self.assertNotIn('synthetic-secret', path.read_text())
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                support.private_exception(path, ValueError('later'), [])

    def test_complete_receipt_published_without_replacement(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'result.json'
            support.publish_json(path, {'state': 'first'})
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                support.publish_json(path, {'state': 'second'})
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse(path.with_name('result.json.pending').exists())

    def test_preexisting_pending_is_not_owned_or_deleted(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'result.json'
            pending = Path(temp) / 'result.json.pending'
            pending.write_text('someone else')
            with self.assertRaises(FileExistsError):
                support.publish_json(path, {})
            self.assertEqual(pending.read_text(), 'someone else')
            self.assertFalse(path.exists())

    def test_pipe_output_is_retained_private_and_secret_redacted(self):
        with tempfile.TemporaryDirectory() as temp:
            process = subprocess.Popen([sys.executable, '-c',
                'import sys;print("before synthetic-password after");print("startup problem",file=sys.stderr)'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logs = support.ProcessLogs(process, Path(temp), 'app', ['synthetic-password'])
            process.wait(timeout=10)
            result = logs.finish()
            self.assertEqual(result['errors'], [])
            stdout = (Path(temp) / result['files'][0]).read_text()
            self.assertIn('[REDACTED]', stdout)
            self.assertNotIn('synthetic-password', stdout)
            self.assertIn('startup problem', (Path(temp) / result['files'][1]).read_text())
            self.assertEqual((Path(temp) / result['files'][0]).stat().st_mode & 0o777, 0o600)

    def test_large_unterminated_line_is_bounded_and_drained(self):
        with tempfile.TemporaryDirectory() as temp:
            process = subprocess.Popen([sys.executable, '-c', 'import sys;sys.stdout.write("x"*3000000)'],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logs = support.ProcessLogs(process, Path(temp), 'app', [])
            self.assertEqual(process.wait(timeout=10), 0)
            result = logs.finish()
            self.assertEqual(result['errors'], [])
            self.assertEqual(result['truncated'], ['app.stdout.private.txt'])
            self.assertLess((Path(temp) / result['files'][0]).stat().st_size, support.MAX_LOG + 100)

    def test_unknown_project_fails_before_creating_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, '-B', str(PACK / 'accept.py'), '--project', temp,
                                     '--browser', sys.executable], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(json.loads(result.stdout)['obstacle_kind'], 'environment')
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_help_requires_no_application_dependency(self):
        result = subprocess.run([sys.executable, '-B', str(PACK / 'accept.py'), '--help'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--browser', result.stdout)


class NavigationTests(unittest.TestCase):
    def test_listener_is_armed_before_action_and_released_after_wait(self):
        page = Mock()
        with support.turbo_visit_completed(page, '?details=14'):
            page.click('View')
        self.assertEqual([call[0] for call in page.mock_calls],
                         ['evaluate', 'click', 'wait_for_function', 'evaluate'])
        options = page.evaluate.call_args_list[0].args[1]
        self.assertEqual(options['href'], '?details=14')
        self.assertEqual(page.wait_for_function.call_args.kwargs['arg'], options['key'])
        self.assertEqual(page.evaluate.call_args_list[-1].args[1], options['key'])

    def test_failed_action_releases_listener_without_waiting(self):
        page = Mock()
        page.click.side_effect = ValueError('action failed')
        with self.assertRaisesRegex(ValueError, 'action failed'):
            with support.turbo_visit_completed(page, '?details=14'):
                page.click('View')
        page.wait_for_function.assert_not_called()
        self.assertEqual(page.evaluate.call_count, 2)

    def test_missing_completed_event_times_out_and_releases_listener(self):
        page = Mock()
        page.wait_for_function.side_effect = TimeoutError('navigation incomplete')
        with self.assertRaisesRegex(TimeoutError, 'navigation incomplete'):
            with support.turbo_visit_completed(page, '?details=14'):
                page.click('View')
        self.assertEqual(page.evaluate.call_count, 2)

    def test_listener_cleanup_error_cannot_turn_a_success_into_silent_pass(self):
        page = Mock()
        page.evaluate.side_effect = [None, RuntimeError('listener cleanup failed')]
        with self.assertRaisesRegex(RuntimeError, 'listener cleanup failed'):
            with support.turbo_visit_completed(page, '?details=14'):
                page.click('View')


if __name__ == '__main__':
    unittest.main()
