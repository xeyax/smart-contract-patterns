# Quality Rules

Apply to every individual requirement. Used by proposer (as generation guide) and validator (as check).

## 0. Plain Language, Essential Only

Write for humans, not for parsers. Focus on what matters — the core capability or constraint.

- Bad: "Authorized operator can trigger emergency deleveraging when health factor drops below threshold, executable even when paused, only operator role"
- Good: "System can unwind leveraged position in emergency to protect depositor funds"

- Bad: "No withdrawal may increase loss exposure per unit of remaining depositors' ownership"
- Good: "When someone withdraws, remaining depositors don't lose value"

**What to keep vs what to drop:**
- Keep **triggers** described as observable outcomes: "in emergency", "when position is at risk"
- Drop **mechanisms**: specific thresholds ("health factor < 1.2"), specific roles ("operator"), specific timing ("within 60 seconds")
- Keep **conditions** that define WHEN the requirement applies, stated as outcomes not mechanisms
- Drop **conditions** that describe HOW to detect the trigger

Test: could a non-technical stakeholder understand this in one read? If not → simplify.

## 1. WHAT not HOW

Test: "could this be implemented differently while satisfying the same need?" If yes → it's WHAT (keep). If text names a specific approach → rewrite.

Forbidden:
- Formulas (`shares = assets * totalSupply / totalAssets`)
- Mechanism/pattern names: HWM, TWAP, share dilution, merkle tree, commit-reveal, snapshot
- Function signatures (`deposit(uint256)`)
- Contract/variable names (`feeReceiver`, `highWaterMark`, `VaultCore`, `ReentrancyGuard`)
- Specific ordering ("X before Y" when alternatives exist)
- Technical mechanisms ("emit event", "use oracle", "call function Z")
- Contract decomposition details ("handlers have zero state", "all state lives in X")
- Data structures ("internal enum IDs", "hardcoded allowlist")
- Library/framework names ("OpenZeppelin", "ReentrancyGuard", "AccessControl")
- Specific role names when the role model is not yet decided ("operator can...", "keeper triggers..."). Use "authorized role" or "the system" instead. WHO can do it = architecture. WHAT can be done = requirement.

Instead of ordering → describe invariant ("must not expose remaining depositors to risk")
Instead of mechanism → describe outcome ("provides observable signal")
Instead of technical mitigation → describe what must not be possible ("not exploitable via single-tx price manipulation")
Instead of specific role → describe capability and access level ("restricted operation that reduces leverage" not "operator triggers deleveraging")

OK: standard names as compliance targets ("ERC-4626 compliant" is WHAT — compliance target, not mechanism)

Examples (bad → good):
- "BTC debt closed before GM returned" → "Withdrawal must not increase liquidation risk for remaining depositors"
- "Vault emits event when drift exceeds threshold" → "System provides observable signal when position drift exceeds configured threshold"
- "Must not use spot AMM price" → "System must not be exploitable via single-transaction price manipulation"
- "Fees owed to the vault are included in NAV" → "Share price reflects all applicable fees at the moment of any operation"
- "Handler contracts have zero mutable state, all state in VaultCore" → "System state is centralized and consistent" (contract decomposition = architecture)
- "Hardcoded swap routes only" → "System uses only predefined, audited token conversion paths" (implementation detail)
- "Share calculation uses pre-deposit snapshot" → "Depositor's share allocation not affected by price changes between initiation and completion" (specific mechanism)
- "ReentrancyGuard on all handlers" → "System prevents reentrancy on all state-changing entry points" (library name)
- "Shares frozen on VaultCore" → "Shares in pending withdrawal cannot be transferred or used" (contract name + mechanism)

## 2. No Vague Terms

Never use: flexible, easy, adequate, sufficient, fast, reliable, scalable, intuitive, user-friendly, safe, robust, efficient, seamless, appropriate, reasonable, minimal, optimal, modern, simple, clean.

Always quantify: "fast" → "< 200k gas", "minimal" → "< 0.1% deviation".

## 3. Singular

One item = one requirement. No "and" combining two different capabilities.
- OK: "deposit assets and receive shares" (one action with its result)
- Not OK: "deposit assets and track referrals" (two capabilities → split)

Split test: "could these parts be decided independently?" If they always happen together as one user flow → keep together. Only split if they can exist or change independently.
- "Cancel raffle and refund participants" → keep together if refund ALWAYS follows cancellation
- "Deposit and track referrals" → split, because deposit works without referrals

## 4. Acceptance Criteria

Every FR should have ≥2 acceptance criteria when the requirement has meaningful edge cases or failure modes: happy path + edge case or negative case.

For simple invariant-style items (NFR, C, or FR where one criterion fully covers the behavior) — one clear pass/fail criterion is sufficient. Don't invent artificial criteria to hit a number.

Criteria describe observable outcomes, not internal mechanics.
- Good: "Full redeem → user share balance becomes zero"
- Good: "After any operation → all allowances == 0" (one criterion, fully covers it)
- Bad: "shares = assets * totalSupply / totalAssets" (formula = HOW)

For complex FR: include happy path, edge cases (zero, first, max), negative cases (→ reverts).

## 5. Verifiable

Every item must be testable. If you can't imagine a concrete pass/fail test → underspecified.

Performance/constraint items must have numbers, not adjectives.

## 6. Self-Contained

Requirement understandable without reading heading or surrounding context.

No pronouns without antecedent, no "the above", no "as mentioned".

## 7. Conditions Explicit

No "when appropriate", "if needed", "under normal conditions" — conditions must be stated as observable triggers.

- Good: "in emergency" (observable state)
- Good: "when position is at risk of external liquidation" (observable outcome)
- Bad: "when health factor < 1.2" (specific threshold = architecture)
- Bad: "when appropriate" (undefined)

## 8. Not Redundant

No duplicates or subsets of existing items. Check text AND acceptance criteria against all existing items.

Same risk described twice with different wording → merge.

Severity: WARNING (not INFO). Duplicates diverge on edit and cause confusion.

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

When flagging an issue, suggest a **complete rewrite** of the full item text (title + body + acceptance criteria) — never a word-level patch ("change X to Y"). The rewrite must be final: if it were accepted as-is, the same validator running again must NOT flag it again.

Before proposing a rewrite:
1. Write the full replacement text
2. Re-check it against ALL 11 rules above
3. If it fails any rule → rewrite again
4. Only propose when the text passes all rules

If an item was flagged in a previous round and the fix didn't stick → the previous rewrite was insufficient. Write a completely new version from scratch based on the original intent, not from the failed rewrite.
