# Pattern Library Index

> Auto-generated from pattern metadata. Regenerate: `python3 scripts/generate-pattern-index.py`

## access-control

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-address-prefix-subaccount-namespace.md | Encode small virtual subaccounts in low address bits and bind them to a first-use owner namespace. | Users need multiple isolated account slots under one wallet identity |
| pattern-block-scoped-mint-redeem-throttle.md | Bound total minting and redemption per block so a hot operator or signer cannot move more than the configured amount inside one block. | A privileged minter, redeemer, bridge, or issuer can change supply quickly |
| pattern-bootstrap-authority-handoff.md | Let a factory hold temporary setup authority only long enough to wire a contract graph, then transfer all lasting roles to the intended owner. | A factory deploys multiple contracts that must be configured atomically |
| pattern-bounded-timelocked-parameter-change.md | Require critical parameter changes to be committed, delayed, bounded, and explicitly applied before they affect protocol economics. | Parameters affect fees, amplification, rates, caps, or admin recipients |
| pattern-break-glass-risk-limiter.md | Give an emergency role narrowly scoped powers to reduce risk limits or disable risky routes without granting the power to re-enable them. | Operators need to react faster than governance during suspected compromise or market stress |
| pattern-clarity-trait-cohort-validation.md | Validate a caller-supplied cohort of trait-typed Clarity contracts by checking each contract identity against configured roles before using the cohort. | A Clarity entrypoint receives trait-typed token, oracle, or wrapper contracts |
| pattern-consumer-scoped-rate-limiter.md | Apply token-bucket limits per approved consumer or route so one actor cannot exhaust shared capacity for unrelated flows. | Multiple protocol components share a constrained operation such as instant redemption, bridge egress, or privileged cons |
| pattern-erc1271-replay-safe-account-signatures.md | Wrap arbitrary external hashes in an account-specific EIP-712 domain before a smart account returns ERC-1271 signature validity. | Smart accounts expose `isValidSignature(bytes32,bytes)` for external protocols |
| pattern-frame-scoped-callback-capability.md | Authorize a callback only for the current execution frame, then clear the capability as soon as it is consumed. | A protocol intentionally cedes control to an external callback during an operation |
| pattern-hook-validated-subaccount-ledger.md | Keep multi-asset subaccount balances in a core ledger while managers and asset hooks validate every transfer batch. | Accounts hold many asset balances under one subaccount id; Transfers must be validated by a manager or risk engine |
| pattern-mutual-parameter-acceptance.md | Require both affected parties to accept shared economic parameters before the new values take effect. | A parameter affects two independent parties, such as manager and user, partner and protocol, or splitter recipients |
| pattern-mutually-exclusive-entity-protocol-allowlist.md | Separate human or legal-entity eligibility from protocol-contract eligibility so one address cannot silently hold both identities. | Regulated tokens distinguish investor/entity eligibility from protocol-contract eligibility |
| pattern-participant-permission-bitmap.md | Encode participant eligibility as compact policy bits so deposits, borrows, transfers, and exits can enforce both account-level and pool-level access. | A pool has private, public, pool-level, or function-level participation modes |
| pattern-pda-scoped-protocol-authority.md | Derive Solana protocol authorities and custody accounts from canonical PDA seeds, then verify every account against the stored authority graph. | A Solana program owns token vaults, mints, obligations, or market authority through PDAs |
| pattern-position-scoped-manager-receiver.md | Delegate position management with separate add/remove privileges and explicit receiver rules for value leaving the position. | A user-owned position can be managed by another account or automation service |
| pattern-scoped-chain-id-bypass-for-wallet-maintenance.md | Allow replayable smart-wallet maintenance only through self-calls, selector allowlists, and reserved nonce domains, never through arbitrary value execution. | A smart account needs the same owner-maintenance operation on multiple chains |
| pattern-selector-scoped-authority.md | Grant operators permission to call specific function selectors on specific targets instead of granting broad owner or admin authority. | Operators need to run recurring maintenance or risk-management calls |
| pattern-self-authenticated-key-registry.md | Let operators register protocol keys only after proving control of the key, then snapshot key history for epoch-scoped verification. | Operators need off-chain signing, consensus, or relay keys distinct from owner accounts |
| pattern-shared-component-reentrancy-lock.md | Put related protocol components behind one shared reentrancy status so callbacks cannot bypass a per-contract lock by entering a sibling component. | Several components share accounting assumptions or token custody; External callbacks can enter more than one component |
| pattern-solana-account-cohort-validation.md | Validate every passed Solana account as part of the expected account cohort before trusting its data, authority, or balance. | A Solana instruction receives many accounts from the caller |
| pattern-timelocked-spell-authority.md | Grant authority to scheduled action contracts only after a delay, with cancelability and separate emergency pause controls. | A system is immutable or proxyless but still needs controlled authority changes |
| pattern-two-step-authority-handoff.md | Stage critical authority or withdrawal-address changes and require confirmation by the new address before activation. | A privileged role controls upgrades, pausing, treasury movement, or withdrawal addresses |
| pattern-two-step-delegated-order-signer.md | Let an account authorize a delegate signer only after both the account and signer confirm the delegation. | Smart-contract accounts need an EOA signer for typed orders |
| pattern-wallet-native-automation-auth-adapter.md | Execute automation through each user's wallet-native permission model instead of asking wallets to trust one global executor shape. | Automation must act through user-owned wallets or proxies |

## automation

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-changeable-trigger-gate.md | Require every strategy trigger to pass, then atomically update only the selected mutable trigger state during execution. | Automated strategies depend on multiple trigger conditions |
| pattern-cranked-validator-set-maintenance.md | Maintain large validator sets through an explicit on-chain phase machine with bounded per-validator cranks and epoch gates. | Validator-set maintenance cannot fit in one transaction or instruction |
| pattern-hash-anchored-strategy-subscription.md | Store only a wallet-bound strategy hash on-chain while bots supply the full strategy data and must match the committed hash before execution. | Automation strategies contain large trigger and action structs; Users or wallets subscribe to immutable strategy terms |
| pattern-registry-routed-wallet-recipes.md | Execute user-wallet recipes by resolving stateless action modules from a registry and piping typed outputs between steps. | Users execute multi-step DeFi operations through their own wallet or proxy |

