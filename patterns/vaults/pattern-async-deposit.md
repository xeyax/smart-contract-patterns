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

For liquid-staking exits, the request can escrow shares and bind the claim to a
historical exchange-rate lookup at the claimable timestamp. That prevents a user
from choosing a later claim time to harvest rewards that accrued after the
cooldown basis was fixed. This should be described as pricing protection, not as
exit liveness: if claim or redeem is globally paused, the fixed basis does not
guarantee users can exit.

### Queue Pricing Caveats

Partial FIFO processing can produce different exchange rates for users in the same queue if each processed slice reads a new NAV. That may be acceptable when the queue explicitly prices each processed batch independently, but it is not the same as one epoch-wide clearing price.

Manual pull redemptions also need a rule for timing optionality. If users can choose when to pull after becoming claimable, either fix their entitlement at processing time or enforce queue order so a user cannot wait for a better claim price while others exit.

### ERC-7540 Claim-Ledger Settlement

ERC-7540-style asynchronous vaults need a claim ledger, not only a pending queue:

- Escrow assets or shares at request time.
- Fulfillment fixes the claimable entitlement before the user-controlled claim call.
- Settlement snapshots `totalAssets`, `totalSupply`, fees, and other mutable conversion terms by request or settlement id before claims.
- Cancellation is a separate pending or claimable state, not an implicit return path.
- Partial fills need weighted execution prices and must preserve solvency across the shared escrow.
- Claim rounding must not let early claimants drain dust needed by later claimants.

For RWA flows that assign off-chain or manager prices, bind every request to a durable request id and a specific price id before claim. A later user-controlled claim can be safe only if it consumes the fixed entitlement from the assigned price id instead of recalculating at claim time.

### Solver-Filled Withdrawal Queue

A withdrawal queue can let external solvers fill mature requests when the vault has configured capacity:

```text
request exit
  -> shares/assets escrowed
  -> maturity and deadline recorded
  -> solver fills within user terms
  -> user claims fixed entitlement
```

This is useful when vault assets are illiquid or bridged, but the request must snapshot user protection terms such as max loss, deadline, receiver, and payout asset. Active requests should be excluded from generic rescue or sweep functions.

### Pending-Exit Parameter Drift

If pending exits reference mutable global terms, governance can unintentionally or maliciously change the user's deal after request time. Snapshot fallback assets, max loss, deadline, fee, and queue priority per request, or require all affected pending requests to be cancelled or removed before the global parameter changes.

### Hybrid Sync/Async Mode

Synchronous deposits and redeems can coexist with async queues only when the current NAV has an explicit validity window and valuation updates cannot change NAV during that window. If the vault cannot preserve that invariant, switch to async-only mode for value-changing entry and exit.

### Epoch Calendar Changes

If claimability depends on period numbers or epoch calendars, period-duration changes are value-affecting. Stage them at future boundaries, allow only one pending calendar config at a time, and make historical lookup use the config active at the queried timestamp.

### Deferred Burn Exit Drift

Some exits lock shares or tokens at request time but burn them only at claim time. That can be safe only when the payout entitlement is fixed at request or fulfillment time and claim does not recalculate the exchange rate. Any exchange-rate drift caused by deferred burns should be explicitly modeled, bounded, and assigned to a known party.

### Beneficiary-Bound Exit Tickets

Delayed LST exits can burn shares up front and create a ticket that records beneficiary, fixed entitlement, and maturity epoch. Claim should verify reserve availability, close or zero the ticket before payment, and decrement aggregate pending-ticket amount and count. Same-epoch stake-delta timing should be accounted for when setting maturity. If claim is paused, document the liveness risk rather than presenting the model as pause-safe.

NFT-style exit tickets are a useful variant when tickets must be transferred,
partially redeemed, or tracked by id. The ticket should snapshot maturity, fee,
liability, and beneficiary or receiver semantics. Partial redemption must reduce
the remaining ticket liability before external payment, and full redemption must
burn or close the ticket.

Round-scoped receipt NFTs are a stronger form when deposits and withdrawals are
settled by discrete rounds. The receipt can be transferable before finalization,
but the settlement round must fund the collection and burn the receipt before
paying the pro-rata claim.

### Operator-Finalized Claim Ledger

When withdrawals depend on off-chain settlement or operator-supplied liquidity,
burn or escrow shares at request time and create a durable request id. The
operator can later fund explicit request ids, but the user claim must consume the
fixed entitlement recorded before claim:

```text
request withdraw
  -> burn or escrow shares
  -> record request id, owner, receiver, and fixed entitlement
operator distribution
  -> fund selected request ids
claim
  -> consume fixed entitlement and pay receiver
```

This is still an operator-liveness model. It improves traceability and prevents
claim-time repricing, but it does not remove custody risk if the operator can
delay, skip, or cancel requests without objective rules.

### Height-Interval Queue Matching

