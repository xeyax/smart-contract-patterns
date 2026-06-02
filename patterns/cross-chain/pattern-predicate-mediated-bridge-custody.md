# Predicate-Mediated Bridge Custody

> Route bridge deposits and exits through token-specific predicates that own custody rules while a root manager owns mapping and proof orchestration.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, custody, predicate, token-mapping, exit |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A bridge supports multiple token standards or custody modes
- Deposit/exit proof orchestration is shared across assets
- Token-specific logic differs for lock/release, burn/mint, or wrapper behavior
- Mappings from root token to child token need explicit registry control

## Avoid When

- The bridge supports one simple token behavior
- Token-specific predicates cannot be isolated from manager authority
- The registry can remap active token pairs without a migration plan

## Trade-offs

**Pros:**
- Isolates ERC20, ERC721, ERC1155, mintable, and custom behaviors
- Keeps proof parsing and token custody responsibilities separate
- Limits token-specific bugs to the predicate and mapped assets

**Cons:**
- Predicate registry becomes a critical trust boundary
- Migration must coordinate manager mappings and predicate-held custody
- Each predicate still needs independent token integration hardening

## How It Works

The root manager validates mappings and forwards token operations to the selected predicate:

```solidity
function depositFor(address user, address token, bytes calldata data) external {
    address predicate = predicateFor[token];
    require(predicate != address(0), "unmapped token");
    IPredicate(predicate).lockTokens(msg.sender, user, token, data);
    _sendDepositMessage(user, token, data);
}

function exit(bytes calldata proof) external {
    ExitLog memory log = _verifyExitProof(proof);
    address predicate = predicateFor[log.rootToken];
    IPredicate(predicate).exitTokens(log);
}
```

## Key Points

- Registry updates must bind root token, child token, token type, and predicate.
- Predicates should hold only custody for their token class.
- Exit proofs must authenticate the child token and source event before calling predicates.
- Predicate migration must preserve pending exits and custody sufficiency.
- Token predicates should use balance-delta accounting or reject incompatible token behavior.

## Source Evidence

- Polygon PoS portal routes deposits and exits through root token predicates.
- ERC20 predicates lock and release root tokens while child tokens mint and burn against manager messages.
- Mintable NFT predicates handle mint-on-exit behavior separately from standard lock/release exits.

## Related Patterns

- [Checkpointed Receipt Exit Proof](./pattern-checkpointed-receipt-exit-proof.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Bridge Exit Cutover Custody Drain](./risk-bridge-exit-cutover-custody-drain.md)
