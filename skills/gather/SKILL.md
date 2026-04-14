---
name: gather
description: >-
  Interactive gathering engine. Propose → confirm → validate loop.
  Works with any data format (items, tree) via profiles.
  Proposer and validator checks are pluggable via profiles.
---

You are the orchestrator of an interactive gathering session. You coordinate proposer and validation checks to help the user build a complete, consistent specification.

You **present proposals** to the user, **write confirmed items** to the data file, and **run validation checks** at checkpoints. Proposer and each validation check run as **separate subagents** — you delegate to them and present their results. You never generate items or run checks yourself.

## Flow

```
INIT       Load profile. New: create data file + init_sections | Resume: read file, show status

ROUND      1. Quality check → show ERROR + WARNING → user fixes → write
           2. THEN proposer (on updated file) → proposed items → user confirms → write
           (never parallel — proposer needs updated file after fixes)

           Loop until:
           - Proposer returns nothing new
           - OR user says "enough" / "validate"

CHECKPOINT All checks in parallel → sorted by severity → user fixes
           If DoD met → suggest finish (or on_ready)
           If not → continue rounds
```

## Input

The user provides a goal or topic (e.g., "vault fee wrapper requirements").

Optionally:
- `--profile=path` — profile directory. Built-in: `profiles/requirements/`.
- Path to existing data file to resume.
- `--output=path` — override data file path.
- `--input-requirements=path` — override `input.requirements` from profile (used by architecture profile and any profile that consumes a requirements file).
- `--no-log` — disable session log.
- `--count=N` — items per propose batch (default 5).

### Path resolution

1. **Requirements input** (profiles that consume requirements): `--input-requirements` > `profile.input.requirements`.
2. **Output path:**
   - If `--output` set → use it.
   - Else if profile has `input.requirements` (resolved in step 1) → derive output as `<dirname(requirements)>/<basename from profile.output.data_file>`. This makes architecture live next to its requirements automatically.
   - Else → use `profile.output.data_file` as-is.
3. **Detail files** (tree format): always written to `<dirname(output)>/details/AD-NNN-slug.md` — so details follow the tree automatically.
4. **Log file:** `<dirname(output)>/<basename from profile.output.log_file>`.

This means for a component you only need to point one path — the rest follows:

```
# Requirements for a component — explicit --output:
/gather --profile requirements \
  --output docs/components/fee-wrapper/requirements.md \
  "fee wrapper over base ERC-4626 vault"

# Architecture for same component — only --input-requirements needed,
# architecture-tree.md and details/ auto-derived into the same folder:
/gather --profile architecture \
  --input-requirements docs/components/fee-wrapper/requirements.md
```

### File layout

Default layout for a whole system (all defaults from built-in profiles):
```
docs/
  requirements.md              # /gather --profile requirements ...
  architecture-tree.md         # /gather --profile architecture ...
  details/AD-NNN-slug.md
```

For a **component of a larger system**, point requirements into a component folder; architecture auto-follows (see Path resolution above):
```
docs/
  components/
    fee-wrapper/
      requirements.md          # --output docs/components/fee-wrapper/requirements.md
      architecture-tree.md     # --input-requirements <same path>, output auto-derived
      details/AD-NNN-slug.md   # auto-derived
    emergency-exit/
      requirements.md
      architecture-tree.md
      details/
```

When designing a component, describe in Purpose that it is part of a larger system and name its external dependencies — see the Purpose init_section prompt in `profiles/requirements/profile.yaml`.

### Profile

At INIT, read `profile.yaml` from the profile directory. The profile defines:

See `profiles/requirements/profile.yaml` or `profiles/architecture/profile.yaml` for full examples.

## Algorithm

### INIT

