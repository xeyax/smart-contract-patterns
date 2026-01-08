# Premium Buffer (Entry/Exit Fee)

> Charge a fee on deposits/withdrawals that covers potential oracle price deviation, eliminating arbitrage profitability.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, fee, premium, oracle, arbitrage, protection |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Low |

## Use When

- Vault uses oracle prices for NAV calculation
- Need simple, synchronous deposit/withdraw flow
- Oracle has known deviation threshold (e.g., Chainlink 0.5-1%)
- Want to protect existing shareholders from arbitrage

## Avoid When

- Users are highly fee-sensitive
- Oracle deviation is unpredictable or very high
- Vault assets are highly correlated (premium becomes unnecessary cost)

## Trade-offs

**Pros:**
- Simple to implement
- No UX change (still synchronous)
- Premium goes to existing shareholders (not protocol)
- Deterministic protection level

**Cons:**
- Cost to legitimate users
- Must be calibrated to oracle deviation
- Doesn't protect against large oracle failures
- May discourage small deposits (fee is proportional)

## How It Works

Premium creates a buffer zone around the oracle price:

```
Deposit:
  shares = (deposit_amount × (1 - premium)) × totalShares / NAV

Withdraw:
  assets = (shares × NAV / totalShares) × (1 - premium)
```

Arbitrage becomes unprofitable when:
```
premium >= oracle_deviation_threshold
```

### Example

```
Oracle deviation threshold: 0.5%
Premium: 0.5%

Attack attempt:
  Oracle price: $100 (stale, real = $99.50)
  Potential arbitrage: 0.5%
  Premium cost: 0.5%
  Net profit: 0%  ← attack neutralized
```

### Where Premium Goes

**Critical design choice:** Premium should go to existing shareholders, not protocol treasury.

```
Without premium: new depositor gets N shares
With premium:    new depositor gets N × (1 - premium) shares
                 remaining value stays in vault → benefits existing holders
```

This compensates shareholders for the risk they bear from oracle inaccuracy.

## Implementation

```solidity
contract PremiumVault {
    uint256 public premiumBps;  // e.g., 50 = 0.5%
    uint256 constant BPS = 10000;

    function deposit(uint256 assets) external returns (uint256 shares) {
        uint256 nav = _calculateNav();

        // Apply premium: depositor receives fewer shares
        uint256 effectiveAssets = assets * (BPS - premiumBps) / BPS;

        if (totalShares == 0) {
            shares = effectiveAssets;
        } else {
            shares = effectiveAssets * totalShares / nav;
        }

        _acceptDeposit(assets);  // full amount goes to vault
        _mintShares(msg.sender, shares);
    }

    function withdraw(uint256 sharesToBurn) external returns (uint256 assets) {
        uint256 nav = _calculateNav();

        // Calculate gross assets for shares
        uint256 grossAssets = sharesToBurn * nav / totalShares;

        // Apply premium: withdrawer receives fewer assets
        assets = grossAssets * (BPS - premiumBps) / BPS;

        _burnShares(msg.sender, sharesToBurn);
        _processWithdrawal(assets);

        // Remaining (grossAssets - assets) stays in vault
    }

    // --- Abstract functions ---
    function _calculateNav() internal view returns (uint256);
    function _acceptDeposit(uint256 amount) internal;
    function _processWithdrawal(uint256 amount) internal returns (uint256);
    function _mintShares(address to, uint256 amount) internal;
    function _burnShares(address from, uint256 amount) internal;
}
```

### Key Points

- `premiumBps` should match or exceed oracle deviation threshold
- Premium applies to both deposits AND withdrawals
- Full deposit amount enters vault; fewer shares minted
- Full shares burned; fewer assets returned

## Calibrating Premium

| Oracle Type | Typical Deviation | Suggested Premium |
|-------------|-------------------|-------------------|
| Chainlink (majors) | 0.5% | 0.5-1% |
| Chainlink (altcoins) | 1-2% | 1-2% |
| TWAP (short window) | Variable | 1-2% |
| Custom oracle | Variable | Match deviation + buffer |

**Multi-asset vaults:** Sum of component oracle deviations may compound.
```
Vault with 3 assets, each 0.5% deviation
Worst case: 1.5% total deviation → premium ≥ 1.5%
```

## Real-World Examples

- [Set Protocol NAVIssuanceModule](https://docs.tokensets.com/developers/contracts/protocol/modules/nav-issuance-module) — `premiumPercentage` parameter
- [Index Coop products](https://indexcoop.com/) — uses Set Protocol premium mechanism

## Related Patterns

- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — the problem this solves
- [Async Deposit/Withdrawal](./pattern-async-deposit.md) — alternative mitigation
- [Delta NAV Share Accounting](./pattern-delta-nav.md) — base pattern

## References

- [Set Protocol NAV Issuance Docs](https://docs.tokensets.com/developers/guides-and-tutorials/protocol/nav-issuance)