## cross-chain

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-authenticated-root-child-tunnel.md | Pair root and child tunnel contracts so each side accepts messages only from the canonical bridge and configured peer tunnel. | A protocol exposes generic cross-chain message tunnels instead of one fixed bridge action |
| pattern-authorized-shared-bridge-lockbox.md | Centralize native-asset bridge custody in a lockbox whose authorized portals and migrations are bounded by shared ownership and configuration checks. | Multiple bridge portals or proof systems need to share native-asset liquidity |
| pattern-bitcoin-spv-state-transition-gate.md | Gate bridge state transitions on Bitcoin transaction, merkle, coinbase, and difficulty proofs while documenting maintainer trust boundaries. | An EVM bridge must verify Bitcoin deposits, sweeps, redemptions, or fraud evidence |
| pattern-bridge-owned-mintable-token-pair.md | Represent bridged assets with mintable tokens whose bridge and remote-token identity are immutable and checked on every mint or burn path. | A canonical bridge mints a destination representation of a remote token |
| pattern-bridged-governance-timelock-receiver.md | Receive governance messages from a canonical bridge, validate the root timelock sender, and queue actions into a local timelock before execution. | Root governance lives on one chain and controls deployments on another |
| pattern-canonical-bridge-counterpart-validation.md | Authenticate both the canonical bridge messenger and the remote application counterpart before finalizing cross-chain messages. | Application contracts receive messages through a canonical rollup or bridge messenger |
| pattern-chain-bound-request-hash.md | Bind cross-chain requests to source chain, destination chain, nonce, operation, participants, value, and payload before accepting remote confirmation. | A bridge mints, burns, unlocks, or confirms value on another chain |
| pattern-checkpointed-receipt-exit-proof.md | Finalize exits by proving a source-chain receipt log inside a finalized checkpoint before releasing or minting destination assets. | Users exit from a child chain or rollup by proving a burn or message event |
| pattern-covenant-gated-bitcoin-staking-output.md | Represent native Bitcoin stake with a Taproot output whose timelock, unbonding, and slashing leaves are validated before app-chain voting power is activated. | A protocol wants native BTC economic security without bridging BTC custody |
| pattern-custodian-attested-mint-burn.md | Mint and burn wrapped assets through merchant requests that are approved and reconciled by a trusted custodian. | The source asset is not trustlessly verifiable on the destination chain |
| pattern-deterministic-cross-chain-factory.md | Deploy peer contract systems at predictable addresses across chains so cross-chain configuration can be precomputed and verified. | The same protocol graph is deployed on multiple chains |
| pattern-dispute-game-gated-withdrawal-finality.md | Finalize rollup withdrawals only after the referenced output root is proven, mature, and accepted by the active dispute-game system. | A rollup bridge releases assets from L2 withdrawal proofs on L1 |
| pattern-dispute-windowed-operator-batch-bridge.md | Let an operator commit batched bridge transfers, then delay execution behind a dispute window where a crew or guardian can stop a bad batch. | A bridge is intentionally operator-mediated rather than proof-verified |
| pattern-domain-scoped-bridge-custody-ledger.md | Hold shared source-chain bridge custody while accounting each destination domain's spendable balance separately. | One bridge escrow holds the same token for multiple destination domains |
| pattern-domain-scoped-message-root-accumulator.md | Accumulate cross-chain message roots by domain and checkpoint combined roots for replay-safe inclusion proofs. | Messages are batched into roots before being proven on another domain |
| pattern-escrow-mint-burn-refund-fallback.md | Pair source escrow or burn with destination validation and automatic refund when bridge settlement cannot safely mint or release. | Bridge deposits lock or burn assets before destination settlement |
| pattern-fraud-window-gated-message-finality.md | Finalize optimistic rollup withdrawals only after the referenced state root is outside the fraud window and the message-passer storage proof verifies. | A legacy optimistic rollup bridge releases L1 assets from L2 withdrawal proofs |
| pattern-liquidity-captain-storage-proof-bridge.md | Let users assign a liquidity captain to front destination liquidity, then reimburse the captain after proving source-chain bridge state. | Destination users need faster liquidity than canonical settlement provides |
| pattern-multi-adapter-message-quorum.md | Send cross-chain messages through multiple bridge adapters and execute only after a session-scoped quorum confirms the same payload. | A protocol cannot rely on one bridge transport for high-value state changes |
| pattern-optimistic-mint-with-debt-reconciliation.md | Mint bridge assets before final settlement under bounded role risk, then repay that optimistic debt when the source-chain proof is finalized. | Final source-chain settlement is slow but deposit discovery can be validated earlier |
| pattern-predicate-mediated-bridge-custody.md | Route bridge deposits and exits through token-specific predicates that own custody rules while a root manager owns mapping and proof orchestration. | A bridge supports multiple token standards or custody modes; Deposit/exit proof orchestration is shared across assets |
| pattern-receipt-acknowledged-relayer-rewards.md | Lock message fees on send and release relayer rewards only after an authenticated reverse receipt confirms delivery. | Cross-chain messages are delivered by third-party relayers |
| pattern-recipient-scoped-message-verifier.md | Let each cross-chain message recipient choose its verifier while a generic mailbox enforces versioning, destination domain, and exact-once delivery. | A shared mailbox delivers messages for many applications |
| pattern-retryable-cross-domain-message-ledger.md | Record successful and failed cross-domain message executions so failed deliveries can be retried while successful deliveries remain exact-once. | Cross-domain messages execute arbitrary destination calls |
| pattern-self-describing-utxo-deposit-reveal.md | Encode depositor, wallet, refund, and routing terms into a Bitcoin deposit script, then reveal and sweep that UTXO with proof-based settlement. | A bridge accepts deposits from a UTXO chain into an account-based chain |
| pattern-signed-custody-routed-mint.md | Authorize mint and redeem orders with typed signatures that bind route, custodian allocation, nonce, expiry, and asset ratios before custody-backed settlement. | Tokens are minted or redeemed against off-chain or custodied reserves |
| pattern-sovereign-bridge-local-balance-tree.md | Track bridge-owned local token balances in a Merkle tree when a sovereign chain cannot or should not mint wrapped supply. | A sovereign chain bridge handles assets it cannot freely mint and burn |
| pattern-stake-backed-dvn-verifier-adapter.md | Plug an external stake-backed validator-set proof into a bridge verifier lane, then forward the verified packet to the canonical receive library. | A bridge or messaging layer supports custom verifier lanes |
| pattern-threshold-custody-wallet-lifecycle.md | Manage bridge custody through rotating threshold-signer wallets with explicit states, liveness timeouts, moving-funds transitions, and fraud challenges. | A bridge custody account is controlled by a threshold signer group |
| pattern-token-owned-bridge-registration.md | Let token contracts opt into bridge mappings while preventing unauthorized peer remapping after registration. | Tokens choose custom bridge gateways or remote token implementations |
| pattern-value-tiered-source-finality.md | Scale required source-chain confirmation depth with the value being minted, released, or credited. | A bridge or staking system accepts probabilistic-finality source-chain transactions |
| pattern-version-gated-message-endpoint-registry.md | Register immutable messenger endpoint versions and let applications accept only registry-known endpoints at or above a monotonic minimum version. | A cross-chain messaging protocol deploys immutable endpoint contracts by version |

### Risks

| File | Triggered When |
|------|---------------|
| risk-bridge-exit-cutover-custody-drain.md | A bridge disables old exits during migration; Predicate or gateway custody can be moved to a new bridge |

### Requirements

| File | Applies To |
|------|-----------|
| req-bridge-exit-liveness.md | R1: Pauses Preserve Safe Exit Paths, R2: Failed Destination Settlement Has A Refund Path, R3: Migration Accounts For In-Flight Messages, R4: Admin Overrides Are Explicitly Trusted, R5: Emergency Exit Pauses Are Scoped And Expiring |
| req-custodial-reserve-backing.md | R1: Full Backing, R2: Public Verifiability, R3: Settlement Traceability, R4: Operational Liveness, R5: Reserve-Gated Minting Fails Closed, R6: Signing Policy Respects Reserve Limits, R7: Migration Preserves Backing |
| req-proof-bridge-exit-safety.md | R1: Source Proof Is Finalized, R2: Exit Nullifier Is Unique And Normalized, R3: Emitter And Event Are Authenticated, R4: Custody Is Sufficient Before Release, R5: Migration Cutovers Preserve Pending Exits, R6: Challenge Or Relay Finality Is Explicit |

