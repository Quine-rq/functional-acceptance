#!/usr/bin/env python3
"""Real browser acceptance. Run from checkout: .venv/bin/python .acceptance-study/artifacts/acceptance_regression.py
No mocks, force_login, stored auth state, product edits, or database mutation outside UI.
Each invocation creates new evidence; stops at first journey obstacle, never retries the journey.
"""
import os, sys, json, time, socket, subprocess, hashlib, re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / ('run-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
OUT.mkdir()
BASE = 'http://127.0.0.1:18741'
RUN = OUT.name.lower()
URL = 'http://127.0.0.1:18742/article.html?case=' + RUN
TITLE = 'Private ' + RUN
NOTES = 'Private research notes ' + RUN + '\nSecond line: retain this context.'
TAGS = ['acceptance', RUN]
CONTROL = 'Control ' + RUN
CREDS = json.loads((ROOT / '.acceptance-study/private.json').read_text())['users']
ENV = dict(os.environ, PYTHONPATH='.acceptance-study:.', DJANGO_SETTINGS_MODULE='study_settings', LD_DISABLE_BACKGROUND_TASKS='True')
processes = []; browser = None; pw = None; page = None; target_id = None; control_id = None
checks = {}; events = []; phase = 'setup'; exit_code = 1
obligations = ['normal_login','invalid_url_feedback','invalid_recovery','save_private_tags_notes','fresh_browser_retrieval','server_restart_retrieval','other_account_no_view','other_account_no_modify','edit_persisted','delete_target','unrelated_intact']

def event(kind, **data):
    value = dict(time=datetime.now(timezone.utc).isoformat(), kind=kind, **data)
    events.append(value)
    with (OUT/'events.jsonl').open('a') as f: f.write(json.dumps(value)+'\n')
    print(json.dumps(value), flush=True)

def check(name, passed, **evidence):
    checks[name] = 'PASS' if passed else 'FAIL'
    event('check', name=name, status=checks[name], **evidence)
    if not passed: raise AssertionError(name)

def snap(label):
    # Never record login, headers, cookies, HTML, or Django debug error pages.
    if '/login' in page.url: return
    if page.locator('body').inner_text().startswith(('OperationalError', 'Traceback')): return
    page.screenshot(path=str(OUT/(label+'.png')), full_page=True)
    (OUT/(label+'.txt')).write_text(page.locator('body').inner_text())
    event('browser_evidence', label=label, url=page.url)

def occupied(port):
    with socket.socket() as s:
        s.settimeout(.15)
        return s.connect_ex(('127.0.0.1',port)) == 0

def start(name, args, port):
    if occupied(port): raise RuntimeError('Required port already occupied; will not stop unowned listener')
    p = subprocess.Popen([str(ROOT/'.venv/bin/python'), *args], cwd=ROOT, env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    processes.append((name,p,port)); event('process_started', name=name, pid=p.pid, command=args)
    for _ in range(100):
        if p.poll() is not None: raise RuntimeError(name+' exited during startup: '+str(p.returncode))
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
    browser = pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True, chromium_sandbox=True, args=['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1'])
    ctx = browser.new_context(viewport={'width':1280,'height':1000},service_workers='block')
    def guard(route):
        u=urlsplit(route.request.url)
        if u.scheme in ('http','https') and (u.scheme!='http' or u.hostname!='127.0.0.1' or u.port not in (18741,18742)):
            event('blocked_out_of_scope_request',host=u.hostname); route.abort()
        else: route.continue_()
    ctx.route('**/*',guard)
    page=ctx.new_page(); page.set_default_timeout(7000)
    page.on('response',lambda r: event('http',method=r.request.method,path=urlsplit(r.url).path,status=r.status) if r.request.is_navigation_request() else None)
    event('browser_started',fresh_profile=True,sandbox=True)

def close_browser():
    global browser
    if browser:
        browser.close(); browser=None; event('browser_closed')

def login(user):
    page.goto(BASE+'/bookmarks')
    expect(page.get_by_label('Username',exact=True)).to_be_visible()
    page.get_by_label('Username',exact=True).fill(user)
    page.get_by_label('Password',exact=True).fill(CREDS[user])
    page.get_by_role('button',name='Login',exact=True).click()
    expect(page).not_to_have_url(re.compile('/login'))
    event('normal_browser_login',user=user)

def fill(url,title,notes,tags):
    page.get_by_label('URL',exact=True).fill(url)
    page.get_by_label('Title',exact=True).fill(title)
    page.get_by_label('Tags',exact=True).fill(' '.join(tags))
    if not page.locator('details.notes').get_attribute('open') == '':
        page.locator('details.notes summary').click()
    page.get_by_label('Notes',exact=True).fill(notes)
    if page.get_by_label('Share',exact=True).count(): page.get_by_label('Share',exact=True).uncheck()

def save():
    page.get_by_role('button',name='Save',exact=True).click()
    expect(page).not_to_have_url(re.compile('/(new|edit)(\\?|$)'))

def row(title): return page.locator('ul.bookmark-list > li').filter(has_text=title)

def details(title):
    page.goto(BASE+'/bookmarks')
    expect(row(title)).to_be_visible()
    row(title).get_by_text('View',exact=True).click()
    modal=page.locator('ld-details-modal'); expect(modal).to_be_visible()
    return int(modal.get_attribute('data-bookmark-id'))

def fields():
    return {k:page.get_by_label(label,exact=True).input_value() for k,label in [('url','URL'),('title','Title'),('notes','Notes'),('tags','Tags')]}

def inspect_saved(id,title,notes,tags,label):
    page.goto(BASE+f'/bookmarks/{id}/edit')
    value=fields()
    check(label, value['url']==URL and value['title']==title and value['notes']==notes and set(value['tags'].split())==set(tags), bookmark_id=id,fields=value)
    snap(label)

try:
    event('identity',head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),python=sys.version.split()[0],script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),target_url=URL,expected_tags=TAGS,expected_notes=NOTES)
    article=start('article',['-m','http.server','18742','--bind','127.0.0.1','--directory','.acceptance-study/article'],18742)
    app=start('application',['manage.py','runserver','127.0.0.1:18741','--noreload'],18741)
    pw=sync_playwright().start(); new_browser(); login('fa_alice'); check('normal_login',True)
    phase='invalid URL and recovery'
    page.get_by_role('link',name='Add bookmark',exact=True).click()
    fill('http://',TITLE,NOTES,TAGS)
    page.get_by_role('button',name='Save',exact=True).click()
    expect(page.get_by_text('Enter a valid URL.',exact=True)).to_be_visible()
    check('invalid_url_feedback',True,message='Enter a valid URL.',url_input=page.get_by_label('URL',exact=True).input_value())
    snap('invalid-url')
    # Same rendered form, no navigation or reset; correct only the URL.
    page.get_by_label('URL',exact=True).fill(URL)
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
    app=start('application-restarted',['manage.py','runserver','127.0.0.1:18741','--noreload'],18741)
    assert app.pid!=old_pid
    close_browser(); new_browser(); login('fa_alice')
    assert details(TITLE)==target_id
    inspect_saved(target_id,TITLE,NOTES,TAGS,'server_restart_retrieval')
    event('restart_correlated',old_pid=old_pid,new_pid=app.pid,bookmark_id=target_id)
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
    page.locator('ld-details-modal').get_by_role('button',name='Delete',exact=True).click()
    expect(page.locator('ld-confirm-dropdown')).to_be_visible()
    snap('delete-confirmation')
    page.locator('ld-confirm-dropdown').get_by_text('Confirm',exact=True).click()
    expect(page.locator('ld-details-modal')).to_have_count(0)
    page.goto(BASE+'/bookmarks'); expect(row(updated_title)).to_have_count(0)
    response=page.goto(BASE+f'/bookmarks/{target_id}/edit')
    check('delete_target',response.status==404,bookmark_id=target_id,status=response.status)
    page.goto(BASE+f'/bookmarks/{control_id}/edit'); control=fields()
    check('unrelated_intact',control=={'url':URL+'&control=1','title':CONTROL,'notes':'Unrelated control notes','tags':' '.join(sorted(['control',RUN]))},bookmark_id=control_id,fields=control)
    snap('unrelated-intact')
    phase='cleanup control through UI'
    details(CONTROL); page.locator('ld-details-modal').get_by_role('button',name='Delete',exact=True).click(); page.locator('ld-confirm-dropdown').get_by_text('Confirm',exact=True).click()
    expect(page.locator('ld-details-modal')).to_have_count(0)
    page.goto(BASE+'/bookmarks'); expect(row(CONTROL)).to_have_count(0); snap('final-empty')
    event('data_cleanup',target_id=target_id,control_id=control_id,owned_bookmarks_absent=True,tags_retained='Unused run-specific tags may remain; no ORM cleanup performed')
    exit_code=0
except Exception as exc:
    # Avoid arbitrary exception text because Playwright can include filled input values.
    event('obstacle',phase=phase,error_type=type(exc).__name__,detail=str(exc) if isinstance(exc,AssertionError) and str(exc) in checks else 'See safe browser evidence; no automatic journey retry',target_id=target_id,control_id=control_id)
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
    for name in obligations: checks.setdefault(name,'UNVERIFIED')
    result={'checks':checks,'phase_at_exit':phase,'exit_code':exit_code,'target_id':target_id,'control_id':control_id,'run':RUN,'processes':[{'name':n,'pid':p.pid,'returncode':p.poll(),'port_closed':not occupied(port)} for n,p,port in processes]}
    (OUT/'result.json').write_text(json.dumps(result,indent=2))
    event('finished',exit_code=exit_code,evidence=str(OUT))
sys.exit(exit_code)
