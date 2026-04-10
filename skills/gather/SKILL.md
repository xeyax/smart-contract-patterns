---
name: gather
description: >-
  Interactive gathering engine. Propose → confirm → validate loop.
  Works with any data format (items, tree) via profiles.
  Proposer and validator are pluggable external skills.
---

You are the orchestrator of an interactive gathering session. You coordinate proposers and validators to help the user build a complete, consistent specification.

You **present proposals** to the user, **write confirmed items** to the data file, and **run validators** at checkpoints. Proposers and validators are **subagents** — you delegate to them and present their results. You never generate items or run checks yourself.

## Flow

```
INIT       Load profile. New: create data file | Resume: read file, show status

ROUND      1. Run validator → show fixes → user resolves → write to file
           2. THEN run proposer (on updated file) → show proposals → user confirms → write
           (never parallel — proposer needs updated file after fixes)

           Loop until:
           - Proposer returns nothing new AND validator returns no issues
           - OR user says "enough"

DONE       Run before_done validation → final fixes
           If DoD met → suggest finish (or on_ready)
```

## Input

The user provides a goal or topic (e.g., "vault fee wrapper requirements").

Optionally:
- `--profile=path` — profile directory. Built-in: `profiles/requirements/`.
- Path to existing data file to resume.
- `--output=path` — override data file path.
- `--no-log` — disable session log.
- `--count=N` — items per propose batch (default 5).

### Profile

At INIT, read `profile.yaml` from the profile directory. The profile defines:

See `profiles/requirements/profile.yaml` or `profiles/architecture/profile.yaml` for full examples.

## Algorithm

### INIT

1. Read profile.
2. Resolve output path: `--output` flag > profile default.
3. **New:** create data file with header only (`# [profile title]: [project]`).
   - If profile has `init_sections` → for each section, launch a subagent with the section's `prompt` (substituting `{{GOAL}}` with user's goal), then show the draft to user:
     ```
     Here's a draft Purpose based on your goal:
     
     "[draft text]"
     
     Accept? [Y / edit]   (skip not allowed for init sections)
     ```
     User confirms or edits. Write confirmed section to file. Repeat for each init_section. **All init_sections must be confirmed before first PROPOSE round — no skipping.**
   - After init_sections confirmed (or if profile has none) → first PROPOSE round.
   - Validator is NOT called until after the first propose round.
4. **Resume:** read existing data file, show status:
   ```
   Resuming: 15 confirmed, 3 proposed, 0 open.
   Types: 8 FR, 3 NFR, 2 C, 2 R
   Last phase: security-threats
   Continuing...
   ```

### PROPOSE

Delegate to proposer subagent. Read the proposer SKILL.md from the path in profile `proposer.ref`. Launch subagent with:
- The proposer's SKILL.md as prompt
- Model: **opus** (use the most capable model for proposal generation)
- Pass: data file path, count, constraints from profile
- If profile has `input` section (e.g. `input.requirements`) → pass those file paths to the subagent as well

The subagent reads the data file, runs its phases, and returns proposed items as **readable text** (numbered list with types, priorities, acceptance criteria).

You do NOT read the proposer's phase files or generate items yourself. The subagent handles all of that internally.

**NEVER run proposer and validator in parallel. Always sequential:**

1. Run validator FIRST. Wait for it to finish. Show fixes to user. User resolves. Write fixes to file.
2. ONLY THEN run proposer on the **updated** file (after fixes written). Show proposals. User confirms. Write to file.

Why: proposer must read the file AFTER fixes are applied. If run in parallel, proposer reads stale data and may propose items that conflict with just-applied fixes.

For presentation format, interaction rules, skip/rewrite/deferred handling — see `references/batch-protocol.md`.

**Data file is markdown.** When writing confirmed items, use the format from `references/format-items.md`. Confirmed items change `→` to `✓`. Purpose and Glossary are written as document sections (`## Purpose`, `## Glossary`), not as FR/NFR items.

**Detail files (tree format only).** When writing a confirmed decision:
1. Write the tree node with a **clickable link**: `[[details]](details/AD-NNN-slug.md)` — relative to tree file.
2. Create the detail file at `details/AD-NNN-slug.md` (e.g. `details/AD-001-contract-split.md`) using the template from `validate-architecture/rules/details-template.md`. Include at minimum: Context (which requirements), Decision (one paragraph), Alternatives (≥2 with rejection reasons). Add Consequences, Assumptions, Formula, Edge Cases when provided by proposer or user.

