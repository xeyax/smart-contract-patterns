# Clarity Trait Cohort Validation

> Validate a caller-supplied cohort of trait-typed Clarity contracts by checking each contract identity against configured roles before using the cohort.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Platform | clarity |
| Tags | access-control, clarity, traits, account-validation, lending |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A Clarity entrypoint receives trait-typed token, oracle, or wrapper contracts
- The protocol stores the expected contract identity for each asset role
- Several same-type contracts must be validated together before accounting
- Incorrect pairing could make a health, collateral, or liquidation check read the wrong asset

## Avoid When

- Contract identities are fixed in code and not caller supplied
- The trait type alone is sufficient because only one implementation can be valid
- The cohort is used only for display and not for value-bearing state changes

## Trade-offs

**Pros:**
- Preserves Clarity trait flexibility without trusting arbitrary implementers
- Prevents same-type account substitution
- Makes asset, zToken, and oracle pairings explicit

**Cons:**
- Adds repetitive validation logic
- Incorrect configuration can reject legitimate flows
- Callers must supply the full expected cohort

## How It Works

Trait typing proves shape, not role. After accepting trait parameters, compare `contract-of` identities against reserve configuration:

```clarity
(define-public (borrow
  (asset <ft-trait>)
  (z-token <ft-trait>)
  (oracle <oracle-trait>)
  (assets (list 100 { asset: <ft-trait>, lp-token: <ft-trait>, oracle: <oracle-trait> })))
  (let ((reserve (try! (get-reserve-state (contract-of asset)))))
    (try! (validate-assets assets))
    (asserts! (is-eq (contract-of z-token) (get a-token-address reserve)) ERR_INVALID_Z_TOKEN)
    (asserts! (is-eq (contract-of oracle) (get oracle reserve)) ERR_INVALID_ORACLE)
    ;; value-bearing accounting follows
    (ok true)))
```

## Implementation

```clarity
(define-read-only (validate-assets
  (assets (list 100 { asset: <ft-trait>, lp-token: <ft-trait>, oracle: <oracle-trait> })))
  ;; enforce expected order, uniqueness, and configured pairings
  (ok true))
```

### Key Points

- Validate every same-type role before reading balances or prices.
- Preserve semantic names through execution so variables do not get swapped.
- Add negative tests that pass a valid trait implementation in the wrong role.
- Keep display-only read helpers separate from value-bearing validation paths.

## Source Evidence

- Zest Protocol `pool-borrow.clar` validates trait-supplied assets, zTokens, and oracles against reserve state before supply, withdraw, borrow, and liquidation-sensitive actions in [`onchain/contracts/borrow/production/pool/pool-borrow.clar`](https://github.com/Zest-Protocol/zest-contracts/blob/3564bc38906e464ec4de774122bb9bbaee20ddc6/onchain/contracts/borrow/production/pool/pool-borrow.clar).
- Zest `validate-assets.test.ts` covers invalid asset cohorts in [`onchain/tests/borrow/validate-assets.test.ts`](https://github.com/Zest-Protocol/zest-contracts/blob/3564bc38906e464ec4de774122bb9bbaee20ddc6/onchain/tests/borrow/validate-assets.test.ts).

## Real-World Examples

- Zest Protocol - Clarity lending pool entrypoints accept trait-typed contracts while enforcing configured asset/oracle/zToken cohorts.

## Related Patterns

- [Solana Account Cohort Validation](./pattern-solana-account-cohort-validation.md)
- [Account Role Confusion](../../ANTIPATTERNS.md#account-role-confusion)
- [Oracle Reliability Requirements](../oracles/req-oracle-reliability.md)

## References

- See Source Evidence.
