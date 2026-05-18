# Architecture Anti-Patterns

Known bad architectural decisions for smart contract systems. Used by validate-architecture to flag problematic designs.

## Structural

### God Contract
One contract handles >50% of system responsibilities.
**Symptoms:** Long responsibility list, many state variables, many external functions, hard to audit in isolation.
**Fix:** Decompose into focused contracts with clear boundaries.

### Circular Dependencies
Contract A depends on B, B depends on A (directly or through chain).
**Symptoms:** Deployment ordering issues, tight coupling, hard to test in isolation.
**Fix:** Extract shared interface or introduce mediator.

### Shared Mutable State
Multiple contracts read/write the same storage slot or external state without clear ownership.
**Symptoms:** Race conditions, unexpected state changes, hard to reason about invariants.
**Fix:** Single owner per state, others read via view functions. A shared custody vault can be acceptable only when it is immutable, has explicit internal ledgers, and has a restricted writer set.

### Missing Abstraction
Direct coupling to external protocol without adapter/interface layer.
**Symptoms:** Protocol-specific types/calls scattered throughout codebase, painful to switch providers.
**Fix:** Adapter contract wrapping external protocol behind stable internal interface.

### Leaky Abstraction
Internal implementation details exposed through contract interfaces.
**Symptoms:** Callers need to know internal state layout, function parameters expose internal concepts.
**Fix:** Interface describes WHAT not HOW. Hide internal mechanics.

### Prose-Only Security Guardrail
Documentation, deployment scripts, or comments describe a security limit that the contract never enforces.
**Symptoms:** README says withdrawals are capped, minimums apply, or unsafe amounts are rejected, but no runtime check or invariant test exists.
**Risk:** Operators, users, and auditors rely on a nonexistent control; later code changes preserve the prose while behavior remains unsafe.
**Fix:** Encode the guard in contract logic or tests, or explicitly mark it as an operational policy outside the trust-minimized path.

## Access Control

### Unrestricted Admin
Owner/admin can change critical parameters instantly without timelock, bounds, or multi-sig.
**Symptoms:** Setter functions with no delay, no upper/lower bounds on parameters, single EOA as owner.
**Risk:** Rug pull, accidental misconfiguration, governance attack.
**Fix:** Timelock on critical changes, hard-coded bounds on parameters, multi-sig or governance for admin. Delegated operator modules help only when targets, selectors, and parameter caps are hard-bounded or timelocked. Treat allowlist, maintainer, vault-status, and bridge-trust-list changes as critical even when they are not numeric parameters.

### Stale-State Bound Check
Setter validates an old stored value or unrelated state instead of the proposed new parameter.
**Symptoms:** `require(currentFee <= MAX_FEE)` inside `setFee(newFee)`, tests cover only existing valid values, or events emit the proposed value while bounds check another variable.
**Risk:** A critical parameter can be set outside intended bounds even though the setter appears guarded.
**Fix:** Validate proposed inputs directly, test failing over-limit proposals from both valid and invalid current states, and emit old/new values.

### Fixed-Window Revocation Blind Spot
Permission revocation scans only a small recent window of a linked list or append-only log.
**Symptoms:** Helper revokes "all" permissions but stops after N entries, or older approvals are unreachable without manual iteration.
**Risk:** Stale authority remains active after users or operators believe it was revoked.
**Fix:** Store indexed permission state, expose cursor-based revocation, or require callers to revoke exact entries while making incomplete revocation visible.

### Missing Pause
No emergency stop mechanism. If exploit found, no way to stop bleeding.
**Symptoms:** No pause function, or pause doesn't cover all entry points.
**Fix:** Pausable with clear scope (what's paused, what's not — e.g., pause deposits but not withdrawals).

### Pause Traps Funds
Pause blocks ALL operations including withdrawals.
**Symptoms:** Pause disables both deposit and withdraw/redeem, or bridge pause blocks exits/refunds after users have burned or escrowed assets.
**Risk:** Users cannot exit during emergency.
**Fix:** Pause blocks new inflows and unsafe state transitions first. Withdrawals, claims, and refunds remain available when solvent; claim/redeem pauses need narrower permissions, monitoring, expiry, or an explicit emergency playbook. If not every exit path is safe, keep the safest solvent exit path open, such as proportional withdrawal while swaps and imbalanced exits are paused. For veto or rage-quit governance, document whether paused withdrawal queues, oracles, or bridges can deadlock proposal liveness.

