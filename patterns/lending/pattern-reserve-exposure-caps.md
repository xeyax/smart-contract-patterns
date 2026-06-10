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

## Trade-offs

**Pros:**
- Bounds worst-case exposure to illiquid or correlated assets without relying on liquidation mechanics working under stress.
- Cheap to enforce: one comparison against a stored total before each state change.
- Lets governance grow exposure gradually after listing instead of betting the market on day-one parameters.
- Separate supply, borrow, isolation, and debt-ceiling caps allow targeted control per failure mode.

**Cons:**
- Caps are only as good as their coverage: mint, portal, migration, and collateral-enabling paths each need the check, and one missed path voids the bound.
- Accrued interest can push totals past the cap, forcing an explicit policy on whether that blocks repay/withdraw-adjacent flows; risk-reducing deltas need carve-outs or healthy actions revert.
- Hard caps create denial-of-entry at the boundary: legitimate users get reverts when utilization sits near the cap, and cap-watching bots can front-run freed headroom.
- Parameter governance becomes a recurring operational burden and attack surface; cap increases are high-risk actions that need liquidity analysis each time.
- Per-channel or per-market caps can give false comfort: headroom in each bucket says nothing about global balance-sheet solvency without aggregate ratio checks.

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
- Fixed-maturity lending markets need both market-level and currency-level debt
  limits because maturity settlement can move exposure between fCash and cash
  buckets.

## Source Evidence

- Aave V3 uses reserve-level supply and borrow caps, isolation-mode debt ceilings, and exposure controls alongside liquidation parameters.
- Sky/Maker DSS risk checks allow position changes that improve safety even when debt ceilings or collateralization constraints would reject risk-increasing changes.
- Satoshi Core applies per-market CDP debt caps and Nexus total/daily mint caps in [`src/core/TroveManager.sol`](https://github.com/Satoshi-Protocol/satoshi-core/blob/7f5eddaed965904fde10ea1d40c4c4b3ea118ada/src/core/TroveManager.sol) and `src/core/NexusYieldManager.sol`.
- Reservoir combines PSM, savings, and fixed-maturity term debt caps with global balance-sheet ratio checks in [`src/CreditEnforcer.sol`](https://github.com/reservoir-protocol/reservoir/blob/95c83d4512a1042f241842431d53d44c0d204801/src/CreditEnforcer.sol).
- Zest Protocol combines supply caps, borrow caps, isolated-collateral flags, borrowable-isolated assets, and aggregate isolated debt ceilings in [`onchain/contracts/borrow/production/pool/pool-borrow.clar`](https://github.com/Zest-Protocol/zest-contracts/blob/3564bc38906e464ec4de774122bb9bbaee20ddc6/onchain/contracts/borrow/production/pool/pool-borrow.clar), with isolation-mode tests under `onchain/tests/borrow`.
- Abracadabra whitelisted cauldrons verify Merkle proof debt caps against the
  resulting borrow part after fee/cap math, not merely the user-requested amount,
  in [`contracts/WhitelistedCauldronV3.sol:278-292`](https://github.com/abracadabra-money/magic-internet-money/blob/23266d17969a95e69199670cba9d0060bff33340/contracts/WhitelistedCauldronV3.sol#L278-L292),
  [`contracts/WhitelistedCauldronV3.sol:488-490`](https://github.com/abracadabra-money/magic-internet-money/blob/23266d17969a95e69199670cba9d0060bff33340/contracts/WhitelistedCauldronV3.sol#L488-L490),
  and [`contracts/Whitelister.sol:24-35`](https://github.com/abracadabra-money/magic-internet-money/blob/23266d17969a95e69199670cba9d0060bff33340/contracts/Whitelister.sol#L24-L35).
- GHO caps stablecoin issuance by facilitator buckets and tests bucket-cap
  minting and zero-cap behavior in [`src/contracts/gho/GhoToken.sol:34`](https://github.com/aave/gho-core/blob/c6335a0bb9cba099960c5378b1ff0db190b8da8f/src/contracts/gho/GhoToken.sol#L34),
  [`src/contracts/gho/GhoToken.sol:84`](https://github.com/aave/gho-core/blob/c6335a0bb9cba099960c5378b1ff0db190b8da8f/src/contracts/gho/GhoToken.sol#L84),
  and [`src/test/TestGhoToken.t.sol:171`](https://github.com/aave/gho-core/blob/c6335a0bb9cba099960c5378b1ff0db190b8da8f/src/test/TestGhoToken.t.sol#L171).
- Notional V3 caps market and currency exposure through risk-parameter storage and free-collateral checks in [`contracts/internal/markets`](https://github.com/notional-finance/contracts-v3/blob/ae20d99ebfb0b14cf7b08421722b85849fb11edf/contracts/internal/markets) and [`contracts/internal/valuation`](https://github.com/notional-finance/contracts-v3/blob/ae20d99ebfb0b14cf7b08421722b85849fb11edf/contracts/internal/valuation).

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Balance-Sheet Solvency Gate](./pattern-balance-sheet-solvency-gate.md)
- [Kinked Utilization Rate Model](./pattern-kinked-utilization-rate-model.md)
- [Dust-Aware Liquidation Cap](./pattern-dust-aware-liquidation-cap.md)
- [Correlated Collateral Basket](../../ANTIPATTERNS.md#correlated-collateral-basket)
