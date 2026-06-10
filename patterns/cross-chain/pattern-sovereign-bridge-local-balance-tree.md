# Sovereign Bridge Local Balance Tree

> Track bridge-owned local token balances in a Merkle tree when a sovereign chain cannot or should not mint wrapped supply.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, sovereign-chain, balance-tree, local-exit-root, custody |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A sovereign chain bridge handles assets it cannot freely mint and burn
- Inbound claims increase bridge inventory and outbound transfers decrease it
- Local balance changes must be included in bridge roots for later proofs
- Emergency repair paths are needed for tree or inventory inconsistencies

## Avoid When

- The bridge can safely mint and burn canonical wrapped supply
- Local inventory is tracked only by external token balances with no internal ledger
- Emergency root or balance repair can bypass user claims without a governance playbook
- The bridge cannot prove inventory changes in a canonical exit tree

## Trade-offs

**Pros:**
- Supports sovereign or non-mintable token variants
- Makes local bridge inventory part of the proof system
- Separates bridge balance updates from arbitrary token balance drift

**Cons:**
- Local balance tree correctness becomes a custody invariant
- Emergency repair authority is highly privileged
- Outbound and inbound paths must update the tree symmetrically

## How It Works

Maintain a local balance tree keyed by token identity. Inbound claims credit the
bridge's local inventory and update the tree. Outbound bridge transfers debit the
inventory and update the tree before publishing the next local exit root.

```solidity
function claimInbound(TokenKey memory token, uint256 amount, Proof calldata proof) external {
    _verifyClaim(proof);
    localBalance[token] += amount;
    _updateBalanceTree(token, localBalance[token]);
    _releaseToUser(token, amount);
}

function bridgeOutbound(TokenKey memory token, uint256 amount) external {
    _pullFromUser(token, amount);
    localBalance[token] -= amount;
    _updateBalanceTree(token, localBalance[token]);
    _appendOutboundLeaf(token, amount);
}
```

## Implementation

- Key balances by canonical token identity and domain.
- Update internal balances before publishing roots or releasing claims.
- Prove that inbound and outbound paths update the same tree semantics.
- Gate emergency root or balance repair behind timelocked, monitored governance.
- Test inbound claim, outbound bridge, duplicate claim, insufficient inventory, emergency repair, and root-removal hazards.

## Source Evidence

- Polygon zkEVM/Agglayer sovereign bridge variants update local balance tree state on claims and outbound bridges in [`contracts/sovereignChains/AgglayerBridgeL2.sol`](https://github.com/0xPolygonHermez/zkevm-contracts/blob/110bda5a03e70ee7331bc06407a8e79226d3e520/contracts/sovereignChains/AgglayerBridgeL2.sol).
- Polygon zkEVM tests cover sovereign bridge local balance behavior and emergency repair paths in `test/contractsv2/BridgeL2SovereignChain.test.ts`.

## Real-World Examples

- Polygon zkEVM/Agglayer sovereign bridge tracks local balances for sovereign-chain bridge variants.

## Related Patterns

- [Domain-Scoped Message Root Accumulator](./pattern-domain-scoped-message-root-accumulator.md)
- [Bridge-Owned Mintable Token Pair](./pattern-bridge-owned-mintable-token-pair.md)
- [Proof Bridge Exit Safety Requirements](./req-proof-bridge-exit-safety.md)

## References

- Polygon zkEVM/Agglayer bridge source.