## Oracle & Price

### Oracle Monoculture
Single oracle source, no fallback, no validation.
**Symptoms:** One Chainlink feed, no staleness check, no deviation check, no backup.
**Risk:** Oracle downtime or manipulation → incorrect pricing → fund loss.
**Fix:** Staleness threshold, deviation bounds, fallback oracle or circuit breaker.

### Spot Price Dependency
Using instantaneously manipulable price (DEX spot, single-block read) for value-bearing operations.
**Symptoms:** Price read from AMM pool in same transaction as value transfer.
**Risk:** Flash loan → manipulate price → exploit → repay in same tx.
**Fix:** TWAP, multi-block averaging, or oracle with manipulation resistance.

## Economic

### Unbounded Iteration
Loop over user-controlled or growing data structure without gas limit.
**Symptoms:** Array that grows with users/deposits, loop in core operation.
**Risk:** Gas DoS — operation becomes too expensive as data grows.
**Fix:** Bounded batch processing, pagination, or restructure to avoid loops. Lazy time-bucket catchup loops need a max backlog, public batching, or keeper incentives. If users can append entries to another account's array, require a minimum economic size, owner-only append semantics, or pagination so attackers cannot gas-DoS a victim's aggregate views or withdrawals. Relay-style view aggregators over operators, keys, vaults, or validator sets can be acceptable for off-chain indexing, but should not become on-chain dependencies without pagination or hard caps.

### Fee-on-Transfer Blindness
Assumes token transfer delivers exact amount. Doesn't account for fee-on-transfer or rebasing tokens.
**Symptoms:** `transferFrom(amount)` followed by using `amount` directly without checking balance delta.
**Risk:** Accounting mismatch, exploitable for value extraction.
**Fix:** Measure actual balance change and account using the received amount, or explicitly reject fee-on-transfer tokens at onboarding.

### Missing Slippage Protection
Value-bearing operation (swap, deposit, mint) without user-specified bounds on acceptable outcome.
**Symptoms:** No `minAmountOut`, no `maxSlippage`, no `deadline` parameter.
**Risk:** Sandwich attack, stale transaction execution at unfavorable price.
**Fix:** User-provided slippage bounds + deadline. For dynamic pricing, require max-cost bounds and quote expiry; for admin-configured swap templates, validate router allowlists, selectors, calldata insertion offsets, and approval scope. For delta-derived liquidity mints or increases, cap token inputs and require a minimum liquidity or position delta, because max token amounts alone do not prove the user received enough position value.

### Quote Execution Formula Drift
Quoted helper functions use a different formula than the state-changing execution path.
**Symptoms:** `getAmountIn` calls output math, previews omit dynamic fees, or off-chain quotes use stale router formulas.
**Risk:** Users set wrong slippage bounds, integrators route through stale math, or economic checks pass against a quote the execution path never honors.
**Fix:** Share quote and execution math libraries, test public quote helpers against execution, and treat quote-only fixes as compatibility-sensitive upgrades.

### Donation Attack Surface
Share price manipulable via direct token transfer to contract.
**Symptoms:** `totalAssets()` reads token balance directly, no virtual offset or internal accounting.
**Risk:** Attacker donates tokens → inflates share price → first depositor gets ~0 shares.
**Fix:** Virtual shares/assets offset, minimum first deposit, or internal accounting not based on balance. Also check lifecycle predicates that depend on zero token balance; donations can grief removal or cleanup flows even without share inflation. For 1:1 wrappers, surplus accounting plus a controlled skim receiver can neutralize donations. Donation recovery sweeps should be capped to proven excess and ordered before syncing internal cash to the external balance.

## State & Lifecycle

### Uninitialized Proxy
Upgradeable proxy without initializer protection.
**Symptoms:** `initialize()` without `initializer` modifier, or no initialization check.
**Risk:** Attacker calls initialize on implementation, takes ownership.
**Fix:** OpenZeppelin `initializer` modifier, or `_disableInitializers()` in constructor. For reinitializers, gate each revision once and test that repeated or skipped revision initializers cannot overwrite authority, storage namespaces, or version state.

### Latched Invalid Initialization
One-shot initializer records partial or invalid configuration before validating all required fields.
**Symptoms:** `initialized = true` or equivalent latch can be set while required addresses, chain ids, or limits are zero.
**Risk:** Contract becomes permanently bricked or deploys peers with unusable configuration.
**Fix:** Validate all required fields before setting irreversible initialization state; test zero/partial configs.

