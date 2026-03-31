# Quality Rules

Apply to every individual requirement. Used by proposer (as generation guide) and validator (as check).

## 1. WHAT not HOW

Test: "could this be implemented differently while satisfying the same need?" If yes → it's WHAT (keep). If text names a specific approach → rewrite.

Forbidden:
- Formulas (`shares = assets * totalSupply / totalAssets`)
- Mechanism/pattern names: HWM, TWAP, share dilution, merkle tree, commit-reveal
- Function signatures (`deposit(uint256)`)
- Contract/variable names (`feeReceiver`, `highWaterMark`)
- Specific ordering ("X before Y" when alternatives exist)
- Technical mechanisms ("emit event", "use oracle", "call function Z")

Instead of ordering → describe invariant ("must not expose remaining depositors to risk")
Instead of mechanism → describe outcome ("provides observable signal")
Instead of technical mitigation → describe what must not be possible ("not exploitable via single-tx price manipulation")

OK: standard names as compliance targets ("ERC-4626 compliant" is WHAT — compliance target, not mechanism)

Examples (bad → good):
- "BTC debt closed before GM returned" → "Withdrawal must not increase liquidation risk for remaining depositors"
- "Vault emits event when drift exceeds threshold" → "System provides observable signal when position drift exceeds configured threshold"
- "Must not use spot AMM price" → "System must not be exploitable via single-transaction price manipulation"
- "Fees owed to the vault are included in NAV" → "Share price reflects all applicable fees at the moment of any operation"

## 2. No Vague Terms

Never use: flexible, easy, adequate, sufficient, fast, reliable, scalable, intuitive, user-friendly, safe, robust, efficient, seamless, appropriate, reasonable, minimal, optimal, modern, simple, clean.

Always quantify: "fast" → "< 200k gas", "minimal" → "< 0.1% deviation".

## 3. Singular

One item = one requirement. No "and" combining two different capabilities.
- OK: "deposit assets and receive shares" (one action with its result)
- Not OK: "deposit assets and track referrals" (two capabilities → split)

## 4. Acceptance Criteria

Every FR must have ≥2 acceptance criteria: one happy path + one edge case or negative case.

Criteria describe observable outcomes, not internal mechanics.
- Good: "Full redeem → user share balance becomes zero"
- Bad: "shares = assets * totalSupply / totalAssets" (formula = HOW)

Include: happy path, edge cases (zero, first, max), negative cases (→ reverts).

## 5. Verifiable

Every item must be testable. If you can't imagine a concrete pass/fail test → underspecified.

Performance/constraint items must have numbers, not adjectives.

## 6. Self-Contained

Requirement understandable without reading heading or surrounding context.

No pronouns without antecedent, no "the above", no "as mentioned".

## 7. Conditions Explicit

No "when appropriate", "if needed", "under normal conditions" — conditions must be stated explicitly.

## 8. Not Redundant

No duplicates or subsets of existing items. Check text AND acceptance criteria against all existing items.

Same risk described twice with different wording → merge.

## 9. Not Trivial

No platform guarantees stated as requirements ("transactions are atomic", "integer overflow prevented" for Solidity 0.8+).

No tautologies. No obvious consequences of another item that add no new testable information.

## 10. Quantified

Performance and constraint requirements must have specific numbers.

"Low latency" → specify ms. "Minimal gas" → specify max gas. "High availability" → specify uptime %.

## 11. Status & Type Complete

Every item has: status (✓/→/?), priority (Must/Should/Could), type (FR/NFR/C/R).

No TBD/TBR/TBS terms — resolve or flag.

## Validator: Suggest Complete Rewrites

When flagging an issue, suggest a **complete rewrite** of the full item text — not a word patch. Verify your own suggestion passes ALL rules above before proposing it.
