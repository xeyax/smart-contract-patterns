# Operator-Routed Liquid Staking Share

> Mint a non-rebasing liquid-staking share while routing deposits to selected validators or operators behind an exchange-rate ledger.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, liquid-staking, operator, validator, exchange-rate |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Users need a transferable non-rebasing claim on delegated stake
- Deposits can be routed across curated validators or operators
- The protocol tracks total delegated stake and token supply for exchange-rate minting
- Operator preference affects staking yield or validator concentration

## Avoid When

- Validator selection is permissionless and cannot be curated
- Exchange-rate accounting cannot include pending rewards, slashing, and undelegations
- Users require direct control of validator selection
- The system cannot monitor operator concentration

## How It Works

Deposits mint shares against an internal exchange rate and delegate the underlying asset through a selected operator:

```solidity
function deposit(uint256 assets, address operator) external returns (uint256 shares) {
    require(operatorRegistry.isPreferredDepositOperator(operator), "operator");
    shares = assets * totalSupply() / totalDelegatedStake();
    _mint(msg.sender, shares);
    _delegate(operator, assets);
}
```

The share token does not rebase. Rewards and losses move the exchange rate instead.

### Directed Stake Overlay Variant

If users or governance can direct stake toward specific validators, track directed stake separately from actual validator stake balances. Deposits and withdrawals should reconcile against directed stake first, then roll residual changes into undirected stake or internal balances so unrelated pool flows do not silently distort directed allocations.

## Key Points

- Keep delegated stake, undelegated assets, fees, rewards, and slashing in exchange-rate math.
- Curate deposit and withdrawal operators separately when roles differ.
- Emit delegation routing events for concentration monitoring.
- Do not treat the internal exchange rate as a liquid market price.
- Test first deposit, zero supply, reward accrual, slashing, and operator removal.
- Keep directed-stake overlays separate from actual validator stake balances.
- Reconcile deposits and withdrawals against directed stake before changing undirected stake.

## Source Evidence

- Stader BNBx mints a non-rebasing LST share from deposits routed through preferred validator operators and derives the exchange rate from delegated stake and token supply.
- Jito StakeNet reconciles directed stake for deposits and withdrawals separately from actual validator balances, with unit tests for in-sync, deposit-side, withdrawal-side, and over-withdrawal cases.

## Related Patterns

- [Curated Validator Operator Registry](./pattern-curated-validator-operator-registry.md)
- [Liquid Staking Loss Accounting Requirements](./req-liquid-staking-loss-accounting.md)
- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
