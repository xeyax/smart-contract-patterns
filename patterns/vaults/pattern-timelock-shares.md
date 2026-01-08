# Timelock on Shares

> Shares are issued immediately but cannot be transferred or redeemed for a specified period, preventing instant arbitrage profit extraction.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, timelock, lock, flash-loan, arbitrage |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Low |

## Use When

- Want instant share issuance (better UX than async)
- Need to prevent flash loan attacks
- Vault has long-term holders who don't need immediate liquidity
- Combined with other protections (premium, circuit breaker)

## Avoid When

- Users need immediate liquidity
- Short-term trading is expected use case
- Timelock period is impractical for the asset type

## Trade-offs

**Pros:**
- Instant share issuance (good UX for long-term holders)
- Eliminates flash loan attack vector
- Adds price risk for attacker (can't exit immediately)
- Simple to implement

**Cons:**
- **Does NOT prevent unfair share allocation** — attacker still gets more shares than deserved
- Only removes instant profit extraction, not the underlying arbitrage
- Locked capital reduces flexibility for legitimate users
- May discourage deposits from users who value liquidity

## Critical Limitation

**This pattern does not fully solve oracle arbitrage.**

```
Oracle: ETH = $2000 (stale LOW, real = $2100)

Attacker deposits $1000:
  - Gets shares priced at $2000/ETH
  - Receives MORE shares than fair value

With 24h timelock:
  - Attacker still has MORE shares than deserved
  - Just can't exit for 24 hours
  - If price stays at $2100, attacker profits after timelock
  - Only loses if price drops below $2000 during lock
```

**What it prevents:**
- Flash loan attacks (borrow → deposit → withdraw → repay)
- Instant risk-free arbitrage
- MEV sandwich attacks on share minting

**What it doesn't prevent:**
- Unfair share allocation at deposit time
- Long-term holding of overvalued position
- Attacker with own capital (not borrowed)

## Requirements Satisfied

This pattern **partially** satisfies [Vault Fairness Requirements](./req-vault-fairness.md):
- **R4: No Timing Advantage** — partially satisfied; instant extraction prevented, but timing advantage at deposit still exists

Does **not** satisfy:
- **R1: No Value Extraction** — attacker still extracts value via unfair share allocation
- **R2: Fair Share Price** — shares still priced on stale oracle

## How It Works

Track when shares were minted; block transfer/redeem until timelock expires:

```
1. User deposits → shares minted immediately
2. mintTimestamp[user] = block.timestamp
3. User tries to transfer/redeem
4. Check: block.timestamp >= mintTimestamp[user] + timelockDuration
5. If not, revert
```

## Implementation

```solidity
contract TimelockSharesVault is ERC20 {
    uint256 public timelockDuration;  // e.g., 24 hours

    // Track when each user last received shares
    mapping(address => uint256) public lastMintTimestamp;

    function deposit(uint256 assets) external returns (uint256 shares) {
        shares = _calculateShares(assets);

        _transferAssets(msg.sender, assets);
        _mint(msg.sender, shares);

        // Update timelock
        lastMintTimestamp[msg.sender] = block.timestamp;
    }

    function withdraw(uint256 sharesToBurn) external returns (uint256 assets) {
        require(
            block.timestamp >= lastMintTimestamp[msg.sender] + timelockDuration,
            "Shares timelocked"
        );

        assets = _calculateAssets(sharesToBurn);
        _burn(msg.sender, sharesToBurn);
        _transferAssets(address(this), msg.sender, assets);
    }

    // Override ERC20 transfer to enforce timelock
    function transfer(address to, uint256 amount) public override returns (bool) {
        require(
            block.timestamp >= lastMintTimestamp[msg.sender] + timelockDuration,
            "Shares timelocked"
        );
        return super.transfer(to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        require(
            block.timestamp >= lastMintTimestamp[from] + timelockDuration,
            "Shares timelocked"
        );
        return super.transferFrom(from, to, amount);
    }

    // --- Abstract functions ---
    function _calculateShares(uint256 assets) internal view returns (uint256);
    function _calculateAssets(uint256 shares) internal view returns (uint256);
    function _transferAssets(address from, address to, uint256 amount) internal;
}
```

### Per-Mint Tracking (More Precise)

Track each mint separately instead of last mint:

```solidity
struct MintRecord {
    uint256 shares;
    uint256 timestamp;
}

mapping(address => MintRecord[]) public mintHistory;

function deposit(uint256 assets) external returns (uint256 shares) {
    shares = _calculateShares(assets);
    _mint(msg.sender, shares);

    mintHistory[msg.sender].push(MintRecord({
        shares: shares,
        timestamp: block.timestamp
    }));
}

function getUnlockedShares(address user) public view returns (uint256) {
    uint256 unlocked = 0;
    MintRecord[] storage history = mintHistory[user];

    for (uint i = 0; i < history.length; i++) {
        if (block.timestamp >= history[i].timestamp + timelockDuration) {
            unlocked += history[i].shares;
        }
    }

    return unlocked;
}

function withdraw(uint256 sharesToBurn) external returns (uint256 assets) {
    require(sharesToBurn <= getUnlockedShares(msg.sender), "Insufficient unlocked shares");
    // ... withdrawal logic
    // ... update mintHistory (complex bookkeeping)
}
```

## Timelock Duration Considerations

| Duration | Protection Level | UX Impact |
|----------|------------------|-----------|
| 1 hour | Low (oracle updates faster) | Minimal |
| 24 hours | Medium (covers most oracle cycles) | Noticeable |
| 7 days | High (significant price movement likely) | Significant |

**Factors:**
- Oracle update frequency (Chainlink: 1 hour heartbeat for majors)
- Asset volatility (higher vol → shorter timelock may suffice)
- User expectations (DeFi users expect faster than TradFi)

## Variations

### Graduated Unlock

Shares unlock gradually over time:

```solidity
function getUnlockedPercentage(address user) public view returns (uint256) {
    uint256 elapsed = block.timestamp - lastMintTimestamp[user];

    if (elapsed >= timelockDuration) return 100;
    return elapsed * 100 / timelockDuration;
}
```

### Timelock Bypass with Premium

Allow early exit with penalty fee:

```solidity
function earlyWithdraw(uint256 sharesToBurn) external returns (uint256 assets) {
    uint256 timeRemaining = (lastMintTimestamp[msg.sender] + timelockDuration) - block.timestamp;

    if (timeRemaining > 0) {
        // Penalty proportional to remaining time
        uint256 penaltyBps = timeRemaining * maxPenaltyBps / timelockDuration;
        assets = _calculateAssets(sharesToBurn) * (BPS - penaltyBps) / BPS;
    } else {
        assets = _calculateAssets(sharesToBurn);
    }

    _burn(msg.sender, sharesToBurn);
    _transferAssets(address(this), msg.sender, assets);
}
```

### Reset on Additional Deposit

Each deposit resets the timelock (Enzyme-style):

```solidity
function deposit(uint256 assets) external returns (uint256 shares) {
    shares = _calculateShares(assets);
    _mint(msg.sender, shares);

    // Reset timelock for ALL shares (stricter)
    lastMintTimestamp[msg.sender] = block.timestamp;
}
```

## Combination with Other Patterns

Timelock alone is insufficient. Combine with:

| Combination | Effect |
|-------------|--------|
| Timelock + Premium | Premium covers oracle deviation; timelock prevents flash loans |
| Timelock + Async | Redundant (async already delays share issuance) |
| Timelock + Circuit Breaker | Circuit breaker blocks during deviation; timelock adds holding requirement |

**Recommended:** Timelock + Premium Buffer for comprehensive protection.

## Real-World Examples

- [Enzyme Finance](https://specs.enzyme.finance/) — `sharesActionTimelock` parameter (24h recommended)
- [Yearn V2](https://docs.yearn.fi/) — withdrawal queue acts as implicit timelock

## Related Patterns

- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — the problem (partially addressed)
- [Premium Buffer](./pattern-premium-buffer.md) — complementary protection
- [Async Deposit/Withdrawal](./pattern-async-deposit.md) — alternative approach

## References

- [Enzyme Known Risks](https://specs.enzyme.finance/topics/known-risks-and-mitigations)
- [Flash Loan Attack Vectors](https://www.paradigm.xyz/2020/11/so-you-want-to-use-a-price-oracle)
