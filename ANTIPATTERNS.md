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
**Fix:** Single owner per state, others read via view functions.

### Missing Abstraction
Direct coupling to external protocol without adapter/interface layer.
**Symptoms:** Protocol-specific types/calls scattered throughout codebase, painful to switch providers.
**Fix:** Adapter contract wrapping external protocol behind stable internal interface.

### Leaky Abstraction
Internal implementation details exposed through contract interfaces.
**Symptoms:** Callers need to know internal state layout, function parameters expose internal concepts.
**Fix:** Interface describes WHAT not HOW. Hide internal mechanics.

## Access Control

### Unrestricted Admin
Owner/admin can change critical parameters instantly without timelock, bounds, or multi-sig.
**Symptoms:** Setter functions with no delay, no upper/lower bounds on parameters, single EOA as owner.
**Risk:** Rug pull, accidental misconfiguration, governance attack.
**Fix:** Timelock on critical changes, hard-coded bounds on parameters, multi-sig or governance for admin.

### Missing Pause
No emergency stop mechanism. If exploit found, no way to stop bleeding.
**Symptoms:** No pause function, or pause doesn't cover all entry points.
**Fix:** Pausable with clear scope (what's paused, what's not — e.g., pause deposits but not withdrawals).

### Pause Traps Funds
Pause blocks ALL operations including withdrawals.
**Symptoms:** Pause disables both deposit and withdraw/redeem.
**Risk:** Users cannot exit during emergency.
**Fix:** Pause blocks deposits only. Withdrawals always available.

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
**Fix:** Bounded batch processing, pagination, or restructure to avoid loops.

### Fee-on-Transfer Blindness
Assumes token transfer delivers exact amount. Doesn't account for fee-on-transfer or rebasing tokens.
**Symptoms:** `transferFrom(amount)` followed by using `amount` directly without checking balance delta.
**Risk:** Accounting mismatch, exploitable for value extraction.
**Fix:** Measure actual balance change, or explicitly reject fee-on-transfer tokens.

### Missing Slippage Protection
Value-bearing operation (swap, deposit, mint) without user-specified bounds on acceptable outcome.
**Symptoms:** No `minAmountOut`, no `maxSlippage`, no `deadline` parameter.
**Risk:** Sandwich attack, stale transaction execution at unfavorable price.
**Fix:** User-provided slippage bounds + deadline.

### Donation Attack Surface
Share price manipulable via direct token transfer to contract.
**Symptoms:** `totalAssets()` reads token balance directly, no virtual offset or internal accounting.
**Risk:** Attacker donates tokens → inflates share price → first depositor gets ~0 shares.
**Fix:** Virtual shares/assets offset, minimum first deposit, or internal accounting not based on balance.

## State & Lifecycle

### Uninitialized Proxy
Upgradeable proxy without initializer protection.
**Symptoms:** `initialize()` without `initializer` modifier, or no initialization check.
**Risk:** Attacker calls initialize on implementation, takes ownership.
**Fix:** OpenZeppelin `initializer` modifier, or `_disableInitializers()` in constructor.

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
**Fix:** Use SafeERC20, check return values, handle reverts explicitly.

### Composability Assumption
Architecture assumes external protocol behavior that may change.
**Symptoms:** Hard-coded addresses, assumed interface stability, no version check.
**Risk:** External protocol upgrades, changes behavior, or gets exploited → cascading failure.
**Fix:** Adapter layer, version checks, circuit breaker on unexpected behavior.

### Hook/Callback Trust
Protocol calls external hooks/callbacks (Uniswap V4 hooks, ERC-777 receivers, flash loan callbacks) without restricting what the hook can do.
**Symptoms:** External hook can re-enter or call back into protocol state. No hook sandboxing.
**Risk:** Malicious hooks manipulate protocol state mid-execution. Uniswap V4 hook exploits: $11M+.
**Fix:** Restrict hook capabilities (read-only where possible), reentrancy locks spanning entire operation, whitelist hooks through governance.

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
**Fix:** Liquidity buffer (10-20% TVL always liquid), pro-rata withdrawal during stress, forced unwind triggers.

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
**Fix:** Measure actual balance change, or explicitly reject fee-on-transfer tokens.

