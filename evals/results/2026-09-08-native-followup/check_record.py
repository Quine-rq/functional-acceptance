"""Retained evidence consistency, not live execution or collection authenticity."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read(root, name):
    return json.loads((root / name).read_text(encoding='utf-8'))


def check(root=ROOT):
    root = root.resolve()
    manifest = read(root, 'manifest.json')
    names = set()
    for entry in manifest['entries']:
        name = entry['path']
        relative = Path(name)
        require(not relative.is_absolute() and '..' not in relative.parts
                and relative.as_posix() == name, 'Bounded canonical path')
        require(name not in names, 'Unique evidence path')
        names.add(name)
        file = root / relative
        require(file.is_file() and not file.is_symlink()
                and file.resolve().is_relative_to(root), 'Ordinary bounded evidence file')
        require(not any(p.is_symlink() for p in file.parents if p != root and p.is_relative_to(root)), 'No linked evidence parents')
        data = file.read_bytes()
        require(len(data) == entry['bytes'] and hashlib.sha256(data).hexdigest() == entry['sha256'], 'Evidence changed: ' + name)
        if file.suffix in ('.json', '.jsonl', '.md', '.txt', '.py', '.csv', '.stdout', '.stderr', '.xml'):
            # Malformed UTF-8 is an intentional export counterexample in one
            # retained CSV. Scan text safely; the digest above preserves bytes.
            text = data.decode('utf-8', errors='replace')
            require(not re.search(r'(?:sk-ant-|github_pat_)[A-Za-z0-9_-]{24,}', text), 'Credential-shaped material: ' + name)
            require(not re.search(r'/Users/[^\s<>]+|/(?:private/)?var/folders/[^\s<>]+', text), 'Private path: ' + name)
            require(not re.search(r'"type"\s*:\s*"(?:thinking|reasoning)"|"signature"\s*:', text), 'Private native stream field: ' + name)
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    require(not any(p.is_symlink() for p in root.rglob('*')), 'No unregistered symlinks')
    require(actual == names | {'manifest.json', 'check_record.py'}, 'Exact registered file inventory')
    versions = read(root, 'codex/versions.json')
    require([v['completed_trials'] for v in versions] == [12, 2, 12, 12], 'No missing or invented Codex trials')
    for version in versions:
        detail = read(root, 'codex/' + version['version'] + '/summary.json')
        require(len(detail['trials']) == version['completed_trials'], 'Version-scoped native count')
        for trial in detail['trials']:
            prefix = f"codex/{version['version']}/eval-{trial['eval_id']}-{trial['scenario']}/{trial['configuration']}/"
            require(read(root, prefix + 'grading.json')['summary'] == trial['grade_summary'], 'Independent Codex grade retained')
            require(trial['execution_exit'] == 0 and not trial['forced']
                    and not trial['protected_changes'] and trial['actual_model'] is None, 'Native completion without inferred model identity')
            if trial['scenario'] in ('plan', 'historical', 'near-miss'):
                require(trial['created_file_count'] == 0, 'Read-only native scope')
        for config in ('with_skill', 'old_skill'):
            trials = [r for r in detail['trials'] if r['configuration'] == config]
            require(sum(r['grade_summary']['passed'] for r in trials) == version['by_configuration'][config]['passed_assertions'], 'Version aggregate matches individual grades')
    require(versions[-1]['by_configuration']['with_skill']['passed_assertions'] == 24
            and versions[-1]['by_configuration']['old_skill']['passed_assertions'] == 25, 'Keep final candidate failure')
    tokens = 0
    for relative in ('generation/with_skill', 'generation/old_skill', 'handoff/replay', 'handoff/maintenance'):
        metadata = read(root, 'sqlite/' + relative + '/metadata.json')
        require(metadata['source_head'] == '85b1be10c81d9dd3567e36faf8dd411e4a8789bd'
                and metadata['exit_code'] == 0 and not metadata['forced']
                and not metadata['protected_changes'], 'Completed fixed-upstream native call')
        tokens += metadata['usage']['input_tokens'] + metadata['usage']['output_tokens']
        if relative.startswith('handoff/'):
            require(metadata['skill_installed'] is False, 'No-Skill replay and maintenance')
    require(tokens == 1657921, 'Native token sum excludes cached subset double counting')
    red = read(root, 'sqlite/fault/native-red/result.json')
    green = read(root, 'sqlite/fault/native-green/result.json')
    require(red['runner_returncode'] == green['runner_returncode'] == 124
            and red['writer_alive_after_inner_deadline'] and not red['passed']
            and green['no_post_return_writes'] and green['active_pid_recorded']
            and green['passed'], 'Preserve actual native lifecycle counterexample')
    summary = read(root, 'claude/summary.json')
    rows = summary['records']
    require(len(rows) == len({r['id'] for r in rows}) == 10, 'All ten Claude calls retained')
    costs = passed = reads = 0
    for row in rows:
        prefix = 'claude/runs/' + row['id'] + '/'
        timing = read(root, prefix + 'timing.json')
        grading = read(root, prefix + 'grading.json')
        observation = read(root, prefix + 'observations.json')
        require(grading['summary'] == row['score'], 'Frozen per-trial grade')
        require(observation['before_after_actual_equal'] and observation['child_ended']
                and observation['native_child_exit_code'] == 0 and not observation['forced'], 'Observed read-only completion')
        require(not observation['protected_changes'] and not observation['created_files'], 'Retained read-only scope')
        require(observation['loading'] == row['loading'], 'No inferred loading promotion')
        require(timing['client_estimated_cost_usd'] == row['client_estimated_cost_usd'], 'Per-trial cost match')
        costs += timing['client_estimated_cost_usd']
        passed += grading['summary']['passed']
        reads += observation['loading'] == 'OBSERVED_COMPLETE_READ'
    require(abs(costs - summary['totals']['client_estimated_cost_usd']) < 1e-9
            and abs(costs - .4295049) < 1e-9 and costs < 5, 'CLI cost estimates, not verified billing')
    require(passed == 31 and reads == 8, 'Retain failed assertions and unverified slash loading')
    for version in read(root, 'claude/versions.json'):
        require(hashlib.sha256((root / 'claude' / version['file']).read_bytes()).hexdigest() == version['sha256'], 'Actual Skill version bytes')
    results = read(root, 'checks/integrated/results.json')
    require(len(results) == 13 and all(r['code'] == 0 and r['signal'] is None for r in results), 'Integrated local checks')
    for version in ('310', '314'):
        for name, count in [('core', 93), ('export', 23), ('lifecycle', 11), ('identity', 3)]:
            log = (root / f'checks/integrated/{version}-{name}.stderr.txt').read_text()
            require(re.search(rf'Ran {count} tests in .*\n\nOK\s*$', log), 'Actual distinct test count')
    require(read(root, 'checks/initial-failure.json')['failures'] == 1, 'Keep initial test failure')
    probes = read(root, 'checks/startup-probe.json')
    require([r['returncode'] for r in probes] == [124, 70]
            and all(r['cleanup']['terminal'] for r in probes), 'Timing counterexample retained')
    require(read(root, 'checks/cli-startup-red/result.json')['code'] == 1
            and read(root, 'checks/cli-startup-green/result.json')['code'] == 0, 'Inner startup RED/GREEN retained')
    plugin = read(root, 'checks/identity/real-plugin-assessment.json')
    require([r['code'] for r in plugin['records']] == [0, 2, 0]
            and [r['plugin_marker_present'] for r in plugin['records']] == [True, False, False]
            and not plugin['changed_source_files'], 'Real pre-import rejection and healthy control')
    native = root / 'checks/native-final'
    canonical = lambda rows: json.dumps(sorted(rows, key=lambda row: row['id']), ensure_ascii=False, sort_keys=True)
    expected = read(native, 'contacts.input.json')
    require(canonical(read(native, 'contacts.export.json')) == canonical(expected), 'Complete final native export')
    snapshots = [read(native, p.name) for p in sorted(native.glob('*.snapshot.json'))]
    require(len(snapshots) == 6 and all(s['unrelated'] == read(native, 'unrelated.input.json') for s in snapshots), 'Six native unrelated-data boundaries')
    require(all(canonical(s['contacts']) == canonical(expected) for s in snapshots[1:]), 'All post-import contacts preserved')
    termination = read(native, 'termination.json')
    require(termination['returncode'] == 0 and termination['cleanup']['terminal']
            and termination['cleanup']['group_after_cleanup'] == 'absent', 'Final native group termination')
    commands = [read(native, p.name) for p in native.glob('*.command.json')]
    require(len(commands) == 10 and all(c['terminal'] and not c['timed_out'] for c in commands), 'Native CLI termination')
    require(read(native, '05-duplicate.command.json')['returncode'] != 0, 'Actual duplicate refusal')
    identities = read(native, 'source-sha256.json')
    for name in ('__init__.py', 'run.py', 'lifecycle.py', 'test_onboarding.py'):
        require(hashlib.sha256((root / 'checks/integrated-source' / name).read_bytes()).hexdigest() == identities['acceptance/' + name], 'Final executed pack identity')
    print(f'Consistent retained record: {len(names)} files; not live execution, authenticity or billing proof.')


if __name__ == '__main__':
    check()