## governance

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-bounded-token-inflation.md | Constrain privileged token minting with explicit rate, amount, recipient, and delay bounds so governance cannot silently create unlimited supply. | Governance or a rewards controller can mint protocol tokens; Inflation is expected but should be predictable |
| pattern-capped-linear-voting-escrow.md | Mint non-transferable voting power that accrues linearly from staked principal up to a configured cap and burns on unstake. | Governance wants longer participation to earn more voting weight |
| pattern-composable-voting-power-calculator.md | Compute voting power from normalized token, vault, price, and weight components behind explicit calculator modules. | Voting power depends on several tokens, vault shares, or restaked positions |
| pattern-condition-gated-deadlock-tiebreaker.md | Grant a narrow committee recovery powers only after objective deadlock conditions and timeouts prove normal governance cannot progress. | Governance can become blocked by an exit, pause, or veto state |
| pattern-dynamic-power-gauge-allocation.md | Store user gauge preferences as basis-point weights while deriving effective gauge votes from current voting power. | Users allocate changing voting power across gauges or reward nodes |
| pattern-epoch-committed-validator-set-header.md | Commit each epoch's validator-set root, quorum rule, key tag, and capture timestamp before verifying epoch-scoped messages. | A relay or settlement layer verifies messages against changing validator sets |
| pattern-global-settlement-state-machine.md | Shut down a protocol through explicit phases that freeze new risk, snapshot prices, process positions, compute redemption rates, and let claimants redeem. | A system needs a credible emergency shutdown path; Liabilities must be redeemed against remaining collateral |
| pattern-local-settlement-rage-quit-escrow.md | Resolve a governance dispute by moving locked stakeholder claims into an immutable local exit escrow while the main system continues with a fresh signaling escrow. | A veto or dispute mechanism must offer an exit without globally shutting down the protocol |
| pattern-proposal-embedded-execution-guards.md | Include guard calls inside executable governance proposals so final dynamic conditions are checked atomically at execution time. | Proposal validity depends on dynamic state at execution time |
| pattern-stakeholder-extensible-governance-timelock.md | Let economically exposed stakeholders lock claims into a signaling escrow that extends proposal delay and can escalate to an exit path. | Token governance can execute actions that affect another stakeholder class |

### Risks

| File | Triggered When |
|------|---------------|
| risk-exit-dependent-governance-deadlock.md | Veto, rage-quit, or emergency governance depends on users exiting before proposals proceed |
| risk-supply-referenced-veto-support-drift.md | Veto support is measured as a percentage of token supply, shares, or withdrawal claims |
| risk-uncapped-chain-voting-power-concentration.md | Validator-set power is aggregated from multiple chains or subnetworks |

### Requirements

| File | Applies To |
|------|-----------|
| req-veto-governance-liveness-and-exit-safety.md | R1: Proposal Scheduling Remains Bounded, R2: Exit Escalation Has One Clear Active Cohort, R3: Exit Processing Is Public And Bounded, R4: Deadlock Recovery Is Objective |

## lending

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-balance-sheet-solvency-gate.md | Gate stablecoin issuance and reserve allocation against protocol-level assets, liabilities, risk-weighted assets, and liquidity ratios. | A protocol issues stablecoin or credit through multiple modules |
| pattern-band-ranged-soft-liquidation-amm.md | Liquidate collateral gradually by placing it across oracle-priced AMM bands before hard liquidation is needed. | A collateralized debt protocol wants smoother liquidation than a single auction or seizure point |
| pattern-bounded-rate-source-adapter.md | Convert an external benchmark or savings rate into a lending rate only after applying freshness, bounds, spread, and fallback rules. | Borrow or supply rates should follow an external benchmark |
| pattern-callback-funded-lending-settlement.md | Let a lending action call a borrower, supplier, or liquidator callback, then atomically pull or verify the owed assets before the action completes. | Lending actions need composable funding from another protocol in the same transaction |
| pattern-compressed-amount-storage-directional-rounding.md | Store large lending amounts in compressed form only when every rounding direction is explicit, conservative, and tested at dust boundaries. | A lending core packs many amounts into storage-constrained slots; Exact full-precision storage would be too expensive |
| pattern-comptroller-risk-gate.md | Route market actions through a central risk module that approves borrows, redeems, transfers, and liquidations before state changes. | A lending protocol has multiple collateral and borrow markets |
| pattern-debt-converting-flash-loan.md | Allow unpaid flash-loan principal to become normal borrow debt only after the same risk, fee, callback, and accounting checks as an ordinary borrow. | Flash borrowers should be able to keep part of the borrowed amount as debt |
| pattern-deferred-status-check-frame.md | Batch lending operations can defer account and vault status checks until the outer execution frame exits, then validate every touched account before state is released. | Users need batch operations that temporarily move through an unsafe intermediate state |
| pattern-dual-asset-stability-buffer.md | Hold both volatile collateral and stable liquidity so redemptions, rebalances, or liquidations can consume the safest buffer first. | A stablecoin or lending pool holds yield-bearing or volatile collateral |
| pattern-dust-aware-liquidation-cap.md | Bound in-flight liquidation debt and fail partial liquidations that would leave uneconomic dust positions or null auctions. | Liquidations create auctions or protocol inventory that has operational capacity |
| pattern-elevation-scoped-borrow-mode.md | Allow higher borrow power only inside a constrained collateral group with one debt asset and explicit group-level risk limits. | A lending market wants higher LTV for tightly related collateral |
| pattern-explicit-bad-debt-realization.md | When liquidation cannot cover debt, reduce market supply and borrow totals immediately so insolvency is visible instead of hidden in stale accounting. | Liquidation can leave debt uncovered after seizing all collateral |
| pattern-hint-assisted-risk-ordered-position-list.md | Maintain liquidation or redemption priority in a sorted position list while callers supply hints to avoid full scans. | Position priority depends on a sortable risk metric such as collateral ratio or interest rate |
| pattern-isolated-permissionless-market.md | Let anyone create lending markets only when each market's collateral, debt, oracle, and interest-rate state is isolated from every other market. | The protocol wants permissionless market creation |
| pattern-kinked-utilization-rate-model.md | Increase borrow rates slowly below a target utilization and sharply above it to discourage liquidity exhaustion. | A lending market needs dynamic borrow and supply rates |
| pattern-lazy-borrow-index.md | Track global borrow interest with an index so borrower debt can be updated on demand instead of looping over all borrowers. | Borrow interest accrues continuously or per block; The protocol has many borrowers |
| pattern-liquidation-grace-period-with-bad-debt-escape.md | Delay ordinary liquidations after an asset freeze or incident, but allow immediate liquidation when the account is already bad debt. | A market needs a freeze or grace period after oracle, collateral, or market incidents |
| pattern-move-receipt-bound-flash-loan.md | Bind a Move flash loan to repayment by returning a non-storable receipt that must be consumed in the same transaction. | A Move-based lending protocol offers atomic flash liquidity |
| pattern-nontransferable-debt-token-delegation.md | Represent borrow liabilities as non-transferable debt tokens and expose delegated borrowing through a separate allowance surface. | Borrow balances are represented as tokenized liabilities; Debt should not be sold or transferred like an asset claim |
| pattern-packed-reserve-risk-configuration.md | Pack reserve risk parameters and operational flags into a named config word with masks, bounds, decode helpers, and setter validation. | A reserve has many hot-path risk parameters or operational flags |
| pattern-product-sum-stability-pool-accounting.md | Distribute liquidation losses and collateral gains to pooled backstop depositors with global product and sum accumulators. | A CDP or lending protocol has a pooled liquidation backstop; Liquidations reduce every depositor's principal pro-rata |
| pattern-progressive-protocol-liquidity-limits.md | Expand protocol-specific withdrawal and borrow capacity over time while shrinking limits immediately after risk-reducing actions. | Multiple protocol adapters share a liquidity core; Each adapter needs bounded borrow or withdrawal capacity |
| pattern-protocol-absorbed-liquidation-inventory.md | Absorb underwater accounts into protocol reserves first, then sell seized collateral from protocol inventory under reserve and slippage constraints. | Liquidations should not require a liquidator to repay exact borrower debt in the same transaction |
| pattern-rate-ordered-redemption-queue.md | Let borrower-selected interest rates determine redemption priority, so low-rate debt accepts more redemption risk. | Borrowers can choose or adjust their own interest rate; The stablecoin can be redeemed against borrower collateral |
| pattern-reserve-exposure-caps.md | Bound how much a lending market can supply, borrow, or expose to one asset so risk parameters cannot rely on liquidation mechanics alone. | A market lists assets with limited liquidity or correlated risk |
| pattern-resettable-dutch-liquidation-auction.md | Sell liquidated collateral through a descending-price auction that can be reset when it becomes stale or too far below its starting price. | Collateral is sold after liquidation rather than seized directly by the liquidator |
| pattern-reward-indexed-erc1155-collateral-wrapper.md | Wrap ERC20 deposits or reward-bearing pool positions into ERC1155 ids that encode the underlying asset, pool, and reward-index snapshot used for collateral valuation. | A lending protocol accepts many ERC20 or LP positions as collateral |
| pattern-risk-bucketed-position-ticks.md | Group debt positions by risk-ratio buckets so redemptions, rebalances, and liquidations can process the riskiest buckets first. | Positions can be ordered by a discrete debt ratio, collateral ratio, or similar risk metric |
| pattern-risk-priority-liquidation-sequencing.md | Force liquidations in multi-asset accounts to address the riskiest debt and weakest collateral before safer legs. | Borrower accounts can hold multiple debt and collateral assets |
| pattern-rolling-fixed-maturity-debt-tokens.md | Issue tokenized debt claims whose ids encode rolling maturities, burn discounted stablecoin at mint, and mint face value after maturity. | A stablecoin or credit protocol wants fixed-maturity funding instruments |
| pattern-scaled-balance-token-accounting.md | Store token balances scaled by a liquidity or debt index so interest accrues globally while user balances update lazily. | A lending protocol represents supplied or borrowed positions as transferable or account-bound tokens |
| pattern-share-denominated-lending-accounting.md | Track supply and borrow positions as market shares against total assets so interest and losses are allocated proportionally. | A lending market needs proportional supply or borrow accounting |
| pattern-single-borrow-asset-market.md | Build each lending market around one borrowable base asset with separate collateral assets, reducing cross-asset borrow complexity. | The protocol wants one borrow asset per market |
| pattern-solana-instruction-paired-flash-loan.md | On Solana, validate flash-loan borrow and repay instructions as a matched pair inside the same transaction. | A Solana lending program offers atomic flash loans; The transaction can include both borrow and repay instructions |
| pattern-yield-preserving-collateral-wrapper.md | Wrap yield-bearing strategy shares into a non-transferable collateral token that mirrors rewards while the position is pledged in a lending market. | Users want to borrow against yield-bearing vault or strategy shares |

