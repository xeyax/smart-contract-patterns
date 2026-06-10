# Balance Delta Transfer Accounting

> Account for the actual token amount received by measuring balance changes around transfers.

## Metadata

| Property | Value |
|----------|-------|
| Category | token-integration |
| Tags | token, erc20, fee-on-transfer, balance-delta, accounting |
| Complexity | Low |
| Gas Efficiency | Medium |
| Audit Risk | Low |

## Use When

- The protocol accepts arbitrary or curated ERC20 collateral
- Fee-on-transfer, rebasing, or non-standard ERC20 behavior is possible
- Mint, deposit, repay, or share accounting depends on inbound amount
- The token may return no boolean value

## Avoid When

- The protocol explicitly rejects all non-standard tokens at onboarding
- External token balances can change independently during the transfer
- Measuring the contract's token balance is itself unsafe due to hooks or callbacks

## Trade-offs

**Pros:**
- Accounting always matches tokens actually received, neutralizing fee-on-transfer, no-return, and false-return discrepancies.
- Cheap and local — two `balanceOf` reads, no registry or token-metadata dependency.
- The same measurement doubles as a rejection tool: revert when received differs from requested for unsupported tokens.
- Generalizes across legs: CPI claims, zap residues, custodian transfers, and per-hop AMM inputs.

**Cons:**
- Two extra `balanceOf` calls per transfer leg add gas, multiplied across multi-hop and multi-asset flows.
- Unsafe when balances can move independently mid-transfer (rebasing, hooks, reentrancy) without guards or asset-class carve-outs.
- The guarantee scopes narrowly: exact-input support does not extend to exact-output or all liquidity-exit paths, and teams over-generalize it.
- `minOut` semantics (pre-fee vs recipient-net) become a documentation and integration burden.
- Direct-to-custodian flows escape the measurement unless every recipient leg is checked separately.

## How It Works

```solidity
function doTransferIn(address token, address from, uint256 amount) internal returns (uint256 received) {
    uint256 beforeBalance = IERC20(token).balanceOf(address(this));
    _safeTransferFrom(token, from, address(this), amount);
    uint256 afterBalance = IERC20(token).balanceOf(address(this));

    received = afterBalance - beforeBalance;
    require(received > 0, "nothing received");
}
```

Use `received`, not requested `amount`, in mint/share/repay accounting.

## Key Points

- Measure balance before and after the transfer.
- Handle no-return and false-return ERC20s explicitly.
- Account with the received amount.
- Combine with a reentrancy guard if token hooks can run during transfer.
- If using curated tokens instead, document and enforce the rejection boundary.
- On Solana or Token-2022-style systems, combine post-CPI balance/internal-ledger reconciliation with explicit extension allowlists or rejections for transfer hooks, nonzero transfer fees, paused tokens, and unsafe confidential-transfer settings.
- For AMM route variants, compute actual per-hop input as pair balance minus reserves and check the final recipient balance delta; scope support to exact-input paths unless exact-output fee behavior is explicitly handled.
- For liquidity removal or withdrawal APIs, specify whether `minOut` is measured before transfer fees or as recipient-net output; exact-input swap support does not automatically make all exit paths fee-on-transfer safe.
- Deterministic Token-2022 transfer-fee extensions can be supported with canonical extension reads and fee normalization, but this is narrower than arbitrary fee-on-transfer token support.
- When normalizing the received delta to a canonical precision, explicitly reject token decimals above the canonical scale or prove the exponent cannot underflow.
- Direct-to-custodian transfers need the same actual-received guarantee. If the protocol never holds the asset locally, either reject fee-on-transfer tokens at onboarding or verify recipient balance deltas for every custodian leg.
- Balance deltas are also useful after trusted CPI claims or zap legs: measure the vault or ledger before and after the CPI, then fund rewards or residual accounting from the observed increase.
- For AMMs with stored balances, disable direct `exchange_received`-style paths
  for rebasing pools and explicitly separate actual-received accounting from
  stored balance updates, rate oracles, and ERC4626 asset classes.
- Fee-on-transfer support in AMM routers should check the recipient's final balance delta for exact-input swaps; it should not imply that all add/remove liquidity paths are fee-on-transfer safe.
- Explicit rejection can use the same balance-delta measurement: compare requested and received amounts and revert when the token is not meant to be supported.

## Source Evidence

