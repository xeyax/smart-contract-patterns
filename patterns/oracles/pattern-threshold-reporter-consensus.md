# Threshold Reporter Consensus

> Require a quorum of permissioned reporters to submit the same oracle payload before mutating accepted protocol state.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, quorum, reporters, consensus, accepted-state |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A protocol has a trusted reporter set for off-chain observations
- Updates should mutate accepted state, not only expose a price read
- Values are expensive or impossible to verify fully on-chain
- Public execution after quorum improves liveness

## Avoid When

- The source can be verified cryptographically on-chain
- A single external feed with explicit freshness is sufficient
- Reporter membership is centralized and cannot be monitored

## Trade-offs

**Pros:**
- Rejects unilateral reporter mistakes
- Separates submission from execution
- Lets any caller execute once quorum is reached
- Works for balances, rates, prices, and other state reports

**Cons:**
- Reporter collusion remains a trust assumption
- Liveness depends on enough active reporters
- Same-payload quorum can reject legitimate small discrepancies
- Membership changes can affect pending votes

## How It Works

Reporters submit a payload keyed by report timestamp or epoch. The protocol counts identical payloads and accepts the value only when the threshold is reached.

```solidity
function submitReport(uint256 epoch, bytes32 payloadHash, Report calldata report) external onlyReporter {
    require(!submitted[epoch][msg.sender], "duplicate");
    require(_hash(report) == payloadHash, "bad hash");

    submitted[epoch][msg.sender] = true;
    voteCount[epoch][payloadHash] += 1;

    if (voteCount[epoch][payloadHash] >= threshold) {
        pending[epoch] = report;
    }
}

function executeReport(uint256 epoch) external {
    Report memory report = pending[epoch];
    require(report.timestamp != 0, "no quorum");
    _validateBounds(report);
    _updateAcceptedState(report);
}
```

### Serialized Downstream Execution

If accepted reports drive later protocol actions, the oracle should prevent a newer report from superseding a pending one before downstream execution is handled:

```solidity
require(!hasUnhandledReport, "previous report pending");
pendingReport = report;
hasUnhandledReport = true;
```

The executor can then enforce slot, block, wait-period, or rate-limit checks before finalizing the state transition.

### Same-Block Settlement Fence

When accepted reports update reward indexes, Merkle roots, migrations, or other claim-critical state, dependent actions can be blocked until a later block:

```solidity
require(lastReportBlock < block.number, "same block report");
```

This reduces same-block sandwiching around public report execution, at the cost of one-block latency.

### Signed Payload Quorum

Some systems submit one payload with several reporter signatures instead of
separate on-chain submissions. The same consensus requirements still apply:
reject duplicate signers, bind deadline and timestamp, enforce monotonic updates
and stale checks, and validate confidence or heartbeat bounds before accepting
the payload.

### Merkle-Rooted Epoch Sidecar Variant

Canonical epoch feed data can be verified against a relay Merkle root while a
trusted-provider sidecar submits comparable values in the prior-round window.
The sidecar should reject duplicate providers, require minimum turnout, compute
a median, and reject medians whose neighboring submissions exceed a spread cap.

## Key Points

- Key duplicate submissions by reporter and report id.
- Count exact payloads or normalize values before counting.
- Apply freshness, cadence, and deviation bounds before updating accepted state.
- For signed collateral or balance attestations, require sorted unique reporters, monotonic per-reporter timestamps, and an accepted report time derived from the minimum valid signer timestamp.
- For block-range reports, align report windows deterministically and reject gaps, overlaps, future/freshness violations, and non-finalized source ranges.
- Allow public execution after quorum to avoid keeper monopoly.
- Treat reporter membership and threshold changes as critical governance actions.
- Serialize accepted reports when downstream execution must process them in order.
- Add a same-block settlement fence when report execution changes rewards, claim roots, transfers, or migration prices that users can act on immediately.
- Add a downstream quarantine or pause path when an agreed payload fails protocol sanity checks; same-payload quorum proves reporter agreement, not report safety.
- For signed-payload quorum, sort or otherwise deduplicate signers before counting and bind signatures to the exact feed, timestamp, deadline, and payload fields.
- For Merkle-rooted sidecars, bind values to an epoch or voting round and test timestamp monotonicity for both canonical and trusted-provider prices.
- Validator-set reports should bind the validator root, deadline, and intended vault or module action into the signed or quorum payload so accepted data cannot be replayed into a different operator action.

## Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| Quorum without freshness | Old values can be accepted late | Require report timestamps and max age |
| Quorum without bounds | Reporters can move state too far in one update | Combine with historical or rate limits |
| Single operator controls reporters | Quorum is only cosmetic | Monitor independence and threshold assumptions |
| No duplicate key | One reporter can satisfy quorum repeatedly | Track submissions by reporter and epoch |
| Overwritten pending report | Downstream actions skip an accepted state | Block new accepted reports until the previous one is handled |
| Agreement without report-window continuity | Sparse off-chain state can skip events | Require contiguous finalized ranges |

## Source Evidence

- Rocket Pool requires trusted node submissions, rejects duplicate submissions, and accepts network balance/price updates only after matching submissions reach threshold.
- Once enough reports match, execution can be called publicly, preserving liveness if the original reporters do not execute.
- Ether.fi uses same-hash reporter quorum, blocks new reports while a prior report is unhandled, and gates downstream execution by consensus, block/slot timing, wait periods, and APR caps.
- StakeWise V2 prevents reward reports and dependent reward, Merkle, transfer, claim, or migration actions from finalizing in the same block.
- M0 validates sorted unique reporter signatures, stores monotonic per-reporter timestamps, uses the minimum valid signer timestamp for accepted collateral reports, and rejects stale reports relative to dependent state.
- Mantle mETH tracks duplicate and replacement reports per reporter, aligns report windows, forwards only after quorum, and quarantines or pauses downstream state when accepted payloads fail sanity checks.
- Derive V2/Lyra feed contracts accept signed oracle payloads with reporter threshold checks, duplicate rejection, deadline and timestamp binding, stale checks, monotonic updates, confidence bounds, and settlement heartbeat validation in [`src/feeds`](https://github.com/derivexyz/v2-core/blob/96796a61dcb1dc852e25518b00cc1a79fb3caeeb/src/feeds).
- Flare FAssets `FtsoV2PriceStore` verifies epoch feed values against a relay Merkle root, accepts trusted-provider submissions in a bounded prior-round window, rejects duplicates, computes a median, and enforces spread and timestamp invariants in [`contracts/ftso/implementation/FtsoV2PriceStore.sol`](https://github.com/flare-foundation/fassets/blob/37c1be508a33c0d0ce31216aef45958fd4e5281e/contracts/ftso/implementation/FtsoV2PriceStore.sol).
- StakeWise V3 separates keeper oracle, rewards, and validator payload handling across [`contracts/keeper/KeeperOracles.sol`](https://github.com/stakewise/v3-core/blob/31b2da5e9c729b00ead0db16369141608410bee8/contracts/keeper/KeeperOracles.sol), [`contracts/keeper/KeeperRewards.sol`](https://github.com/stakewise/v3-core/blob/31b2da5e9c729b00ead0db16369141608410bee8/contracts/keeper/KeeperRewards.sol), and [`contracts/keeper/KeeperValidators.sol`](https://github.com/stakewise/v3-core/blob/31b2da5e9c729b00ead0db16369141608410bee8/contracts/keeper/KeeperValidators.sol).
- Puffer guardian validation signs or approves validator operations through [`mainnet-contracts/src/GuardianModule.sol`](https://github.com/PufferFinance/puffer-contracts/blob/380600060cd231fd8616ba167e674d4140486dbb/mainnet-contracts/src/GuardianModule.sol), making signer quorum and payload binding part of validator lifecycle safety.

## Related Patterns

- [Historical Bounds](./pattern-historical-bounds.md) - bounds accepted report changes
- [Multi-Source Validation](./pattern-multi-source-validation.md) - compares independent sources rather than same-payload reporters
- [Oracle Centralization Risk](./risk-oracle-centralization.md) - reporter-set collusion and liveness assumptions
