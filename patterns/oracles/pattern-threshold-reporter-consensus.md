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

## Key Points

- Key duplicate submissions by reporter and report id.
- Count exact payloads or normalize values before counting.
- Apply freshness, cadence, and deviation bounds before updating accepted state.
- Allow public execution after quorum to avoid keeper monopoly.
- Treat reporter membership and threshold changes as critical governance actions.
- Serialize accepted reports when downstream execution must process them in order.

## Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| Quorum without freshness | Old values can be accepted late | Require report timestamps and max age |
| Quorum without bounds | Reporters can move state too far in one update | Combine with historical or rate limits |
| Single operator controls reporters | Quorum is only cosmetic | Monitor independence and threshold assumptions |
| No duplicate key | One reporter can satisfy quorum repeatedly | Track submissions by reporter and epoch |
| Overwritten pending report | Downstream actions skip an accepted state | Block new accepted reports until the previous one is handled |

## Source Evidence

- Rocket Pool requires trusted node submissions, rejects duplicate submissions, and accepts network balance/price updates only after matching submissions reach threshold.
- Once enough reports match, execution can be called publicly, preserving liveness if the original reporters do not execute.
- Ether.fi uses same-hash reporter quorum, blocks new reports while a prior report is unhandled, and gates downstream execution by consensus, block/slot timing, wait periods, and APR caps.

## Related Patterns

- [Historical Bounds](./pattern-historical-bounds.md) - bounds accepted report changes
- [Multi-Source Validation](./pattern-multi-source-validation.md) - compares independent sources rather than same-payload reporters
- [Oracle Centralization Risk](./risk-oracle-centralization.md) - reporter-set collusion and liveness assumptions
