# Hash-Anchored Strategy Subscription

> Store only a wallet-bound strategy hash on-chain while bots supply the full strategy data and must match the committed hash before execution.

## Metadata

| Property | Value |
|----------|-------|
| Category | automation |
| Tags | automation, strategy, subscription, hash, bot |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Automation strategies contain large trigger and action structs
- Users or wallets subscribe to immutable strategy terms
- Bots need to submit full calldata at execution time
- On-chain storage should remain compact

## Avoid When

- Strategy data changes frequently without explicit resubscription
- Hash encoding is ambiguous or versionless
- Bots can choose different wallet, trigger, or action terms at execution
- Users need full on-chain discoverability without off-chain indexing

## How It Works

Store a hash that binds the wallet and strategy terms:

```solidity
function subscribe(Strategy calldata strategy) external {
    bytes32 hash = hashStrategy(msg.sender, strategy);
    subscriptionHash[msg.sender][strategy.id] = hash;
}

function execute(address wallet, Strategy calldata strategy) external {
    require(subscriptionHash[wallet][strategy.id] == hashStrategy(wallet, strategy), "strategy");
    _run(strategy);
}
```

The bot can provide rich calldata, but execution is limited to the user's committed strategy hash.

## Key Points

- Domain-separate hash version, wallet, chain, strategy id, triggers, actions, and permissions.
- Require resubscription for any material strategy change.
- Reject missing, cancelled, or wallet-mismatched subscriptions.
- Pair with trigger gates that decide whether execution is currently allowed.
- Test hash mismatch for every value-bearing strategy field.

## Source Evidence

- Defi Saver V3 stores wallet-bound subscription hashes and requires bots to supply full strategy structs that match before trigger and action execution.

## Related Patterns

- [Changeable Trigger Gate](./pattern-changeable-trigger-gate.md)
- [Chain-Bound Request Hash](../cross-chain/pattern-chain-bound-request-hash.md)
