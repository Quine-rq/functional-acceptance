"""Recheck retained bytes and observations; does not run hosts or prove authenticity."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


for name in ('behavior-manifest.json', 'native-manifest.json'):
    for relative, identity in read(ROOT / name)['files'].items():
        path = (ROOT / relative).resolve()
        require(path.is_relative_to(ROOT) and not path.is_symlink(), relative)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == identity['published_sha256'], relative)

records = sorted((ROOT / 'behavior').iterdir())
require(len(records) == 11, 'Keep ten current trials and the separate old-Skill trial')
csv_count = 0
for record in records:
    meta, grade = read(record / 'metadata.json'), read(record / 'grading.json')
    require(meta['code'] == 0 and not meta['forced'], record.name + ' host completion')
    require(not meta['protected_changes'], record.name + ' protected inputs')
    require(sum(e['passed'] for e in grade['expectations']) == grade['summary']['passed'], record.name + ' grade arithmetic')
    if meta['scenario'] != 'coverage':
        require(meta['created_files'] == [], record.name + ' read-only file inventory')
        continue
    fixture = read(record / 'project/fixtures/pages.json')
    expected = [row for page in fixture['pages'] for row in page['records']]
    paths = [p for p in meta['created_files'] if p.endswith('.csv')]
    require(len(paths) == 1, record.name + ' actual CSV count')
    with (record / 'project' / paths[0]).open(encoding='utf-8', newline='') as stream:
        actual = list(csv.DictReader(stream))
    require(len(expected) == 5 and len(actual) == 4 and actual == expected[:-1], record.name + ' exact observed defect')
    require(expected[-1]['id'] == 'r-005', record.name + ' missing record')
    csv_count += 1
require(csv_count == 7, 'Seven real CSV outcomes including old Skill')
require(not read(ROOT / 'behavior/codex-missing-with-v1/grading.json')['skill_loading']['skill_body_read'], 'Do not upgrade non-loading to invocation')
for config in ('with', 'without'):
    grade = read(ROOT / f'behavior/codex-coverage-{config}-v2/grading.json')
    require(not grade['expectations'][3]['passed'], 'Keep unexecuted overwrite branch visible')

cases = {'healthy': (0, 'PASS'), 'note-loss': (1, 'FAIL'),
         'missing-observation': (2, 'UNVERIFIED'), 'expired-session': (0, 'PASS'),
         'lost-response': (0, 'PASS'), 'unicode-notes': (0, 'PASS')}
final = read(ROOT / 'independent/final-results.json')
require(len(final) == 4 and [r['scenario'] for r in final] == ['healthy', 'note-loss', 'missing-observation', 'expired-session'], 'Keep matrix stopped at unexpected timeout')
for row in final:
    directory = ROOT / 'native/independent' / row['run_dir']
    result = read(directory / 'result.json')
    events = [json.loads(line) for line in (directory / 'events.jsonl').read_text().splitlines()]
    expected = (2, 'UNVERIFIED') if row['scenario'] == 'expired-session' else cases[row['scenario']]
    require((row['code'], result['business_verdict']) == expected, row['scenario'])
    require(result['execution_cleanup'] == 'stopped', 'Independent cleanup')
    require(all(p['returncode'] is not None and p['port_closed'] for p in result['processes']), 'Recorded services stopped')
    require(any(e['kind'] == 'execution_inputs_unchanged' for e in events), 'Fixed source/environment identity')
    identity = next(e for e in events if e['kind'] == 'identity')
    require(hashlib.sha256((directory / 'executed_regression.py').read_bytes()).hexdigest() == identity['script_sha256'], 'Executed script snapshot')
    for name, digest in read(directory / 'pack-identity.json').items():
        require(hashlib.sha256((directory / 'native-pack' / name).read_bytes()).hexdigest() == digest, 'Native pack snapshot')
    if row['scenario'] == 'note-loss':
        failed = next(e for e in events if e['kind'] == 'check' and e['name'] == 'save_private_tags_notes')
        require(failed['status'] == 'FAIL' and failed['evidence']['fields']['notes'] == '', 'Actual note loss')
        continue
    db = {e['label']: e['rows'] for e in events if e['kind'] == 'database_observation'}
    checks = {e['name']: e for e in events if e['kind'] == 'check'}
    require(any(e['kind'] == 'sensitive_page_evidence_omitted' and e['label'] == 'bob-write-denied' for e in events), 'Debug 404 capture omitted')
    require(not any(e['kind'] == 'browser_evidence' and e['label'] == 'bob-write-denied' for e in events), 'No debug-page evidence claim')
    if row['scenario'] == 'missing-observation':
        require(result['checks']['server_restart_retrieval_database'] == 'UNVERIFIED', 'Missing observation stays unverified')
    if row['scenario'] == 'expired-session':
        require(checks['expired_session_recovered']['evidence']['bookmark_id'] == result['target_id'], 'Same object after login')
        require('control cleaned' not in db and result['obstacle_kind'] == 'harness-or-observation', 'Keep cleanup gap visible')
        require(any(r['id'] == result['control_id'] for r in db['target deleted']), 'Pending control object retained')
    else:
        require(db['initial'] == db['invalid URL'] == db['control cleaned'], 'Prior bookmark baseline retained')
    if row['scenario'] == 'lost-response':
        require(checks['uncertain_write_found_once']['evidence']['object_ids'] == [result['target_id']], 'No blind resubmit')
        require(any(e['kind'] == 'response_lost_after_server' and e['status'] == 302 for e in events), 'Real POST completed before loss')
    if row['scenario'] == 'unicode-notes':
        observed = checks['server_restart_retrieval']['evidence']['fields']['notes']
        require(observed == identity['expected_notes'] and '🧭' in observed and '中文验收' in observed, 'Exact Unicode after restart')

failed = read(ROOT / 'controllers/hardening-native-faults/results.json')[0]
require(failed['signal'] == 'SIGKILL' and failed['forced'] and failed['result'] is None, 'Keep failed interrupted attempt')
fixed = {r['scenario']: r for r in read(ROOT / 'controllers/hardening-native-faults-fixed/results.json')}
require(set(fixed) == {'interrupt', 'receipt-collision', 'occupied-port'}, 'Three fault probes')
require(all(r['code'] == 2 and not r['forced'] and r['owned_services_stopped'] for r in fixed.values()), 'Fault probes stop and cannot qualify')
require(fixed['interrupt']['result']['obstacle_kind'] == 'interrupted', 'Controlled interrupted verdict')
require(fixed['receipt-collision']['result'] is None and fixed['receipt-collision']['pending_receipt'], 'Pending receipt is not success')
require(fixed['occupied-port']['unowned_listener_preserved'], 'Do not stop unowned listeners')

diagnostic = read(ROOT / 'independent/diagnostic-results.json')
require([r['scenario'] for r in diagnostic] == ['expired-session', 'lost-response', 'unicode-notes'], 'Keep all three explicit diagnostic attempts')
for row in diagnostic:
    directory = ROOT / 'native/independent' / row['run_dir']
    result = read(directory / 'result.json')
    events = [json.loads(line) for line in (directory / 'events.jsonl').read_text().splitlines()]
    identity = next(e for e in events if e['kind'] == 'identity')
    require(hashlib.sha256((directory / 'executed_regression.py').read_bytes()).hexdigest() == identity['script_sha256'], 'Diagnostic script identity')
    for name, digest in read(directory / 'pack-identity.json').items():
        require(hashlib.sha256((directory / 'native-pack' / name).read_bytes()).hexdigest() == digest, 'Diagnostic pack snapshot')
    checks = {e['name']: e for e in events if e['kind'] == 'check'}
    db = {e['label']: e['rows'] for e in events if e['kind'] == 'database_observation'}
    require(result['execution_cleanup'] == 'stopped' and not row['timed_out'], 'Diagnostic processes stopped without watchdog')
    require(any(e['kind'] == 'execution_inputs_unchanged' for e in events), 'Diagnostic fixed inputs')
    if row['scenario'] == 'unicode-notes':
        require((row['code'], result['business_verdict']) == (2, 'UNVERIFIED') and result['data_cleanup'].startswith('not-completed-or-unobserved;'), 'Keep second cleanup failure')
        observed = checks['server_restart_retrieval']['evidence']['fields']['notes']
        require(observed == identity['expected_notes'] and '🧭' in observed and '中文验收' in observed, 'Actual Unicode retained despite later cleanup failure')
        steps = [e['step'] for e in events if e['kind'] == 'native_step']
        require('target.confirm_click' in steps and 'target.modal_closed' not in steps, 'Precise incomplete confirm step')
        require('control cleaned' not in db and not result['qualified_pass'], 'Do not upgrade partial run')
    else:
        require((row['code'], result['business_verdict'], result['data_cleanup']) == (0, 'PASS', 'baseline-restored'), 'Diagnostic complete scoped result')
        require(db['initial'] == db['control cleaned'], 'Diagnostic prior rows preserved')
        if row['scenario'] == 'expired-session':
            require(checks['expired_session_recovered']['evidence']['bookmark_id'] == result['target_id'], 'Diagnostic same object after login')
        else:
            require(checks['uncertain_write_found_once']['evidence']['object_ids'] == [result['target_id']], 'One object after uncertain write')
            require(any(e['kind'] == 'response_lost_after_server' and e['status'] == 302 for e in events), 'Actual POST completed before response loss')

red_root = ROOT / 'diagnostics/raf-render-callsite-injection'
green_root = ROOT / 'diagnostics/raf-render-wait-recheck'
require((red_root / 'observe.js').read_bytes() == (green_root / 'observe.js').read_bytes(), 'Timing injection unchanged across regression recheck')
red, green = read(red_root / 'result.json'), read(green_root / 'result.json')
require(red['source_hashes'] == green['source_hashes'], 'Same application and timing-control source')
for probe, is_green in ((red, False), (green, True)):
    require(probe['error_type'] is None and not probe['blocked_write_attempts'] and not probe['confirm_clicked'], 'Non-destructive diagnostic boundary')
    require(probe['all_bookmark_rows_unchanged'] and probe['ports_free'], 'Diagnostic baseline and service cleanup')
    rounds = probe['groups'][0]['rounds']
    require(len(rounds) == 3 and probe['scheduling_injection']['not_natural_root_cause_proof'], 'Three scoped controlled observations')
    for row in rounds:
        events = row['events']
        match = next(e for e in events if e['kind'] == 'injection.matched')
        require(match['callback_source'] == '()=>e()' and match['matched_callsite']['line'] == 19 and match['matched_callsite']['column'] == 11228, 'Exact render callsite, not progress callback')
        require(any(e['kind'] == 'injection.delivered' and e['raf_restored'] and e['cancel_restored'] for e in events), 'Scheduling hook restored')
        cache = next(e['time_ms'] for e in events if e['kind'] == 'turbo:before-cache' and e['phase'] == 'dispatch')
        loaded = next(e['time_ms'] for e in events if e['kind'] == 'turbo:load' and e['phase'] == 'dispatch' and e['detail_url_path'] == '/bookmarks?details=14')
        visible = next(e['time_ms'] for e in events if e['kind'] == 'action' and e['name'] == 'confirm.observed_visible')
        if is_green:
            ready = next(e['time_ms'] for e in events if e['kind'] == 'action' and e['name'] == 'details.navigation_completed')
            clicked = next(e['time_ms'] for e in events if e['kind'] == 'action' and e['name'] == 'delete.begin')
            require(cache <= loaded <= ready <= clicked < visible, 'Matching visit completes before interaction')
            require(row['final_state']['confirm_visible'] and not row['removed_before_exit'] and row['exit_action'] == 'Cancel', 'Confirm remains available before explicit cancel')
        else:
            require(visible < cache < loaded and row['before_cache_correlated_removal'] and row['removed_before_exit'], 'Retain all three controlled red observations')

current = read(ROOT / 'independent/readiness-final-results.json')
require([r['scenario'] for r in current] == list(cases), 'All six final candidate cases, in order')
for row in current:
    directory = ROOT / 'native/independent' / row['run_dir']
    result = read(directory / 'result.json')
    events = [json.loads(line) for line in (directory / 'events.jsonl').read_text().splitlines()]
    identity = next(e for e in events if e['kind'] == 'identity')
    require((row['code'], result['business_verdict']) == cases[row['scenario']], 'Final scoped control outcome')
    require(row['independent_ok'] and not row['timed_out'] and row['candidate_identity_unchanged'], 'Independent final checks, no watchdog')
    require(row['prior_rows_exactly_unchanged'] and result['execution_cleanup'] == 'stopped', 'Prior rows and execution cleanup')
    require(hashlib.sha256((directory / 'executed_regression.py').read_bytes()).hexdigest() == identity['script_sha256'], 'Current executed snapshot')
    for name, digest in read(directory / 'pack-identity.json').items():
        require(hashlib.sha256((directory / 'native-pack' / name).read_bytes()).hexdigest() == digest, 'Current native pack bytes')
    require(any(e['kind'] == 'execution_inputs_unchanged' for e in events), 'Current environment identity')
    checks = {e['name']: e for e in events if e['kind'] == 'check'}
    if row['scenario'] == 'note-loss':
        require(not row['owned_run_bookmarks_removed'] and checks['save_private_tags_notes']['evidence']['fields']['notes'] == '', 'Retain actual note-loss counterexample')
        continue
    require(row['owned_run_bookmarks_removed'] and result['data_cleanup'] == 'baseline-restored', 'Current scoped data cleanup')
    require(any(e['kind'] == 'native_step' and e['step'] == 'details.navigation_completed' for e in events), 'New readiness path executed')
    db = {e['label']: e['rows'] for e in events if e['kind'] == 'database_observation'}
    require(db['initial'] == db['control cleaned'], 'Exact current baseline restoration')
    require(any(e['kind'] == 'sensitive_page_evidence_omitted' and e['label'] == 'bob-write-denied' for e in events), 'Sensitive debug page omitted')
    if row['scenario'] == 'missing-observation':
        require(result['checks']['server_restart_retrieval_database'] == 'UNVERIFIED' and not result['qualified_pass'], 'Missing evidence still blocks pass after navigation change')
    elif row['scenario'] == 'expired-session':
        require(checks['expired_session_recovered']['evidence']['bookmark_id'] == result['target_id'], 'Current reauthentication object')
    elif row['scenario'] == 'lost-response':
        require(checks['uncertain_write_found_once']['evidence']['object_ids'] == [result['target_id']], 'Current uncertain write not resubmitted')
    elif row['scenario'] == 'unicode-notes':
        require(checks['server_restart_retrieval']['evidence']['fields']['notes'] == identity['expected_notes'] and '🧭' in identity['expected_notes'], 'Current exact Unicode across restart')

print('Record checks passed: 11 behavior records, 7 actual CSVs, preserved failures, 3 red/3 green timing observations and six final scoped native controls. Not a live rerun, product pass or authenticity proof.')
