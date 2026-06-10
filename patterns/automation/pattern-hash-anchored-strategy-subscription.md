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

## Trade-offs

**Pros:**
- One 32-byte hash per subscription regardless of strategy size, keeping storage compact
- The wallet-bound hash prevents bots from substituting terms or executing against the wrong wallet
- Mandatory resubscription makes every material strategy change explicit and user-authorized
- Bots can supply rich calldata at execution time without any trusted off-chain storage

**Cons:**
- Strategy contents are opaque on-chain; users and integrators depend on off-chain indexing to know what is subscribed
- If the off-chain strategy data is lost, the hash alone cannot reconstruct it and the subscription becomes unexecutable
- An encoding gap, such as a field omitted from the hash or no version domain, silently lets bots vary the unbound terms
- Re-hashing the full strategy struct on every execution costs gas proportional to strategy size
- Even minor parameter tweaks force a full resubscription transaction

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
