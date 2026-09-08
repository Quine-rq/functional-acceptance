"""POSIX ownership and bounded teardown for this acceptance pack, not a daemon."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def write_record(path, value):
    """A record is either absent or complete; absence is never terminal proof."""
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def group_state(pgid):
    try:
        os.killpg(pgid, 0)
        return 'present'
    except ProcessLookupError:
        return 'absent'
    except OSError:
        return 'unknown'


def finish_group(process, grace=2):
    """Only a group created in this call may be signalled; never replay disk PIDs."""
    pgid = process.pid  # start_new_session=True: the child is the group leader.
    assert pgid > 1 and pgid != os.getpgrp()
    errors = []
    initial = group_state(pgid)
    for sig in (signal.SIGTERM, signal.SIGKILL):
        if group_state(pgid) == 'absent':
            break
        try:
            os.killpg(pgid, sig)
        except ProcessLookupError:
            pass
        except OSError as error:
            errors.append(type(error).__name__ + ': ' + str(error))
        deadline = time.monotonic() + grace
        while time.monotonic() < deadline:
            process.poll()  # Reap our direct child; orphan reaping belongs to OS.
            if group_state(pgid) == 'absent':
                break
            time.sleep(.02)
    try:
        process.wait(timeout=grace)
        waited = True
    except subprocess.TimeoutExpired:
        waited = False
    state = group_state(pgid)
    return {'pgid': pgid, 'group_at_cleanup': initial, 'group_after_cleanup': state,
            'leader_waited': waited, 'leader_returncode': process.returncode,
            'terminal': waited and state == 'absent', 'errors': errors}


class InterruptedRun(Exception):
    def __init__(self, signum):
        self.signum = signum


def run_group(argv, *, cwd, env, stdout, stderr, run, timeout=180):
    if os.name != 'posix':
        raise RuntimeError('This pack requires POSIX process-group support')
    process = None
    code, state = 70, 'launch failed'
    outcome = {'started_unix': time.time(), 'timeout_seconds': timeout}
    previous = {}

    def interrupted(signum, _frame):
        raise InterruptedRun(signum)

    for signum in (signal.SIGINT, signal.SIGTERM):
        previous[signum] = signal.signal(signum, interrupted)
    try:
        process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        write_record(run / 'pytest.started.json', {'pid': process.pid, 'pgid': process.pid,
                     'argv': argv, 'started_unix': outcome['started_unix'], 'terminal': False})
        try:
            code, state = process.wait(timeout=timeout), 'exited'
        except subprocess.TimeoutExpired:
            code, state = 124, 'pytest timeout'
    except InterruptedRun as error:
        code, state = 128 + error.signum, 'interrupted by signal ' + str(error.signum)
    except BaseException as error:
        code, state = 70, 'runner error: ' + type(error).__name__ + ': ' + str(error)
    finally:
        # A second Ctrl-C/TERM cannot interrupt bounded teardown and lose ownership.
        for signum in previous:
            signal.signal(signum, signal.SIG_IGN)
        try:
            if process is None:
                # An exception/signal inside Popen may precede the returned
                # handle. Do not convert lack of a PID record into proof of no
                # child; this uncommon launch window is explicitly fail-closed.
                cleanup = {'terminal': False, 'group_after_cleanup': 'unknown; no returned process handle', 'leader_waited': False}
                code, state = 70, state + '; launch state UNKNOWN; retain artifacts, do not retry/clean'
            else:
                cleanup = finish_group(process)
                if not cleanup['terminal']:
                    code, state = 70, state + '; process state UNKNOWN; retain artifacts, do not retry/clean'
                elif state == 'exited' and cleanup['group_at_cleanup'] != 'absent':
                    code, state = 70, 'pytest exited with surviving descendants; group stopped'
            outcome.update({'pid': process.pid if process else None, 'returncode': code, 'state': state,
                            'cleanup': cleanup, 'ended_unix': time.time()})
            write_record(run / 'termination.json', outcome)
        finally:
            for signum, handler in previous.items():
                signal.signal(signum, handler)
    return code
