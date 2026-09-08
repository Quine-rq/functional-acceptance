# Review an update without losing local changes

Use this procedure for a project-local **ordinary copy**. Stop agents that could
read or change that copy before replacement, and use one writer. Shared universal
hosts read the same `.agents/skills/functional-acceptance` directory; Claude's
`.claude/skills/functional-acceptance` copy is separate.

The pinned third-party installer replaces the destination before copying. A
successful reinstall can discard local edits; interruption can leave a partial
package. It is not a merge or transactional updater. The procedure below stages
the risky operation away from the working installation.

## 1. Prepare two reviewed sources

Record the full Git commit of the installed baseline and the proposed candidate.
Use separate, fresh temporary project directories outside all Skill discovery
roots. Install the candidate there with the pinned command from
[INTEGRATIONS.md](INTEGRATIONS.md#pin-update-recover-and-remove), using the full
commit source URL and exactly one host. Keep the candidate's `skills-lock.json`
alongside it. Never put the temporary project inside the live Skill directory.

If the installed source commit is unknown, mark it unknown and back up the exact
installed directory. Do not invent a baseline from the candidate. Recover the
original reviewed source before using the comparison as an unchanged-copy check.
Installing the old pinned source into a separate temporary project can establish
its package bytes, but a lock file alone does not authenticate a locally edited copy.

## 2. Compare before replacing anything

The development checkout provides a read-only comparison utility, requiring the
same Node 22 environment as the installer:

```sh
node integration/review-update.mjs /path/to/BASELINE /path/to/INSTALLED /path/to/STAGED_CANDIDATE
```

Replace all three paths with inspected **Skill directories**, not project roots.
The utility lists added, removed and changed files for both local customizations
and the proposed update; it compares file hashes and executable bits. Exit `0`
means the installed copy matches the supplied baseline. Exit `2` means local
changes need review. Exit `1` means the comparison could not be established,
including links, missing entrypoints or oversized inputs. No files are written.

Neither `0` nor a matching hash approves a new instruction, proves source origin,
validates all resource links, or grants replacement authority. Review the proposed
diff and test the candidate in its temporary project. Compare trusted, quiescent
copies: this tool is not a security boundary against concurrent filesystem changes.

If local changes exist, keep the working installation in place. Port those changes
to a separate reviewed candidate or explicitly decide to retire them; rerun the
candidate checks. There is no `--force` or silent local-edit deletion in this tool.

## 3. Back up, then replace in a maintenance window

1. Keep a byte-verified backup of the exact installed directory outside every
   Skill discovery directory. Preserve the existing project `skills-lock.json`
   separately if present; it may contain unrelated Skills.
2. With all affected agents stopped, move the installed directory to its named
   backup location, then move the reviewed staged Skill directory into the now
   absent destination. Keep both on the same filesystem. Do not copy over a
   populated destination or run the installer against the live copy.
3. Verify the installed bytes against the approved candidate. Review only this
   Skill's lock entry against the staged lock and preserve all unrelated entries.
   If that metadata reconciliation is unfinished, label the copy unmanaged and
   avoid automatic `skills update`; a filesystem move does not update installer
   metadata. This project does not provide a lock-file merger.
4. Reload the host, check its actual loaded path, and perform the bounded plan-only
   and authorized execution checks from the integration guide. Keep the old copy
   until this is verified. A filesystem test is not host reload/behavior proof.

The two moves are **not an atomic directory exchange**. If interrupted after the
first move, the live copy may be absent while the backup remains intact. Do not
restart an agent until the state below is reconciled. This procedure does not
promise power-loss durability, unattended rollout or concurrent-editor safety.

## Recovery

| Observed state after the installer/writer has stopped | Safe next action |
| --- | --- |
| Staging failed; original installation remains | Keep using the unchanged original; retain failed staging for diagnosis and use a fresh staging directory |
| Live destination absent; reviewed backup intact | Restore the named backup into the absent destination, then compare bytes and reload |
| Partial or suspect live destination | Move it to a separate quarantine directory outside discovery, then restore the verified backup; retain the partial copy for diagnosis |
| Both destination and backup exist but identity is unclear | Stop and inspect both; do not overwrite either or infer which is newest from a filename |
| Backup is missing/corrupt or a writer may still be active | Keep the installation unverified and resolve ownership/source first; do not claim recovery |

Restore/reconcile the saved lock entry when rolling back; keep unrelated entries.
Do not remove backups, failed copies or acceptance evidence as a side effect of
an update. Old reports are history: recheck material against the selected helper,
and collect fresh evidence for the next product acceptance run.

## What is tested

`npm --prefix integration test` exercises the real pinned installer in disposable
projects for both directory layouts. Controlled SIGKILL after the first copied
entry reproduces partial direct reinstallation, loss of local edits, verified
backup restoration, and staging failure leaving live bytes untouched. Separate
checks cover modification detection, links, limits and replacement/rollback.
The fault hook is development-only and is not copied into the six-file Skill.

The tests use synthetic previous instruction bytes, not a claim to cover every
past release. The [m1 fixtures](tests/fixtures/m1-history/README.md) separately
check older material with the current relocated helper. Remote retrieval pinning
has its earlier [record](integration/results/2026-09-08.json); no new interrupted
download, host reload, lock merge or power-failure test is implied here.
