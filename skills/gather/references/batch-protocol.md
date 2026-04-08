# Batch Protocol

Universal rules for presenting items to the user and collecting responses. Applies to both PROPOSE batches and VALIDATE issues.

## Present

Show items as a numbered list with a round header:

```
[Round N] K items from [source]:

1. [item]
2. [item]
3. [item]

Accept all? [Y / numbers to edit / skip N]
```

Source examples: "proposer (goal decomposition)", "validator (quality check)", "validator (completeness)".

Rule: **Show EVERY item before it can become ✓.** Nothing is confirmed without the user seeing it first.

Rule: **Fixes and proposals are separate batches.** If validator found issues → show fixes first, resolve them. Only then show new proposals. Never mix fixes and proposals in one batch.

### Proposed Items Format

Show as readable text, not yaml. Group related items visually:

```
N. → [TYPE] Title or short text
   Priority: Must | Group: Core Vault
   Rationale: why this is needed
   Acceptance:
   - criterion 1
   - criterion 2
   Risks: R-NNN (if applicable)
```

For risks:
```
N. → [R] Risk title
   Priority: Must
   Mitigation: what system must prevent (or "accepted")
```

### Validation Issues Format

Fixes are shown as a separate batch before proposals. Include full requirement text:

```
[Round N — fixes]

1. ⚠ FR-003: "System charges fee on yield accrued since last collection"
   → Rewrite: "Fee charged only on net positive gains"
   Fix? [Y/skip/edit]
```

Icons: ✗ = ERROR, ⚠ = WARNING, ℹ = INFO.

## Collect — write first, then discuss

Process items until ALL are resolved or skipped, then exit. On every user response:

### Step 1: PARSE

Parse the response. A single message may contain accepts, edits, skips, AND discussion. Separate decidable from discussion.

Only explicitly addressed items are resolved. **Items not mentioned stay pending.** Never assume silence = acceptance.

### Step 2: WRITE — before anything else

**Write ALL confirmed items to data file NOW.** Update counters.

For proposed items: user accepts → change `→` to `✓`, write to file.
For validation fixes: user accepts fix → apply change to existing item.
For suggested new items from validator: user accepts → write as `✓`.

**Placement:** each item has a `placement` field from the proposer/validator:
- `placement.after: ID` → insert after that item in the file
- `placement.group: "name"` → append to that group
- `placement.parent: "AD-NNN"` → insert as child (tree format only)
- No placement → append at end (items format) or ask user (tree format)

This step is non-negotiable. Even if one item needs discussion, all other confirmed items must be written first.

### Step 3: RESPOND

Only after writing:
- Remaining pending items > 0 → show them
- User wants to discuss/edit → handle inline
- All resolved or skipped → exit to next phase (VALIDATE after PROPOSE, PROPOSE after VALIDATE)

**Edits.** If user says "change 3 to [new text]" and provides exact text → write to file with `✓`.

**Rewrites.** If user gives feedback that requires reformulation ("make it more high-level", "rewrite as risk", "remove HOW details") → show the rewritten version and wait for confirmation before writing. Never rewrite + record in one step.

**Skips.** Two types:
- **Skip without reasoning** ("skip 3") → not written. May reappear in future rounds.
- **Skip with reasoning** ("skip 3, not sure if needed because depends on epoch design") → written as `?` (deferred) with the reasoning. See below.

**User reasoning on rejected/skipped items.** When user rejects or skips an item AND provides reasoning, this reasoning is valuable context. Record it:
- **Override with alternative:** record as the user's version (show for re-approval), with the original proposal as a rejected alternative in details.
- **Partial accept with uncertainty:** record the decision with the uncertainty noted in Assumptions section of details ("Dolomite oracle may not provide needed prices — TBD").
- **Conditional skip with reasoning:** record as `?` (open question) with the user's reasoning as context. Don't lose the reasoning — it feeds future decisions.

Never discard user reasoning. Skip with reasoning = deferred item, not a silent drop.

**Format per data type:**
- **Tree:** `?` node with reasoning in Details under Assumptions/Context section.
- **Items:** `?` status item with `**Deferred:**` field containing user's reasoning and dependency if any. Item stays in the list — proposer sees it and won't re-propose. Validator can flag: "FR-012 deferred since Round 1, blocking decision AD-005 now resolved — revisit?"

## Log

Every batch interaction is a loggable round. After items are resolved, dispatch session-logger (background) with:
- Round number (sequential across all PROPOSE and VALIDATE rounds)
- What was presented (numbered list)
- User response (verbatim or close paraphrase)
- What was recorded (items written / issues fixed)
