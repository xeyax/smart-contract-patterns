# Delta NAV Share Accounting

> Calculate vault shares based on proportional change in Net Asset Value.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, shares, erc4626, deposit, withdraw, nav |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Single-asset vault (one underlying token)
- Multi-asset vault where all assets can be priced in common unit (via oracles)
- All deposits are fungible (no distinction between depositors' assets)
- Assets grow uniformly (yield accrues to entire pool)
- Need ERC4626 compatibility

## Avoid When

- Need to track which specific assets each depositor contributed
- Withdrawal must return the same assets that were deposited
- Non-fungible positions (e.g., NFT-based vaults)
- Need to track individual deposit timestamps (for vesting, lock-ups)

## Trade-offs

**Pros:**
- Simple and well-understood
- Gas efficient (minimal storage)
- ERC4626 standard compliance
- Easy to integrate with other DeFi protocols

**Cons:**
- Vulnerable to inflation attack (first depositor exploit) without mitigation
- Rounding errors can accumulate
- No per-depositor tracking capability
- Share price manipulation possible via direct token transfers

## How It Works

The core principle: shares represent proportional ownership of total assets.

**Deposit (mint shares):**
```
shares = deposit_amount * total_supply / total_assets
```

**Withdraw (burn shares):**
```
assets = shares_amount * total_assets / total_supply
```

**Share price:**
```
price_per_share = total_assets / total_supply
```

### Example

1. Initial state: 0 shares, 0 assets
2. Alice deposits 100 USDC → receives 100 shares (1:1 for first deposit)
3. Vault earns 10 USDC yield → total assets = 110, shares = 100
4. Bob deposits 110 USDC → receives `110 * 100 / 110 = 100` shares
5. Total: 200 shares, 220 assets
6. Alice withdraws 100 shares → receives `100 * 220 / 200 = 110` USDC

### Multi-Asset Vault Considerations

When vault holds multiple assets or deploys to multiple strategies:

**Vault must control asset ratios internally.** Depositors provide a single asset (or proportional mix), and the vault decides how to allocate across underlying assets/strategies.

Why:
- Arbitrary single-sided deposits would change vault's risk profile for all shareholders
- Rebalancing to target allocation incurs slippage and gas costs
- Without vault-controlled allocation, share price calculation becomes inconsistent

**Pattern:**
```
User deposits USDC → Vault allocates to: 40% Aave, 30% Compound, 30% ETH
                  → Vault manages rebalancing internally
User withdraws   → Receives USDC (vault liquidates proportionally)
```

## Implementation

```solidity
contract DeltaNavVault {
    uint256 public totalShares;
    mapping(address => uint256) public shares;

    /// @notice Calculate total NAV across all strategies/assets
    /// @dev Implementation depends on vault type:
    ///      - Single asset: just balance
    ///      - Multi-asset: sum of (balance * price) for each asset
    ///      - With strategies: sum of strategy.totalValue()
    function totalNav() public view returns (uint256) {
        return _calculateNav();
    }

    function deposit(uint256 amount) external returns (uint256 sharesToMint) {
        uint256 navBefore = totalNav();

        _acceptDeposit(amount);  // transfer, deploy to strategies, etc.

        uint256 navAfter = totalNav();
        uint256 deltaNav = navAfter - navBefore;

        if (totalShares == 0) {
            sharesToMint = deltaNav;  // first deposit: 1:1
        } else {
            sharesToMint = (deltaNav * totalShares) / navBefore;
        }

        shares[msg.sender] += sharesToMint;
        totalShares += sharesToMint;
    }

    function withdraw(uint256 sharesToBurn) external returns (uint256 assetsReturned) {
        uint256 nav = totalNav();

        // Calculate proportional NAV for shares
        uint256 navShare = (sharesToBurn * nav) / totalShares;

        shares[msg.sender] -= sharesToBurn;
        totalShares -= sharesToBurn;

        assetsReturned = _processWithdrawal(navShare);  // liquidate, transfer, etc.
    }

    // --- Abstract functions (implementation varies by vault type) ---

    function _calculateNav() internal view returns (uint256);
    function _acceptDeposit(uint256 amount) internal;
    function _processWithdrawal(uint256 navAmount) internal returns (uint256);
}
```

### Key Points

- `totalNav()` — vault-specific: balances, oracle prices, strategy values
- `_acceptDeposit()` — receive assets, deploy to strategies
- `_processWithdrawal()` — liquidate positions, return assets to user
- Core pattern: `navBefore` → action → `navAfter` → `deltaNav`
- **Rounding:** Always round down for minting (favor vault), round down for burning (favor vault)
- **First deposit:** Usually 1:1 ratio, but vulnerable to inflation attack
- **Zero check:** Prevent minting zero shares on small deposits

## Security Considerations

### Inflation Attack

An attacker can exploit the first deposit:
1. Deposit 1 wei → get 1 share
2. Donate large amount directly to vault
3. Next depositor gets 0 shares due to rounding

**Mitigation:** Use virtual offset (see related patterns) or require minimum first deposit.

### Direct Transfer to Vault

Anyone can send tokens directly to vault without calling `deposit()`. This increases `totalAssets` without minting new shares, raising `price_per_share`.

**Impact:**
- Existing shareholders **benefit** (their shares worth more)
- Sender loses tokens (gift to vault)
- NAV becomes unpredictable if vault relies on `balanceOf()`

**Risk:** This is the basis of the **inflation attack** — attacker donates to manipulate rounding.

**Mitigation:** Track assets internally instead of using `balanceOf()`, or use virtual shares offset.

### Oracle Arbitrage

When NAV is calculated using oracle prices, stale prices create arbitrage opportunities. Attackers can deposit when oracle shows inflated prices or withdraw when oracle shows deflated prices.

**See:** [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) for detailed analysis and mitigations.

## Real-World Examples

- [OpenZeppelin ERC4626](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol)
- [Yearn V2 Vaults](https://github.com/yearn/yearn-vaults/blob/main/contracts/Vault.vy)
- [Solmate ERC4626](https://github.com/transmissions11/solmate/blob/main/src/tokens/ERC4626.sol)

## Related Patterns

- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — risk inherent to oracle-based NAV
- [Premium Buffer](./pattern-premium-buffer.md) — mitigation via entry/exit fees
- [Async Deposit/Withdrawal](./pattern-async-deposit.md) — mitigation via delayed settlement
- [Proportional Deposit/Withdrawal](./pattern-proportional-deposit.md) — alternative without oracles
- Virtual Offset Share Accounting — inflation attack protection (TODO)

## References

- [EIP-4626: Tokenized Vault Standard](https://eips.ethereum.org/EIPS/eip-4626)
- [OpenZeppelin ERC4626 Security](https://docs.openzeppelin.com/contracts/4.x/erc4626)
