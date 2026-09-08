#!/usr/bin/env python3
"""Maintained native linkding journey. Use --help; historical study stays unchanged.
Only loopback targets and synthetic identities; one fresh run per invocation.
"""
import os, sys, json, time, socket, subprocess, hashlib, re, sqlite3, argparse, signal
from contextlib import closing
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qs
from support import (validate_project, load_credentials, ProcessLogs, classify,
                     publish_json, inventory, snapshot_pack, environment_identity,
                     capture_allowed, initial_notes, StopRequest, ExecutionInterrupted,
                     private_exception)
PACK = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--project", required=True, help="Pinned, isolated linkding checkout")
parser.add_argument("--browser", required=True, help="Existing Chrome/Chromium executable; never downloaded")
parser.add_argument("--case", choices=("healthy", "note-loss", "missing-observation", "expired-session", "lost-response", "unicode-notes"), default="healthy")
args = parser.parse_args()
try:
    ROOT = validate_project(args.project)
    PRIVATE = load_credentials(ROOT)
    BROWSER = str(Path(args.browser).resolve(strict=True))
    if not os.access(BROWSER, os.X_OK):
        raise ValueError("Browser must be executable")
    if not (ROOT / ".acceptance-study/preparation.json").is_file():
        raise ValueError("Run the maintained prepare command first")
    if json.loads((ROOT / ".acceptance-study/preparation.json").read_text())["state"] != "prepared":
        raise ValueError("Preparation is incomplete; inspect its receipt")
    ENVIRONMENT_IDENTITY = environment_identity(ROOT, PACK)
    from playwright.sync_api import sync_playwright, expect
except (OSError, ValueError, ImportError, KeyError, TypeError, subprocess.SubprocessError) as error:
    print(json.dumps({"business_verdict": "UNVERIFIED", "completion": "partial",
                      "obstacle_kind": "environment", "error_type": type(error).__name__,
                      "next": "Check the pinned checkout, preparation receipt, Python dependencies and browser path."}))
    sys.exit(2)