### Implicit Decimal Assumption
Protocol hardcodes 18 decimals or assumes all tokens have same decimals.
**Symptoms:** No per-token decimal normalization, share math doesn't account for decimal differences.
**Risk:** USDC (6 decimals) valued as 1e12× correct amount. Common in multi-token vaults.
**Fix:** Read and normalize decimals per token, scale to canonical precision, fuzz with varying decimals.

### Approval Persistence
Protocol requests unlimited approval, approved spender contracts are upgradeable.
**Symptoms:** `type(uint256).max` approval, no permit2, no session-scoped approvals.
**Risk:** Compromised or maliciously upgraded contract drains all users. Multichain exploit.
**Fix:** Permit2 or ERC-7674 transient approvals, exact-amount approvals, time-bound approvals.

## Governance

### Flash Loan Governance
Governance token = voting token, no snapshot, no minimum holding period.
**Symptoms:** No snapshot mechanism, proposal execution without timelock, emergency bypass.
**Risk:** Flash loan borrow governance tokens → pass malicious proposal in one tx. Beanstalk: $182M.
**Fix:** Snapshot voting at prior block, time-weighted voting power, mandatory timelock on all paths.

### Governance as Arbitrary Execution
Governor contract executes arbitrary calldata against any target.
**Symptoms:** No target/function whitelist, weak community monitoring, no veto mechanism.
**Risk:** Passed proposal becomes unrestricted execution primitive. Can drain treasury, brick protocol.
**Fix:** Whitelist targets/selectors, separate parameter changes from code upgrades, veto/guardian role.

## Lending / Borrowing

### Toxic Liquidation Spiral
Lending protocol allows illiquid collateral, fixed liquidation bonus, no circuit breaker.
**Symptoms:** No liquidity-aware parameters, no cascading liquidation protection, no bad-debt backstop.
**Risk:** Liquidations push prices down → more liquidations → bad debt. Aave V2: $1.7M bad CRV debt.
**Fix:** Liquidity-aware listing, graduated liquidation, bad-debt backstop, halt beyond LTV threshold.

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
**Fix:** Timelock + high-threshold multisig, per-cohort beacons, upgrade monitoring with auto-pause.

### Storage Layout Drift
Upgradeable contracts without namespaced storage, no layout diffing in CI.
**Symptoms:** No EIP-7201, variables inserted between existing ones, multiple inheritance.
**Risk:** Storage collision corrupts critical state (owner, balances). Silently catastrophic.
**Fix:** EIP-7201 namespaced storage, layout compatibility checks in CI, append-only with gap slots.

## Cross-Chain

### Bridge Message Replay
Cross-chain message lacks chain ID binding, replay protection depends on single nonce.
**Symptoms:** No per-chain deduplication, shared small validator set.
**Risk:** Valid message on Chain A replayed on Chain B. Wormhole, Ronin, Nomad exploits.
**Fix:** (sourceChain, destChain, nonce) tuples, per-chain deduplication, independent validator sets.

### Bridge Custodian Concentration
Bridge holds all locked assets in single custodian, no withdrawal rate-limiting.
**Symptoms:** Hot wallet key management, small multisig (2-of-5), no anomaly detection.
**Risk:** Key compromise drains entire bridge. Ronin: $624M, Harmony: $100M, Multichain: $126M.
**Fix:** Rate-limit withdrawals, anomaly detection with auto-pause, distributed key management (MPC/TSS).

## DeFi Architecture

### Shared Pool Sink
Multiple independent pools/strategies share single token vault.
**Symptoms:** One vault contract holds funds for all strategies, one set of access controls.
**Risk:** Single vulnerability drains all connected pools. Balancer V2: $128M across all chains.
**Fix:** Isolate funds per pool/strategy, per-pool withdrawal caps, independent access control.

### Unguarded Batch Composition
Contract exposes multicall/batch that chains arbitrary internal calls without restriction.
**Symptoms:** `multicall()` or `cook()` with no whitelist on composable actions.
**Risk:** Individually valid calls composed to break invariants. Abracadabra `cook()` exploit.
**Fix:** Whitelist composable actions, re-validate invariants after entire batch, disallow dangerous combinations.

### Permissionless Market Without Guardrails
Anyone can create pools/markets with arbitrary tokens and parameters.
**Symptoms:** No parameter bounds, no curation, no risk isolation for new markets.
**Risk:** Malicious token pool drains paired assets. Euler V1: $197M.
**Fix:** Parameter bounds at protocol level, curated allowlists or risk tiers, isolated risk for permissionless pools.
