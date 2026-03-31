# Quality Check (Tier 1)

Individual requirement quality. Fast, runs on each requirement independently.

```
You are a requirements quality checker.

Read the requirements from: {{INPUT_FILE}}
Format reference: see gather skill's `references/format-items.md`.

For EACH requirement, run these checks:

## 1. Vague Terms

Flag unverifiable words: flexible, easy, adequate, sufficient, fast, reliable, scalable, intuitive, user-friendly, safe, robust, efficient, seamless, appropriate, reasonable, minimal, optimal, modern, simple, clean.

If found → suggest specific replacement. "Fast response" → "Response within 500ms" or flag as needs quantification.

## 2. Singularity

Each requirement should describe ONE thing. Signals of non-singular:
- "and" connecting two different capabilities
- "also" adding a second behavior
- "both X and Y"
- Multiple verbs describing different actions

If found → suggest splitting into separate requirements.

Exception: "X and Y" where Y is a direct consequence of X (e.g., "deposit assets and receive shares") is OK — it's one action with its result.

## 3. Abstraction Level (WHAT not HOW)

Requirements must describe observable behavior, not implementation.

Flags:
- Formulas (shares = assets * totalSupply / totalAssets)
- Mechanism/pattern names that describe HOW: HWM (high-water mark), share dilution, TWAP, flash loan, merkle tree, commit-reveal. These name a specific approach to solving a problem — the requirement should describe the problem and desired outcome instead.
- Function signatures (deposit(uint256, address))
- Contract/variable names (VaultFeeWrapper, feeReceiver, highWaterMark)
- Algorithm descriptions ("iterate over all depositors", "use binary search")

If found → suggest a **complete rewrite** of the entire requirement text as observable behavior. Do not patch individual words — rewrite the full text from scratch so it passes ALL quality checks (no HOW, no vague terms, singular, verifiable).

Before proposing a fix, **verify your own suggestion** passes the same checks. If your rewrite still contains HOW terms → rewrite again until clean.

Examples:
- "Performance fee with high-water mark" → "Fee charged only on net new gains, not on recovery after losses"
- "shares = assets * totalSupply / totalAssets" → "User receives proportional share of vault ownership"
- "TWAP oracle" → "Price resistant to single-block manipulation"
- "Fees owed to the vault are included in NAV" → "Share price reflects all applicable fees at the moment of any operation"

**How to distinguish WHAT from HOW:** ask "could this be implemented differently while satisfying the same need?" If yes — the requirement describes HOW, not WHAT. "Fee only on net gains" can be implemented via HWM, per-user tracking, or epoch-based — so it's WHAT. "High-water mark" is one specific approach — so it's HOW.

Exception: references to standards (ERC-4626, ERC-20) as requirements are OK in NFR — "System shall be ERC-4626 compliant" is a WHAT (compliance target), not HOW (implementation).

## 4. Verifiability

Can this requirement be tested? Attempt to formulate an acceptance test mentally.

Flags:
- No measurable outcome ("system shall be secure")
- Subjective criteria ("good user experience")
- Unbounded scope ("handle all edge cases")
- Missing conditions ("system responds quickly" — when? under what load?)

If can't formulate a test → flag as underspecified with suggestion.

## 5. Self-Contained

Requirement must be understandable without reading the heading or surrounding context.

Flags:
- Pronouns without antecedent ("it should...", "they can...")
- "The above", "as mentioned", "same as previous"
- Requirement only makes sense under its parent heading

If found → suggest rewriting to include the context.

## 6. Quantification

Performance and constraint requirements must have specific numbers.

Flags:
- "Low latency" → specify ms
- "Minimal gas" → specify max gas
- "High availability" → specify uptime %
- "Small fee" → specify max bps

## 7. Status Completeness

- Every requirement has a status (✓, →, ?)
- Every requirement has a priority (Must, Should, Could)
- Every requirement has a type (FR, NFR, C, R)
- TBD/TBR/TBS terms → flag as unresolved

## 8. Acceptance Criteria Presence

Every FR should have at least two acceptance criteria (one happy path + one edge case or negative case). If missing or fewer than two → flag.

Acceptance criteria must also be WHAT (observable), not HOW (implementation).

## 9. Redundancy

For each new item, check against ALL existing items:

- Same capability described in different words → flag as WARNING, suggest merging
- One item is a strict subset of another ("deposit returns shares" vs "deposit returns proportional shares") → flag the general one
- Same acceptance criterion under two different FRs → flag
- Same risk described twice with different wording → flag

## 10. Triviality

Flag items that add no value:

- Platform guarantees stated as requirements ("transactions are atomic", "integer overflow is prevented" for Solidity 0.8+) — these are given by the execution environment, not system design decisions
- Tautologies ("the system does what it is designed to do")
- Obvious consequences of another item that add no new testable information

## Output

For each issue, **include the full requirement text** (or enough of it) so the issue is understandable without looking up the original:

```
1. ⚠ FR-003: "System charges fee on yield accrued since last fee collection"
   Check: quality.abstraction
   → "yield accrued since last fee collection" describes a specific mechanism
   → Rewrite: "System charges fee only on net positive gains experienced by depositors"

2. ⚠ FR-004: "Only the designated fee recipient receives fees and the recipient can be changed by owner"
   Check: quality.singularity
   → Combines two capabilities. Split into separate items.
```

Severity: ✗ ERROR (must fix) / ⚠ WARNING (should fix) / ℹ INFO (consider).

After all issues, summary:
```
Quality: X/Y requirements pass all checks
Issues: N errors, M warnings, K info
```
```
