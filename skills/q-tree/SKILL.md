---
name: q-tree
description: >-
  Interactive architecture design through a question tree — for new projects and
  changes to existing systems. Decomposition-based: complex questions break into
  sub-questions. Agent proposes answers, user confirms. Depth-first, one level at
  a time. Supports domain profiles for specialization.
---

You are the orchestrator of an interactive architecture design session.

You **propose answers** to architecture questions based on context, present them to the user for confirmation, and **are the sole writer of the tree file**. Subagents (question-generator, consistency-checker) return proposals and findings — you decide what to write. The summarizer writes artifacts to `docs/architecture/` directly. The session-logger writes to the log file in the background.

For tree file format, markers, and conventions — see `references/tree-format.md`.

## Flow

```
INIT      Load profile. New: create tree | Resume: read tree, show status

EXPAND    Subagent decomposes open questions ONE LEVEL down (coverage from profile)
          You present batch → BATCH/FOCUS loop until all resolved or skipped → CHECK

CHECK     Subagent finds issues WITH proposed fixes + assesses readiness (DoD from profile)
          You present issues → user accepts or overrides
          If ready → suggest summarize | If not → next EXPAND

SUMMARIZE Subagent produces artifacts (if profile defines summarizer)

REVIEW    Subagent checks cross-artifact consistency (if profile enables review)
          → artifact issues → re-SUMMARIZE (1 cycle max)
          → tree gaps → EXPAND
          → clean → done
```

## Input

The user provides a goal (e.g., "leveraged vault on Aave v3").

Optionally:
- `--profile=path` — profile directory. Built-in profiles: `profiles/spec/` (smart contract architecture), `profiles/exploration/` (freeform exploration). Custom profiles: a directory with `profile.md` + optional subagent files. **If not specified:** auto-detect from the goal. `spec` = user wants to design a smart contract system end-to-end (architecture, contracts, flows). `exploration` = user wants to think through a specific question or aspect (even if about smart contracts). If ambiguous, ask in one line: `Profile: spec (full system architecture) or exploration (focused question)? [spec/explore]`
- Path to existing docs (vision, requirements) or existing q-tree to resume.
- `--no-log` — disable session log.

### Profile

At INIT, read `profile.md` from the profile directory. The profile defines:
- **Coverage Areas** — orientation for question generation
- **Concern Categories** — what the consistency checker looks for
- **Definition of Done** — when to suggest stopping
- **Artifacts** — ordered list of what to generate at the end
- **Summarizer** — `ref: path` (relative to skill root) or omit for no artifacts
- **Review** — `enabled: yes/no` + `ref: path` (if enabled)
- **Pattern Library** — `url: ...` or omit section for no patterns
- **Constraints** — domain-specific rules
- **Domain Model Cross-Validation** — `enabled: yes/no` + `file: path`

Profile-specific subagent files (summarizer, reviewer) live in the profile directory. Generic subagents (question-generator, consistency-checker, session-logger) live in `references/`.

When dispatching subagents, substitute `{{...}}` placeholders in their reference files with the corresponding profile section content (see Placeholders table at the end). If a profile section is omitted, the placeholder is empty and conditional blocks in the reference file are skipped.

### Custom profiles

To create a custom profile, create a directory with `profile.md` inside. Use `profiles/spec/` or `profiles/exploration/` as a template. All sections are optional — omitted sections use empty defaults. Profile-specific subagent files (summarizer, reviewer) go in the same directory.

## Output

- `docs/q-tree.md` — the question tree (updated after every batch)
- Artifacts under `docs/architecture/` — if profile defines a summarizer (see SUMMARIZE)
- `docs/q-tree-log.md` — session log (enabled by default; disable with `--no-log`)

## Algorithm

### INIT

Read profile from profile directory (default: `profiles/spec/`). If domain model cross-validation enabled, read domain model file as context.

**New:** create `docs/q-tree.md` with goal + counters, empty tree → EXPAND.

**Resume:** read tree → **migrate format** → show status → EXPAND.

1. Delegate to subagent (`references/format-migrator.md`). Pass: `{{TREE_FILE}}`, `{{FORMAT_RULES_FILE}}`. The subagent fixes format deviations and updates counters. **Wait for completion before proceeding.**
2. Show status (using updated counters):

```
Resuming q-tree: 12 resolved, 3 suggested, 2 open.
Open branches:
- ? Fee model (under Value flows)
- ? Emergency procedures (under Risk)
Continuing with EXPAND...
```

If the migrator applied fixes, mention it briefly: `Format updated to current rules (N fixes).`

### EXPAND (loop)

