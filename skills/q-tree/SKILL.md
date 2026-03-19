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

### CHECK

Delegate to subagent (`references/consistency-checker.md`).
Pass: tree file path, `{{PROFILE_CONCERNS}}`, `{{PROFILE_COVERAGE}}`, `{{PROFILE_DOD}}`, `{{PATTERNS_URL}}`, `{{DOMAIN_MODEL_FILE}}`.

**Issues found** — present each WITH a proposed fix:
```
Issue: Balancer flash + USDT — Balancer doesn't support USDT flash loans
Fix: → switch to Aave for USDT pairs (0.05% fee). Accept? [Y/n/alt]
```
User accepts fix → update tree. User overrides → record override. Re-run checker if changes were significant.

**Re-emergence** — if a fix requires changing an earlier confirmed (✓) answer, revert that answer to → (suggested new value) in the tree and present to the user:
```
Re-opened: "Oracle: Chainlink" (was ✓, conflicts with "support long-tail tokens")
New suggestion: → Chainlink + fallback to Uniswap TWAP for long-tail. Accept? [Y/n/alt]
```

**Sensitive decisions** — if the checker reports high-impact answers, show them:
```
Sensitive: "Chain: Arbitrum" affects 3 other decisions (gas, protocols, bridge)
```
This is informational — no action needed, just awareness for the user.

**No issues** → say "No consistency issues."

**Readiness** — the checker also returns a readiness assessment. When readiness signals are positive, proactively suggest stopping:

```
[Readiness] Coverage: 5/5 relevant areas resolved. No blocker issues.
Last batch: 4/6 questions were execution-scope.
Ready to summarize? [Y / continue with "deeper into X"]
```

If the profile has no summarizer, suggest ending instead:
```
[Readiness] Goal appears answered. No open branches blocking the conclusion.
End session? [Y / continue with "deeper into X"]
```

**User providing execution-level answers** is a strong readiness signal — the user is already thinking in specifics. Record as ✓, then check.

**If not ready** — continue to next EXPAND.

The user can always say "enough" to force summarize, or "continue" to keep going after a readiness prompt.

### SUMMARIZE

Only if profile defines a summarizer. Otherwise session ends at CHECK (tree is the output).

Delegate to subagent (ref from profile, e.g. `profiles/spec/summarizer.md`).
Pass: tree file path, `{{SUMMARY_DIR}}`, `{{PATTERNS_URL}}`.
Artifacts generated in profile-defined order (each uses prior as context).

If review enabled → REVIEW. Otherwise → present artifact list.

### REVIEW

Only if profile has review enabled. Delegate to subagent (ref from profile, e.g. `profiles/spec/reviewer.md`).
Pass: `{{SUMMARY_DIR}}`, `{{TREE_FILE}}`.

**Artifact issues** → re-run SUMMARIZE once with corrections. Max 1 cycle — if issues persist, report to user.

**Tree gaps** — present as new ? questions:
```
Review found 2 tree gaps:
1. [cross-flow] migrate flow missing slippage — ? Max slippage for migration swaps?
2. [dependency] No oracle interface — ? Which oracle interface to use?

Fix gaps? [Y / pick numbers / skip]
```
- Y → gaps become ? questions, return to EXPAND. After resolution, full SUMMARIZE + REVIEW again. **Max 2 cycles** — then finalize with gaps noted.
- Pick numbers → selected become questions, rest skipped. Same cycle limit.
- Skip → finalize as-is.

**Clean** → present artifact list.

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
