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

## Source Evidence

- JustLend accepts no-return ERC20s, rejects false returns, measures balance delta as actual received amount, and mints/repays from actual received amounts.
- Kamino Lend performs post-token-CPI vault and ledger checks and rejects unsupported Token-2022 mint/account extensions around lending reserves.
- Uniswap V2 Router02 supports fee-on-transfer exact-input swap variants by deriving each hop's actual input from pair balances and checking the final recipient balance delta.
- QuickSwap's V2 periphery illustrates the same exact-input fee-on-transfer route mechanics and the need to keep liquidity-removal min-out semantics explicit in `/private/tmp/defillama-source/QuickSwap__quickswap-periphery/contracts/UniswapV2Router02.sol`.
- Loopscale/Meteora DAMM v2 reads Token-2022 transfer-fee extension state and normalizes included/excluded amounts for swap and liquidity math while rejecting unsupported extensions.
- Reservoir's PSM mints against actual received underlying before decimal normalization in `/private/tmp/defillama-source/reservoir-protocol__reservoir/src/PegStabilityModule.sol`; the `18 - decimals` normalization also illustrates why supported decimal ranges need an onboarding guard.
- Satoshi Nexus mints from actual received collateral deltas in `/private/tmp/defillama-source/Satoshi-Protocol__satoshi-core/src/core/NexusYieldManager.sol`, while Sophon's custom USDC bridge uses a balance delta and then rejects non-exact transfers for canonical USDC bridge deposits.
- Ethena's 2023 Code4rena snapshot routes mint collateral directly from the benefactor to custodian addresses in `/private/tmp/defillama-source/code-423n4__2023-10-ethena/contracts/EthenaMinting.sol`, which is safe only for curated exact-transfer collateral or with per-recipient received-amount checks.
- Meteora Dynamic Fee Sharing funds rewards from post-CPI balance deltas in `/private/tmp/defillama-source/MeteoraAg_dynamic-fee-sharing/programs/dynamic-fee-sharing/src/instructions/ix_fund_by_claiming_fee.rs`, and Meteora Zap records residual token ledgers in `/private/tmp/defillama-source/MeteoraAg_zap-program/programs/zap/src/state/user_ledger.rs`.
- Curve StableSwap NG measures actual received tokens, maintains stored balances,
  documents rebasing and ERC4626/rate-oracle asset classes, and disables
  `exchange_received` for rebasing pools in `/private/tmp/defillama-source/curvefi__stableswap-ng/contracts/main/CurveStableSwapNG.vy:1-52`,
  `/private/tmp/defillama-source/curvefi__stableswap-ng/contracts/main/CurveStableSwapNG.vy:357-496`,
  `/private/tmp/defillama-source/curvefi__stableswap-ng/contracts/main/CurveStableSwapNG.vy:532-565`,
  and `/private/tmp/defillama-source/curvefi__stableswap-ng/tests/pools/exchange/test_exchange_received.py:100-150`.

## Related Anti-Patterns

- [Fee-on-Transfer Blindness](../../ANTIPATTERNS.md#fee-on-transfer-blindness)
- [Unchecked External Return](../../ANTIPATTERNS.md#unchecked-external-return)
- [Extension-Gated Transfer-Fee Normalization](./pattern-extension-gated-transfer-fee-normalization.md)