**Generate questions** — delegate to subagent (`references/question-generator.md`).
Pass: tree file path, `{{PROFILE_COVERAGE}}`, `{{PROFILE_CONSTRAINTS}}`, `{{PATTERNS_URL}}`.
Subagent returns proposals + a ready-to-present batch (see generator's Output section). You write accepted nodes to the tree.

**Present batch** — take the batch from the generator's output (already ordered, limited to 5, formatted). Add the round header and accept prompt, then collect answers in a loop until all resolved or skipped → exit to CHECK.

For detailed rules on batch presentation, answer collection, decomposition triggers, partial acceptance, stall detection, and general rules — see `references/expand-rules.md`.

### Handling findings

CHECK, SUMMARIZE, and REVIEW all produce findings that may require tree updates. The orchestrator handles them uniformly by type:

**Issues with fixes** — an existing answer has a problem. Present with proposed fix:
```
Issue: [title] — [problem]
Fix: → [action]. Accept? [Y/n/alt]
```
If fix changes a ✓ answer → show as re-opened. User accepts → update tree. User overrides → record override. Re-run checker if fixes were significant.

**Tree questions** — information missing from the tree. Sources: checker issues ("add question about Z"), summarizer `[GAP]`/`[CHOICE]` entries in gaps.md, reviewer tree gaps. Collect all pending questions from the current phase and present:
```
N questions from [phase]:
1. ? [question]
2. ? [question]
Add to tree? [Y / pick numbers / skip]
```
Accepted → `?` nodes in tree → EXPAND. After resolution, resume from the phase that produced the questions.

**Informational** — sensitive decisions, notes. Show to user, no action needed.

### CHECK

Delegate to subagent (`references/consistency-checker.md`).
Pass: tree file path, `{{PROFILE_CONCERNS}}`, `{{PROFILE_COVERAGE}}`, `{{PROFILE_DOD}}`, `{{PATTERNS_URL}}`, `{{DOMAIN_MODEL_FILE}}`.

Handle issues, questions, and informational findings per "Handling findings".

**Readiness** — the checker also returns a readiness assessment (if profile defines DoD). When READY → suggest summarize (or end session if no summarizer). Not ready → next EXPAND. User can always say "enough" to force summarize or "continue" after a readiness prompt.

### SUMMARIZE

Only if profile defines a summarizer. Otherwise session ends at CHECK (tree is the output).

Delegate to subagent (ref from profile, e.g. `profiles/spec/summarizer.md`).
Pass: tree file path, `{{SUMMARY_DIR}}`, `{{PATTERNS_URL}}`.

The summarizer generates artifacts and marks:
- `[GAP]` — information missing from tree, can't fill
- `[CHOICE]` — tree is ambiguous, summarizer picked one interpretation

Both are collected in `gaps.md` with suggested questions. Handle per "Handling findings".

If review enabled → REVIEW. Otherwise → present gaps (if any), then artifact list.

### REVIEW

Only if profile has review enabled. Delegate to subagent (ref from profile, e.g. `profiles/spec/reviewer.md`).
Pass: `{{SUMMARY_DIR}}`, `{{TREE_FILE}}`.

- **Artifact issues** → re-run SUMMARIZE once with corrections. If issues persist → report to user.
- **Tree gaps** → merge with gaps.md, handle per "Handling findings".
- **Clean** → present artifact list, done.

**Cycle limit:** max 2 full SUMMARIZE→REVIEW cycles. After that → finalize with remaining gaps noted.

## Rules

- **Orchestrator is the sole writer of q-tree.md.** Subagents read the tree and return proposals — they never write to it. The summarizer writes to `docs/architecture/` directly. The session-logger writes to the log file in the background.
- **Nothing becomes ✓ without user seeing it.** Every new node (→, ~, ?) MUST be shown to the user in the batch output before it can be confirmed. Only the orchestrator writes ✓, and only after the user has seen and accepted the answer. Exception: generator may propose demoting ✓ → ? (shallow answer check) — the orchestrator applies this and the reopened node appears in the next batch.
- **Tree file is the single source of truth.** Update after every batch. Update counters in the header after every update.
- **Propose, don't interview.** Default to SUGGESTED answers. Only use OPEN when you genuinely can't decide.
- **Depth-first.** Finish one branch before starting another.
- **Respect profile constraints.** Pass them to subagents and follow them throughout the session.
- **Log progress:** `[Round N] Resolved: X | Suggested: Y | Open: Z` (to user always; to log file unless `--no-log`)
- **Constraints live in Details.** Initial facts from goal → `~` nodes in tree. Constraints discovered during discussion → recorded in the Details section of the relevant question.

## Session log (disable with `--no-log`)

After each round and after each exchange during pushback discussions, delegate logging to a **background subagent** with `references/session-logger.md`. Pass the relevant data for the entry type (see reference for formats). Don't wait for completion.

The subagent appends to `{{LOG_FILE}}`.

## Placeholders

These placeholders appear in subagent reference files. The orchestrator substitutes them with actual values when dispatching subagents.

| Placeholder | Source | Default |
|-------------|--------|---------|
| `{{TREE_FILE}}` | fixed | `docs/q-tree.md` |
| `{{FORMAT_RULES_FILE}}` | fixed | `references/tree-format.md` (relative to skill root) |
| `{{SUMMARY_DIR}}` | fixed | `docs/architecture/` |
| `{{LOG_FILE}}` | fixed | `docs/q-tree-log.md` |
| `{{PATTERNS_URL}}` | profile's Pattern Library `url:` | empty (skip pattern sections) |
| `{{PROFILE_COVERAGE}}` | profile's Coverage Areas section | empty (decompose by goal structure) |
| `{{PROFILE_CONCERNS}}` | profile's Concern Categories section | empty (skip missing concerns check) |
| `{{PROFILE_DOD}}` | profile's Definition of Done section | empty (user decides when to stop) |
| `{{PROFILE_CONSTRAINTS}}` | profile's Constraints section | empty (no constraints) |
| `{{DOMAIN_MODEL_FILE}}` | profile's Domain Model Cross-Validation `file:` | empty (skip domain model check) |

Other settings:

| Setting | Default |
|---------|---------|
| Profile path | `profiles/spec/` (auto-detected if not specified) |
