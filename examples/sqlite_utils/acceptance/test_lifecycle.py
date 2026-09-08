"""Standard-library-only regression for the pack's POSIX supervisor.

Run: python -B -m unittest discover -s acceptance -p test_lifecycle.py -v
All subprocesses are synthetic, bounded and owned by this test invocation.
"""
import ast
import contextlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from acceptance import lifecycle

THIS = Path(__file__).resolve()


def wait_for(path, seconds=4):
    end = time.monotonic() + seconds
    while not path.exists() and time.monotonic() < end:
        time.sleep(.01)
    if not path.exists():
        raise AssertionError('Timed out waiting for owned child marker ' + str(path))


def child_role(role, directory, behavior):
    if role == 'writer':
        if behavior == 'cli-timeout-slow':
            time.sleep(.65)
        if behavior == 'ignore-term':
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
        lifecycle.write_record(directory / 'writer.json', {'pid': os.getpid(), 'pgid': os.getpgrp()})
        end = time.monotonic() + 10
        while time.monotonic() < end:
            with (directory / 'heartbeat').open('a') as out:
                out.write('tick\n')
            time.sleep(.03)
        return 0
    if role == 'leader':
        if behavior in ('orphan', 'orphan-slow'):
            if behavior == 'orphan-slow':
                time.sleep(.65)  # Slow interpreter/setup must not select timeout instead.
            subprocess.Popen([sys.executable, '-B', str(THIS), '--child', 'writer', str(directory), behavior])
            wait_for(directory / 'writer.json')
            return 0
        # Exercise the real fixture's invoke, without importing pytest/sqlite-utils
        # or executing the fixture's business setup. No translated implementation.
        source = THIS.with_name('test_onboarding.py')
        journey = next(n for n in ast.parse(source.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'journey')
        invoke = next(n for n in journey.body if isinstance(n, ast.FunctionDef) and n.name == 'invoke')
        namespace = {'sys': sys, 'os': os, 'time': time, 'subprocess': subprocess,
                     'ROOT': THIS.parents[1], 'run': directory, 'commands': {},
                     'write_record': lifecycle.write_record, 'save': lifecycle.write_record}
        if behavior in ('cli-timeout', 'cli-timeout-slow'):
            original_wait = subprocess.Popen.wait

            def scaled_wait(self, timeout=None):
                if timeout == 20:
                    wait_for(directory / 'writer.json')
                return original_wait(self, timeout=.3 if timeout == 20 else timeout)

            subprocess.Popen.wait = scaled_wait
        exec(compile(ast.Module(body=[invoke], type_ignores=[]), str(source), 'exec'), namespace)
        namespace['invoke']('blocking', [str(THIS), '--child', 'writer', str(directory), behavior], module=False)
        return 0
    cmd = [sys.executable, '-B', str(THIS), '--child', 'leader', str(directory), behavior]
    fail_start_record = behavior == 'record-error'
    real_write = lifecycle.write_record

    def record(path, value):
        if fail_start_record and path.name == 'pytest.started.json':
            raise OSError('Synthetic record failure')
        return real_write(path, value)

    real_popen = subprocess.Popen

    class SafetyObservedPopen(real_popen):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            real_write(directory / 'test-owned-group.json', {'pid': self.pid, 'pgid': self.pid})
            self.first_wait = True

        def wait(self, timeout=None):
            if self.first_wait:
                self.first_wait = False
                # The timeout scenarios measure cleanup of a running writer,
                # not interpreter startup speed. Bound readiness separately.
                if behavior not in ('record-error', 'orphan', 'orphan-slow'):
                    wait_for(directory / 'writer.json')
            return super().wait(timeout=timeout)

    with (directory / 'stdout').open('wb') as out, (directory / 'stderr').open('wb') as err:
        with patch.object(lifecycle, 'write_record', record), patch.object(lifecycle.subprocess, 'Popen', SafetyObservedPopen):
            return lifecycle.run_group(cmd, cwd=directory, env={'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1'},
                                       stdout=out, stderr=err, run=directory, timeout=4 if behavior in ('signal', 'interrupt', 'cli-timeout', 'cli-timeout-slow', 'orphan', 'orphan-slow') else .5)


@unittest.skipUnless(os.name == 'posix', 'The acceptance runner requires POSIX')
class LifecycleTests(unittest.TestCase):
    def exercise(self, behavior, expected):
        with tempfile.TemporaryDirectory(prefix='acceptance-lifecycle-') as raw:
            directory = Path(raw)
            runner = subprocess.Popen([sys.executable, '-B', str(THIS), '--child', 'runner', raw, behavior], start_new_session=True)
            try:
                if behavior in ('signal', 'interrupt'):
                    wait_for(directory / 'writer.json')
                    runner.send_signal(signal.SIGTERM if behavior == 'signal' else signal.SIGINT)
                self.assertEqual(runner.wait(timeout=9), expected)
                result = json.loads((directory / 'termination.json').read_text())
                self.assertTrue(result['cleanup']['terminal'], result)
                self.assertEqual(result['cleanup']['group_after_cleanup'], 'absent', result)
                self.assertTrue(result['cleanup']['leader_waited'])
                if behavior not in ('orphan', 'orphan-slow', 'record-error'):
                    started = json.loads((directory / 'blocking.started.json').read_text())
                    writer = json.loads((directory / 'writer.json').read_text())
                    self.assertEqual(started['pid'], writer['pid'])
                    self.assertEqual(started['pgid'], writer['pgid'])
                    self.assertFalse(started['terminal'])
                if behavior in ('cli-timeout', 'cli-timeout-slow'):
                    command = json.loads((directory / 'blocking.command.json').read_text())
                    self.assertTrue(command['timed_out'])
                    self.assertTrue(command['terminal'])
                    self.assertNotEqual(command['returncode'], 0)
                if (directory / 'heartbeat').exists():
                    before = (directory / 'heartbeat').read_bytes()
                    time.sleep(.12)
                    self.assertEqual((directory / 'heartbeat').read_bytes(), before)
                return result
            finally:
                # Safety fallback only for the process group just created here.
                records = [directory / 'test-owned-group.json', directory / 'pytest.started.json', directory / 'writer.json']
                groups = {runner.pid}
                for record in records:
                    if record.exists():
                        groups.add(json.loads(record.read_text())['pgid'])
                for pgid in groups:
                    self.assertGreater(pgid, 1)
                    self.assertNotEqual(pgid, os.getpgrp())
                    with contextlib.suppress(ProcessLookupError):
                        os.killpg(pgid, signal.SIGKILL)
                runner.wait(timeout=2)

    def test_total_timeout_stops_descendant_writes(self):
        self.assertEqual(self.exercise('timeout', 124)['state'], 'pytest timeout')

    def test_sigterm_is_cleaned_before_return(self):
        self.assertEqual(self.exercise('signal', 143)['state'], 'interrupted by signal 15')

    def test_sigint_is_cleaned_before_return(self):
        self.assertEqual(self.exercise('interrupt', 130)['state'], 'interrupted by signal 2')

    def test_sigterm_ignoring_writer_is_escalated(self):
        self.exercise('ignore-term', 124)

    def test_normal_parent_exit_with_live_writer_fails_closed(self):
        self.assertIn('surviving descendants', self.exercise('orphan', 70)['state'])

    def test_slow_startup_does_not_mask_surviving_writer_case(self):
        self.assertIn('surviving descendants', self.exercise('orphan-slow', 70)['state'])

    def test_record_failure_after_spawn_still_reaps_group(self):
        self.assertIn('runner error', self.exercise('record-error', 70)['state'])

    def test_cli_timeout_stops_fixture_before_further_observations(self):
        self.assertEqual(self.exercise('cli-timeout', 1)['state'], 'exited')

    def test_cli_timeout_starts_after_synthetic_writer_is_ready(self):
        self.assertEqual(self.exercise('cli-timeout-slow', 1)['state'], 'exited')

    def test_unknown_observation_cannot_be_reported_terminal(self):
        with tempfile.TemporaryDirectory(prefix='acceptance-unknown-') as raw:
            directory = Path(raw)
            # All observation/signalling are mocked here; no real PID is touched.
            child = unittest.mock.Mock(pid=987654, returncode=0)
            child.wait.return_value = 0
            with patch.object(lifecycle.subprocess, 'Popen', return_value=child), \
                 patch.object(lifecycle, 'group_state', return_value='unknown'), \
                 patch.object(lifecycle.os, 'killpg', side_effect=PermissionError('synthetic denied')), \
                 patch.object(lifecycle.time, 'monotonic', side_effect=range(1000)):
                code = lifecycle.run_group(['synthetic'], cwd=directory, env={}, stdout=None, stderr=None, run=directory)
            result = json.loads((directory / 'termination.json').read_text())
            self.assertEqual(code, 70)
            self.assertFalse(result['cleanup']['terminal'])
            self.assertEqual(result['cleanup']['group_after_cleanup'], 'unknown')
            self.assertIn('UNKNOWN', result['state'])

    def test_interrupted_launch_without_handle_is_unknown(self):
        with tempfile.TemporaryDirectory(prefix='acceptance-launch-') as raw:
            directory = Path(raw)
            with patch.object(lifecycle.subprocess, 'Popen', side_effect=lifecycle.InterruptedRun(signal.SIGTERM)):
                code = lifecycle.run_group(['synthetic'], cwd=directory, env={}, stdout=None, stderr=None, run=directory)
            result = json.loads((directory / 'termination.json').read_text())
            self.assertEqual(code, 70)
            self.assertFalse(result['cleanup']['terminal'])
            self.assertIn('launch state UNKNOWN', result['state'])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--child':
        sys.exit(child_role(sys.argv[2], Path(sys.argv[3]), sys.argv[4]))
    unittest.main()
