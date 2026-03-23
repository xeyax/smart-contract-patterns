# Proportional Deposit/Withdrawal

> Users deposit and withdraw all vault assets proportionally, eliminating the need for oracle-based NAV calculation.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, proportional, lp, amm, in-kind, no-oracle |
| Complexity | Low |
| Gas Efficiency | Medium |
| Audit Risk | Low |

## Use When

- Multi-asset vault/pool with known composition
- Want to avoid oracle dependency entirely
- Users can acquire all component assets
- In-kind redemption is acceptable

## Avoid When

- Users want single-asset deposit UX
- Component assets are hard to acquire
- Vault composition changes frequently
- Gas cost of multi-token transfers is prohibitive

## Trade-offs

**Pros:**
- No oracle needed — eliminates arbitrage risk entirely
- Simple, deterministic share calculation
- No premium/fees required for protection
- Mathematically clean: shares = contribution / pool

**Cons:**
- Poor UX: user must have all assets in correct ratio
- Higher gas: multiple token transfers
- Not suitable for single-asset deposit flows
- Slippage if user needs to acquire assets first

## How It Works

### Deposit

User provides all assets in proportion to current vault holdings:

```
Vault holds: 100 ETH + 200,000 USDC
Ratio: 1 ETH : 2000 USDC

User wants 10% of vault:
  Deposits: 10 ETH + 20,000 USDC
  Receives: 10% of total shares
```

No NAV calculation needed — share percentage equals contribution percentage.

### Withdrawal (In-Kind)

User burns shares, receives proportional slice of all assets:

```
User holds: 10% of shares
Vault holds: 100 ETH + 200,000 USDC

User redeems all shares:
  Burns: 10% of total shares
  Receives: 10 ETH + 20,000 USDC
```

### Math

```
For deposit:
  shares_minted = min(
    deposit_asset_1 / vault_asset_1,
    deposit_asset_2 / vault_asset_2,
    ...
  ) × total_shares

For withdrawal:
  for each asset:
    amount_out = shares_burned / total_shares × vault_balance
```

## Implementation

```solidity
contract ProportionalVault {
    address[] public assets;
    uint256 public totalShares;
    mapping(address => uint256) public shares;

    function deposit(uint256[] calldata amounts) external returns (uint256 sharesToMint) {
        require(amounts.length == assets.length, "Invalid amounts");

        if (totalShares == 0) {
            // First deposit: shares = arbitrary base (e.g., sum of values)
            sharesToMint = _sumAmounts(amounts);
        } else {
            // Calculate minimum ratio across all assets
            uint256 minRatio = type(uint256).max;
            for (uint i = 0; i < assets.length; i++) {
                uint256 vaultBalance = _getBalance(assets[i]);
                uint256 ratio = amounts[i] * 1e18 / vaultBalance;
                if (ratio < minRatio) minRatio = ratio;
            }
            sharesToMint = minRatio * totalShares / 1e18;
        }

        // Transfer all assets
        for (uint i = 0; i < assets.length; i++) {
            _transferIn(assets[i], amounts[i]);
        }

        shares[msg.sender] += sharesToMint;
        totalShares += sharesToMint;
    }

    function withdraw(uint256 sharesToBurn) external returns (uint256[] memory amountsOut) {
        require(shares[msg.sender] >= sharesToBurn, "Insufficient shares");

        amountsOut = new uint256[](assets.length);

        for (uint i = 0; i < assets.length; i++) {
            uint256 vaultBalance = _getBalance(assets[i]);
            amountsOut[i] = sharesToBurn * vaultBalance / totalShares;
            _transferOut(assets[i], amountsOut[i]);
        }

        shares[msg.sender] -= sharesToBurn;
        totalShares -= sharesToBurn;
    }

    // --- Abstract functions ---
    function _getBalance(address asset) internal view returns (uint256);
    function _transferIn(address asset, uint256 amount) internal;
    function _transferOut(address asset, uint256 amount) internal;
    function _sumAmounts(uint256[] calldata amounts) internal pure returns (uint256);
}
```

### Key Points

- `min()` across all ratios ensures user can't deposit disproportionate amounts
- Excess amounts beyond minimum ratio are not accepted (or returned)
- No oracle calls anywhere in the flow
- Withdrawal always in-kind (receive all assets)

## Variations

### Single-Sided with Rebalance

Allow single-asset deposit, but rebalance internally:

```
User deposits: 1000 USDC
Vault swaps: 500 USDC → 0.25 ETH (internally)
User receives: shares based on post-swap proportional value
```

**Caveat:** This reintroduces swap price risk.

### Weighted Proportional (Balancer-style)

Assets have target weights, proportional means matching weights:

```
Target: 50% ETH, 30% USDC, 20% WBTC

Proportional deposit of $1000:
  $500 ETH + $300 USDC + $200 WBTC
```

### In-Kind vs Single-Asset Redemption

Some vaults offer choice:
- **In-kind:** Receive proportional slice of all assets
- **Single-asset:** Vault sells other assets, user receives one (incurs slippage)

## Real-World Examples

- [Uniswap V2 LP](https://github.com/Uniswap/v2-core) — proportional add/remove liquidity
- [Balancer Proportional Joins](https://docs.balancer.fi/concepts/pools/joins-and-exits.html) — weighted pool joins
- [Curve Base Pool](https://curve.readthedocs.io/) — option for proportional deposits

## Related Patterns

- [ZapIn Proportional Deposit](./pattern-proportional-zapin.md) — adds periphery ZapIn for single-token UX on top of this pattern
- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — this pattern avoids the risk entirely
- [Delta NAV Share Accounting](./pattern-delta-nav.md) — alternative that uses oracles
- [Premium Buffer](./pattern-premium-buffer.md) — alternative mitigation for oracle-based vaults

## References

- [Uniswap V2 Whitepaper](https://uniswap.org/whitepaper.pdf)
- [Balancer Docs: Joins and Exits](https://docs.balancer.fi/concepts/pools/joins-and-exits.html)
