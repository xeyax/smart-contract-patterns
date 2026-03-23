# Batch Protocol

Universal rules for presenting items to the user and collecting responses. Applies to ALL batch interactions: EXPAND questions, CHECK issues, SUMMARIZE gaps, REVIEW gaps.

## Present

Show items as a numbered list with a round header and accept prompt:

```
[Round N] K items from [source]:

1. [item]
2. [item]
3. [item]

Accept all? [Y / numbers to change / skip N]
```

Source examples: "decomposing Access Control", "consistency check", "summarizer gaps", "review gaps".

Rule: **Show EVERY item before it can become ✓.** Nothing is confirmed without the user seeing it first.

## Collect — write first, then discuss

Process items until ALL are resolved or skipped, then exit. On every user response, follow this order strictly:

### Step 1: PARSE

Parse the response as a whole. A single message may contain answers, overrides, skips, AND follow-up questions or discussion. Separate them: what is decidable now vs what needs discussion.

Only items explicitly addressed (accepted, overridden, skipped) are resolved. **Items not mentioned stay pending.** Never assume silence = acceptance.

### Step 2: WRITE — before anything else

**Write ALL confirmed/resolved items to tree file NOW.** Update counters. This happens before any discussion, follow-up, or next batch.

Also write new `?` nodes when the user raises a design question not yet in the tree (e.g. "what if the oracle goes down?"). Factual questions ("what is TWAP?") → answer inline, no node. Design uncertainty → `?` node under the relevant parent.

This step is non-negotiable. Even if one item needs discussion, all other confirmed items must be written first.

### Step 3: RESPOND

Only after writing, address the rest:
- Remaining pending items > 0 → show them:
  ```
  Recorded 1, 3. Remaining:
  2. [item text]
  Accept? [Y / override / skip]
  ```
- User asked for details / wants to dig in → discuss (phase-specific routing, see expand-rules.md)
- All items resolved or skipped → exit to next phase

**Dismissed items.** If an item resolves as "not needed / removed / follows from X" — don't create a new node. Merge the dismissal into the existing related node's answer and Details. One decision = one node.

## Log

Every batch interaction is a loggable round. After items are resolved, dispatch session-logger (background) with:
- What was presented (numbered list)
- User response (verbatim or close paraphrase)
- What was recorded (markers written to tree)
- Phase-specific results (check findings, readiness, etc.)

This applies to ALL phases — not just EXPAND rounds. CHECK findings, SUMMARIZE gaps, REVIEW gaps are all logged as rounds with sequential numbering.
