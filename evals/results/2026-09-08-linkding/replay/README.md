# Native linkding replay

This is a study-specific regression, not a new Skill runtime, a universal test adapter or an upstream contribution. It uses real browser login, real Django forms, real HTTP metadata loading and a separate read-only SQLite connection. No model, Skill installation or CSV helper is used by this command.

## Prepare a new isolated checkout

Review the scripts before running. Use a **new directory**, not a production or existing development database. Dependencies may require network downloads; the application journey itself uses only loopback ports `18741` and `18742`. Normal permission to start local servers and Chrome is required. Do not disable the browser sandbox to work around a host limitation.

1. Clone [linkding](https://github.com/sissbruecker/linkding), and in that new clone check out commit `65813a75404b1319aca8b09700fadc0b15adabaf` detached. Preserve its MIT license.
2. Create `.acceptance-study/` in the clone. Copy the contents of this directory's `environment/` into it. Create `.acceptance-study/artifacts/` and copy `assisted_regression.py` there. Do **not** copy old evidence, databases, credentials, `.agents/` or this repository's development instructions.
3. From the new linkding checkout, install its locked dependencies and build its assets:

```sh
uv sync --frozen --python python3.14
npm ci --ignore-scripts --no-audit --no-fund
npm run build
```

The measured environment was macOS, Python 3.14.4, Node 22.22.3, Django 6.0.7, Playwright 1.62.0 and Chrome 152.0.7977.76. The script uses the existing executable `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`; other browsers/platforms have not been checked. No automatic browser download is performed.

4. Prepare the isolated database and two ordinary synthetic accounts:

```sh
.venv/bin/python .acceptance-study/prepare.py
```

Preparation refuses an existing database or credentials. It generates a new local secret and passwords, migrates SQLite and disables sharing, archive/background jobs, favicons and previews. The settings module redirects persistent paths; upstream source remains unchanged. Credentials stay in the mode-600 `.acceptance-study/private.json` and must not be published. A preparation failure is not an acceptance pass; inspect its owned state before deciding how to recover.

## Run and inspect

```sh
.venv/bin/python .acceptance-study/artifacts/assisted_regression.py
```

Each call uses unique synthetic URLs/tags and a new `assisted-run-*` evidence directory. It refuses occupied ports rather than terminating their listeners. Chrome uses new profiles with its sandbox enabled; page requests are restricted to the two study endpoints. Application background tasks are disabled by the reviewed local settings; this is not a system-wide outbound firewall.

Read `result.json`, `events.jsonl`, the script snapshot and screenshots together. Exit 0 alone is insufficient. The required checks must have corresponding native/browser/database observations, the exact target ID must agree across stages, and application/article processes must be stopped with closed ports. Old reports are history, not fresh facts.

The sequence checks invalid-input recovery, saves a private item and a separate control, reopens a fresh browser, terminates/restarts the real server, tests Bob's denied access/write to Alice's exact item, edits it as Alice, and deletes it through confirmation. It then verifies the control remained unchanged before removing only this run's control. A separate SQLite connection checks exact fields and IDs. Existing synthetic bookmark rows from these two accounts form a baseline and must remain byte-for-field equal after this run; this allows failed attempts to remain intact without resetting the database.

On an obstacle, execution stops and preserves evidence, IDs and any written bookmarks. Do not blindly rerun a failed write. Inspect those exact IDs and the recorded failure before an explicitly reviewed retry. Never remove historical data simply to make a test pass.

## Retention and scope

The script closes owned browser and server processes in `finally` and exposes unfinished cleanup separately. Run-owned bookmarks are removed through the UI only after verifying deletion scope; unused tags, accounts, sessions and evidence remain in the isolated local study environment. Failed attempts' bookmarks are retained. It does not promise a globally empty database.

The historical screenshot name `final-empty.png` means the latest run's bookmarks are absent; an earlier retained baseline can still appear on that page. Use the exact final database observation to interpret it.

This verifies one bounded bookmark journey. It does not cover arbitrary external websites, concurrency, lost responses, disk exhaustion, mobile UI, all authorization paths or production deployment. A study author replay is not an independent external-human handoff or a with/without-Skill comparison.
