# Batch 10 Findings

Dry-run analyses were run against the final 2 source candidates discoverable from the current DefiLlama top-300 source map.

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Firelight | `firelight-protocol/firelight-core` | `74351b1` | ERC-4626-style vault, delayed withdrawals, regulated share controls |
| Reserve Protocol | `reserve-protocol/staking-contract` | `8fe57f8` | ERC-4626 staking vaults, multi-reward indexes, reward streaming |

## Accepted Catalog Updates

- Added `patterns/rewards/risk-reward-token-accrual-dos.md` for multi-reward vaults where bad external reward tokens can block normal user actions.
- Updated lazy reward indexes with high-precision scalar and zero-supply accrual carry-forward/recovery guidance.
- Updated queued reward streaming with instant-payout flash-deposit risk.
- Updated virtual share offsets with donation-griefing and missing-zero-share-check caveats.
- Updated participant permission guidance with regulated vault-share endpoint checks and frozen-account claim-ledger rescue semantics.
- Updated async withdrawal guidance with fixed-entitlement delayed withdrawals, pending-asset reservation, and epoch-calendar update caveats.

## Rejected Or Merged Candidates

- Firelight's delayed withdrawal flow was merged into existing async withdrawal docs instead of becoming a standalone pattern.
- Firelight pause behavior was not added because pausing deposits, withdrawals, and claims is already covered by `Pause Traps Funds`.
- Firelight historical snapshot functions were rejected for now because no strong downstream invariant or reusable protocol pattern was found.
- Reserve's chained ERC-4626 router was rejected as a standalone pattern because it overlaps existing vault composability and router guidance.
- Reserve's direct reward-token donation behavior was merged into existing reward-balance accounting caveats.

## Contradiction Review

- Firelight is not evidence that request-time async withdrawals eliminate timing arbitrage; it is evidence for fixed claim ledgers and pending-asset reservation.
- Firelight blocklisting is not a launch transfer gate; it is a regulated vault-share custody exception with explicit `Permissioned Exit Custody` risks.
- Virtual share offsets are framed as making donation attacks unprofitable, not as eliminating all donation griefing.
- Reserve instant reward payout is framed as unsafe for externally triggerable rewards unless same-transaction entry and claim are prevented.

## Verification

- Both source repositories were inspected by dry-run subagents using `skills/harvest-patterns/SKILL.md`.
- Existing catalog docs, `patterns/INDEX.md`, and `ANTIPATTERNS.md` were compared before accepting updates.
- Full catalog index regeneration and staged markdown validation were run before commit.
