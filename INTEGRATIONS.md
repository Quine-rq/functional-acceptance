# Agent integration — development preview

## Scope and acceptance criteria

Developers should be able to take the same acceptance workflow into their existing coding agent without copying this repository's development instructions, historical evaluations, or local evidence into that agent's context.

Before this change, the Skill and helper lived at the repository root beside development files. The CSV sample ran locally, but installation, discovery and execution in another host had not been checked.

This change separates one self-contained `skills/functional-acceptance/` package. Installation uses an existing ecosystem tool rather than a new package manager. It does not add an agent runtime, tool permissions, account connection, product-specific runner, or formal release.

Before calling this slice checked:

1. The package contains its own referenced instructions and optional helper; no parent checkout or author-machine path is required.
2. A pinned installer can discover, copy, and remove it in isolated project directories for the selected hosts. Inspect file contents, not just installer exit codes.
3. Reinstalled copies preserve the source bytes. Document actual replacement behavior and protect user-edited copies through an explicit review/backup step; do not promise transactional upgrades.
4. The installed helper can recheck healthy, defective, and missing-observation material from a different working directory.
5. Host discovery and actual agent behavior are reported separately from package/installer checks. Unavailable hosts remain unverified.

Keep existing CSV verdicts, evidence semantics, native sample commands, and historical results unchanged. Missing execution tools must not block a plan-only request or turn an unobserved user outcome into PASS. No shared user configuration or live global Skill directory is modified by these checks.

## Precedents and decisions

Official sources inspected on 2026-09-08:

- [Agent Skills specification](https://agentskills.io/specification): one named directory, standard name/description, relative resources and progressive loading. We use the shared fields, not host-specific tool allowlists or command interpolation.
- [OpenAI's gh-fix-ci](https://github.com/openai/skills/tree/main/skills/.curated/gh-fix-ci): a bounded workflow with a separately invoked helper and explicit prerequisites. We keep the helper path relative to the installed Skill, not the user's current directory.
- [Anthropic's webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing): focused Skill plus supporting scripts. We borrow the packaging pattern, not its browser-specific workflow or permissions.
- [Vercel Skills CLI](https://github.com/vercel-labs/skills): existing agent-specific installation, copying and removal. Pin the tested CLI version. Its installation code replaces a same-name destination, so repeat installation is not a backup or merge mechanism.

These are design references, not copied implementations. Their support claims do not become this project's support claims.

## Install into one project

Development preview, not a supported release. Read the [Skill](skills/functional-acceptance/SKILL.md) and its resources first. License selection is still pending.

The tested installer is `skills@1.5.24`, requiring Node 22.20+. It is a separate third-party tool, not part of the Skill runtime. The following commands may download it from npm and fetch this public repository. `DO_NOT_TRACK=1` disables that installer's telemetry; the host's own data handling is separate.

From the root of the project where you want to use the Skill, first list the available package:

```sh
DO_NOT_TRACK=1 npx --yes skills@1.5.24 add Quine-rq/functional-acceptance --list
```

**Fresh destination only:** inspect the paths in the table below first. The installer replaces a same-name directory, including local edits. If one already exists, use the update precautions below instead of running this blindly.

For Codex, install a project-local copy:

```sh
DO_NOT_TRACK=1 npx --yes skills@1.5.24 add Quine-rq/functional-acceptance --skill functional-acceptance --agent codex --copy --yes
```

Replace `codex` with exactly one target below. No `--global`, wildcard target, hooks, MCP servers, or permission allowlist is needed. The current package contains six files, including the native-workflow reference; tests, evaluation outputs, repository `AGENTS.md`, and development dependencies are not copied. The older five-file measurements below describe their recorded source revision.

| Host | Installer target | Project location | Discovery / invocation reference |
| --- | --- | --- | --- |
| Codex | `codex` | `.agents/skills/functional-acceptance/` | [Official Skills docs](https://learn.chatgpt.com/docs/build-skills): verify the loaded path; CLI/IDE can select with `$` or `/skills` |
| Claude Code | `claude-code` | `.claude/skills/functional-acceptance/` | [Official Skills docs](https://code.claude.com/docs/en/skills): `/functional-acceptance`; check same-name personal overrides |
| Cursor | `cursor` | `.agents/skills/functional-acceptance/` | [Official Skills docs](https://cursor.com/docs/skills): view Skills and select by `/` |
| GitHub Copilot | `github-copilot` | `.agents/skills/functional-acceptance/` | [Official Skills docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills): load when the request matches |
| OpenCode | `opencode` | `.agents/skills/functional-acceptance/` | [Official Skills docs](https://opencode.ai/docs/skills/): discover and load through the native Skill tool |

Four targets share the **same project directory**. They do not receive isolated versions; installing/updating/removing that directory affects every host that reads it. Claude's project copy is separate. Host settings, precedence and version differences can still prevent loading. Remote/cloud sessions need files accessible in their own environment; this command does not upload local user skills or configure remote agents.

## Verify the installed copy

1. Confirm the host has discovered `functional-acceptance` at the expected project path. A same-name global copy or installed plugin is not proof of loading this one. Restart/reload if the host does not see a new directory.
2. Start with a bounded prompt: “Use functional-acceptance to plan acceptance for this feature; do not run the application.” Provide the actual requirements and project. Expect a plan, independent expected results and explicit gaps, not a fabricated PASS or demands for credentials just to plan.
3. Only then request execution in an authorized test environment. Verify that the host uses actual project tools, reopens the relevant output, and preserves missing observations. Installing the Skill does not add those tools.

The optional helper needs Python 3.10+ and a suitable POSIX filesystem. Its only implemented mapping is local CSV; it is not a generic adapter for every test framework. The installed [host guide](skills/functional-acceptance/references/host-compatibility.md) separates Skill paths, project paths, capabilities and evidence. Normal plan-only use has no Python dependency.

## Pin, update, recover and remove

Pin both the installer and the Skill source when recording a reproducible run. The owner/repository command above tracks the moving default branch. For a reviewed commit, use `https://github.com/Quine-rq/functional-acceptance/tree/FULL_COMMIT_SHA/skills/functional-acceptance` as the source, replacing `FULL_COMMIT_SHA` with the actual 40-character commit. Do not infer a source pin from the installer version or a folder hash alone.

Before updating: inspect and back up the exact installed directory outside all Skill discovery directories, record the source commit, and compare your local edits. Do not place evidence inside the Skill. Test the chosen revision in a fresh project first. Reinstallation replaces the old copy; it does not merge edits or guarantee atomic recovery after interruption. If an install fails, inspect the named destination and restore the reviewed backup before relying on it. We have not fault-tested third-party installation or its update service.

From the same project, after identifying this installation and any local edits:

```sh
DO_NOT_TRACK=1 npx --yes skills@1.5.24 remove functional-acceptance --yes
```

This removes that name from the project's agent locations, including copies shared by several hosts; it is not a per-host disable switch. It does not remove global installations. Keep a backup for recovery. Check the actual directories and host inventory afterwards; a CLI exit alone is insufficient. Unrelated Skill names and project files are checked for preservation in our tests.

Without Node, the same package directory can be copied manually into the documented host location. Treat that as an unmanaged copy: review the files, refuse unintended replacement, retain the source commit, and verify host discovery. Manual copying and platform-specific file-manager behavior are not covered by the installer tests.

## Measured coverage — 2026-09-08

Source commit `f4b1ef9bb1b57f69e9b0a9107fa484df879c006c`: 66 helper/collector/package tests and 23 standalone tests passed locally on both Python 3.10.20 and 3.14.4; all ten installer tests passed on Node 22.22.3. [The matching CI run](https://github.com/Quine-rq/functional-acceptance/actions/runs/34185450287) passed both Python jobs and the installation job on Ubuntu 24.04. The record describes this source revision, not later changes.

A separate installation from that exact GitHub commit into a temporary Claude Code project path returned all five files byte-identical to the source, retained the full commit in `skills-lock.json`, and was then removed. This tested remote retrieval and source pinning, not the Claude model. [Machine-readable record and file digests](integration/results/2026-09-08.json).

| Layer | Observed result | What it does not prove |
| --- | --- | --- |
| Package | Shared YAML parsed; all local links stay inside the package; only the five runtime files ship | Useful model behavior or every future host version |
| Installer | Node 22.22.3 + `skills@1.5.24` on macOS: five targets install/reinstall/remove byte-identical copies; unknown host/name rejected; unrelated files preserved | Native host discovery or transactional/safe merging of local edits |
| Relocated helper | Real healthy/defective/missing-observation runs rechecked as PASS/FAIL/UNVERIFIED from another working directory; installation unchanged | Another business project or another execution mapping |
| Codex discovery | CLI 0.146.0 `skills/list` returns the installed, enabled repo Skill and UI metadata; after removal and rescan it is absent | Model invocation or execution of a user journey |
| Codex behavior | Separate CLI 0.153.4 smoke checks exercised natural loading, native CSV execution, planning, regression, a near-miss and missing history; a read-only write violation was found and narrowly rechecked after correction | Repeated reliability, a controlled baseline, other host models or a second project; see the [full record](evals/results/2026-09-08-host-smoke/README.md) |
| External-project study | The unchanged Skill loaded in linkding; its independent run stopped on a local socket-bind denial. An author-assisted native browser/Django/SQLite journey subsequently passed after regression corrections | Not autonomous completion, an independent human handoff or a supported browser adapter; all attempts are in the [linkding record](evals/results/2026-09-08-linkding/README.md) |
| Other hosts | Official paths inspected; installer filesystem checks only | Claude Code, Cursor, Copilot and OpenCode discovery/behavior remain unverified |

The optional Codex probe initially timed out in the restricted environment, then exposed a startup permission error. The same probe passed with normal process permissions, without invoking a model or changing shared configuration. The failed attempts are not counted as successes.

Reproduce package/helper tests with the two Python commands in the README. Reproduce the ten installer tests with:

```sh
npm --prefix integration ci --ignore-scripts --no-audit --no-fund
npm --prefix integration test
```

With an existing Codex installation, the separate no-model discovery probe is:

```sh
node integration/check-codex-discovery.mjs
```

It creates and cleans an isolated temporary project and does not install into the user's global Skill folders. Codex itself may need normal permission to initialize its runtime state. A timeout or unavailable host is a failed/unverified check, not a skipped success. The default CI runs package/helper and installer tests, not this host-dependent probe.

The behavior probe also found that PATH CLI 0.146.0 could discover the Skill but could not invoke the configured model. An existing app-bundled 0.153.4 executable worked without changing the user's model or global setup. Record the actual executable/version and distinguish host startup errors from Skill behavior; this observation is not a minimum-version guarantee.

## Product-hardening follow-up

The [new record](evals/results/2026-09-08-product-hardening/README.md) adds a
six-file package, repeated native Codex comparisons and a maintained linkding
handoff. Packaging and behavior remain separate: the current installed Skill was
actually read in four of five measured Codex requests. A historical-evidence
request did not load it, despite the installed path being listed.

Claude Code 2.1.220 was invoked in two isolated project configurations using its
existing authentication. Both stopped with authentication 403 before task tool
execution. No credential was migrated, forwarded to a suggested endpoint or
reconfigured. They are environment failures, not second-host compatibility proof.
Cursor, Copilot and OpenCode still have installer checks only.

Current local checks and release gates are in [the results](PRODUCT-HARDENING-RESULTS.md).
No new remote CI or release success is implied by historical green jobs.
