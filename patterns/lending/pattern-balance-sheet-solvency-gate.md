# Balance-Sheet Solvency Gate

> Gate stablecoin issuance and reserve allocation against protocol-level assets, liabilities, risk-weighted assets, and liquidity ratios.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | stablecoin, solvency, balance-sheet, debt-cap, liquidity-ratio |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A protocol issues stablecoin or credit through multiple modules
- Each issuance channel needs a debt ceiling, but local caps are not enough for system solvency
- Assets can be allocated into adapters with different risk weights or durations
- Liabilities include savings balances, fixed-maturity debt, or other protocol-issued claims

## Avoid When

- Risk is purely per-account and a market comptroller already covers every action
- Assets and liabilities cannot be valued on-chain with conservative enough inputs
- Managers can allocate or withdraw reserves without running the same solvency checks
- Governance wants discretionary off-chain solvency policy rather than enforceable gates

## Trade-offs

**Pros:**
- Catches unsafe issuance even when a local debt cap still has room
- Lets reserves move across adapters while preserving global balance-sheet constraints
- Makes asset, equity, and liquidity ratios explicit monitoring surfaces

**Cons:**
- Depends on adapter valuation and duration classifications
- Centralizes policy in one high-impact controller
- Ratio checks can become liveness bottlenecks during oracle or adapter outages

## How It Works

Route every issuance path through a controller that checks the local channel cap
before minting, then checks global ratios after the state change:

```solidity
function mintSaving(uint256 amount) external {
    require(savingDebt + amount <= savingDebtMax, "saving cap");

    savingModule.mint(msg.sender, amount);

    require(assetRatio() >= minAssetRatio, "asset ratio");
    require(equityRatio() >= minEquityRatio, "equity ratio");
    require(liquidityRatio(durationWindow) >= minLiquidityRatio, "liquidity ratio");
}
```

Adapters report total value, risk-weighted value, and duration. The controller
derives liabilities from outstanding savings claims and fixed-maturity debt.
Short-term liquidity ratios compare assets available inside a duration window
against liabilities maturing inside the same window.

### Dual-Index Liability Variant

Stablecoin issuers can carry separate indexed supply and liability bases. For
example, token holders may earn through an earning-supply index while minters owe
through an active-debt index. Balance-sheet checks must convert both principal
ledgers through their current indexes before comparing collateral, supply, owed
amounts, and mint capacity.

## Key Points

- Check per-channel caps before minting and global ratios after every issuance or allocation.
- Include savings, term debt, and other protocol liabilities in the same denominator.
- Separate total asset value from risk-weighted assets and short-term liquid assets.
- Treat adapter onboarding, risk weights, duration windows, and ratio floors as critical governance actions.
- Allow risk-reducing actions where possible even if ratios are already breached.
- Invariant-test each debt ceiling and global ratio under mixed issuance and allocation sequences.
- When supply and owed liabilities use separate indexes, sync or compute both indexes at the same decision point before minting, burning, freezing, or applying penalties.

## Source Evidence

- Reservoir's `CreditEnforcer` gates PSM, saving module, and term issuance with channel debt caps, then checks asset, equity, and liquidity ratios in `/private/tmp/defillama-source/reservoir-protocol__reservoir/src/CreditEnforcer.sol`.
- Reservoir computes assets, liabilities, risk-weighted assets, short-term assets, and short-term liabilities from PSM, savings, term, and adapter state, with ratio and debt-cap invariants in `/private/tmp/defillama-source/reservoir-protocol__reservoir/test/invariants`.
- M0 tracks earning token supply and minter owed M through separate indexed principal ledgers in `MToken.sol` and `MinterGateway.sol`, with tests around active owed M indexing and collateral penalties in `/private/tmp/defillama-source/m0-foundation__protocol`.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Reserve Exposure Caps](./pattern-reserve-exposure-caps.md)
- [Action-Scoped Bounded Risk Prices](../oracles/pattern-action-scoped-bounded-lending-prices.md)
- [Privileged Supply Mutation](../../ANTIPATTERNS.md#privileged-supply-mutation)