### Missing Migration Path
Immutable contract with no plan for upgrade/migration.
**Symptoms:** No proxy, no migration documentation, no "deploy new + pause old" flow.
**Risk:** Bug found post-deploy → no way to fix, funds stuck or at risk.
**Fix:** If immutable by design → document migration path explicitly (pause + redeem + redeposit). If upgradeability needed → proxy pattern.

### State Machine Gaps
Entity with lifecycle states but undefined transitions or unreachable states.
**Symptoms:** State enum with no path to reach certain values, or no path back from terminal state.
**Risk:** Contract stuck in unexpected state, locked funds.
**Fix:** Complete state transition table — every (state, action) pair defined.

## Composability

### Reentrancy Setup
External call to untrusted contract before state is finalized.
**Symptoms:** State read → external call → state write pattern (violates CEI).
**Risk:** Callback re-enters contract, reads stale state, extracts value.
**Fix:** Checks-Effects-Interactions pattern, reentrancy guard, or state finalization before external calls.

### Unchecked External Return
External call without checking return value or handling revert.
**Symptoms:** `token.transfer()` without return value check, `externalContract.call()` without success check.
**Risk:** Silent failure, incorrect accounting.
**Fix:** Use SafeERC20, check return values, handle reverts explicitly. Fallback adapters must not treat out-of-gas, empty returndata, unexpected selectors, or arbitrary reverts as valid default values unless the default is explicitly conservative and monitored.

### Composability Assumption
Architecture assumes external protocol behavior that may change.
**Symptoms:** Hard-coded addresses, assumed interface stability, no version check.
**Risk:** External protocol upgrades, changes behavior, or gets exploited → cascading failure.
**Fix:** Adapter layer, version checks, circuit breaker on unexpected behavior.

### Hook/Callback Trust
Protocol calls external hooks/callbacks (Uniswap V4 hooks, ERC-777 receivers, flash loan callbacks) without restricting what the hook can do.
**Symptoms:** External hook can re-enter or call back into protocol state. No hook sandboxing.
**Risk:** Malicious hooks manipulate protocol state mid-execution. Uniswap V4 hook exploits: $11M+.
**Fix:** Restrict hook capabilities (read-only where possible), reentrancy locks spanning entire operation, whitelist hooks through governance. Bind callback caller/context to the expected pool, market, or order; advisory hooks should be bounded-gas/best-effort and must not control critical invariants. If callbacks are allowed, prove or test that no critical storage writes happen after the external callback. Validate hook interfaces and trust boundaries on replacement paths, not only at initial setup. Block periphery operations such as position transfer, subscribe, or unsubscribe while the core manager is unlocked, and clear subscription state before external notification so gas griefing cannot pin stale callbacks. For flash-loan automation, grant temporary wallet permissions only around the callback and assert lender, initiator, and post-callback revocation.

### Unkeyed Transient Execution Context
Transient scratch storage or per-transaction context is shared across callers, wallets, or operations without a key.
**Symptoms:** Action A writes a scratch value that action B can read, or nested recipe/flash-loan execution reuses global transient slots.
**Risk:** A malicious module can poison later steps, read another operation's context, or bypass assumptions about one-frame isolation.
**Fix:** Key transient state by caller, wallet, operation id, or execution frame, and clear or settle it at the end of the frame. Transient storage is acceptable when state is keyed and invariants prove no unsettled delta crosses the operation boundary.

### Account Role Confusion
Code validates a set of same-type accounts but later reads or writes one role using another role's variable.
**Symptoms:** `baseVault` and `quoteVault` both have correct type checks, but later accounting loads both balances from the same account variable; Solana account arrays or long EVM parameter lists reuse adjacent names.
**Risk:** Accounting, settlement, or authority checks use the wrong account after initial validation, causing mispriced deposits, withdrawals, or custody movement.
**Fix:** Use role-specific account structs, validate account cohorts together, keep semantic names through execution, and add negative tests that swap same-type accounts.

### Unvalidated External Contract
Protocol integrates with external contracts passed as parameters, validates token addresses but not the contract itself.
**Symptoms:** No registry of trusted contracts, no bytecode/factory verification.
**Risk:** Attacker deploys malicious contract mimicking expected interface. BetterBank: $5M loss.
**Fix:** Registry of validated contracts, factory-pattern integration, governance-curated allowlists.

