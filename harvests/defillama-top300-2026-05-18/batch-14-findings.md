# Batch 14 Findings

Expanded discovery inspected 11 additional public source repositories across Solana AMMs, appchain perps, Bitcoin and EVM bridges, vaults, and lending backstops. BENQI was cloned for a future pass, but the initial lending/vault subagent errored before producing evidence, so it is not counted in this batch.

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Orca DEX | `orca-so/whirlpools` | `a119d79` | Concentrated-liquidity fee snapshots and Token-2022 policy |
| Meteora AMM | `MeteoraAg/damm-v2` | `58a13fc` | Activation-scoped fee scheduling and transfer-fee normalization |
| Drift Protocol | `drift-labs/protocol-v2` | `0ae3e3b` | Deferred; perps source not inspected deeply enough |
| dYdX V4 | `dydxprotocol/v4-chain` | `5ee9766` | Appchain CLOB settlement, liquidation, and OI-scaled margin |
| Stacks sBTC | `stacks-network/sbtc` | `a97172e` | Signer-mediated withdrawal escrow and reserve limits |
| xDAI Stake Bridge | `gnosischain/tokenbridge-contracts` (`xdaibridge`) | `52afd25` | USDS migration, route compatibility, and claim liveness |
| Stargate V2 | `stargate-protocol/stargate-v2` | `8c41a96` | Path credits and bridge cutover playbooks |
| fx Protocol | `AladdinDAO/fx-protocol-contracts` | `5e198e9` | Deferred; not enough line-level evidence in this pass |
| QuickSwap Periphery | `QuickSwap/quickswap-periphery` | `522a941` | Rejected/deferred as router overlap |
| Yearn V3 | `yearn/yearn-vaults-v3` | `104a2b2` | Locked-profit shares and unlock governance caveats |
| Blend Pools V2 | `blend-capital/blend-contracts-v2` | `ba22b48` | Backstop bad debt and two-sided auction scaling |

## Accepted Catalog Updates

- Added perps patterns for proposer-validated MemCLOB settlement, bounded orderbook liquidation/deleveraging, and open-interest-scaled margin requirements.
- Added a liquidity pattern for activation-scoped launch fee scheduling.
- Updated concentrated-liquidity docs with Orca fee-growth and tick-crossing evidence.
- Updated Token-2022 transfer-fee guidance with extension badges and partial-fill normalization.
- Updated bridge docs for signer-mediated withdrawal escrow, signer-side reserve limits, output-asset binding during migration, xDAI route compatibility, Stargate cutover sequencing, and path-scoped credits.
- Updated Yearn locked-profit smoothing with locked-share fee/loss offsets and zero-duration unlock caveats.
- Updated lending loss and auction docs with Blend's backstop-assigned bad debt and two-sided block-scaled auction fill rules.
- Updated `ANTIPATTERNS.md` to make output-asset binding explicit for cross-chain signature or message scopes during collateral migrations.

## Rejected Or Deferred Candidates

- Drift Protocol V2 remains queued for a deeper perps pass; no catalog claim was accepted from the narrowed scan.
- dYdX proposal-coupled oracle validation and epoch funding premium aggregation were deferred as strong future candidates but outside the three-pattern cap for this pass.
- Orca adaptive fees, PDA oracle state, trade-enable timestamp, and tick-array traversal were treated as overlap with existing dynamic-fee and tick-crossing docs.
- Meteora volatility accumulator fees and rewards overlapped existing dynamic-fee and reward-index docs.
- Gnosis Hashi sidecar validation was not accepted as positive quorum evidence because the inspected configuration did not make it mandatory.
- AladdinDAO fx and QuickSwap Periphery did not receive accepted updates due insufficient evidence or category overlap.
- Yearn function-specific role bitmaps and clone factories were rejected as existing access-control and clone-factory coverage.
- Blend pool-factory guardrails were deferred to a broader Blend pass because the accepted bad-debt and auction updates were stronger.

## Contradiction Review

- dYdX MemCLOB settlement is scoped to appchains with consensus-coupled proposer operations, not general AMM orderbook maintenance.
- Open-interest-scaled margin is framed as a soft margin curve, not a hard exposure cap.
- Meteora launch fee scheduling is a launch/activation tool, not a generic oracle or volatility safety guarantee.
- sBTC signer-side reserve limits are documented as signer-policy controls, not on-chain proof of backing.
- Stargate path credits are treated as shared-liquidity accounting and do not eliminate bridge finality or migration risks.
- Yearn zero-duration profit unlock is explicitly value-affecting governance behavior, not a smoothing guarantee.
- Blend backstop assignment delays terminal default; it is not described as immediate supplier haircut.

## Verification

- Dry-run harvest subagents compared candidates against the catalog and anti-patterns before edits.
- Catalog index regeneration and staged markdown validation were run before commit.