### Requirements

| File | Applies To |
|------|-----------|
| req-collateral-threshold-separation.md | R1: Liquidation Threshold Exceeds Borrow Threshold, R2: Action Checks Use The Correct Threshold, R3: Freshness Scope Is Documented, R4: Risk Reductions Preserve Exit Windows, R5: Liquidation Bonus Does Not Invert Collateral Safety |
| req-credit-loss-accounting.md | R1: Loss State Is Explicit, R2: Losses Cannot Exceed Accounted Assets, R3: Normal Issuance Respects Loss State |
| req-lending-accounting-freshness.md | R1: Accrue Before Value-Changing Actions, R2: Freshness Scope Is Explicit, R3: Stale Actions Fail Closed, R4: Parameter Changes Accrue First, R5: Stale Collateral Reports Have Explicit Consequences |

## liquidity

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-activation-scoped-launch-fee-scheduler.md | Taper AMM fees after pool activation using time, price-progress, or rate-limited launch schedules. | A new pool needs higher initial fees during launch or price discovery |
| pattern-address-encoded-hook-permissions.md | Encode a hook contract's lifecycle permissions into its address bits and validate that returned selectors match the invoked hook. | Hook capabilities must be known before pool initialization |
| pattern-amplified-stable-invariant.md | Use an amplification parameter to make swaps near a peg behave like a high-liquidity constant-sum market while preserving constant-product style safety away from the peg. | Assets should trade close to a shared value, peg, or redemption ratio |
| pattern-bounded-cranked-orderbook-maintenance.md | Maintain external AMM maker orders through resumable cranks with per-call limits, stored cursors, and cancel/settle fallbacks. | An AMM maintains many external maker orders |
| pattern-canonical-amm-pool-factory.md | Create each AMM pool at a deterministic canonical address or id keyed by sorted token pair and immutable pool parameters. | A protocol supports many pools with identical logic |
| pattern-complementary-outcome-netting.md | Net binary outcome-token orders by minting or merging complete sets when same-side orders cross. | Outcome tokens are complementary claims over the same collateral |
| pattern-concentrated-liquidity-ranges.md | Represent LP positions as liquidity active only between lower and upper ticks so capital is concentrated around selected prices. | LPs should choose price ranges instead of passively providing across all prices |
| pattern-conservative-lst-router-value-preservation.md | Route swaps and liquidity changes across LST reserves only after syncing conservative underlying value and proving pool value does not decrease under the configured calculators. | A pool routes between multiple liquid staking tokens |
| pattern-constant-leverage-solvency-amm.md | Price swaps through a leveraged debt/collateral AMM while checking that the final virtual solvency value stays inside the allowed envelope. | A pool represents a leveraged collateral/debt position instead of a simple token reserve pair |
| pattern-constant-product-reserve-delta-amm.md | Price swaps by inferring actual token input from reserve deltas, applying fees, and requiring the constant-product invariant to hold. | A two-asset pool should follow `x * y = k`; The pair contract can read token balances and maintain internal reserves |
| pattern-discrete-price-bin-liquidity-book.md | Represent AMM liquidity as shares in discrete price bins and route swaps through the next non-empty bin. | Liquidity should sit at discrete price levels instead of continuous tick ranges |
| pattern-fixed-yield-implied-rate-amm.md | Price fixed-maturity yield claims with implied-rate math instead of a constant-product reserve curve. | The traded asset is a principal token, yield token, or fixed-maturity claim |
| pattern-hook-governed-dynamic-lp-fee.md | Let a pool mark its LP fee as dynamic, then restrict stored fee updates and per-swap fee overrides to the pool's trusted hook. | Pool fees should react to volatility, inventory, order flow, or external signals |
| pattern-hook-returned-custom-accounting-deltas.md | Let trusted AMM hooks return signed token deltas that the singleton manager settles through the same net-delta ledger as core swaps. | Hooks need to implement fees, wrappers, curves, or other custom accounting |
| pattern-invariant-delta-liquidity-accounting.md | Mint and burn LP shares from the change in an AMM invariant, with imbalance fees and slippage bounds around the invariant delta. | A pool supports imbalanced or single-sided deposits and withdrawals |
| pattern-lazy-virtual-order-twamm.md | Execute long-term AMM orders lazily in virtual intervals before ordinary pool actions observe reserves. | Users need to split large swaps across time inside an AMM; Executing every interval eagerly would be too expensive |
| pattern-minimum-liquidity-lock.md | Permanently lock a small amount of initial LP supply so the first depositor cannot fully control or reset pool share price. | AMM LP supply starts at zero; Initial LP shares are minted from deposited reserves or invariant value |
| pattern-offpeg-dynamic-fee.md | Increase AMM fees as pool balances move away from the expected peg or balance so trades that worsen imbalance pay more. | Pool assets are expected to stay close to a peg or fair ratio; Trades that worsen imbalance increase LP risk |
| pattern-orderbook-backed-amm-inventory-accounting.md | Account for AMM liquidity deployed to an external orderbook by reconciling vault balances, open orders, unsettled fills, and protocol PnL. | An AMM posts some pool inventory as maker orders on an external orderbook |
| pattern-range-fee-growth-snapshots.md | Track fee growth outside and inside each tick range so concentrated-liquidity positions can accrue fees lazily without iterating over LPs. | LP positions are active only inside price ranges; Fees should accrue only while a position's range is active |
| pattern-shared-liquidity-kernel.md | Centralize custody and interest accounting in a restricted liquidity core while user-facing fTokens, vaults, and DEX modules act as adapters. | Multiple protocol modules need to draw from the same supplied liquidity |
| pattern-singleton-flash-accounting-pool-manager.md | Keep many AMM pools in one manager and settle all per-currency deltas to zero at the end of an unlocked operation. | Many pools share the same execution environment and benefit from lower transfer overhead |
| pattern-twap-deviation-dynamic-fee.md | Adjust AMM swap fees by the bounded deviation between current price and a recent TWAP. | AMM fee should rise during short-term price dislocation or volatility |
| pattern-user-directed-liquidity-migrator.md | Atomically pull old LP tokens, remove liquidity, add liquidity to the new pool under user bounds, and refund leftovers. | Users need to migrate LP positions between pool versions |
| pattern-verified-callback-settlement.md | Let AMM pools optimistically call external payers during mint, swap, or flash operations, then verify post-callback balances before finalizing. | The pool needs optimistic settlement for swaps, mints, or flash loans |
| pattern-volatility-accumulator-dynamic-fee.md | Increase AMM swap fees from a decaying accumulator of recent price movement and trade clustering instead of only inventory imbalance. | A pool wants fees to rise during rapid price movement or clustered trading |

