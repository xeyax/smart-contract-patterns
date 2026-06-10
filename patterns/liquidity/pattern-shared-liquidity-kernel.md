# Shared Liquidity Kernel

> Centralize custody and interest accounting in a restricted liquidity core while user-facing fTokens, vaults, and DEX modules act as adapters.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | liquidity, kernel, lending, adapter, custody |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Multiple protocol modules need to draw from the same supplied liquidity
- The system can restrict writers to audited protocol contracts
- A single core can own token custody and authoritative accounting
- User-facing modules can translate actions into core operate calls

## Avoid When

- Independent products need isolated custody or blast-radius control
- External integrations can write to the core directly
- Core accounting cannot enforce per-protocol limits and callback settlement

## Trade-offs

**Pros:**
- One custody and accounting owner gives all modules deeper shared liquidity than isolated per-product pools.
- The narrow `operate` interface concentrates accrual, limits, and settlement checks in one audited choke point instead of per-module reimplementations.
- Per-protocol limits inside the core cap the blast radius of a compromised or buggy adapter.
- New products (fTokens, vaults, DEX modules) ship as adapters without migrating liquidity or re-auditing custody.

**Cons:**
- The core is a single point of failure: a kernel accounting bug or admin-key compromise exposes every module's funds at once.
- Adapter onboarding requires trust decisions and limit tuning per protocol; the writer set becomes a standing governance and review burden.
- Callback and balance-delta settlement paths (leveraged routers, transformers) are high-skill audit surface where one missed sender or receipt-token check breaks custody.
- Packed core storage forces integrators through official resolvers, adding an off-chain dependency for accurate reads.
- Shared liquidity couples module risk: one protocol's drawdown or limit exhaustion can starve unrelated modules, and cross-chain paths need credit scoping to avoid route-level theft of liquidity.

## How It Works

The liquidity core owns reserves and exposes a narrow operation interface to approved protocols:

```solidity
function operate(
    address token,
    int256 supplyDelta,
    int256 borrowDelta,
    address callbackTarget,
    bytes calldata data
) external onlyProtocol returns (uint256 supplyExchangePrice, uint256 borrowExchangePrice) {
    _accrue(token);
    _applyProtocolLimits(msg.sender, token, supplyDelta, borrowDelta);
    _runSettlementCallback(callbackTarget, data);
    _reconcileBalances(token);
}
```

Adapters implement fTokens, vaults, DEX positions, or liquidations while the core remains the single accounting owner.

### Leveraged Router Callback Variant

A user-facing router can compose borrow withdrawals, a transformer callback, and redeposit into the shared core in one operation:

```text
operate:
  withdraw borrowed assets
  call transformer
  verify receipt token
  deposit produced collateral
```

This remains a controlled shared-liquidity exception only if the callback is restricted to the margin core, the callback sender is bound to the expected router, produced receipt tokens match the staking pool or market, and user slippage/deadline constraints are enforced by the transformer data.

## Key Points

- Keep the core's writer set small and protocol-scoped.
- Enforce per-protocol borrow and withdrawal limits inside the core.
- For cross-chain shared pools, scope credits by path or peer so one route cannot consume another route's liquidity.
- Use callback or balance-delta settlement when adapters source tokens externally.
- Provide official resolvers so users do not depend on raw packed storage.
- Frame this as a controlled exception to generic shared mutable state warnings.
- For leveraged router flows, authenticate core callback caller and router sender, then verify produced collateral before redepositing it.
- For PSM-style reserves, exclude accrued fees from spendable stablecoin inventory.
- Enforce buy/sell limits inside the shared reserve kernel, and route reserve movement through constrained adapter managers.
- For leveraged callback helpers, authenticate the market callback, bind user position ownership, and verify the borrowed asset, minted collateral, and repayment deltas before returning control.

## Source Evidence

- Fluid uses a shared liquidity layer for custody and accounting, while fTokens, vaults, and DEX modules route user actions through protocol-scoped liquidity operations.
- Dolomite's Harvest strategy integration composes leveraged farming actions through a shared margin core with callback restrictions and receipt-token checks; the reusable lesson is the authenticated callback boundary, not the specific farming route.
- Lista PSM reserve accounting excludes accrued fees from spendable stablecoin inventory, enforces daily buy limits, and routes reserves through a constrained vault manager.
- Stargate V2 maintains path-scoped credits in [`packages/stg-evm-v2/src/libs/Path.sol`](https://github.com/stargate-protocol/stargate-v2/blob/8c41a9670d1b7d910862826829e44a23aa1afea0/packages/stg-evm-v2/src/libs/Path.sol) and ties pool balances to credits and pending bus amounts through `StargateBase.sol` and invariant tests in `StargateInvariantTest.t.sol`.
- Reservoir sRUSD loopers compose Morpho borrow/supply callbacks with sRUSD mint/redeem and repay flows in [`src`](https://github.com/reservoir-protocol/srusd-loop/blob/f97aaab1ff1028601e2fa888f1161978cf3711ed/src), illustrating a leveraged callback helper variant that must remain tightly settlement-checked.

## Related Patterns

- [Progressive Protocol Liquidity Limits](../lending/pattern-progressive-protocol-liquidity-limits.md)
- [Verified Callback Settlement](./pattern-verified-callback-settlement.md)
- [Shared Mutable State](../../ANTIPATTERNS.md#shared-mutable-state)
