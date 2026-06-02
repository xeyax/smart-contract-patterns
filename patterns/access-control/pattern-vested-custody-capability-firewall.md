# Vested Custody Capability Firewall

> Reserve locked vesting funds while allowing only whitelisted destinations and message shapes to use the locked balance.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, vesting, custody, whitelist, message-filter |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Locked tokens must still participate in staking, voting, or protocol maintenance
- The beneficiary should control only a limited capability surface before unlock
- The chain or protocol exposes value-bearing actions as arbitrary messages
- Locked and unlocked balances share the same wallet or custody account

## Avoid When

- Locked funds should be completely immobile
- Allowed destinations or message shapes cannot be precisely specified
- The allowlist must support frequent revocation but the mechanism is append-only
- Vesting schedule parameters cannot be validated before funding

## Trade-offs

**Pros:**
- Allows useful protocol participation without arbitrary transfer power
- Preserves the locked amount through reserve logic
- Makes pre-unlock capabilities inspectable

**Cons:**
- Message filters are easy to under-specify
- Destination allowlists become governance-critical
- Locked and unlocked balance accounting must be exact across every send path

## How It Works

Before sending value, the wallet computes the still-locked amount. If any balance
is locked, the send must match a whitelisted destination and an allowed message
shape. The wallet then reserves the locked amount so the operation cannot drain
vesting principal.

```solidity
function sendMessage(address target, bytes4 selector, uint256 value, bytes calldata data) external {
    uint256 locked = _lockedAmount(block.timestamp);

    if (locked > 0) {
        require(isWhitelistedTarget[target], "target");
        require(isAllowedSelector[target][selector], "selector");
        require(_messageShapeAllowed(target, selector, data), "shape");
    }

    _reserveLockedBalance(locked);
    _send(target, value, data);
}
```

## Implementation

- Compute locked balance from immutable or tightly bounded schedule parameters.
- Validate destination, bounce or callback behavior, state-init fields, selector, and message body.
- Reserve locked funds before the outbound action can reduce wallet balance below the locked amount.
- Allow unrestricted sends only after the vesting balance is fully unlocked.
- Treat whitelist changes as critical governance and test forbidden opcode/message variants.

## Source Evidence

- TON vesting wallet computes locked amount, filters sends to whitelisted destinations and elector/config message shapes, and reserves locked balance with `raw_reserve` in `/private/tmp/defillama-source/ton-blockchain__vesting-contract/contracts/vesting_wallet.fc`.
- TON vesting tests cover allowed staking-related sends and rejected disallowed operations in `/private/tmp/defillama-source/ton-blockchain__vesting-contract/tests/VestingWallet.spec.ts`.

## Real-World Examples

- TON vesting wallet - locked custody with whitelisted staking and configuration capabilities.

## Related Patterns

- [Selector-Scoped Authority](./pattern-selector-scoped-authority.md)
- [Isolated Vesting Schedule Escrow](../rewards/pattern-isolated-vesting-schedule-escrow.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)

## References

- See Source Evidence.