### Risks

| File | Triggered When |
|------|---------------|
| risk-front-runnable-pool-initialization.md | Pool deployment and price initialization are separate transactions; Initialization is public and one-shot |
| risk-tick-crossing-gas-dos.md | Swap execution loops through initialized ticks; Tick spacing can be small |
| risk-zero-liquidity-price-control.md | Active liquidity can become zero inside the valid tick range; Swaps are allowed while no range is active |

### Requirements

| File | Applies To |
|------|-----------|
| req-concentrated-liquidity-invariants.md | R1: Active Liquidity Matches Tick State, R2: Range Entry and Exit Are Atomic, R3: Position Accounting Uses Range Snapshots |
| req-constant-product-amm-invariants.md | R1: Reserve State Matches Accounted Balances, R2: Fee-Adjusted Product Does Not Decrease, R3: LP Supply Has First-Deposit And Protocol-Fee Rules, R4: Oracle Accumulators Advance From Prior Reserves |
| req-lp-virtual-price-monotonicity.md | R1: Fee-Only Operations Do Not Decrease Virtual Price, R2: Share Supply Changes Match Invariant Delta, R3: Cached Virtual Prices Preserve Freshness Semantics |
| req-net-delta-settlement-invariants.md | R1: Operation Frame Bounds All Deltas, R2: Nonzero Delta Count Matches Delta Storage, R3: Token Settlement Uses Fresh Synced Balances, R4: Shared Vault Reserves Are App-Scoped |

## math

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-bounded-continuous-compounding-index.md | Accrue continuously compounded balances with a bounded fixed-point exponential approximation and explicit rounding direction. | Balances accrue at a continuously compounded rate |
| pattern-full-precision-directed-rounding.md | Use full-width multiplication/division and explicit rounding direction for financial math where intermediate products can overflow native word size. | A formula computes `a * b / denominator` and `a * b` can exceed 256 bits |

## monitoring

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-operation-cadence-liveness-agent.md | Monitor keeper-dependent operations against expected cadence, amounts, and state movement so delayed maintenance is detected before users are stuck. | Protocol liveness depends on bots, keepers, or operators |
| pattern-public-slot-reader-lens.md | Expose efficient public reads for packed or singleton storage through typed slot-reader functions and libraries. | Core state is packed, nested, or keyed in a singleton contract |
| pattern-read-only-protocol-health-checker.md | Package production and fork invariant checks into read-only contracts or scripts that return structured health results without mutating protocol state. | A protocol has many deployed pools, strategies, managers, or upgradeable instances |
| pattern-read-only-signer-proposal-validator.md | Expose non-mutating validation for proposed off-chain signer payloads before threshold signers produce irreversible signatures. | Off-chain signers must approve custody-moving payloads |
| pattern-read-only-storage-resolver-facade.md | Publish resolver contracts that decode packed core storage into stable read models without giving users direct write access to the core. | Core contracts pack storage aggressively for gas; Users, UIs, and keepers need structured state views |
| pattern-revert-encoded-simulation-quote.md | Run the real mutating path in a simulation call, then intentionally revert with encoded quote data before irreversible settlement. | A quote depends on the same branching logic as execution; Duplicating quote logic would drift from the real path |

## oracles

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-action-scoped-bounded-lending-prices.md | Use action-specific bounded prices or validity flags for borrowing, liquidation, funding, settlement, and margin checks. | A lending protocol wants to resist oracle pumps that create new borrow capacity |
| pattern-chainlink-integration.md | Integrate Chainlink price feeds for reliable off-chain oracle data with built-in manipulation resistance. | Need manipulation-resistant price for major assets; Asset has Chainlink feed available |
| pattern-conservative-amm-lp-collateral-oracle.md | Price AMM LP collateral with conservative pool-internal pricing plus fresh external feed hops, while preserving exchange-rate and reentrancy caveats. | A lending market accepts curated AMM LP tokens as collateral |
| pattern-dex-spot-price.md | Read current price directly from DEX pool — real-time but manipulation-vulnerable. | Need real-time price for display purposes; Combined with other validation (not used alone for value transfer) |
| pattern-historical-bounds.md | Validate price against historical min/max to detect anomalies and extreme deviations. | Need sanity check for oracle prices; Want to detect extreme price movements |
| pattern-multi-source-validation.md | Cross-check prices from multiple oracle sources to detect anomalies and identify which source is malfunctioning. | High-value operations depend on oracle price; Need to distinguish between oracle types of failures |
| pattern-multihop-price.md | Derive token price in USD through an intermediate base asset when no direct token/stable pool exists. | Token has no direct pool against stablecoins; Token has liquidity against major assets (WETH, WBTC) |
| pattern-peg-ratio-monitor.md | Track normalized market-price and fair-value ratios for pegged or redeemable assets so operators can detect depeg before it becomes bad debt. | An asset should trade near a peg, redemption value, or exchange-rate value |
| pattern-permissionless-bridged-source-rate-relay.md | Let anyone relay a deterministic source-chain exchange rate through an authenticated bridge while keeping freshness and deviation checks explicit. | A destination chain needs a source-chain staking or vault exchange rate |
| pattern-threshold-reporter-consensus.md | Require a quorum of permissioned reporters to submit the same oracle payload before mutating accepted protocol state. | A protocol has a trusted reporter set for off-chain observations |
| pattern-twap-oracle.md | Time-Weighted Average Price from DEX pools — manipulation-resistant on-chain price discovery. | Need manipulation-resistant on-chain price; Asset has sufficient DEX liquidity |
| pattern-upgrade-slot-pinned-rate-adapter.md | Pin an upgradeable upstream program's last upgrade slot and fail valuation until governance accepts the new slot. | A rate adapter reads state from an upgradeable upstream Solana program |
| pattern-user-opt-in-pending-oracle-registry.md | Stage oracle replacements behind a delay while allowing selected users or vaults to opt into the pending oracle early. | Oracle migrations need a review delay before global activation |

