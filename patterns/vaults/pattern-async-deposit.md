# Async Deposit/Withdrawal

> Separate the request and execution of deposits/withdrawals to eliminate timing arbitrage opportunities.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, async, epoch, queue, arbitrage, protection, erc7540 |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Vault has significant oracle latency or deviation
- Underlying assets are illiquid (RWA, staked assets)
- Need strong protection against timing arbitrage
- Vault requires time to rebalance or liquidate positions

## Avoid When

- Users expect instant liquidity
- Gas costs of two transactions are prohibitive
- Vault assets are highly liquid and oracle is reliable
- Simple fee-based protection is sufficient

## Trade-offs

**Pros:**
- Eliminates timing arbitrage completely
- Works with any oracle quality
- Natural fit for illiquid underlying assets
- Allows vault to prepare liquidity

**Cons:**
- Worse UX (delayed settlement)
- Two transactions required (higher gas)
- Complexity in tracking pending requests
- Users bear price risk during delay

## How It Works

### Approach 1: Delayed Deploy (Yearn-style)

Deposit goes to idle pool first, deployed to strategies later by keeper:

```
1. User deposits USDC
   → USDC added to totalIdle
   → Shares minted immediately at current NAV

2. Later: Keeper calls deployFunds()
   → USDC swapped/deployed to strategies
   → totalIdle decreases, totalDebt increases
   → Any slippage affects all shareholders equally
```

**Why it works:** Arbitrageur cannot predict what price keeper will execute at. No timing advantage.

### Approach 2: Request/Claim (Epoch-based)

User requests deposit/withdraw, executes after epoch ends:

```
Epoch N:
  - User requests deposit of 1000 USDC
  - Request recorded, USDC locked

Epoch N+1:
  - NAV calculated at epoch boundary
  - All pending deposits processed at same NAV
  - User can claim shares
```

**Why it works:** All users in same epoch get same price. No front-running possible.

### Approach 3: Timelock (Enzyme-style)

Shares cannot be transferred for a period after minting:

```
1. User deposits, receives shares
2. sharesActionTimelock starts (e.g., 24 hours)
3. User cannot transfer/redeem until timelock expires
```

**Why it works:** Flash loan attacks impossible. Arbitrageur must hold position through price uncertainty.

## Implementation

### Epoch-Based System

```solidity
contract EpochVault {
    uint256 public currentEpoch;
    uint256 public epochDuration;

    struct DepositRequest {
        uint256 assets;
        uint256 epoch;
    }

    mapping(address => DepositRequest) public pendingDeposits;
    mapping(uint256 => uint256) public epochNav;  // NAV at epoch end

    function requestDeposit(uint256 assets) external {
        _transferAssets(msg.sender, assets);

        pendingDeposits[msg.sender] = DepositRequest({
            assets: assets,
            epoch: currentEpoch
        });
    }

    function claimShares() external returns (uint256 shares) {
        DepositRequest memory request = pendingDeposits[msg.sender];
        require(request.epoch < currentEpoch, "Epoch not ended");

        uint256 nav = epochNav[request.epoch];
        shares = request.assets * totalShares / nav;

        delete pendingDeposits[msg.sender];
        _mintShares(msg.sender, shares);
    }

    function processEpoch() external {
        // Called by keeper at epoch boundary
        epochNav[currentEpoch] = _calculateNav();
        currentEpoch++;
    }

    // --- Abstract functions ---
    function _calculateNav() internal view returns (uint256);
    function _transferAssets(address from, uint256 amount) internal;
    function _mintShares(address to, uint256 amount) internal;
}
```

### Delayed Deploy (Yearn-style)

```solidity
contract DelayedDeployVault {
    uint256 public totalIdle;   // assets not yet deployed
    uint256 public totalDebt;   // assets in strategies

    function totalAssets() public view returns (uint256) {
        return totalIdle + totalDebt;
    }

    function deposit(uint256 assets) external returns (uint256 shares) {
        uint256 nav = totalAssets();

        // Shares calculated on current NAV (includes idle)
        shares = (nav == 0) ? assets : assets * totalShares / nav;

        _transferAssets(msg.sender, assets);
        totalIdle += assets;
        _mintShares(msg.sender, shares);
    }

    // Called by keeper, not atomically with deposit
    function deployToStrategy(address strategy, uint256 amount) external onlyKeeper {
        require(amount <= totalIdle, "Insufficient idle");

        totalIdle -= amount;
        totalDebt += _deployFunds(strategy, amount);  // may differ due to slippage
    }

    // --- Abstract functions ---
    function _deployFunds(address strategy, uint256 amount) internal returns (uint256 deployed);
}
```

### Key Points

- Deposit and strategy deployment are separate transactions
- NAV at deposit time includes idle funds (no manipulation benefit)
- Slippage during deployment affects all shareholders proportionally
- Keeper can optimize timing/routing for deployment

## ERC-7540: Async Vault Standard

Emerging standard for async ERC4626 vaults:

```solidity
interface IERC7540 {
    function requestDeposit(uint256 assets, address receiver, address owner) external returns (uint256 requestId);
    function pendingDepositRequest(address owner) external view returns (uint256 assets);
    function claimableDepositRequest(address owner) external view returns (uint256 assets);
    function deposit(uint256 assets, address receiver, address owner) external returns (uint256 shares);

    // Similar for redemptions...
}
```

## Real-World Examples

- [Yearn V3](https://github.com/yearn/yearn-vaults-v3) — `auto_allocate` flag controls immediate vs delayed deploy
- [Enzyme Finance](https://enzyme.finance/) — `sharesActionTimelock` parameter
- [ERC-7540 Draft](https://ethereum-magicians.org/t/eip-7540-asynchronous-erc-4626-tokenized-vaults/16153) — async vault standard

## Related Patterns

- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — the problem this solves
- [Premium Buffer](./pattern-premium-buffer.md) — alternative mitigation (synchronous)
- [Delta NAV Share Accounting](./pattern-delta-nav.md) — base pattern

## References

- [ERC-7540 Proposal](https://ethereum-magicians.org/t/eip-7540-asynchronous-erc-4626-tokenized-vaults/16153)
- [Yearn V3 Technical Spec](https://github.com/yearn/yearn-vaults-v3/blob/master/TECH_SPEC.md)
