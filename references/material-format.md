# Experimental material format: m1

Use this reference only for the bundled local CSV mapping. It is a narrow development interface, not a universal test format. Unknown versions are rejected. The collector is trusted: consistency checks and digests do not authenticate where an artifact came from.

## Native execution first

Run the project's reviewed native checks. The sample collector in `examples/paginated_export/accept.py` records actual subprocess termination and copies the executed program/input to a unique evidence directory. It never calls commands found in input material. The helper reads that directory without running code or making network requests.

From the repository root:

```sh
python3 scripts/acceptance.py --contract RUN/contract.json --run RUN/run.json --root RUN --format json
```

Replace `RUN` with one actual run directory. Use `--format markdown` for a human-readable report. Output goes to stdout unless `--output NEW_FILE` is supplied; existing files are never overwritten. Exit 0 means qualified scoped PASS, 1 means a valid counterexample, and 2 means incomplete, invalid, or unavailable material/output. A report still distinguishes business facts from cleanup and coverage.

JSON reports include `business_verdict`, `qualified_pass`, `completion`, `material_status`, per-goal/obligation/attempt details, cleanup/retention, and `material_usage`. A business PASS with unfinished execution or cleanup retains that fact but has `qualified_pass: false`, partial completion, and exit 2. The collector reopens material for each report format; if those checks disagree, its overall exit is incomplete and existing reports remain historical rather than a qualified handoff.

## Contract

All keys below are required unless described otherwise. Extra keys are rejected rather than silently interpreted. IDs are nonempty bounded strings and unique within their collection. `schema_version` is exactly `m1`.

- `journey`: the original user outcome in a short sentence.
- `target`: `{ "id": "local-export", "sha256": "<executed program digest>" }`.
- `input_sha256`: the frozen input file digest.
- `goals`: nonempty list of `{id, text, source, obligations, gap, exclusion}`. `obligations` is a list of obligation IDs. Exactly one routing choice is nonempty: obligations, a textual `gap`, or `exclusion: {reason, source}`. Other choices are respectively `[]`, `null`, `null`. All obligations must be routed. A tool shortage is a gap, not an exclusion.
- `obligations`: list of `{id, expected, required, applicable, exclusion, mapping, columns, rows}`. Required/applicable are booleans. An inapplicable obligation has a sourced `{reason, source}` exclusion; otherwise exclusion is null. M1 supports only mapping `csv-exact/v1`. Columns are nonempty unique strings; rows are lists of strings with matching width. Row order, values, and duplicates are significant; this expectation is chosen for this sample, not a universal export rule. Unknown mappings remain UNVERIFIED.
- `scope`: `{environment, upstream, claim}`. The sample uses `isolated-local`, `synthetic-pages`, and an explicit claim limited to the local CLI/file workflow. These are descriptive, not permission grants or source authentication.

## Run

- `schema_version`, `id`, `contract_sha256`: digest is of the exact frozen contract bytes, not parsed/reformatted JSON.
- `runtime` and `input`: each is an artifact reference `{path, sha256}`. Their digests must match the contract. The collector snapshots the same bytes it executes/reads, not just a repository HEAD identifier.
- `tool`: `{name, version}` identifying the actual collector/interpreter combination.
- `attempts`: list of `{id, execution, observations}`. `execution` is an artifact reference to the raw native process record. `observations` contains `{obligation_id, artifact}` with one observation per obligation per attempt. Missing entries become UNVERIFIED; later attempts do not erase earlier ones.
- `execution_state`: `completed`, `interrupted`, or `unknown`.
- `cleanup`: `{state, details}`, where state is `clean`, `retained`, `residual`, or `unknown`. `retained` means only explicitly run-owned output/evidence is intentionally retained, no active writer or other residual is known. The collector must actually confirm its child terminated. This local run has no backend deletion work.
- `retention`: `{policy: "until-owner-removes", details}`. M1 does not implement expiry or background deletion. Keep each run independent. Rechecking missing or modified evidence invalidates its current qualification without rewriting prior reports.

## Native process record: local-process/v1

Required fields are `schema_version`, `run_id`, `attempt_id`, `target_sha256`, `input_sha256`, `argv` (nonempty string list), `completed` (boolean), `exit_code` (integer or null), `output` (artifact reference or null), `stdout` and `stderr` (strings). IDs/digests must match the run and contract; each observation must reference the same output artifact. The strings in argv/stdout/stderr are never executed or interpreted as verdicts.

Only a terminated, zero-exit sample process with a matching output artifact qualifies for the CSV mapping in M1. Other process outcomes are execution gaps, not automatically product defects. That is an explicit mapping limitation, not a rule for all future tools. The helper reads the CSV itself, decodes UTF-8, parses strictly, and compares the fixed header and rows. Malformed or mismatched observed CSV is a concrete counterexample; absent/unreadable/changed material is UNVERIFIED.

## Reading and reporting bounds

Evidence references are relative to the explicit root. Absolute paths, traversal, symlinks, nonregular files, unsupported extensions, and oversized inputs are rejected. Allowed evidence extensions are `.json`, `.csv`, `.py`, and `.txt`. A file is bounded to 2 MiB; a run to 128 evidence references and 16 MiB read. JSON inputs are also bounded, reject duplicate keys and nonfinite numbers, and have capped record counts. These are initial local safety limits, not benchmark claims.

The helper enforces material rules; the agent must still validate user-goal extraction, permitted scope, truth of collection, and whether the mapping's semantics fit the actual request. It cannot notice an outcome omitted from both the user's copied request and the contract. A wholly fabricated internally consistent run is outside its guarantee.

Markdown renders supplied text as escaped text, not active links/HTML. Reports are local by default and not automatically sanitized for publication; review them before sharing. Synthetic fixtures are the only intended public example data.