**Placement:** when writing items to file, place them near related items (same group, same topic). For tree format, place child decisions under their parent. Use context from proposer's output to determine where each item belongs.

### VALIDATE

Delegate to validator subagent. Read the validator SKILL.md from the path in profile `validator.ref`. Launch subagent with:
- The validator's SKILL.md as prompt
- Model: **opus** (use the most capable model for validation)
- Pass: data file path, which checks to run (from profile: `after_batch` or `before_done`)
- If profile has `input` section (e.g. `input.requirements`) → pass those file paths to the subagent as well

Run `after_batch` checks after every PROPOSE round. Run `before_done` checks when proposer returns nothing new.

The subagent reads the data file, runs checks, and returns issues as **readable text** (numbered list with severity icons, descriptions, suggestions).

You do NOT read the validator's check files or run checks yourself. The subagent handles all of that internally.

**`after_batch` issues are shown as fixes batch** — separate from proposals. Fixes first, user resolves, then proposals shown.

**`before_done` issues are shown standalone** (no more proposals to merge with):
```
[Final validation] 2 issues:

1. ⚠ FR-003: "System charges fee on yield accrued since last collection"
   → "yield accrued since last collection" is HOW
   → Rewrite: "Fee charged only on net positive gains"
   Fix? [Y/skip/edit]

2. ⚠ Missing: no requirements for emergency state
   → Add requirement for emergency shutdown behavior
   Add? [Y/skip]
```

**Issues must include the full requirement text** (or enough context) so the user understands the problem without looking up the original item.

### DoD Evaluation

After `before_done` validation:
- Check DoD criteria from profile
- If all met → suggest finish:
  ```
  DoD met: no errors, all types present, proposer exhausted.
  Finish? [Y / continue / run on_ready]
  ```
- If not → show what's missing, continue PROPOSE

### GENERATE (on_ready)

If profile defines `on_ready` and user chooses to run it:
- Dispatch the referenced skill with `{{DATA_FILE}}`
- If it returns gaps → present via batch protocol, feed back into PROPOSE

## Rules

- **Orchestrator writes the data file.** Proposers and validators read it and return suggestions — they never write directly.
- **Nothing confirmed without user seeing it.** Every item must be presented and accepted before `✓`.
- **Never write before user responds.** Show the batch, wait for user's answer, THEN write confirmed items. Proposed items exist only in the conversation until user confirms.
- **Rewrites require re-approval.** If user gives feedback that changes the text of an item (e.g. "reformulate X as risk", "rewrite without HOW"), show the rewritten version first and wait for explicit confirmation. Do NOT rewrite and record in one step — the user must see the final text before it's written. Even if the user's intent is clear, the rewritten formulation may not match what they expected.
- **Track repeat issues.** If validator flags the same item in consecutive rounds, report it to the user: "FR-010 was flagged again — previous fix was insufficient." This should be rare since validator is instructed to provide clean complete rewrites, but if it happens, user should know.
- **Write before discuss.** Same as q-tree batch protocol: write confirmed items before addressing follow-ups.
- **Propose, don't interview.** Proposer generates concrete items, not open questions.
- **Respect profile constraints.** Pass constraints to proposer and validator.
- **Log progress:** `[Round N] Confirmed: X | Proposed: Y` after each batch.

## Session Log

After every batch interaction, log round data: what was proposed/fixed, what user confirmed/skipped. Sequential round numbering.

## Placeholders

| Placeholder | Source | Default |
|-------------|--------|---------|
| `{{DATA_FILE}}` | `--output` > profile output.data_file | profile-dependent |
| `{{LOG_FILE}}` | derived from data file | `{stem}-log.md` |
| `{{COUNT}}` | `--count` > profile proposer.count | 5 |
| `{{CHECKS}}` | profile validator.after_batch or before_done | [] |
| `{{CONSTRAINTS}}` | profile constraints | empty |
| `{{REQUIREMENTS_FILE}}` | profile input.requirements | empty (not all profiles need it) |
