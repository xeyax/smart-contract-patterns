# Decision Quality Rules

Apply to every individual architecture decision. Used by proposer (as generation guide) and validator (as check).

## 1. Decision is a HOW

Architecture decisions describe HOW to achieve a requirement — specific approach, mechanism, pattern. This is the opposite of requirements (which describe WHAT).

Test: does this decision name a **concrete approach** that could be swapped for a different approach while still satisfying the same requirement? If yes → it's a valid architecture decision.

- Good: "Global HWM via share dilution" — names specific mechanism
- Bad: "System charges fee only on net gains" — this is a requirement (WHAT), not a decision (HOW)

Every decision must trace to at least one requirement (FR/NFR/R/C).

## 2. Alternatives Documented

Every decision must have ≥2 alternatives considered (including the chosen one). Each alternative has:
- What it is (one sentence)
- Why rejected or chosen (concrete reason, not "too complex")

Decisions with only one option → either it's not really a decision (it's a constraint) or alternatives weren't explored.

## 3. Consequences Stated

Every decision has consequences — both positive and negative. Trade-offs must be explicit.

- Good: "Late depositor free-ride accepted (standard in Yearn, Enzyme)"
- Bad: no consequences section, or only positive consequences listed

## 4. No Vague Terms

Same list as requirements: flexible, easy, adequate, sufficient, fast, reliable, scalable, intuitive, user-friendly, safe, robust, efficient, seamless, appropriate, reasonable, minimal, optimal, modern, simple, clean.

Quantify: "low gas" → "< 200k gas per deposit".

## 5. Singular

One decision per item. "Use global HWM and share dilution" → could be two decisions (HWM granularity + fee collection mechanism).

Test: could the two parts be decided independently? If yes → split.

## 6. Assumptions Explicit

If the decision depends on something being true that isn't guaranteed → state as assumption.

- "Base vault PPS is accurate" → assumption (what if oracle lag?)
- "Only owner holds base shares" → assumption (what if compromised?)

Assumptions feed into trust-assumptions artifact.

## 7. Context Provided

Every decision has context: why is this decision needed? What requirement drives it?

No context → unclear if the decision is necessary.

## 8. Not Redundant

No duplicate decisions. No decision that is a direct consequence of another (derivable without new information).

## 9. Formulas Verifiable

If a decision includes a formula → it must be complete (all variables defined) and consistent with other decisions' formulas.

## 10. ID Assigned

Every decision has a unique ID: AD-NNN (Architecture Decision). Sequential numbering.

## 11. Title = Topic → Choice

Decision title must contain BOTH the **topic** (what problem/question is being decided) AND the **choice** (what was chosen). The reader should understand the decision from the title alone, without opening the detail file.

Format: `AD-NNN: <topic> → <choice>` or `AD-NNN: <topic> — <choice>`.

- Good: `AD-004: Parallel execution → multiprocessing.Pool (not threading — GIL)`
  - Topic: "parallel execution" — what is being decided
  - Choice: "multiprocessing.Pool" — what was chosen, with hint why
- Good: `AD-009: Cost model contract → Protocol-based pluggable interface`
- Good: `AD-011: Survivorship bias → out of scope, R-002 accepted`
- Bad: `AD-004: Multiprocessing Pool for Parallel Strategy Runs` — only the choice, no topic
- Bad: `AD-009: Cost Model Interface` — only the topic, no choice
- Bad: `AD-004: How to parallelize` — only the topic as a question

The title is a **compressed ADR**: topic is the "what question", choice is the "what we decided". Together they let a reviewer scan the tree and understand all decisions without clicking through.
