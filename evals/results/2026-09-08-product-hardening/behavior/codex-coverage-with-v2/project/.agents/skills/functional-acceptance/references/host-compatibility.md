# Working through an agent host

The host supplies discovery, reasoning, tools, and permissions. A `SKILL.md` directory supplies instructions, not a browser, shell, account, model, or safety sandbox. A successful installation does not prove a workflow ran.

## Resolve the right roots

Use the path of the **loaded** `SKILL.md` to locate this package's `references/` and `scripts/`. Do not resolve them against the project working directory, a remembered checkout, or another same-name Skill. Read the relevant reference from that installed copy. If the host cannot locate it, report the missing resource rather than silently substituting another revision.

Keep the project working directory separate. Run project-native commands there; store evidence in the project's authorized run location, never in the installed Skill. A remote host must be able to access the actual resources and evidence; a path on a developer's laptop does not establish remote access.

## Match capabilities to the requested outcome

| Request | Necessary capability | If it is missing |
| --- | --- | --- |
| Plan acceptance | Read the supplied requirements and relevant project material | Deliver the grounded plan and name missing information; do not demand execution credentials |
| Run a CLI/file check | Invoke the reviewed native command, observe termination, reopen its actual output | Keep the affected checks UNVERIFIED; a saved command or exit code alone is insufficient |
| Verify a UI or remote object | Reach the authorized target and observe the same object through the required user path | Preserve that gap; a shell, mock, or API response is not automatically a replacement |
| Recheck `m1` CSV material | Read the run and execute the bundled helper with Python 3.10+ on a suitable POSIX filesystem | State that mechanical checking was not performed; do not invent a report |

Inspect the current host's tool inventory rather than hard-code tool names, assume every host has Bash, or copy another host's tool-call syntax. Choose only what the present journey needs. For a long-running or mutating operation, also establish its bounded wait/stop and recovery path before starting it.

The optional helper verifies only the mapping in [material-format.md](material-format.md). It is not a prerequisite for a plan or for separately attributed observations whose agreed evidence conditions are met. If the user requires its mechanical report, missing runtime support remains a delivery gap. Never install dependencies or grant permissions merely because the Skill was loaded.

## Handoff across hosts

Record the actual project/runtime and run evidence locations, the native repeat command and its working directory, and outstanding observations. Do not transfer credentials or assume another host inherits permissions. Recheck access and material identity in the receiving environment; an old report is history, not a fresh run. See the source repository's integration guide for measured host coverage, not a guarantee implied by these instructions.
