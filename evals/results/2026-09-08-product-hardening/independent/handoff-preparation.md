# Independent native handoff — preparation only

Recorded at 2026-09-08T05:53:32Z. This is evidence from an independent agent executor, not from a human user. No live acceptance case has run.

## Scope and information used

The sole procedural guide read was `<TASK_ROOT>/outputs/functional-acceptance/examples/linkding/README.md`, together with the complete referenced `prepare.py`, `accept.py`, `support.py`, `server.py`, `environment/study_settings.py`, and `environment/article.html`. No historical study, functional-acceptance Skill, or prior study outcome was inspected.

Assignment-supplied environment assistance: offline seed repository, existing uv/npm cache paths, existing Chrome path, and a prepare-only hold because another study uses the same ports. These details are not supplied by the README and therefore this is not an unaided environment-discovery trial.

Work directory: `<TASK_ROOT>/work/linkding-independent-handoff`.

## Exact preparation commands and results

The initial read-only command `ls -ld <TASK_ROOT>/work/linkding-independent-handoff` returned exit 1 / no such file or directory. This confirmed a fresh destination; no existing path was overwritten.

The clone command ran from `<TASK_ROOT>`:

```sh
/usr/bin/time -p git clone --no-hardlinks <TASK_ROOT>/work/linkding-native-replay <TASK_ROOT>/work/linkding-independent-handoff
```

Exit 0; real 0.17 s, user 0.07 s, sys 0.10 s. Source HEAD, checked before cloning with `git -C <TASK_ROOT>/work/linkding-native-replay rev-parse HEAD`, was the documented pin `65813a75404b1319aca8b09700fadc0b15adabaf`. Preparation independently enforced the same pin and tracked-source cleanliness.

All remaining commands ran from the new clone:

```sh
/usr/bin/time -p env UV_CACHE_DIR=<TASK_ROOT>/work/linkding-uv-cache UV_PYTHON_DOWNLOADS=never uv sync --frozen --offline --python python3.14
```

Exit 0; real 10.59 s, user 0.04 s, sys 0.42 s. Installed 53 locked packages. Interpreter: CPython 3.14.4 from `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14`. Includes Playwright 1.62.0 and Django 6.0.7. No Python/browser download or global configuration change.

```sh
/usr/bin/time -p npm ci --offline --cache <TASK_ROOT>/work/linkding-npm-cache --ignore-scripts --no-audit --no-fund
```

Exit 0; real 1.31 s, user 0.98 s, sys 1.44 s. Installed 159 packages. The independent uv/npm installs overlapped, so individual elapsed times should not be summed as total preparation wall time.

```sh
/usr/bin/time -p npm run build
```

Exit 0; real 3.98 s, user 4.65 s, sys 0.54 s. Built JS and both themes. Both theme builds warned that caniuse-lite data was 13 months old. The suggested network update was not executed and locks were not changed.

```sh
/usr/bin/time -p .venv/bin/python <TASK_ROOT>/outputs/functional-acceptance/examples/linkding/prepare.py --project <TASK_ROOT>/work/linkding-independent-handoff
```

Exit 0; real 4.06 s, user 1.97 s, sys 0.41 s. Printed only preparation status and the owned state directory. Receipt state: `prepared`. No failed preparation or automatic retry occurred.

## Read-only readiness verification

```sh
git status --short --untracked-files=no
sed -n '1,80p' .acceptance-study/preparation.json
stat -f '%Sp %N' .acceptance-study .acceptance-study/private.json .acceptance-study/db.sqlite3 .acceptance-study/artifacts
test -x '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
```

All exit 0. Tracked source status was empty. Receipt: `prepared`. State and artifacts directories have mode 0700; private.json has mode 0600. The database file has mode 0644 inside the mode-0700 directory. Only file metadata was inspected; neither database contents nor credentials were printed. Chrome is executable; Chrome was not launched.

No app, browser, or server has been started. No accept.py invocation has occurred. No commit, push, pack edit, upstream source edit, or global configuration change was made. The isolated synthetic preparation state is retained for the authorized next phase.

## Identity recorded before the live phase

SHA-256:

| File | Digest |
| --- | --- |
| uv.lock | 5ff80ccb3022fd0d667c9dfc31c2f2cbadf714dc05f9b8e35fbb8750814f8f7f |
| package-lock.json | 5121ff6e9c803bd97e846e43e832477a1e3a9372c612e5db1cf98662369e982d |
| README.md | 38755d37b67d8d011f4166d285685341bc8695bbae7b78dea7e30e6dad0e4182 |
| prepare.py | a2df835be909c7d6d219cb3b40edbf0fdd9631e03905cc8f1160f9c445777e66 |
| accept.py | bd05e46270e891ed22bc252987139ea2d3e95b9e8132985a4292cc7224620709 |
| support.py | 3274eb5ed918e0bea69688beec8b86e42df3d6f3129e3cc5ed6407bbf481449e |
| server.py | 63b1b402def9a4fbcc477ff317bc1b41957695033d7498625bf24be9e6186863 |
| environment/study_settings.py | dd72545f0cf343cd3af2342320f7978c45534a17109af076b37a4c4307b4841b |
| environment/article.html | 93af781aa8b0f63cdb4b68d19d26788fcb730e884c10e477fc7601d6a13cf9d1 |

Digests were obtained with `shasum -a 256` over the exact files named above, using absolute paths for the pack files.

## Handoff gaps and next phase

There was no blocking preparation ambiguity after applying the assignment's offline environment details. The README names the source repository and pinned SHA but does not provide an exact clone/checkout command; the supplied local seed was already at the pin. The README's example installs are network-capable and do not spell out offline cache flags; the assignment required these overrides. Neither omission prevented preparation here, but both should remain explicit assistance in interpreting this trial.

Live runtime, port availability, browser sandbox viability, result semantics, object/process evidence, cleanup, and the five frozen case outcomes remain unverified. No acceptance PASS can be inferred from preparation success.

The pending documented healthy command, after ports are released and live execution is authorized, is:

```sh
.venv/bin/python <TASK_ROOT>/outputs/functional-acceptance/examples/linkding/accept.py --project <TASK_ROOT>/work/linkding-independent-handoff --browser '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' --case healthy
```