## Vault / ERC-4626

### Vault Inflation (First-Depositor)
ERC-4626 vault with no virtual offset, totalAssets reads balance directly, no minimum initial deposit.
**Symptoms:** No dead shares, no _decimalsOffset, no internal accounting.
**Risk:** Attacker deposits 1 wei, donates tokens to inflate share price, subsequent depositors get 0 shares. sDOLA: $239K.
**Fix:** Virtual share offset (OpenZeppelin _decimalsOffset), internal asset accounting, minimum initial deposit.

### Withdrawal Queue Starvation
Vault strategy locks all funds in external protocols, no reserved liquidity buffer.
**Symptoms:** No liquidity reserve, FIFO withdrawal queue, no forced unwind trigger.
**Risk:** During stress, liquid reserves depleted. Late withdrawers stuck indefinitely. Bank-run dynamics.
**Fix:** Liquidity buffer (10-20% TVL always liquid), pro-rata withdrawal during stress, forced unwind triggers. Queue processing must be gas-bounded and mass exits must not brick finalization. Manual pull redemptions should fix entitlement or enforce queue order so users cannot wait for a favorable later price while others exit.

### Permissioned Exit Custody
Withdrawal or migration escrow lets only an owner or operator release user funds without user-specific entitlement or queue semantics.
**Symptoms:** Owner-only escrow withdrawal, no recorded beneficiary balance, or migration custody that relies on social process.
**Risk:** Users cannot independently claim assets and must trust the operator not to delay, reorder, or redirect exits.
**Fix:** Record user entitlements, queue order, and claim conditions on-chain. Beneficiary-specific pending redemptions improve traceability, but they do not remove custody risk if only an operator can execute or cancel and there is no timeout, queue, or user claim path. If permissioned custody is temporary for migration, publish the migration boundary, operator trust assumptions, and final user claim path.

### Rebasing Token Accounting
Protocol holds rebasing tokens (stETH, AMPL, aTokens) but uses balance-snapshot model.
**Symptoms:** No wrapper for rebasing tokens, internal accounting diverges after rebase.
**Risk:** Positive rebases create extractable surplus, negative rebases make protocol insolvent.
**Fix:** Wrap rebasing tokens (wstETH not stETH), or share-based internal accounting.

## Token Integration

### Fee-on-Transfer Blindness
Assumes token transfer delivers exact amount requested.
**Symptoms:** `transferFrom(amount)` followed by using `amount` directly without balance delta check.
**Risk:** Accounting mismatch with fee-on-transfer tokens, exploitable for value extraction.
**Fix:** Measure actual balance change and account using the received amount, or explicitly reject fee-on-transfer tokens at onboarding.

### Implicit Decimal Assumption
Protocol hardcodes 18 decimals or assumes all tokens have same decimals.
**Symptoms:** No per-token decimal normalization, share math doesn't account for decimal differences.
**Risk:** USDC (6 decimals) valued as 1e12× correct amount. Common in multi-token vaults.
**Fix:** Read and normalize decimals per token, scale to canonical precision, fuzz with varying decimals. If the system only supports 18-decimal accounting, reject non-18-decimal tokens and feeds at every onboarding path.

### Approval Persistence
Protocol requests unlimited approval, approved spender contracts are upgradeable.
**Symptoms:** `type(uint256).max` approval, no permit2, no session-scoped approvals.
**Risk:** Compromised or maliciously upgraded contract drains all users. Multichain exploit.
**Fix:** Permit2 or ERC-7674 transient approvals, exact-amount approvals, time-bound approvals. For stored route templates, validate approved router and calldata before granting allowance.

### Permit Front-run Griefing
Protocol bundles an EIP-2612 permit with a value-bearing action and reverts if the permit nonce was already consumed.
**Symptoms:** `permit()` is called first, then deposit/withdraw/repay assumes the permit succeeded.
**Risk:** An observer front-runs the same permit, consumes the nonce, and makes the user's bundled action revert or miss a deadline.
**Fix:** Treat permit failure as non-fatal when allowance is already sufficient for the action. Check final allowance before proceeding, and still enforce amount and deadline bounds.

