# Authorized Shared Bridge Lockbox

> Centralize native-asset bridge custody in a lockbox whose authorized portals and migrations are bounded by shared ownership and configuration checks.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, custody, lockbox, migration, native-asset |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Multiple bridge portals or proof systems need to share native-asset liquidity
- Custody migration must happen atomically with proof-system migration
- The system can enforce a restricted set of authorized portals or lockboxes
- Shared ownership and global pause configuration are part of the bridge trust model

## Avoid When

- Independent bridges should have isolated custody and blast radius
- Authorization can be changed instantly by a weak admin
- Liquidity can migrate without preserving pending exit obligations

## How It Works

The lockbox accepts deposits from authorized bridge portals and unlocks withdrawals only to authorized release paths:

```solidity
function lockETH() external payable onlyAuthorizedPortal {
    lockedBalance += msg.value;
}

function unlockETH(address to, uint256 amount) external onlyAuthorizedPortal {
    lockedBalance -= amount;
    _safeTransferETH(to, amount);
}

function authorizePortal(address portal, bool allowed) external onlyOwner {
    require(_sameProxyAdminOwner(portal), "owner mismatch");
    authorizedPortals[portal] = allowed;
}
```

Migration moves custody only as part of a versioned bridge cutover that defines which proof system owns each exit boundary.

## Key Points

- Restrict writers to authenticated portals, lockboxes, or migration contracts.
- Check shared owner, global configuration, and pause domains before authorization.
- Keep custody migration atomic with proof-method migration.
- Publish a final source boundary for old exits and a claim path for pending exits.
- Do not present shared custody as safer than isolated custody unless writer set and accounting invariants are explicit.

## Source Evidence

- Optimism Bedrock's ETH lockbox authorizes portals and lockboxes, verifies shared proxy-admin ownership and superchain configuration, and coordinates liquidity migration with portal proof-system migration.

## Related Patterns

- [Dispute-Game Gated Withdrawal Finality](./pattern-dispute-game-gated-withdrawal-finality.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Shared Pool Sink](../../ANTIPATTERNS.md#shared-pool-sink)
