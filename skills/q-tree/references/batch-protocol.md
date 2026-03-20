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

## Collect — parse, write, loop

Process items until ALL are resolved or skipped, then exit. On every user response:

1. **Parse** the response as a whole. A single message may address some items and ignore others.
2. **Match each part of the response to specific item numbers.** Only items explicitly addressed (accepted, overridden, skipped) are resolved. **Items not mentioned stay pending.**
3. **Write immediately.** Every confirmed answer, override, or skip → write to tree file now. Never hold confirmed items in memory across exchanges.
4. **Route:**
   - All items resolved or skipped → exit.
   - Remaining items > 0 → show remaining unanswered with a brief reminder:
     ```
     Recorded 1, 3. Remaining:
     2. [item text]
     Accept? [Y / override / skip]
     ```
   - Phase-specific routing (decomposition in EXPAND, etc.) — see phase rules.

**Critical rule: if user answered K out of N items, only K are recorded. The other N-K are shown again.** Never assume silence = acceptance.

## Log

Every batch interaction is a loggable round. After items are resolved, dispatch session-logger (background) with:
- What was presented (numbered list)
- User response (verbatim or close paraphrase)
- What was recorded (markers written to tree)
- Phase-specific results (check findings, readiness, etc.)

This applies to ALL phases — not just EXPAND rounds. CHECK findings, SUMMARIZE gaps, REVIEW gaps are all logged as rounds with sequential numbering.