### Signature Scope Drift
Signature or permit authorizes a token allowance but omits the exact vault, pool, asset, route, action, or domain that will consume it.
**Symptoms:** One tranche/share token can be used through multiple vaults or assets, but signatures bind only owner, spender, and token amount.
**Risk:** A valid signature for one path is replayed or redirected into another path with different economics or restrictions.
**Fix:** Bind signatures to chain id, verifying contract, nonce, deadline, action, vault/pool id, asset, receiver, and route-specific parameters. Reject signatures that rely on shared token allowance when multiple settlement contexts exist. Cross-chain systems may use stable domain substitutes only when the substitute explicitly commits to the subnetwork, verifier context, and replay boundary.

## Governance

### Flash Loan Governance
Governance token = voting token, no snapshot, no minimum holding period.
**Symptoms:** No snapshot mechanism, proposal execution without timelock, emergency bypass.
**Risk:** Flash loan borrow governance tokens → pass malicious proposal in one tx. Beanstalk: $182M.
**Fix:** Snapshot voting at prior block, time-weighted voting power, mandatory timelock on all paths. Vote-weight caps and post-vote transfer locks reduce token reuse but are not a full snapshot substitute.

### Governance as Arbitrary Execution
Governor contract executes arbitrary calldata against any target.
**Symptoms:** No target/function whitelist, weak community monitoring, no veto mechanism. Operator or receiver contract can hold funds and execute arbitrary calldata.
**Risk:** Passed proposal becomes unrestricted execution primitive. Can drain treasury, brick protocol.
**Fix:** Whitelist targets/selectors, separate parameter changes from code upgrades, veto/guardian role. Critical parameter and auth changes should emit events with old and new values so monitoring can detect silent configuration drift.

## Lending / Borrowing

### Toxic Liquidation Spiral
Lending protocol allows illiquid collateral, fixed liquidation bonus, no circuit breaker.
**Symptoms:** No liquidity-aware parameters, no cascading liquidation protection, no bad-debt backstop.
**Risk:** Liquidations push prices down → more liquidations → bad debt. Aave V2: $1.7M bad CRV debt.
**Fix:** Liquidity-aware listing, graduated liquidation, bad-debt backstop, halt beyond LTV threshold. Avoid broad liquidation/seize pauses unless there is a separate bad-debt containment plan.

### Correlated Collateral Basket
Multiple collateral types are highly correlated but treated as independent.
**Symptoms:** stETH + rETH + cbETH all accepted without aggregate exposure limit.
**Risk:** Systemic ETH depeg devalues ALL collateral simultaneously. Individual params look safe, portfolio is concentrated.
**Fix:** Aggregate exposure limits per asset class, correlation-aware risk parameters, stress testing.

### Price Feed Asymmetric Staleness
Two oracle feeds for a pair with different update frequencies.
**Symptoms:** Collateral price from Chainlink (hourly), debt price from DEX TWAP (per-block).
**Risk:** During fast moves, stale feed creates mispricing window. Borrow against overvalued collateral.
**Fix:** Symmetric oracle architecture, maximum staleness gap enforcement, pause on divergence.

## MEV / Ordering

### Mempool-Visible Value Transfer
User-facing swap/deposit broadcasts exact amounts to public mempool.
**Symptoms:** No commit-reveal, no private submission, no batch auction, large default slippage.
**Risk:** Every transaction sandwichable. Systematic value extraction from users.
**Fix:** Private tx submission (Flashbots Protect), batch auctions, commit-reveal, protocol-level slippage bounds.

## Upgrade / Proxy

### Beacon Proxy Single Point of Failure
Many instances share single Beacon, Beacon owner is EOA or low-threshold multisig.
**Symptoms:** One global beacon for all vaults/pools, no upgrade monitoring.
**Risk:** Compromising Beacon owner upgrades ALL instances simultaneously.
**Fix:** Timelock + high-threshold multisig, per-cohort beacons, upgrade monitoring with auto-pause. Consider instance-owned delegates, rollback paths, or version-gated upgrade registries when blast-radius control matters.

### Delegatecall Context Confusion
A contract can be called through `delegatecall` even though its logic assumes `address(this)` is the original deployed contract.
**Symptoms:** Functions rely on immutables, self-address checks, pool identity, or storage context, but can be reached through arbitrary proxies.
**Risk:** Code executes against unexpected storage or caller context, bypassing assumptions about pool identity or contract state.
**Fix:** Add no-delegatecall guards to functions that depend on original contract context, such as an immutable self-address comparison, or make delegatecall support explicit with shared storage-layout tests.