OUT = ROOT / ".acceptance-study/artifacts" / ('run-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
try:
    OUT.mkdir(mode=0o700)
    (OUT / 'executed_regression.py').write_bytes(Path(__file__).read_bytes())
    PACK_IDENTITY = snapshot_pack(PACK, OUT / 'native-pack')
    publish_json(OUT / "pack-identity.json", PACK_IDENTITY)
    publish_json(OUT / "environment-identity.json", ENVIRONMENT_IDENTITY)
except (OSError, ValueError) as error:
    print(json.dumps({'business_verdict': 'UNVERIFIED', 'completion': 'partial',
                      'obstacle_kind': 'evidence-delivery', 'error_type': type(error).__name__,
                      'execution_started': False, 'attempted_run': str(OUT)}))
    sys.exit(2)
BASE = 'http://127.0.0.1:18741'
RUN = OUT.name.lower()
URL = 'http://127.0.0.1:18742/article.html?case=' + RUN
TITLE = 'Private ' + RUN
NOTES = initial_notes(RUN, args.case)
TAGS = ['acceptance', RUN]
CONTROL = 'Control ' + RUN
CREDS = PRIVATE['users']
ENV = dict(os.environ, PYTHONPATH='.acceptance-study:.', PYTHONDONTWRITEBYTECODE='1', DJANGO_SETTINGS_MODULE='study_settings', LD_DISABLE_BACKGROUND_TASKS='True')
processes = []; browser = None; pw = None; page = None; target_id = None; control_id = None
checks = {}; events = []; phase = 'setup'; exit_code = 2; obstacle_kind = None; logs = {}; evidence_failed = False

stopping = StopRequest()
signal.signal(signal.SIGTERM, stopping.request)
signal.signal(signal.SIGINT, stopping.request)
obligations = ['normal_login','invalid_url_feedback','invalid_recovery','save_private_tags_notes','fresh_browser_retrieval','server_restart_retrieval','other_account_no_view','other_account_no_modify','edit_persisted','delete_target','unrelated_intact']

def event(kind, **data):
    global evidence_failed
    value = dict(time=datetime.now(timezone.utc).isoformat(), kind=kind, **data)
    events.append(value)
    try:
        with (OUT/'events.jsonl').open('a') as f: f.write(json.dumps(value)+'\n')
        print(json.dumps(value), flush=True)
        return True
    except OSError:
        # Loss of reporting must not interrupt the finally block's stop loop.
        evidence_failed = True
        return False

class BusinessMismatch(Exception):
    pass

def check(name, passed, **evidence):
    stopping.checkpoint()
    value = 'PASS' if passed else 'FAIL'
    # Retain the observation before publishing its in-memory verdict.
    if not event('check', name=name, status=value, evidence=evidence):
        checks[name] = 'UNVERIFIED'
        raise OSError('Evidence recording failed')
    checks[name] = value
    if not passed: raise BusinessMismatch(name)

def database(label):
    stopping.checkpoint()
    # Separate read-only SQLite connection; bookmark facts only, never auth/session data.
    uri = (ROOT / '.acceptance-study/db.sqlite3').as_uri() + '?mode=ro'
    with closing(sqlite3.connect(uri, uri=True)) as db:
        db.row_factory = sqlite3.Row
        rows = [dict(r) for r in db.execute('SELECT b.id, u.username AS owner, b.url, b.title, b.notes, b.shared FROM bookmarks_bookmark b JOIN auth_user u ON u.id=b.owner_id WHERE u.username IN (?, ?) ORDER BY b.id', ('fa_alice', 'fa_bob'))]
        for r in rows:
            r['tags'] = [t[0] for t in db.execute('SELECT t.name FROM bookmarks_tag t JOIN bookmarks_bookmark_tags bt ON bt.tag_id=t.id WHERE bt.bookmark_id=? ORDER BY t.name', (r['id'],))]
    event('database_observation', label=label, rows=rows)
    return rows

def snap(label):
    stopping.checkpoint()
    # Never persist login or recognized Django debug-page pixels/body text.
    if page is None or not capture_allowed(page):
        event('sensitive_page_evidence_omitted', label=label,
              reason='Login/debug-page capture denied; use status and object observations'); return
    page.screenshot(path=str(OUT/(label+'.png')), full_page=True)
    (OUT/(label+'.txt')).write_text(page.locator('body').inner_text())
    event('browser_evidence', label=label, url=page.url)

def occupied(port):
    with socket.socket() as s:
        s.settimeout(.15)
        return s.connect_ex(('127.0.0.1',port)) == 0

def start(name, args, port):
    stopping.checkpoint()
    if occupied(port): raise RuntimeError('Required port already occupied; will not stop unowned listener')
    p = subprocess.Popen([sys.executable, *args], cwd=ROOT, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    processes.append((name,p,port))
    logs[p.pid] = ProcessLogs(p, OUT, name, [PRIVATE['django_secret'], *CREDS.values()])
    event('process_started', name=name, pid=p.pid, command=args, private_logs=logs[p.pid].files)
    for _ in range(100):
        stopping.checkpoint()
        if p.poll() is not None:
            event('startup_exit',name=name,pid=p.pid,returncode=p.returncode)
            raise RuntimeError(name+' exited during startup: '+str(p.returncode))
        if occupied(port): return p
        time.sleep(.1)
    raise RuntimeError(name+' startup timeout')

def stop(name,p,port):
    if p.poll() is None:
        p.terminate()
        try: p.wait(timeout=5)
        except subprocess.TimeoutExpired: p.kill(); p.wait(timeout=5)
    event('process_stopped',name=name,pid=p.pid,returncode=p.returncode,port_closed=not occupied(port))

def new_browser():
    global browser, page
    stopping.checkpoint()
    browser = pw.chromium.launch(executable_path=BROWSER, headless=True, chromium_sandbox=True, args=['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1'])
    ctx = browser.new_context(viewport={'width':1280,'height':1000},service_workers='block')
    def guard(route):
        u=urlsplit(route.request.url)
        if u.scheme in ('http','https') and (u.scheme!='http' or u.hostname!='127.0.0.1' or u.port not in (18741,18742)):
            event('blocked_out_of_scope_request',host=u.hostname); route.abort()
        else: route.continue_()
    ctx.route('**/*',guard)
    page=ctx.new_page(); page.set_default_timeout(7000)
    page.on('response',lambda r: event('http',method=r.request.method,path=urlsplit(r.url).path,status=r.status) if r.request.is_navigation_request() else None)
    event('browser_started',fresh_profile=True,sandbox=True,version=browser.version)

def close_browser():
    global browser
    if browser:
        browser.close(); browser=None; event('browser_closed')

def login(user):
    stopping.checkpoint()
    page.goto(BASE+'/bookmarks')
    expect(page.get_by_label('Username',exact=True)).to_be_visible()
    page.get_by_label('Username',exact=True).fill(user)
    page.get_by_label('Password',exact=True).fill(CREDS[user])
    page.get_by_role('button',name='Login',exact=True).click()
    expect(page).not_to_have_url(re.compile('/login'))
    event('normal_browser_login',user=user)

def fill(url,title,notes,tags):
    stopping.checkpoint()
    page.get_by_label('URL',exact=True).fill(url)
    page.get_by_label('Title',exact=True).fill(title)
    page.get_by_label('Tags',exact=True).fill(' '.join(tags))
    if not page.locator('details.notes').get_attribute('open') == '':
        page.locator('details.notes summary').click()
    page.get_by_label('Notes',exact=True).fill(notes)
    if page.get_by_label('Share',exact=True).count(): page.get_by_label('Share',exact=True).uncheck()

def save():
    stopping.checkpoint()
    page.get_by_role('button',name='Save',exact=True).click()
    expect(page).not_to_have_url(re.compile('/(new|edit)(\\?|$)'))

def row(title): return page.locator('ul.bookmark-list > li').filter(has_text=title)

def details(title):
    stopping.checkpoint()
    event('native_step', step='details.list_navigation', title=title)
    page.goto(BASE+'/bookmarks')
    expect(row(title)).to_be_visible()
    event('native_step', step='details.view_click', title=title)
    row(title).get_by_text('View',exact=True).click()
    modal=page.locator('ld-details-modal'); expect(modal).to_be_visible()
    event('native_step', step='details.visible', bookmark_id=modal.get_attribute('data-bookmark-id'))
    return int(modal.get_attribute('data-bookmark-id'))

def confirm_delete(bookmark_id, label):
    stopping.checkpoint()
    modal = page.locator('ld-details-modal')
    expect(modal).to_have_attribute('data-bookmark-id', str(bookmark_id))
    event('native_step', step=label+'.delete_click', bookmark_id=bookmark_id)
    modal.get_by_role('button', name='Delete', exact=True).click()
    confirmation = page.locator('ld-confirm-dropdown').get_by_role('button', name='Confirm', exact=True)
    event('native_step', step=label+'.await_confirmation', bookmark_id=bookmark_id)
    expect(confirmation).to_be_visible()
    if label == 'target': snap('delete-confirmation')
    stopping.checkpoint()
    event('native_step', step=label+'.confirm_click', bookmark_id=bookmark_id)
    confirmation.click()
    expect(modal).to_have_count(0)
    event('native_step', step=label+'.modal_closed', bookmark_id=bookmark_id)

def fields():
    return {k:page.get_by_label(label,exact=True).input_value() for k,label in [('url','URL'),('title','Title'),('notes','Notes'),('tags','Tags')]}

def inspect_saved(id,title,notes,tags,label):
    page.goto(BASE+f'/bookmarks/{id}/edit')
    value=fields()
    check(label, value['url']==URL and value['title']==title and value['notes']==notes and set(value['tags'].split())==set(tags), bookmark_id=id,fields=value)
    if args.case == "missing-observation" and label == "server_restart_retrieval":
        event("observation_withheld", obligation=label + "_database", reason="Explicit missing-observation control")
        checks[label + "_database"] = "UNVERIFIED"
        snap(label)
        return
    rows = database(label)
    matching = [r for r in rows if r['url'] == URL]
    expected = {'id': id, 'owner': 'fa_alice', 'url': URL, 'title': title, 'notes': notes, 'shared': 0, 'tags': sorted(tags)}
    check(label+'_database', matching == [expected], bookmark_id=id)
    snap(label)

try:
    event('identity',head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),python=sys.version.split()[0],script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),target_url=URL,expected_tags=TAGS,expected_notes=NOTES)
    baseline = database('initial')
    check('initial_scope_unused', not any(r['url'] in (URL, URL+'&control=1') for r in baseline), retained_baseline_ids=[r['id'] for r in baseline])
    article=start('article',['-m','http.server','18742','--bind','127.0.0.1','--directory','.acceptance-study/article'],18742)
    server_args = [str(OUT / 'native-pack/server.py'), '--project', str(ROOT)]
    if args.case == "note-loss":
        server_args.append("--note-loss")
    event("scenario", name=args.case, mutation="runtime pre_save clears notes" if args.case == "note-loss" else None)
    app=start('application',server_args,18741)
    pw=sync_playwright().start(); new_browser(); login('fa_alice'); check('normal_login',True)
    phase='invalid URL and recovery'
    page.get_by_role('link',name='Add bookmark',exact=True).click()
    fill('http://',TITLE,NOTES,TAGS)
    page.get_by_role('button',name='Save',exact=True).click()
    expect(page.get_by_text('Enter a valid URL.',exact=True)).to_be_visible()
    check('invalid_url_feedback',True,message='Enter a valid URL.',url_input=page.get_by_label('URL',exact=True).input_value())
    check('invalid_url_not_persisted', database('invalid URL') == baseline)
    snap('invalid-url')
    # Same rendered form, no navigation or reset; correct only the URL.
    with page.expect_response(lambda r: urlsplit(r.url).path == '/api/bookmarks/check/' and r.status == 200 and r.request.method == 'GET' and parse_qs(urlsplit(r.url).query).get('url') == [URL]) as metadata_response:
        page.get_by_label('URL',exact=True).fill(URL)
    metadata = metadata_response.value.json()['metadata']
    check('real_http_metadata', metadata.get('title') == 'Acceptance study article', metadata_title=metadata.get('title'), response_status=metadata_response.value.status, requested_article=parse_qs(urlsplit(metadata_response.value.url).query)['url'][0])
    if args.case == "lost-response":
        def lose_response(route):
            if route.request.method != "POST":
                route.continue_()
                return
            response = route.fetch(max_redirects=0)
            event("response_lost_after_server", method="POST", status=response.status,
                  requested_path=urlsplit(route.request.url).path)
            route.abort("failed")
        page.route("**/bookmarks/new", lose_response)
        page.get_by_role('button',name='Save',exact=True).click()
        # Pump browser callbacks; inspect exact state before any resubmission.
        deadline = time.monotonic() + 7
        while not any(e["kind"] == "response_lost_after_server" for e in events) and time.monotonic() < deadline:
            page.wait_for_timeout(50)
        if not any(e["kind"] == "response_lost_after_server" for e in events):
            raise RuntimeError("Lost-response probe did not occur")
        page.unroute("**/bookmarks/new", lose_response)
        persisted = [r for r in database("after lost response") if r["url"] == URL]
        check("uncertain_write_found_once", len(persisted) == 1, object_ids=[r["id"] for r in persisted])
        target_id = persisted[0]["id"]
        page.goto(BASE + '/bookmarks')
        check("lost_response_recovered_without_resubmit", details(TITLE) == target_id, bookmark_id=target_id)
    else:
        save(); target_id=details(TITLE)
    check('invalid_recovery',True,bookmark_id=target_id)
    inspect_saved(target_id,TITLE,NOTES,TAGS,'save_private_tags_notes')
    phase='create unrelated control'
    page.goto(BASE+'/bookmarks/new'); fill(URL+'&control=1',CONTROL,'Unrelated control notes',['control',RUN]); save()
    control_id=details(CONTROL); snap('control-created')
    phase='fresh browser persistence'
    close_browser(); new_browser(); login('fa_alice')
    check('fresh_browser_retrieval',details(TITLE)==target_id,bookmark_id=target_id)
    inspect_saved(target_id,TITLE,NOTES,TAGS,'fresh_browser_fields')
    phase='actual application restart'
    old_pid=app.pid; stop('application',app,18741)
    app=start('application-restarted',server_args,18741)
    assert app.pid!=old_pid
    close_browser(); new_browser(); login('fa_alice')
    assert details(TITLE)==target_id
    inspect_saved(target_id,TITLE,NOTES,TAGS,'server_restart_retrieval')
    event('restart_correlated',old_pid=old_pid,new_pid=app.pid,bookmark_id=target_id)
    if args.case == "expired-session":
        page.context.clear_cookies()
        page.goto(BASE + f'/bookmarks/{target_id}/edit')
        expect(page.get_by_label('Username',exact=True)).to_be_visible()
        event("session_removed", bookmark_id=target_id, login_visible=True)
        login('fa_alice')
        inspect_saved(target_id,TITLE,NOTES,TAGS,'reauthenticated_same_object')
        check("expired_session_recovered", True, bookmark_id=target_id)
    phase='other ordinary account isolation'
    close_browser(); new_browser(); login('fa_bob')
    page.goto(BASE+'/bookmarks'); expect(row(TITLE)).to_have_count(0)
    response=page.goto(BASE+f'/bookmarks?details={target_id}')
    absent=TITLE not in page.locator('body').inner_text() and NOTES.splitlines()[0] not in page.locator('body').inner_text() and page.locator('ld-details-modal').count()==0
    check('other_account_no_view',absent,bookmark_id=target_id,status=response.status); snap('bob-no-view')
    response=page.goto(BASE+f'/bookmarks/{target_id}/edit')
    check('bob_edit_get_denied',response.status in (403,404) and page.get_by_label('Notes',exact=True).count()==0,status=response.status,bookmark_id=target_id)
    snap('bob-edit-denied')
    # Adversarial real browser form POST using Bob's normal-login CSRF, not an API client.
    page.goto(BASE+'/bookmarks/new')
    fill(URL,'ATTACK '+RUN,'ATTACK NOTES',['attack'])
    page.locator('form').filter(has=page.get_by_label('URL',exact=True)).evaluate('(form, action) => { form.action=action; form.setAttribute("data-turbo","false"); }',f'/bookmarks/{target_id}/edit')
    with page.expect_navigation() as nav: page.get_by_role('button',name='Save',exact=True).click()
    denied=nav.value.status in (403,404)
    event('bob_exact_id_write_attempt',bookmark_id=target_id,status=nav.value.status,submitted_title='ATTACK '+RUN)
    snap('bob-write-denied')
    close_browser(); new_browser(); login('fa_alice')
    inspect_saved(target_id,TITLE,NOTES,TAGS,'owner_unchanged_after_attack')
    check('other_account_no_modify',denied,bookmark_id=target_id,owner_reopened_unchanged=True)
    phase='edit and reopen'
    updated_title=TITLE+' edited'; updated_notes=NOTES+'\nEdited after restart.'; updated_tags=[RUN,'edited']
    page.get_by_label('Title',exact=True).fill(updated_title); page.get_by_label('Notes',exact=True).fill(updated_notes); page.get_by_label('Tags',exact=True).fill(' '.join(updated_tags)); save()
    inspect_saved(target_id,updated_title,updated_notes,updated_tags,'edit_persisted')
    phase='delete with unrelated control'
    assert details(updated_title)==target_id
    confirm_delete(target_id, 'target')
    page.goto(BASE+'/bookmarks'); expect(row(updated_title)).to_have_count(0)
    response=page.goto(BASE+f'/bookmarks/{target_id}/edit')
    check('delete_target',response.status==404,bookmark_id=target_id,status=response.status)
    remaining = database('target deleted')
    expected_control = {'id': control_id, 'owner': 'fa_alice', 'url': URL+'&control=1', 'title': CONTROL, 'notes': 'Unrelated control notes', 'shared': 0, 'tags': sorted(['control', RUN])}
    check('delete_target_database', remaining == sorted(baseline+[expected_control], key=lambda r:r['id']), target_id=target_id, control_id=control_id)
    page.goto(BASE+f'/bookmarks/{control_id}/edit'); control=fields()
    check('unrelated_intact',control['url']==URL+'&control=1' and control['title']==CONTROL and control['notes']=='Unrelated control notes' and set(control['tags'].split())=={'control',RUN},bookmark_id=control_id,fields=control)
    snap('unrelated-intact')
    phase='cleanup control through UI'
    assert details(CONTROL) == control_id
    confirm_delete(control_id, 'control')
    page.goto(BASE+'/bookmarks'); expect(row(CONTROL)).to_have_count(0); snap('final-empty')
    check('run_bookmarks_cleaned_baseline_preserved', database('control cleaned') == baseline)
    event('data_cleanup',target_id=target_id,control_id=control_id,owned_bookmarks_absent=True,tags_retained='Unused run-specific tags may remain; no ORM cleanup performed')
    exit_code=0
