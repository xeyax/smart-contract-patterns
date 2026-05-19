# Value-Tiered Source Finality

> Scale required source-chain confirmation depth with the value being minted, released, or credited.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, finality, bitcoin, confirmations, risk |
| Complexity | Medium |
| Gas Efficiency | Low |
| Audit Risk | High |

## Use When

- A bridge or staking system accepts probabilistic-finality source-chain transactions
- Reorg cost and value at risk should be compared explicitly
- Low-value transfers need faster UX than high-value transfers
- The protocol can estimate transferred value before minting or crediting

## Avoid When

- The source chain has deterministic finality through the verified proof system
- Value cannot be computed safely before finality gating
- Operators can bypass the finality table without a separate risk process
- Users expect one fixed confirmation rule for all transfers

## Trade-offs

**Pros:**
- Matches finality cost to value at risk
- Improves UX for small transfers without weakening large transfers
- Makes confirmation policy explicit and testable

**Cons:**
- Requires maintaining value thresholds
- Price or amount conversion errors can understate risk
- Still depends on the underlying light-client or relay trust model

## How It Works

Map value ranges to confirmation requirements:

```solidity
function requiredConfirmations(uint256 amount) public pure returns (uint256) {
    if (amount < SMALL_TRANSFER) return 3;
    if (amount < MEDIUM_TRANSFER) return 6;
    return 12;
}

function finalizeDeposit(DepositProof calldata proof, uint256 amount) external {
    _verifyInclusion(proof);
    require(proof.confirmations >= requiredConfirmations(amount), "not final enough");
    _mint(proof.receiver, amount);
}
```

Thresholds should be denominated in a stable risk unit or in source asset amounts whose risk is reviewed regularly.

## Implementation

```solidity
struct FinalityTier {
    uint256 maxAmount;
    uint256 confirmations;
}

function _tierFor(uint256 amount) internal view returns (uint256 confirmations) {
    for (uint256 i; i < tiers.length; i++) {
        if (amount <= tiers[i].maxAmount) return tiers[i].confirmations;
    }
    return maxConfirmations;
}
```

### Key Points

- Apply the tier before minting, crediting voting power, or releasing assets.
- Use the same normalized amount in tier tests and production checks.
- Emit tier changes and treat threshold reductions as risk-increasing governance actions.
- Pair with source-chain proof and replay protection; tiering is not a proof system.

## Source Evidence

- Lorenzo BTC staking verifies Bitcoin inclusion and gates minting on amount-tiered confirmation thresholds in `/private/tmp/defillama-source/Lorenzo-Protocol__lorenzo/x/btcstaking/keeper/msg_server.go` and `x/btcstaking/keeper/utils.go`.
- Lorenzo tests cover confirmation-depth tiers in `/private/tmp/defillama-source/Lorenzo-Protocol__lorenzo/x/btcstaking/keeper/utils_test.go`.

## Real-World Examples

- Lorenzo Protocol - Bitcoin staking mint finality depends on amount-tiered confirmation requirements.

## Related Patterns

- [Bitcoin SPV State Transition Gate](./pattern-bitcoin-spv-state-transition-gate.md)
- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Trusted SPV Boundary Omitted](../../ANTIPATTERNS.md#trusted-spv-boundary-omitted)

## References

- See Source Evidence.
