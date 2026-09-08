# Reuse and recovery record — 2026-09-08

Starting repository commit: `ac8eda6e35b58583ae521f2989302c73dbb1d0fa`.
This is scoped development evidence, not a release qualification.

- [Stability schedule and results](stability/results.json): three rounds of four
  complete browser journeys, then seeded note loss, missing observation,
  interruption and occupied-port controls. Sixteen scheduled runs met their own
  expectations; only twelve are healthy/recovery PASS results.
- [First retained failure](stability/first-incident.json): before that batch,
  loopback binding was denied. The collector then failed on `ps EPERM`, before
  persisting its own process-exit/stdout record. The native receipt/events survive;
  subsequent read-only inspection confirmed cleanup. This is not an independently
  recorded successful trial and is not in the twelve-flow stability denominator.
- [Final audit](stability/final-audit.json): 67 browser starts/closes; original
  bookmark IDs 3/12 unchanged, new seeded-failure object 47 retained. Tags increased
  from 15 to 29. Normal login sessions are retained, not counted or dumped.
- [Behavior execution matrix](behavior/execution-matrix.json): one old-Skill
  explicit request executed and independently met six assertions. Eleven planned
  trials and the Claude attempt were not run after approval rejection. There are
  **zero completed pairs**, no candidate-behavior result and no improvement claim.
- [Unfamiliar-project attempt](sqlite/pair-result.json): fixed sqlite-utils source
  and native dependencies were prepared, but both candidate/baseline invocations
  exited during host initialization, before model events. No generated native
  regression or no-Skill handoff exists; do not present these as onboarding passes.

The main user authorized continued work and skipping owner-dependent items.
Normal approval rejected further submission to the configured native Agent
service; no authentication, model, provider or safety settings were changed and
no alternate route was used. A separate explicit permission question remains
pending. External humans, license choice, security contact and release are not done.

## Check retained evidence

```sh
python3 -B evals/results/2026-09-08-reuse/check_record.py
```

The checker reads captured artifacts, compares bytes and selected actual
observations, and preserves unavailable outcomes. It does not invoke a model,
start a browser, authenticate collection, or qualify future application versions.
Run the current native instructions for new product evidence.

`manifest.json` records each original source digest and its public-copy digest.
Task-root/home paths use placeholders; CSV and captured executable bytes are
unchanged. Original records remain local. Credentials, databases, raw startup or
exception logs, screenshots and private process snapshots are excluded. References
to screenshots in captured events identify local evidence, not bundled public
images. Digests detect modification; they do not prove truthful collection.

The standard Skill reviewer is generated separately in the task's
`functional-acceptance-workspace/iteration-3`. It includes explicit NOT-RUN cards
and the one real output. No human review is claimed. The supplied aggregation
utility was run on the sole graded record only; its synthetic delta against an
absent second configuration was removed and native usage retained. The resulting
single-record statistics are descriptive, not a comparative benchmark.

Upgrade and older-material results, maintenance boundaries and unresolved gates
are summarized in [REUSE-RESULTS.md](../../../REUSE-RESULTS.md).