- JustLend accepts no-return ERC20s, rejects false returns, measures balance delta as actual received amount, and mints/repays from actual received amounts.
- Kamino Lend performs post-token-CPI vault and ledger checks and rejects unsupported Token-2022 mint/account extensions around lending reserves.
- Uniswap V2 Router02 supports fee-on-transfer exact-input swap variants by deriving each hop's actual input from pair balances and checking the final recipient balance delta.
- QuickSwap's V2 periphery illustrates the same exact-input fee-on-transfer route mechanics and the need to keep liquidity-removal min-out semantics explicit in [`contracts/UniswapV2Router02.sol`](https://github.com/QuickSwap/quickswap-periphery/blob/522a94168b0814d0776d834119df377f03898807/contracts/UniswapV2Router02.sol).
- Loopscale/Meteora DAMM v2 reads Token-2022 transfer-fee extension state and normalizes included/excluded amounts for swap and liquidity math while rejecting unsupported extensions.
- Reservoir's PSM mints against actual received underlying before decimal normalization in [`src/PegStabilityModule.sol`](https://github.com/reservoir-protocol/reservoir/blob/95c83d4512a1042f241842431d53d44c0d204801/src/PegStabilityModule.sol); the `18 - decimals` normalization also illustrates why supported decimal ranges need an onboarding guard.
- Satoshi Nexus mints from actual received collateral deltas in [`src/core/NexusYieldManager.sol`](https://github.com/Satoshi-Protocol/satoshi-core/blob/7f5eddaed965904fde10ea1d40c4c4b3ea118ada/src/core/NexusYieldManager.sol), while Sophon's custom USDC bridge uses a balance delta and then rejects non-exact transfers for canonical USDC bridge deposits.
- Ethena's 2023 Code4rena snapshot routes mint collateral directly from the benefactor to custodian addresses in [`contracts/EthenaMinting.sol`](https://github.com/code-423n4/2023-10-ethena/blob/9fd8e26fc596601c3359ceac8951740c4d5e09c7/contracts/EthenaMinting.sol), which is safe only for curated exact-transfer collateral or with per-recipient received-amount checks.
- Meteora Dynamic Fee Sharing funds rewards from post-CPI balance deltas in [`programs/dynamic-fee-sharing/src/instructions/ix_fund_by_claiming_fee.rs`](https://github.com/MeteoraAg/dynamic-fee-sharing/blob/f9be4a9a94cf21f1955344bd459eb120e0c8d5af/programs/dynamic-fee-sharing/src/instructions/ix_fund_by_claiming_fee.rs), and Meteora Zap records residual token ledgers in [`programs/zap/src/state/user_ledger.rs`](https://github.com/MeteoraAg/zap-program/blob/c8dd95b4327158320238e2c4094507ab33883830/programs/zap/src/state/user_ledger.rs).
- Curve StableSwap NG measures actual received tokens, maintains stored balances,
  documents rebasing and ERC4626/rate-oracle asset classes, and disables
  `exchange_received` for rebasing pools in [`contracts/main/CurveStableSwapNG.vy:1-52`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/contracts/main/CurveStableSwapNG.vy#L1-L52),
  [`contracts/main/CurveStableSwapNG.vy:357-496`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/contracts/main/CurveStableSwapNG.vy#L357-L496),
  [`contracts/main/CurveStableSwapNG.vy:532-565`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/contracts/main/CurveStableSwapNG.vy#L532-L565),
  and [`tests/pools/exchange/test_exchange_received.py:100-150`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/tests/pools/exchange/test_exchange_received.py#L100-L150).
- Aerodrome V1 router supports fee-on-transfer exact-input swap variants by measuring actual pool input/output and final recipient deltas in [`contracts/Router.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/contracts/Router.sol), with tests in [`test/Router.t.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/test/Router.t.sol).
- Teller V2 rejects fee-on-transfer principal in borrower funding paths by verifying the receiver balance delta equals the requested amount in [`packages/contracts/contracts/TellerV2.sol`](https://github.com/teller-protocol/teller-protocol-v2/blob/49c0be13f5371c71fa9c97af78509a16c23d3626/packages/contracts/contracts/TellerV2.sol).
- mStable supports configured transfer-fee basket assets by measuring actual received amounts before invariant accounting in [`contracts/masset/MassetLogic.sol`](https://github.com/mstable/mStable-contracts/blob/51da0272104d207abcbecb5dd545fec2e6abbfe9/contracts/masset/MassetLogic.sol).

## Related Anti-Patterns

- [Fee-on-Transfer Blindness](../../ANTIPATTERNS.md#fee-on-transfer-blindness)
- [Unchecked External Return](../../ANTIPATTERNS.md#unchecked-external-return)
- [Extension-Gated Transfer-Fee Normalization](./pattern-extension-gated-transfer-fee-normalization.md)
