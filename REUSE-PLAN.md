# Reuse and recovery: implementation contract

> Historical plan note: its licensing and private-contact tasks describe the
> plan's original baseline. The repository now uses the [MIT License](LICENSE)
> and publishes [security](SECURITY.md) and [support](SUPPORT.md) boundaries.
> The private reporting route has since been enabled and verified.

Starting point: `ac8eda6e35b58583ae521f2989302c73dbb1d0fa`, 2026-09-08.

## User result

A developer can bring this Skill into an unfamiliar project, verify the requested
outcomes without an author-written acceptance script, and hand the resulting
native checks to another executor. Installing or upgrading the package must not
silently discard the developer's local changes.

Current evidence: the shipped six-file package and maintained linkding pack work
within their recorded scope. Earlier paired runs omitted a runnable requirement;
the installer replaces local changes; a second host has not executed successfully.
The matching [remote CI](https://github.com/Quine-rq/functional-acceptance/actions/runs/34197483133)
passed both Python jobs and installation. That result covers the starting commit,
not this iteration.

## Invariants

- Preserve every original target and distinguish observation gaps from failures.
- Keep the Skill portable and small; no universal runtime or package manager.
- Preserve historical evidence and all new failed attempts. No upstream fixes or
  synthetic defects presented as discoveries in an unmodified upstream project.
- Only synthetic, isolated local data; no account/configuration changes or public
  messages. Source retrieval and existing authenticated evaluation tools are in scope.
- No automatic push or release in this iteration. License choice, private security
  contact and human participation remain owner gates and may be skipped.

## Work and acceptance

1. **Coverage:** reconcile requested outcomes with executed assertions before
   handoff. Compare the revised Skill against a byte-preserved starting snapshot,
   using native host traces and actual files. Include explicit/natural invocation,
   plan-only, historical read-only and adjacent non-acceptance requests. Report
   actual loading independently of correct answers; do not demand loading for an
   out-of-scope near-miss.
2. **Unfamiliar project:** fixed public sqlite-utils checkout, native dependency
   setup only. Give independent execution the user contract, not a prepared test
   or hidden expected verdict. Retain preparation, execution, generated regression
   and failures. Replay without the Skill, then extend the contract with a real
   maintenance requirement. Agent replay is not a human pilot.
3. **Stability:** repeat the existing browser recovery controls from fresh run
   directories; preserve natural failures and all pre-existing objects. Verify
   ownership, termination and cleanup separately from business results.
4. **Upgrade recovery:** inspect the actual pinned installer, reproduce replacement
   and interrupted copy in disposable projects, and test a staged update/backup
   workflow. Keep local changes, unrelated files and old evidence intact. Validate
   historical m1 material with the new installed copy. Do not call the third-party
   installer transactional or add untested automatic recovery claims.
5. **Second host:** one bounded check with existing available authentication; skip
   if authorization needs the owner. No provider migration or credential forwarding.
6. **Handoff:** run local regression suites, verify retained records and links,
   prepare the standard Skill evaluation viewer, and commit exact reviewed paths.
   Report gaps rather than checking off unsupported release or human-benefit gates.

The user's instruction permits skipping human review for continued implementation.
The viewer remains available for later review; no human rating is invented.
