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

### Why Async Eliminates Arbitrage

Oracle arbitrage requires **timing advantage** — knowing when oracle price differs from real price and acting on it. Async breaks this by removing user's control over the pricing moment.

**Key criterion: Who controls when NAV is calculated?**

| NAV calculated at | User controls claim timing? | Protection |
|-------------------|---------------------------|------------|
| Request time | Any | ❌ None — user knows price at request |
| Claim time | Yes, freely | ❌ None — user waits for favorable price |
| Claim time | No (auto/fixed window) | ✅ Yes — user can't choose moment |
| Epoch boundary | N/A (fixed by protocol) | ✅ Yes — all users get same price |

**The mechanism matters:** Simple "wait 24h" doesn't work if user can choose when to claim. True protection requires removing user's ability to select the pricing moment.

---

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

Shares issued immediately but locked for a period. See [Timelock on Shares](./pattern-timelock-shares.md) for full details.

**Important limitation:** Timelock does NOT prevent unfair share allocation — attacker still gets more shares than deserved, just can't exit instantly. It primarily prevents flash loan attacks.

### Approach 4: Batch Queue Settlement

Requests are accumulated in a queue and processed as an explicit batch:

```
1. Users request deposits or redemptions
   → assets or shares are escrowed
   → request ids define ordering

2. Manager/keeper processes a bounded id range
   → all included requests share one execution price
   → shares/assets distributed pro-rata across included requests

3. Skipped requests remain pending or become refundable
   → bypass rules must be objective and bounded
```

**Why it works:** Users in the same processed batch cannot choose a favorable pricing moment. The manager can net flows and prepare liquidity, but must not be able to cherry-pick only favorable users without a documented bypass rule.

### Approach 5: Cooldown Escrow Exit

Shares or assets can be moved into an escrow during a cooldown period:

```
1. User requests exit
   -> shares are burned or escrowed
   -> claim amount or claim basis is recorded

2. Cooldown elapses
   -> user claims assets from the escrow path
   -> protocol cannot redeploy the reserved amount as free liquidity
```

This works only if the claim basis is fixed or the later pricing moment is not user-selectable. A simple cooldown followed by a discretionary user claim can preserve timing optionality if the user can wait for a favorable exchange rate.

### Queue Pricing Caveats

Partial FIFO processing can produce different exchange rates for users in the same queue if each processed slice reads a new NAV. That may be acceptable when the queue explicitly prices each processed batch independently, but it is not the same as one epoch-wide clearing price.

Manual pull redemptions also need a rule for timing optionality. If users can choose when to pull after becoming claimable, either fix their entitlement at processing time or enforce queue order so a user cannot wait for a better claim price while others exit.

### Public Gas-Bounded Settlement

For queues that need regular processing, make settlement callable by anyone with an explicit maximum:

```solidity
function settle(uint256 maxRequests) external {
    uint256 processed;
    while (processed < maxRequests && _hasPendingRequest() && _hasCapacity()) {
        _settleNextRequest();
        processed++;
    }
}
```

This avoids keeper monopoly and prevents a growing queue from making settlement uncallable. If settlement can be disabled, the disable switch should have the same scrutiny as pausing withdrawals because it can affect exit liveness.

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

### Withdrawal Queue Finalization

Async withdrawals need additional liveness and accounting checks:

- Finalization must be gas-bounded: process explicit ranges or batches, not the entire queue.
- If batch calculation happens off-chain, reconstruct enough state on-chain to reject invalid batches.
- Claiming should not depend on a paused deposit path when solvency allows claims.
- Bypass mechanisms need objective thresholds; otherwise a manager can starve large or unfavorable requests.
- Pending exits may remain liable for losses or slashing until final claim, depending on the protocol's risk model.
- Public settlement should accept a max count or explicit id range and stop cleanly when capacity is exhausted.
- If assets are scarce, refill a [Withdrawal Liquidity Buffer](./pattern-withdrawal-liquidity-buffer.md) before deploying surplus capital.
- Delayed unstaking can burn shares immediately, escrow assets in a manager, and allow claim after a delay; cancellation rules must be explicit and value-neutral.
- Escrowed redemption flows can transfer shares/tokens into a redemption contract, let an operator execute and burn them, and allow public timeout refunds if execution stalls.
- Cooldown escrow exits should fix the claim basis before the user can choose a later claim time.
- Partial queue processing must document whether each processed slice or the whole queue receives one exchange rate.

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
- [Lido](https://github.com/lidofinance/core) — withdrawal queue finalization uses bounded batches and queue invariants
- [Rocket Pool](https://github.com/rocket-pool/rocketpool) — public bounded deposit assignment drains queues without requiring a privileged keeper
- [Renzo](https://github.com/Renzo-Protocol/contracts-public) — withdrawal deficits are refilled before new assets are delegated
- [Reserve Index DTF](https://github.com/reserve-protocol/reserve-index-dtf) — delayed unstaking burns shares, creates claim locks, and allows cancellation
- [Symbiotic](https://github.com/symbioticfi/core) — pending withdrawals remain slashable until epoch finality
- [Ethena](https://github.com/ethena-labs) — cooldown exits escrow user claims before delayed withdrawal
- [Maple Finance](https://github.com/maple-labs/maple-core-v2) — withdrawal queues show partial FIFO pricing and manual redemption timing caveats
- [ERC-7540 Draft](https://ethereum-magicians.org/t/eip-7540-asynchronous-erc-4626-tokenized-vaults/16153) — async vault standard

## Related Patterns

- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — the problem this solves
- [Premium Buffer](./pattern-premium-buffer.md) — alternative mitigation (synchronous)
- [Delta NAV Share Accounting](./pattern-delta-nav.md) — base pattern

## References

- [ERC-7540 Proposal](https://ethereum-magicians.org/t/eip-7540-asynchronous-erc-4626-tokenized-vaults/16153)
- [Yearn V3 Technical Spec](https://github.com/yearn/yearn-vaults-v3/blob/master/TECH_SPEC.md)