### Risks

| File | Triggered When |
|------|---------------|
| risk-exchange-rate-valuation.md | Collateral value comes from staking, vault, or wrapper exchange rates |
| risk-oracle-centralization.md | Relying on a single oracle source creates single points of failure and trust assumptions. |
| risk-oracle-frontrunning.md | Attackers exploit predictable oracle updates to front-run price changes and extract value. |
| risk-oracle-staleness.md | Price or rate data has a heartbeat, deviation threshold, relay delay, or manual update cadence |
| risk-price-manipulation.md | Attackers manipulate on-chain price sources to exploit protocols that rely on them. |

### Requirements

| File | Applies To |
|------|-----------|
| req-oracle-reliability.md | R1: Freshness, R2: Accuracy, R3: Manipulation Resistance, R4: Availability |

## perps

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-bounded-orderbook-liquidation-deleveraging.md | Cap per-block orderbook liquidation attempts and fall back to deterministic deleveraging when fills cannot safely absorb risk. | Perpetual positions are liquidated through an orderbook or matching engine |
| pattern-capped-pnl-impact-pool-risk-accounting.md | Compute perps pool value with capped trader PnL, pending fees, and separate price-impact pools before allowing actions that can extract liquidity. | A perpetuals market uses shared long and short liquidity pools |
| pattern-fee-pool-capped-asymmetric-funding.md | Cap protocol-paid funding by fee-pool reserves and allow side-specific funding when symmetric rates would overdraw the pool. | Funding can be paid from protocol reserves or a fee pool; Long and short open interest can become materially imbalanced |
| pattern-manager-owned-derivative-cash-settlement.md | Let asset contracts compute derivative settlement while a risk manager owns the authoritative cash adjustment and settled-cash record. | Derivative assets need settlement, expiry, funding, or exercise logic |
| pattern-open-interest-scaled-margin-requirement.md | Increase initial margin as market open interest approaches configured caps, reaching full collateralization at the upper bound. | A perpetual market wants soft exposure control rather than a hard open-interest stop |
| pattern-position-size-scaled-margin-requirement.md | Increase margin requirements and discount positive unrealized PnL as an individual position grows. | Individual large positions are riskier than the same exposure split across smaller traders |
| pattern-progressive-liquidation-state-machine.md | Liquidate unhealthy perpetual accounts through staged modes that bound size, elapsed time, price, dust cleanup, and bankruptcy fallback. | Perpetual liquidations should scale with margin shortage rather than liquidating everything immediately |
| pattern-proposer-validated-memclob-settlement.md | Settle an appchain orderbook by having the block proposer inject deterministic CLOB operations that consensus validates before state writes. | A dedicated appchain runs an in-memory central limit orderbook |
| pattern-scenario-shocked-portfolio-margin.md | Compute initial and maintenance margin from worst-case spot, volatility, skew, basis, collateral-haircut, and confidence scenarios. | Accounts hold portfolios of options, perps, cash, and collateral |
| pattern-solvency-tiered-portfolio-liquidation-auction.md | Liquidate a whole derivative portfolio through Dutch-auction modes that distinguish solvent and insolvent accounts. | Accounts hold multi-asset derivative portfolios rather than one isolated position |

### Requirements

| File | Applies To |
|------|-----------|
| req-adl-reserve-and-funding-risk-controls.md | R1: Reserve And Open Interest Limits Are Explicit, R2: Funding Rounding Cannot Be Avoided By Tiny Updates, R3: ADL Uses Fresh Oracle State And Explicit Thresholds, R4: Backstop Exhaustion And Socialized Loss Are Explicit |

## rewards

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-capped-gauge-emission-redistribution.md | Cap per-gauge reward emissions and redirect excess into an epoch-snapshotted redistributor. | Governance or voters allocate emissions across gauges; Individual gauges need maximum reward flow limits |
| pattern-checkpointed-epoch-reward-buckets.md | Allocate newly received rewards into time buckets and let users claim against historical balance checkpoints for each epoch. | Reward entitlement depends on balances held at epoch boundaries |
| pattern-cumulative-draft-unstaking-queue.md | Represent delayed unstaking claims as cumulative drafts so users can withdraw prefixes without iterating every pending exit. | Stakers must wait before withdrawn stake becomes claimable; Users can create multiple unstaking requests |
| pattern-delayed-cumulative-merkle-claims.md | Stage Merkle reward roots behind a delay and let users claim only the cumulative delta above what they have already received. | Rewards are computed off-chain and published periodically |
| pattern-expiry-bounded-gauge-emission-schedule.md | Schedule gauge emissions for a fixed-maturity market only within the market's active lifetime and under per-second caps. | Liquidity incentives target markets with fixed expiry; Emission rates are set by governance or an operator |
| pattern-index-to-distributor-reward-routing.md | Route rewards for disabled or restricted accounts from a lazy reward index into a distributor checkpoint, then claim them through a separate proof path. | Most users should accrue through a lazy reward index; Some accounts are not allowed to receive rewards directly |
| pattern-indexed-merkle-airdrop.md | Distribute a fixed reward set with an indexed Merkle root and bitmap claim tracking so each allocation can be claimed exactly once. | A fixed off-chain allocation should be claimable on-chain; The root will not be updated cumulatively over time |
| pattern-isolated-vesting-schedule-escrow.md | Create one escrow contract or isolated schedule per vesting grant so vested withdrawals and unvested revocation are tracked independently. | Beneficiaries can have multiple grants with different schedules; Unvested tokens may be revocable by the schedule owner |
| pattern-lazy-reward-index.md | Accrue rewards through a global index and update each user only when they interact or claim. | Rewards accrue continuously or per emission update; The protocol has many suppliers, stakers, or borrowers |
| pattern-nonce-bound-delayed-reward-claim-ledger.md | Separate reward accrual from delayed claim execution by hashing amount, owner, receiver, unlock time, and nonce into a claim id. | Rewards accrue on-chain but should become transferable only after a delay |
| pattern-queued-reward-streaming.md | Queue reward tokens from permissioned distributors, carry leftovers forward, and stream rewards over a fixed duration. | Rewards arrive in discrete deposits but should accrue smoothly; Only approved distributors should fund reward streams |
| pattern-range-liquidity-reward-index.md | Accrue rewards only to concentrated-liquidity positions whose tick ranges are active, using tick-level reward-growth snapshots. | Rewards should incentivize active AMM liquidity, not out-of-range inventory; LP positions have lower and upper ticks |
| pattern-snapshot-gated-integration-reward-distribution.md | Distribute rewards only after integration state, debt state, and processed bitmaps are finalized for the same distribution snapshot. | Rewards depend on off-chain or cross-program accounting snapshots |
| pattern-threshold-principal-reward-waterfall.md | Split unlabeled withdrawal-recipient inflows into principal and rewards by paying tracked principal up to an absolute threshold before routing residual value to rewards. | A staking or validator withdrawal recipient receives unlabeled principal and reward inflows |