### Storage Layout Drift
Upgradeable contracts without namespaced storage, no layout diffing in CI.
**Symptoms:** No EIP-7201, variables inserted between existing ones, multiple inheritance.
**Risk:** Storage collision corrupts critical state (owner, balances). Silently catastrophic.
**Fix:** EIP-7201 namespaced storage, typed storage accessors, layout compatibility checks in CI, append-only with gap slots.

## Cross-Chain

### Bridge Message Replay
Cross-chain message lacks chain ID binding, replay protection depends on single nonce.
**Symptoms:** No per-chain deduplication, shared small validator set.
**Risk:** Valid message on Chain A replayed on Chain B. Wormhole, Ronin, Nomad exploits.
**Fix:** Bind operation, source chain, destination chain, nonce, participants, value, and payload into the request hash; keep per-chain deduplication and independent validator sets. Price relays also need source-feed keyed freshness and monotonic timestamp checks.

### Bridge Endpoint Authentication Mismatch
Bridge adapter authenticates the wrong endpoint because it assumes `msg.sender`, source address, or bridge validation semantics match another bridge's model.
**Symptoms:** Adapter checks only local caller, ignores the bridge-reported source chain/address, or treats a forwarder as the remote app without verifying the bridge's validation primitive.
**Risk:** Messages from the wrong chain, adapter, or remote application can execute as trusted bridge payloads.
**Fix:** Authenticate the local bridge adapter, the bridge-provided source chain, the bridge-provided source address, and the expected remote application. Test wrong chain, wrong sender, wrong adapter, and spoofed forwarder cases for every bridge transport.

### Bridge Custodian Concentration
Bridge holds all locked assets in single custodian, no withdrawal rate-limiting.
**Symptoms:** Hot wallet key management, small multisig (2-of-5), no anomaly detection.
**Risk:** Key compromise drains entire bridge. Ronin: $624M, Harmony: $100M, Multichain: $126M.
**Fix:** Rate-limit withdrawals, anomaly detection with auto-pause, distributed key management (MPC/TSS).

### Trusted SPV Boundary Omitted
Bridge documentation or code presents SPV proofs as fully trustless while the relay or proof submitter set is trusted to provide canonical source-chain data.
**Symptoms:** Bitcoin or external-chain proof verifies merkle inclusion and work, but header submission, chain selection, or maintainer admission is centralized or owner-controlled.
**Risk:** Users and integrators overestimate finality guarantees, and governance can admit false or stale source-chain state as canonical.
**Fix:** Document relay maintainer trust, challenge windows, replacement rules, and emergency procedures. Bind bridge state transitions to authenticated relay state and monitor maintainer or allowlist changes as critical governance events.

## DeFi Architecture

### Shared Pool Sink
Multiple independent pools/strategies share single token vault.
**Symptoms:** One vault contract holds funds for all strategies, one set of access controls.
**Risk:** Single vulnerability drains all connected pools. Balancer V2: $128M across all chains.
**Fix:** Isolate funds per pool/strategy, per-pool withdrawal caps, independent access control. A singleton can be acceptable only when market accounting is keyed by immutable market id and formal or invariant tests prove one market cannot drain another.

### Unguarded Batch Composition
Contract exposes multicall/batch that chains arbitrary internal calls without restriction.
**Symptoms:** `multicall()` or `cook()` with no whitelist on composable actions, or payable delegatecall batching where the same `msg.value` is visible to multiple subcalls.
**Risk:** Individually valid calls composed to break invariants. Abracadabra `cook()` exploit.
**Fix:** Whitelist composable actions, re-validate invariants after entire batch, disallow dangerous combinations. For payable multicall, account from actual contract balance deltas or consume value exactly once instead of trusting `msg.value` in each subcall.

### Permissionless Market Without Guardrails
Anyone can create pools/markets with arbitrary tokens and parameters.
**Symptoms:** No parameter bounds, no curation, no risk isolation for new markets.
**Risk:** Malicious token pool drains paired assets. Euler V1: $197M.
**Fix:** Parameter bounds at protocol level, curated allowlists or risk tiers, isolated risk for permissionless pools. Permissionless markets are safer when oracle, LLTV, and rate-model classes are enabled separately and market assets/debt/bad debt are isolated by market id.
