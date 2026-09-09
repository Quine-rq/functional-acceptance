# Risk-first revision: known-case local regression

This is a development result, not a production-benefit or supported-release claim.
The candidate improves observed coverage in these samples but still fails a
delivery deadline. It is not promoted to a mature release by this evaluation.

## Frozen comparison

Three local linkding conditions (healthy, injected initial-note loss, injected
private-details exposure), three configurations and two runs per condition:
18 attempts, including both hard-stop attempts. The source application is pinned
at `65813a75404b1319aca8b09700fadc0b15adabaf`. These injected faults are not alleged
upstream vulnerabilities. All data, accounts and services were synthetic/local.

| Configuration | Defects detected | Core checks observed | Mean native seconds | Native turns within 300 seconds |
| --- | --- | --- | --- | --- |
| Candidate | 4/4 | 42/42 | 316.9 | 2/6 |
| Previous Skill (`e53ed05`) | 3/4 | 40/42 | 309.2 | 2/6 |
| Without target Skill | 3/4 | 39/42 | 288.8 | 4/6 |

All arms had zero confirmed healthy false positives and zero unsupported full-goal
approvals. A valid observed business failure counts as an executed check;
UNVERIFIED does not. Core coverage excludes the separate original-data,
reporting, handoff and authorization-trace assertions.

The candidate dynamically exercised private details in all six runs. The previous
Skill skipped that boundary twice; the no-target arm skipped it three times.
Both comparison arms consequently missed the second injected privacy fault.
The candidate also established complete original-data preservation observations
in 3/6 runs, versus 0/6 for each comparison arm. Coordinator snapshots found no
actual original-data damage in any run; that cannot award executor coverage.

The candidate's second healthy run reached the 360-second outer stop without a
final response. The previous Skill also received an outer-stop signal once, but
had retained a completion event and report. Existing observations remain scored;
delivery status remains separate. The candidate is slower on the observed means,
and only five candidate runs have complete native token usage. Missing usage is
not zero and does not establish savings.

## Identity and method

- Previous package: `e53ed05796e364bc15e72b724aa03a8e5e4b3c56`.
- Candidate: uncommitted nine-file Skill snapshot; canonical inventory SHA-256
  `ce2e8ae6202ccf784386ba2446cb5ff46f635b51e9cda39638d6b59672ff1fc5`.
- The name and description were unchanged. Both installed packages were fully
  read in 6/6 native runs; target discovery was not this revision's bottleneck.
- Identical request and limits, fresh app/state/browser per attempt, unchanged
  competing host Skills, no automatic retries. “Without target Skill” is not a
  bare model with all other Skills removed.
- Native Codex CLI with configured gpt-6-astra/medium; server-side model identity
  was not independently attested. Grading used separate read-only native contexts,
  not blinded or third-party human review. The author checked key counterexamples,
  event-reference attribution, frozen identities and aggregation consistency.

These cases were already known during revision: this is regression on a reused
development set, not held-out generalization. Two repeats on one application and
one native host cannot establish production uplift or cross-host reliability.
Execution means exclude coordinator setup and independent grading and are not an
end-to-end cost study. Raw traces, generated checks and state receipts are retained
in the author's local evaluation workspace, not distributed here: this summary
alone is not an independently reproducible evidence package. Raw attachments may
contain synthetic credentials and are not approved for public upload.

## Separate checks and remaining gate

The [three intent guards](../../risk-first-guards.json) were each run once with
the candidate and previous Skill. Both passed 18/18 assertions. All six traces
only read Skill files; no target execution, network call or executor file creation
was observed. These are plans/history reviews, not successful export or delivery.

All 150 local engineering checks passed, including package relocation and the
five installation targets. Those installation checks are not native behavioral
evaluation on all five hosts. No current remote CI result is claimed.

Next priority: reliable deadline-aware, incremental handoff and dependency-aware
check isolation, then a frozen evaluation on a project not used to design this
revision. Full original-data checks and secondary-object disclosure still need
to become dependable rather than occasional.