### Risks

| File | Triggered When |
|------|---------------|
| risk-reward-token-accrual-dos.md | Deposit, withdraw, transfer, or claim updates all registered reward tokens |

## routing

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-instruction-scoped-signed-message-orders.md | Verify signed order messages against the exact instruction, signer, payload fields, expiry, and replay cache before settlement. | Orders are signed off-chain but verified inside an execution instruction |
| pattern-registry-gated-exchange-fallback.md | Try an allowlisted aggregator route first, then fall back to an allowlisted on-chain wrapper while enforcing final balance-delta slippage. | Off-chain routing can find better prices but cannot be fully trusted |
| pattern-stateless-callback-validated-swap-router.md | Route swaps through compact path data and callback validation while keeping user slippage, deadline, and payer rules at the router boundary. | Swaps may traverse one or more canonical AMM pools; Pool settlement happens through callbacks |
| pattern-stateless-prepaid-amm-router.md | Route AMM swaps by pre-paying the first pair, forwarding intermediate outputs pair-to-pair, and enforcing user slippage at the router boundary. | Pools infer swap input from received token balances; The router should not hold balances after the transaction |
| pattern-tripwire-dutch-auction-fallback.md | Disable risky Dutch-auction routes after anomalous fills and force future trades through a safer fallback until governance reviews the route. | A protocol uses Dutch auctions for rebalancing, revenue, or recollateralization |
| pattern-typed-signed-order-settlement.md | Keep matching off-chain while settling orders on-chain by binding every fillable term in an EIP-712 order and tracking fill state. | Orders are matched off-chain but assets settle non-custodially on-chain |

### Risks

| File | Triggered When |
|------|---------------|
| risk-zero-consideration-signed-order.md | Orders bind maker and taker amounts but allow either amount to be zero |

## token-integration

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-adapter-isolated-core-ledger.md | Keep the core accounting ledger free of token calls and route every token-specific behavior through small audited adapters. | A protocol accepts multiple collateral or asset types |
| pattern-balance-delta-transfer-accounting.md | Account for the actual token amount received by measuring balance changes around transfers. | The protocol accepts arbitrary or curated ERC20 collateral |
| pattern-extension-gated-transfer-fee-normalization.md | Support deterministic token-program transfer fees by reading canonical extension state, normalizing included/excluded amounts, and rejecting unsupported extensions. | The token program exposes canonical, inspectable transfer-fee extension state |
| pattern-semi-fungible-slot-reserve-wrapper.md | Wrap ERC-3525 or other slot-scoped semi-fungible positions into one ERC-20 claim token per slot while the pool owns the underlying slot value id. | Underlying positions are semi-fungible by slot; Each slot should become a fungible ERC-20 claim |

## tokens

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-circulating-supply-exclusion-ledger.md | Track addresses whose balances are intentionally excluded from circulating supply so mint limits, caps, and accounting views use the right denominator. | A token has escrow, treasury, reserve, or protocol-owned balances that should not count as circulating supply |
| pattern-fixed-maturity-principal-yield-tokenization.md | Split a yield-bearing asset into principal and yield claims for a specific expiry. | Users need to trade fixed-rate principal exposure separately from floating yield |
| pattern-historical-basket-redemption-nonces.md | Let users redeem against a recorded basket version so basket changes do not make pending redemption quotes ambiguous. | A redeemable token can switch its backing basket over time |
| pattern-launch-locked-recipient-scoped-transfer-gate.md | Launch a governance or distribution token as non-transferable, then allow controlled transfers through account allowlists and recipient-scoped spend budgets until full transferability is enabled. | A token has an intentional non-transferable launch or distribution phase |
| pattern-paired-supply-change-throttle.md | Rate-limit issuance and redemption as paired directions so one side consumes capacity while the opposite side restores it. | A redeemable token can be issued and redeemed directly against backing assets |
| pattern-principal-reward-split-derivative.md | Represent a staking position with one token for principal and a separate token for accrued rewards. | Principal should remain close to 1:1 with deposited assets |
| pattern-target-unit-backup-basket-substitution.md | Replace failed basket collateral by target unit so backing intent survives token-level default. | A redeemable or index token represents a basket of economic target units |
| pattern-timeboxed-idempotency-key-ledger.md | Record operation keys for a bounded retention window so retried mints, burns, transfers, or redemptions execute at most once. | Off-chain operations can be retried after network or operator failures |
| pattern-token2022-transfer-hook-policy-gate.md | Use Solana Token-2022 transfer hooks and extra account metadata to enforce policy state on every token transfer. | A token needs transfer-time policy checks such as pause, allowlist, or compliance gates |

## upgrades

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-bytecode-split-extension-delegate.md | Split oversized contract code into a primary contract and an extension delegate that serves selected functions through fallback `delegatecall`. | A contract approaches bytecode size limits; Extension functions need access to the same storage layout |
| pattern-namespaced-storage-accessor.md | Isolate upgradeable contract state behind explicit namespace slots and typed accessor libraries. | Contracts are upgradeable and use inheritance or libraries; Multiple modules need independent storage layouts |
| pattern-selector-routed-module-proxy.md | Dispatch proxy fallback calls through a selector-to-implementation registry with reverse selector manifests and collision checks. | A system needs many modules behind one stable address; Function selectors can be assigned to focused implementations |
| pattern-timelocked-address-registry.md | Resolve module addresses by registry IDs while staging each address change behind a per-entry wait period. | Executors or routers resolve modules, actions, wrappers, or adapters by ID |
| pattern-version-gated-upgrade-registry.md | Authorize proxy upgrades only to implementation versions that a registry has approved and not deprecated. | Many proxy instances should share a vetted implementation catalog |

### Risks

| File | Triggered When |
|------|---------------|
| risk-diamond-selector-collision.md | A proxy or diamond delegates unknown selectors to implementation or facets |

