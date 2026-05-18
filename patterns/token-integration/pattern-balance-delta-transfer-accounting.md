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

## Source Evidence

- JustLend accepts no-return ERC20s, rejects false returns, measures balance delta as actual received amount, and mints/repays from actual received amounts.
- Kamino Lend performs post-token-CPI vault and ledger checks and rejects unsupported Token-2022 mint/account extensions around lending reserves.

## Related Anti-Patterns

- [Fee-on-Transfer Blindness](../../ANTIPATTERNS.md#fee-on-transfer-blindness)
- [Unchecked External Return](../../ANTIPATTERNS.md#unchecked-external-return)
