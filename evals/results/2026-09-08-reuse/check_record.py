"""Verify retained material consistency; no live hosts, browsers or credentials."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


def require(value, message):
    if not value:
        raise AssertionError(message)


manifest = read('manifest.json')
names = set()
for entry in manifest['entries']:
    relative = Path(entry['path'])
    require(not relative.is_absolute() and '..' not in relative.parts, 'Bounded record path')
    require(entry['path'] not in names, 'Unique record path')
    names.add(entry['path'])
    file = ROOT / relative
    require(file.is_file() and not file.is_symlink(), 'Ordinary retained file')
    content = file.read_bytes()
    require(len(content) == entry['bytes'], 'Retained size')
    require(hashlib.sha256(content).hexdigest() == entry['sha256'], 'Retained digest: ' + entry['path'])

actual_files = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()}
require(actual_files == names | {'manifest.json', 'README.md', 'check_record.py'}, 'No unregistered evidence files')

index = read('stability/public-candidate-index.json')['entries']
require(len(index) == 17, 'Sixteen scheduled runs plus retained preflight failure')
rows = read('stability/results.json')
require(len(rows) == 16 and len({row['id'] for row in rows}) == 16, 'All scheduled unique runs')
require({row['id'] for row in rows} == {row['id'] for row in read('stability/schedule.json')['schedule']}, 'Frozen schedule preserved')
starts = closes = 0
for row in index:
    prefix = 'native/' + row['id']
    result = read(prefix + '/result.json')
    events = [json.loads(line) for line in (ROOT / prefix / 'events.jsonl').read_text().splitlines()]
    identity = next(e for e in events if e['kind'] == 'identity')
    require(identity['head'] == '65813a75404b1319aca8b09700fadc0b15adabaf', 'Pinned upstream')
    require(hashlib.sha256((ROOT / prefix / 'executed_regression.py').read_bytes()).hexdigest() == identity['script_sha256'], 'Executed native source')
    for name, digest in read(prefix + '/pack-identity.json').items():
        require(hashlib.sha256((ROOT / prefix / 'native-pack' / name).read_bytes()).hexdigest() == digest, 'Pack snapshot')
    starts += sum(e['kind'] == 'browser_started' for e in events)
    closes += sum(e['kind'] == 'browser_closed' for e in events)
    require(result['execution_cleanup'] == 'stopped', 'Native cleanup receipt')
    if row['id'] == 'retained-permission-attempt':
        require(result['business_verdict'] == 'UNVERIFIED' and result['obstacle_kind'] == 'environment', 'Preserve startup gap')
        require(not any(e['kind'] == 'browser_started' for e in events), 'No browser execution during denied startup')
        continue
    observed = next(r for r in rows if r['id'] == row['id'])
    require(observed['termination']['code'] == result['exit_code'] == observed['expected_exit'], 'Observed process exit')
    require(observed['independent_cleanup_known'] and not observed['remaining_owned_processes'] and not observed['timed_out'], 'Independent termination observation')
    require(observed['preservation']['prior_bookmarks_unchanged'] and observed['preservation']['prior_tags_unchanged'], 'Prior data preservation')
    checks = {e['name']: e for e in events if e['kind'] == 'check'}
    db = {e['label']: e['rows'] for e in events if e['kind'] == 'database_observation'}
    if row['id'].startswith(('r1-', 'r2-', 'r3-')):
        require(result['business_verdict'] == 'PASS' and result['qualified_pass'], 'Healthy/recovery scope')
        require(db['initial'] == db['control cleaned'], 'Same prior bookmark rows after UI cleanup')
        require(checks['server_restart_retrieval']['evidence']['fields']['notes'] == identity['expected_notes'], 'Exact notes after restart')
        if result['case'] == 'lost-response':
            require(any(e['kind'] == 'response_lost_after_server' and e['status'] == 302 for e in events), 'Response actually lost after write')
            require(checks['uncertain_write_found_once']['evidence']['object_ids'] == [result['target_id']], 'Same unique recovered object')
        if result['case'] == 'expired-session':
            require(checks['expired_session_recovered']['evidence']['bookmark_id'] == result['target_id'], 'Same object after relogin')
    elif row['id'] == 'control-note-loss':
        require(result['business_verdict'] == 'FAIL' and result['target_id'] == 47, 'Retained seeded defect')
        require(checks['save_private_tags_notes']['evidence']['fields']['notes'] == '' and identity['expected_notes'], 'Actual missing notes counterexample')
    else:
        require(result['business_verdict'] == 'UNVERIFIED' and not result['qualified_pass'], 'No false qualification')
        if row['id'] == 'control-missing-observation':
            require(result['checks']['server_restart_retrieval_database'] == 'UNVERIFIED', 'Required observation remains missing')
        if row['id'] == 'safety-occupied-port':
            require(observed['unowned_listener_preserved'], 'Do not kill foreign listener')

audit = read('stability/final-audit.json')
require(starts == closes == audit['browser_starts'] == audit['browser_closes'] == 67, 'Browser accounting')
require(audit['final_bookmark_ids'] == [3, 12, 47] and audit['original_bookmark_ids'] == [3, 12], 'Failure retained, old objects retained')
require(audit['original_tag_count'] == 15 and audit['final_tag_count'] == 29, 'Do not claim empty database')
matrix = read('behavior/execution-matrix.json')
require((matrix['completed_codex_trials'], matrix['not_run_codex_trials'], matrix['completed_pairs']) == (1, 11, 0), 'Do not fabricate a paired benchmark')
require(not matrix['claude']['attempted'], 'No new second-host claim')
trial = 'behavior/eval-1-coverage-explicit/old_skill/'
observation = read(trial + 'outputs/observations.json')
with (ROOT / trial / 'outputs/export.csv').open(newline='', encoding='utf-8') as file:
    actual = list(csv.DictReader(file))
require(actual == observation['actual'] == observation['expected'][:-1], 'Inspect real retained CSV')
require(observation['before_sha256'] == observation['after_sha256'], 'Protected inputs unchanged')
require(read(trial + 'outputs/existing-output.json')['returncode'] == 2, 'Existing output actually attempted')
require(read(trial + 'grading.json')['summary'] == {'passed': 6, 'failed': 0, 'total': 6, 'pass_rate': 1.0}, 'Single independently graded record')
for config in ['with_skill', 'old_skill']:
    metadata = read('sqlite/' + config + '/metadata.json')
    require(metadata['exit_code'] == 1 and metadata['usage'] is None, 'SQLite host startup remained unexecuted')
    require((ROOT / 'sqlite' / config / 'events.jsonl').read_bytes() == b'', 'No fabricated model/tool events')
require('delta' not in read('behavior/benchmark.json')['run_summary'], 'No delta against missing configuration')
old_grade = read('upgrade/grade.json')
recheck = read('upgrade/recheck.json')
require(old_grade['summary']['failed'] == 1 and recheck['summary']['passed'] == 9, 'Keep original upgrade failure and recheck')
counterexample = recheck['original_counterexample_recheck']
require(counterexample['probe_modes_octal'] == ['0755', '0655', '0755'], 'Same permission counterexample')
require(counterexample['inputs_unchanged'] and counterexample['installed_exec']['error'] == 'EACCES', 'Real execution still refused')
require(counterexample['review_exit'] == 2 and counterexample['local_changes']['changed'] == ['probe.sh'], 'Permission loss detected')
for name, digest in recheck['reviewed_sha256'].items():
    require(hashlib.sha256((ROOT / 'upgrade/reviewed' / name).read_bytes()).hexdigest() == digest, 'Reviewed fixed source snapshot')
require(read('checks/post-review/result.json')['exit_code'] == 0, 'Final installer test execution')
print(f'Retained consistency checks passed: {len(names)} files, 17 native attempts, 1 unpaired host trial. Not live execution or authenticity proof.')