except (Exception, KeyboardInterrupt) as exc:
    # A locator/observer error is not a qualified product counterexample.
    obstacle_kind = ("business" if isinstance(exc, BusinessMismatch) else
                     "interrupted" if isinstance(exc, (KeyboardInterrupt, ExecutionInterrupted)) else
                     "environment" if phase == "setup" else "harness-or-observation")
    event('obstacle',phase=phase,category=obstacle_kind,error_type=type(exc).__name__,
          detail=str(exc) if isinstance(exc,BusinessMismatch) else 'Inspect private startup logs and safe browser evidence; no automatic journey retry',
          target_id=target_id,control_id=control_id)
    try:
        private_exception(OUT/'obstacle.private.txt', exc, [PRIVATE['django_secret'], *CREDS.values()])
        event('private_diagnostic', file='obstacle.private.txt', contains='Redacted exception type, call site and locator details; review locally')
    except OSError:
        evidence_failed = True
    if obstacle_kind != 'interrupted':
        try: snap('obstacle')
        except Exception: pass
finally:
    try: close_browser()
    except Exception: event('cleanup_unresolved',resource='browser')
    if pw:
        try: pw.stop()
        except Exception: event('cleanup_unresolved',resource='playwright')
    for name,p,port in reversed(processes):
        if p.poll() is None:
            try: stop(name,p,port)
            except Exception: event('cleanup_unresolved',resource=name,pid=p.pid)
    for pid, captured in logs.items():
        logged = captured.finish()
        event("process_logs", pid=pid, **logged)
        if logged["errors"]:
            event("cleanup_unresolved", resource="process-log-drain", pid=pid)
    for name in obligations: checks.setdefault(name,'UNVERIFIED')
    try:
        validate_project(ROOT)
        if inventory(PACK) != PACK_IDENTITY or environment_identity(ROOT, PACK) != ENVIRONMENT_IDENTITY:
            raise ValueError('Execution inputs changed')
        event('execution_inputs_unchanged', pack=True, environment=True, pinned_source=True)
    except (OSError, ValueError, subprocess.SubprocessError):
        obstacle_kind = 'execution-identity-changed'
        event('execution_identity_gap', reason='Do not qualify a result across changed execution inputs')
    unresolved = any(e['kind'] == 'cleanup_unresolved' for e in events) or any(p.poll() is None or occupied(port) for _, p, port in processes)
    if evidence_failed:
        obstacle_kind = 'evidence-delivery'
    elif stopping.requested and obstacle_kind is None:
        obstacle_kind = 'interrupted'
    assessment = classify(checks, obstacle_kind, unresolved)
    exit_code = assessment['exit_code']
    result={**assessment, 'checks':checks,'phase_at_exit':phase,'exit_code':exit_code,'target_id':target_id,'control_id':control_id,'run':RUN,'processes':[{'name':n,'pid':p.pid,'returncode':p.poll(),'port_closed':not occupied(port)} for n,p,port in processes]}
    result['execution_cleanup'] = 'unresolved' if unresolved else 'stopped'
    result['data_cleanup'] = ('baseline-restored' if checks.get('run_bookmarks_cleaned_baseline_preserved') == 'PASS'
                              else 'not-completed-or-unobserved; inspect recorded target/control IDs before any write')
    result['case'] = args.case
    result['retention'] = 'Run artifacts, synthetic accounts/tags/sessions and failed-attempt bookmarks retained; no historical cleanup'
    try:
        if not event('finished',exit_code=exit_code,evidence=str(OUT)):
            result.update(qualified_pass=False, completion='partial', obstacle_kind='evidence-delivery', exit_code=2)
            exit_code = 2
        publish_json(OUT/'result.json', result)
    except OSError:
        # A missing final receipt is never an acceptance pass.
        print(json.dumps({'completion': 'partial', 'obstacle_kind': 'evidence-delivery',
                          'owned_run': str(OUT), 'qualified_pass': False}), file=sys.stderr)
        exit_code = 2
sys.exit(exit_code)