For liquid-staking queues satisfied by discrete withdrawal events, each redeem
request and withdrawal event can be represented as a cumulative height interval.
Claim then proves overlap between the request interval and one or more
withdrawal-event intervals instead of scanning the entire queue.

This supports partial claims and off-chain helper discovery, but the on-chain
claim must reject mismatched intervals, already claimed requests, and
out-of-bounds event ids.

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
- Solver-filled queues need request-time entitlement, maturity, deadline, capacity, and rescue exclusions.
- Liquid-staking FIFO batches should fix each batch's entitlement and keep claims available through deposit or staking pauses when solvent.
- Relay and restaking systems must align async settlement cadence with vault slashing, epoch finality, and validator-set capture windows.
- ERC-7540 claim ledgers should snapshot conversion terms at settlement time so user-controlled claims do not recalculate against later fees, supply, or NAV.
- Fixed-entitlement delayed withdrawals can reserve pending assets outside `totalAssets()`, but request-time pricing does not by itself remove timing advantage.
- Epoch calendar changes for pending exits need future-boundary staging and historical lookup by active config.
- Deferred-burn exits must fix payout terms before claim and document any exchange-rate drift while shares remain locked but unburned.
- Beneficiary-bound exit tickets should fix entitlement and maturity, close state before payment, and check reserve liquidity at claim.
- Failed push distributions in exit queues should become user-specific pull claims rather than harvestable yield.
- Operator-finalized withdrawal claims should record fixed request entitlements before the operator distribution step and treat unfunded requests as an exit-liveness risk.
- Height-interval redemption queues should keep cumulative request and withdrawal-event intervals immutable once claimable, and should bound claim input size or search depth.
- Round-scoped payout receipts should bind each receipt to the finalized round and burn it before payout so transferability cannot duplicate claims.

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
- Symbiotic Relay — relay epoch duration and settlement cadence must remain compatible with vault slashing windows and validator-set capture assumptions
- [Ethena](https://github.com/ethena-labs) — cooldown exits escrow user claims before delayed withdrawal
- [Maple Finance](https://github.com/maple-labs/maple-core-v2) — withdrawal queues show partial FIFO pricing and manual redemption timing caveats
- [Centrifuge](https://github.com/centrifuge/liquidity-pools) — ERC-7540 request, fulfill, cancel, and claim flows with shared escrow accounting
- Veda Plasma vaults — solver-filled withdrawal queues combine request-time terms, maturity, deadlines, capacity limits, and active-request rescue exclusions
- Stader BNBx — bounded FIFO withdrawal batches fix batch entitlement and support pause-safe claiming
- Lagoon ERC-7540 vaults — settlement snapshots assets, supply, and fee terms by request/settlement id; sync paths are gated by NAV validity and can be disabled into async-only mode
- Firelight vaults — delayed withdrawals burn shares, record fixed per-period assets and shares, exclude pending withdrawal assets from `totalAssets()`, and expose epoch-calendar update caveats
- Mantle mETH — unstake requests fix the ETH entitlement, record request terms, burn on claim, and document deferred-burn exchange-rate drift.
- Marinade — delayed unstake burns mSOL, records beneficiary-bound SOL entitlement and maturity epoch, and claims from reserve while decrementing aggregate pending balances; claim pause remains a liveness caveat
- Lista stkBNB — batched unstake distribution converts failed pushes to manual pull claims and excludes pending unstake amounts from harvestable yield
- Ondo audit-contest snapshot — RWA request ids and assigned price ids before claim; lower-confidence evidence because the package is not an official production repository
- Astherus Earn — request-numbered withdrawals are created before a bot-funded distribution step and user pull claim, showing the operator-finalized claim-ledger variant.
- Liquid Collective — redeem requests are matched to withdrawal events through cumulative interval logic with full, partial, skipped, out-of-bounds, and already-claimed statuses.
- TON liquid staking — deposit and withdrawal payout NFTs represent round-scoped claims that are funded during round finalization and burned on claim.
- [ERC-7540 Draft](https://ethereum-magicians.org/t/eip-7540-asynchronous-erc-4626-tokenized-vaults/16153) — async vault standard

## Related Patterns

- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — the problem this solves
- [Premium Buffer](./pattern-premium-buffer.md) — alternative mitigation (synchronous)
- [Delta NAV Share Accounting](./pattern-delta-nav.md) — base pattern
- [Operator-Finalized Withdrawal Claim](./pattern-operator-finalized-withdrawal-claim.md) — request ids funded by operator distribution
- [Height-Interval Redemption Queue](./pattern-height-interval-redemption-queue.md) — interval-based claim matching
- [Round-Scoped Transferable Payout Receipts](./pattern-round-scoped-transferable-payout-receipts.md) — transferable receipt NFT variant

## References

- [ERC-7540 Proposal](https://ethereum-magicians.org/t/eip-7540-asynchronous-erc-4626-tokenized-vaults/16153)
- [Yearn V3 Technical Spec](https://github.com/yearn/yearn-vaults-v3/blob/master/TECH_SPEC.md)