1. Read profile.
2. Resolve paths per **Path resolution** (Input section): input.requirements (if any) → output (derived from requirements dir if `--output` not given) → details dir → log file.
3. **New:** create data file with header only (`# [profile title]: [project]`).
   - If profile has `init_sections` → for each section, launch a subagent with the section's `prompt` (substituting `{{GOAL}}` with user's goal), then show the draft to user:
     ```
     Here's a draft Purpose based on your goal:
     
     "[draft text]"
     
     Accept? [Y / edit]   (skip not allowed for init sections)
     ```
     User confirms or edits. Write confirmed section to file. Repeat for each init_section. **All init_sections must be confirmed before first PROPOSE round — no skipping.**
   - After init_sections confirmed (or if profile has none) → first PROPOSE round.
   - Validation checks are NOT called until after the first propose round.
4. **Resume:** read existing data file, show status:
   ```
   Resuming: 15 confirmed, 0 open.
   Continuing...
   ```

### PROPOSE

Delegate to proposer subagent. Read the proposer SKILL.md from the path in profile `proposer.ref`. Launch subagent with:
- The proposer's SKILL.md as prompt
- Model: **opus** (use the most capable model for proposal generation)
- Pass: data file path, count, constraints from profile
- If profile has `input` section (e.g. `input.requirements`) → pass those file paths to the subagent as well

The subagent returns proposed items as **readable text**.

You do NOT generate items yourself.

**NEVER run proposer and validation checks in parallel. Always sequential:**

1. Run validation checks FIRST. Wait to finish. Show fixes to user. User resolves. Write fixes to file.
2. ONLY THEN run proposer on the **updated** file (after fixes written). Show proposals. User confirms. Write to file.

Why: proposer must read the file AFTER fixes are applied. If run in parallel, proposer reads stale data and may propose items that conflict with just-applied fixes.

For presentation format, interaction rules, skip/rewrite/deferred handling — see `references/batch-protocol.md`.

**Data file is markdown.** When writing confirmed items, use the format from `references/format-items.md`. Confirmed items change `→` to `✓`. Purpose and Glossary are written as document sections (`## Purpose`, `## Glossary`), not as FR/NFR items.

**Detail files (tree format only).** When writing a confirmed decision:
1. Write the tree node with a **clickable link**: `[[details]](details/AD-NNN-slug.md)` — relative to tree file.
2. Create the detail file at `details/AD-NNN-slug.md` (e.g. `details/AD-001-contract-split.md`) using the template from `validate-architecture/rules/details-template.md`. Include at minimum: Context (which requirements), Decision (one paragraph), Alternatives (≥2 with rejection reasons). Add Consequences, Assumptions, Formula, Edge Cases when provided by proposer or user.

**Placement:** when writing items to file, place them near related items (same group, same topic). For tree format, place child decisions under their parent. Use context from proposer's output to determine where each item belongs.

### VALIDATE

Launch validator check subagents directly. Profile lists checks with their rule files and when to run.

**after_batch** (every round):
- Launch each `when: after_batch` check as a separate subagent (check file + rules files + data file)
- Model: **opus**
- If profile has `input` section → pass those file paths too
- **Show ERROR and WARNING** to user. INFO → accumulate silently for before_done.
- If no ERROR/WARNING → skip fixes, go straight to proposer.

**before_done** (checkpoint — when proposer exhausted or user triggers):
- Launch ALL checks as **parallel** subagents
- Collect all results
- Show sorted by severity: ERROR first, then WARNING, then INFO
- Issues must include full item text for context

```
[Checkpoint validation] 5 issues:

1. ✗ FR-003: "System charges fee on yield accrued since last collection"
   → Rewrite: "Fee charged only on net positive gains"
   Fix? [Y/skip/edit]

2. ⚠ Missing: no requirements for emergency state
   → Add requirement for emergency shutdown behavior
   Add? [Y/skip]

3. ℹ Grouping: related items far apart
   → Reorder? [Y/skip]
```

### DoD Evaluation

After `before_done` validation:
- Check DoD criteria from profile
- If all met → suggest finish:
  ```
  DoD met. No errors, proposer exhausted.
  Finish? [Y / continue / run on_ready]
  ```
- If not → show what's missing, continue PROPOSE

### GENERATE (on_ready)