## vaults

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-async-deposit.md | Separate the request and execution of deposits/withdrawals to eliminate timing arbitrage opportunities. | Vault has significant oracle latency or deviation; Underlying assets are illiquid (RWA, staked assets) |
| pattern-bounded-rebalance-auction.md | Let managers rebalance basket vaults through auctions while constraining assets, weights, prices, duration, and later parameter changes. | A vault holds a managed basket or index of multiple assets |
| pattern-circuit-breaker.md | Pause deposits/withdrawals when oracle price deviates significantly from a reference price, closing the attack window during suspicious conditions. | Vault relies on oracle for NAV calculation; Assets are volatile or oracle is known to have latency |
| pattern-clone-factory.md | Mass deployment of parameterized vault instances via minimal proxy clones — ~45K gas per vault instead of ~2M. | Many vaults with identical logic but different parameters (fee tiers, recipients, names) |
| pattern-curated-validator-operator-registry.md | Maintain an operator registry that separates validator membership from preferred deposit and withdrawal routing. | Liquid staking depends on a curated validator set; Deposit and withdrawal operations need different preferred operators |
| pattern-delta-nav.md | Calculate vault shares based on proportional change in Net Asset Value. | Single-asset vault (one underlying token) |
| pattern-dynamic-premium.md | Entry/exit fee that varies based on oracle volatility, providing adaptive protection against oracle arbitrage during high-risk periods. | Vault has varying risk levels over time; Fixed premium would be too high during normal conditions |
| pattern-exchange-rate-preserving-lst-cutover.md | Migrate a liquid-staking token to a successor manager by moving backing assets without minting and asserting exchange-rate continuity. | A liquid-staking system must migrate manager contracts without changing token claims |
| pattern-height-interval-redemption-queue.md | Match redemption requests against cumulative withdrawal intervals so claims can be resolved by interval height instead of scanning the full queue. | Redemptions are satisfied by discrete withdrawal events or external unstaking intervals |
| pattern-high-water-mark-fee.md | Charge performance fee only on new profit above the previous peak, paid via share dilution. | Vault generates yield and protocol needs to capture a share of profits |
| pattern-liability-backed-erc4626-savings-share.md | Use ERC4626 shares to represent protocol liabilities where deposits burn the base asset and withdrawals mint it back from controlled supply. | A stablecoin or credit protocol wants an ERC4626-compatible savings token |
| pattern-locked-profit-smoothing.md | Exclude newly harvested profit from strategy value for a fixed window, then release it linearly to prevent timing extraction around harvests. | Strategy profit is realized in discrete harvest transactions; Deposits can occur immediately before or after harvest |
| pattern-operator-finalized-withdrawal-claim.md | Burn or escrow user shares at request time, then let an operator fund specific request ids so users claim fixed entitlements instead of repricing at claim time. | Withdrawals depend on off-chain settlement, external redemption, or operator-provided liquidity |
| pattern-operator-routed-liquid-staking-share.md | Mint a non-rebasing liquid-staking share while routing deposits to selected validators or operators behind an exchange-rate ledger. | Users need a transferable non-rebasing claim on delegated stake |
| pattern-oracle-computed-async-settlement.md | Queue mint or burn requests asynchronously, but compute completion economics from stored request data and oracle state instead of operator-supplied output amounts. | Deposits or redemptions require off-chain processing before completion; A completion operator is needed for liveness |
| pattern-premium-buffer.md | Charge a fee on deposits/withdrawals that covers potential oracle price deviation, eliminating arbitrage profitability. | Vault uses oracle prices for NAV calculation; Need simple, synchronous deposit/withdraw flow |
| pattern-proportional-deposit.md | Users deposit and withdraw all vault assets proportionally, eliminating the need for oracle-based NAV calculation. | Multi-asset vault/pool with known composition; Want to avoid oracle dependency entirely |
| pattern-proportional-zapin.md | External periphery contract converts single-token input into a proportional multi-token deposit, pushing swap slippage to the depositor and eliminating slippage socialisation in managed vaults. | Multi-token vault where a manager rebalances after single-token deposits (slippage socialised across holders) |
| pattern-rate-bounded-nav-report.md | Accept manual or off-chain NAV reports only after the current NAV expires and only within annualized share-price movement guardrails. | Vault NAV is reported by an off-chain manager, accountant, or security council |
| pattern-reserve-split-liquid-staking-receipt.md | Track user-owned and protocol-reserved receipt-token supply separately when a liquid-staking or CDP wrapper keeps part of minted receipts in reserve. | A wrapper mints receipt tokens while retaining part of the receipt supply as protocol reserve |
| pattern-timelock-shares.md | Shares are issued immediately but cannot be transferred or redeemed for a specified period, preventing instant arbitrage profit extraction. | Want instant share issuance (better UX than async); Need to prevent flash loan attacks |
| pattern-user-owned-proxy-vault.md | Deploy one vault/proxy per user so protocol integrations can be automated while custody and position ownership remain isolated. | Users need individualized positions in an external protocol |
| pattern-vault-wrapper.md | Thin ERC4626 vault that wraps a base strategy vault, adding fee/access layers without duplicating strategy logic. | Multiple fee tiers needed over a single strategy (e.g. 0%, 10%, 15%) |
| pattern-virtual-share-offset.md | Add virtual assets and virtual shares to vault conversion math so first-depositor donations cannot round later depositors to zero shares. | Vault share minting uses `assets * totalSupply / totalAssets` |
| pattern-withdrawal-liquidity-buffer.md | Reserve enough liquid assets for claims, route new inflows to queued withdrawal deficits first, and only deploy surplus capital. | Vault assets are deployed into illiquid, staked, or externally managed positions |

### Risks

| File | Triggered When |
|------|---------------|
| risk-liquidation-tick-branch-gas-dos.md | Liquidations iterate through price ticks, branch lists, or position buckets |
| risk-oracle-arbitrage.md | NAV calculation using oracles creates arbitrage opportunities when oracle prices deviate from real market prices. |
| risk-vault-composability.md | Layered ERC4626 vaults introduce compound risks — rounding amplification, shared capacity, propagated failures — not present in single-vault architectures. |

### Requirements

| File | Applies To |
|------|-----------|
| req-liquid-staking-loss-accounting.md | R1: Negative Rewards Are Explicit, R2: Later Rewards Repay Outstanding Penalties First, R3: Migration And Exit Apply Remaining Losses Pro Rata, R4: Pending Exits Are Not Harvestable Yield, R5: Burn-Cover Buckets Are Separate From Ordinary Rewards |
| req-restaking-slashing-accounting.md | R1: Slash Factors Are Explicit And Composable, R2: Queued Withdrawals Preserve Slash Exposure, R3: Capture Times Are Bounded By Vault Epochs, R4: Veto Or Resolver Delay Is A State Machine |
| req-stake-pool-epoch-accounting-freshness.md | R1: Validator Records Are Current Before Value Changes, R2: Pool Backing Is Recomputed From Validated Components, R3: Prior-Epoch Snapshots Support Fees And Rewards |
| req-tiered-loss-waterfall.md | R1: Loss Priority Is Explicit, R2: Tier Capacity Is Measurable, R3: Junior Risk Is Opt-In, R4: Waterfall Execution Preserves Solvency |
| req-vault-fairness.md | R1: No Value Extraction, R2: Fair Share Price, R3: Cost Attribution, R4: No Timing Advantage |

## zero-knowledge

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-bounded-merkle-root-history.md | Keep a fixed-size ring of recent Merkle roots so asynchronous zk proofs can verify membership without accepting unbounded stale state. | Users generate proofs against roots that may be a few blocks old |
| pattern-circuit-bound-external-settlement-hash.md | Hash settlement fields outside the circuit, constrain the hash as a public input, and verify the same hash on-chain before moving tokens. | A zk proof controls public token deposits or withdrawals |

### Requirements

| File | Applies To |
|------|-----------|
| req-shielded-pool-accounting-invariants.md | R1: Known Root Membership, R2: Nullifiers Are Unique, R3: Public Amounts Conserve Value, R4: External Settlement Is Bound |
