# Reserve Exposure Caps

> Bound how much a lending market can supply, borrow, or expose to one asset so risk parameters cannot rely on liquidation mechanics alone.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, risk, supply-cap, borrow-cap, exposure, reserve |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- A market lists assets with limited liquidity or correlated risk
- Governance wants to grow exposure gradually after listing
- Liquidation capacity is smaller than possible supplied or borrowed size
- A protocol needs different caps for supply, borrow, isolation, or debt ceilings

## Avoid When

- The asset is not borrowable and has no protocol exposure beyond custody
- Caps cannot be updated safely as liquidity changes
- Users can bypass caps through wrappers, portals, or alternate markets

## How It Works

Apply cap checks before state changes:

```solidity
function supply(uint256 amount) external {
    accrueInterest();
    require(totalSupplyAssets + amount <= supplyCap, "supply cap");
    _supply(msg.sender, amount);
}

function borrow(uint256 amount) external {
    accrueInterest();
    require(totalBorrowAssets + amount <= borrowCap, "borrow cap");
    _borrow(msg.sender, amount);
}
```

For isolated assets, aggregate exposure can be capped separately from the market's local borrow amount.

## Key Points

- Treat cap increases as high-risk governance actions.
- Define whether accrued interest can push totals above the cap.
- Check caps on mint, borrow, portal, migration, and collateral-enabling paths.
- Pair caps with correlated collateral limits when assets share the same failure mode.
- Monitor cap utilization before listing changes or rate model updates.
- Allow risk-reducing deltas even when an account or market is already above a cap, as long as the action reduces debt, exposure, or unsafe collateralization.
- For stablecoin issuers, cap each issuance channel and combine those caps with global balance-sheet ratios; per-channel headroom alone is not solvency.
- For proof-based or allowlisted borrowing, cap the resulting debt after fees,
  interest, and market cap math, not just the requested action amount.
- For facilitator-style stablecoin minters, enforce per-facilitator bucket
  capacity and expose zero-cap offboarding; bucket caps constrain mint authority
  but are not proof of reserve solvency.

## Source Evidence

- Aave V3 uses reserve-level supply and borrow caps, isolation-mode debt ceilings, and exposure controls alongside liquidation parameters.
- Sky/Maker DSS risk checks allow position changes that improve safety even when debt ceilings or collateralization constraints would reject risk-increasing changes.
- Satoshi Core applies per-market CDP debt caps and Nexus total/daily mint caps in `/private/tmp/defillama-source/Satoshi-Protocol__satoshi-core/src/core/TroveManager.sol` and `src/core/NexusYieldManager.sol`.
- Reservoir combines PSM, savings, and fixed-maturity term debt caps with global balance-sheet ratio checks in `/private/tmp/defillama-source/reservoir-protocol__reservoir/src/CreditEnforcer.sol`.
- Zest Protocol combines supply caps, borrow caps, isolated-collateral flags, borrowable-isolated assets, and aggregate isolated debt ceilings in `/private/tmp/defillama-source/Zest-Protocol__zest-contracts/onchain/contracts/borrow/production/pool/pool-borrow.clar`, with isolation-mode tests under `onchain/tests/borrow`.
- Abracadabra whitelisted cauldrons verify Merkle proof debt caps against the
  resulting borrow part after fee/cap math, not merely the user-requested amount,
  in `/private/tmp/defillama-source/abracadabra-money__magic-internet-money/contracts/WhitelistedCauldronV3.sol:278-292`,
  `/private/tmp/defillama-source/abracadabra-money__magic-internet-money/contracts/WhitelistedCauldronV3.sol:488-490`,
  and `/private/tmp/defillama-source/abracadabra-money__magic-internet-money/contracts/Whitelister.sol:24-35`.
- GHO caps stablecoin issuance by facilitator buckets and tests bucket-cap
  minting and zero-cap behavior in `/private/tmp/defillama-source/aave__gho-core/src/contracts/gho/GhoToken.sol:34`,
  `/private/tmp/defillama-source/aave__gho-core/src/contracts/gho/GhoToken.sol:84`,
  and `/private/tmp/defillama-source/aave__gho-core/src/test/TestGhoToken.t.sol:171`.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Balance-Sheet Solvency Gate](./pattern-balance-sheet-solvency-gate.md)
- [Kinked Utilization Rate Model](./pattern-kinked-utilization-rate-model.md)
- [Dust-Aware Liquidation Cap](./pattern-dust-aware-liquidation-cap.md)
- [Correlated Collateral Basket](../../ANTIPATTERNS.md#correlated-collateral-basket)