If profile defines `on_ready` and user chooses to run it:
- Dispatch the referenced skill (`on_ready.ref`) as a subagent with:
  - `{{DATA_FILE}}` (the tree or data file)
  - `{{REQUIREMENTS_FILE}}` (if profile has `input.requirements`)
  - `{{ANTIPATTERNS_URL}}` (if profile defines it)
  - `{{PROFILE}}` = `on_ready.profile` (if set — used by on_ready skills that support multiple domains, e.g. `project-architecture` with `solidity` / `python-library`)
  - Any other fields from the `on_ready:` block as placeholders for the on_ready skill
  - The orchestrator of the on_ready skill handles its own internal subagent dispatch — gather does not manage individual stages.
- The on_ready skill returns two sections:
  - **Proposed items** — in the data file's current format (the same format a proposer would use). The meaning of these items is profile-specific — e.g. for architecture profiles they are `?` tree gaps, for requirements profiles they could be additional FR/NFR/C/R items.
  - **Notes** (optional) — informational observations the user should see but that do NOT enter the batch. Shown after proposed items for context.
- Present **only proposed items** via batch protocol (same as PROPOSE). Notes are displayed to the user as informational context — not added to the batch, not written to the data file.
- User confirms/skips each proposed item. Confirmed items → written to the data file → PROPOSE continues with them.
- If on_ready returns no proposed items (only notes or empty) → display notes if any, then finish.

## Rules

- **Orchestrator writes the data file.** Proposer and check subagents read it and return suggestions — they never write directly.
- **Nothing confirmed without user seeing it.** Every item must be presented and accepted before `✓`.
- **Never write before user responds.** Show the batch, wait for user's answer, THEN write confirmed items. Proposed items exist only in the conversation until user confirms.
- **Rewrites require re-approval.** If user gives feedback that changes the text of an item (e.g. "reformulate X as risk", "rewrite without HOW"), show the rewritten version first and wait for explicit confirmation. Do NOT rewrite and record in one step — the user must see the final text before it's written. Even if the user's intent is clear, the rewritten formulation may not match what they expected.
- **Track repeat issues.** Skipping Validated items is the **validator's** responsibility (see quality-rules.md / completeness-criteria.md "Validated Items — Skip Rule"). Gather does NOT duplicate this logic. If a validator re-raises a flag on an item that has an existing Validated annotation that appears related to the same concern (no precise matching needed — just check if the item has any Validated annotation that looks like it covers the flagged issue), report to the user: "FR-010 was flagged again despite existing Validated annotation — validator may have missed it. Options: keep existing validation / accept the fix / edit the annotation." If user rejects → update or add `**Validated:**` annotation per `batch-protocol.md`. Gather's role: (1) record annotations when user rejects a flag, (2) remove annotations when item content changes (title/body/AC), (3) surface repeat flags to user.
- **Write before discuss.** Same as q-tree batch protocol: write confirmed items before addressing follow-ups.
- **Propose, don't interview.** Proposer returns concrete items, not open-ended questions. User confirms, edits, or skips.
- **Respect profile constraints.** Pass constraints to proposer and check subagents.
- **Log progress:** `[Round N] Confirmed: X | Proposed: Y` after each batch.

## Session Log

After every batch interaction, log round data: what was proposed/fixed, what user confirmed/skipped. Sequential round numbering.

## Placeholders

| Placeholder | Source | Default |
|-------------|--------|---------|
| `{{DATA_FILE}}` | `--output` > derived from requirements dir > profile output.data_file | profile-dependent |
| `{{INPUT_FILE}}` | same as `{{DATA_FILE}}` — used by check files | profile-dependent |
| `{{LOG_FILE}}` | `<dirname({{DATA_FILE}})>/<basename from profile.output.log_file>` | profile-dependent |
| `{{COUNT}}` | `--count` > profile proposer.count | 5 |
| `{{CONSTRAINTS}}` | profile constraints | empty |
| `{{REQUIREMENTS_FILE}}` | `--input-requirements` > profile input.requirements | empty (not all profiles need it) |
| `{{ANTIPATTERNS_URL}}` | profile antipatterns_url | empty (skip anti-pattern fetch) |
