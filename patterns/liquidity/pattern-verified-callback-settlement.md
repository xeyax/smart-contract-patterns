# Verified Callback Settlement

> Let AMM pools optimistically call external payers during mint, swap, or flash operations, then verify post-callback balances before finalizing.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, callback, settlement, swap, flash |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- The pool needs optimistic settlement for swaps, mints, or flash loans
- Callers can source payment from arbitrary contracts during the callback
- The pool can verify token balance deltas after the callback
- Callback callers can verify the canonical pool address

## Avoid When

- Token balance checks cannot reliably prove payment
- Reentrancy locks cannot span the full operation
- Callback payloads are allowed to control critical pool state

## Trade-offs

**Pros:**
- Payers can source funds during the callback, enabling flash swaps, just-in-time sourcing, and approval-free integrations.
- Post-callback balance verification makes payment proof objective — the pool checks tokens received, not caller claims.
- One settlement shape covers mint, swap, and flash paths, reusing the same lock and balance-check machinery.
- Optimistic transfer-first flow avoids pre-funding and double transfers for sophisticated routers.

**Cons:**
- Reentrancy lock must span the entire operation; any invariant write reachable during the callback outside the lock is an exploit path.
- Trust is asymmetric: the pool is protected by balance checks, but every callback receiver must independently validate the canonical pool address or be drained by spoofed callbacks.
- Balance-delta verification mishandles fee-on-transfer and rebasing tokens, silently converting transfer fees into pool underpayment.
- Contract-only integration — EOAs cannot implement callbacks, so every consumer needs audited periphery code.
- Netting or transfer-skip variants move the proof from token balances to ledger reconciliation, a subtler check that is easier to get wrong.

## How It Works

The pool transfers or accounts optimistically, calls the user callback, then checks that the required token balance was paid:

```solidity
uint256 balanceBefore = token.balanceOf(address(this));
ICallback(msg.sender).swapCallback(amount0Owed, amount1Owed, data);
require(token.balanceOf(address(this)) >= balanceBefore + amountOwed, "underpaid");
```

Periphery callback handlers validate `msg.sender` against the canonical factory-derived pool before paying.

Some shared-liquidity systems support callback modes that skip direct transfers or net transfers across integrated modules. In that variant, the callback still needs a final input/output balance check against the core ledger before the operation commits.

V2 flash-swap receivers are the same trust shape even though the callback name and
pair model differ: the receiver must verify `msg.sender` is the factory-derived
pair for the expected tokens before doing arbitrary work and repaying. Example or
demo receivers are useful evidence for the mechanics, but production code should
still add the same reentrancy, slippage, and token-safety review as any callback.

## Key Points

- Lock the pool for the full callback-settlement operation.
- Verify post-callback balances for each owed token.
- Bind callback caller to token pair, fee tier, and factory.
- If transfer skipping or netting is supported, prove the net input and output are balanced against the liquidity core before committing.
- Avoid writes to critical invariant state after untrusted callbacks unless they are already locked and accounted.
- Periphery callback handlers should verify `msg.sender` is the expected pool or market before paying; core post-callback balance checks do not automatically protect a generic callback helper.
- Callback settlement can be exposed directly by a pool, but the pool must verify
  the exact owed input balance delta after the callback and keep invariant state
  protected by the operation lock.
- Test underpayment, wrong-callback-caller, reentrancy, and fee-on-transfer token assumptions.

## Source Evidence

- Uniswap V3 and PancakeSwap V3 use optimistic mint/swap/flash callbacks, pool-wide locks, callback caller validation, and post-callback balance checks with underpayment tests.
- Fluid liquidity operations include `SKIP_TRANSFERS` and `NET_TRANSFERS` style settlement modes that still enforce final balance and total-input checks around callbacks.
- QuickSwap/Uniswap V2 example flash-swap receivers validate callback sender against the factory-derived pair before repayment in [`contracts/examples/ExampleFlashSwap.sol`](https://github.com/QuickSwap/quickswap-periphery/blob/522a94168b0814d0776d834119df377f03898807/contracts/examples/ExampleFlashSwap.sol); treat this as example-level evidence.
- SunSwap V3 repeats the Uniswap V3 callback settlement shape on TRON with router-side callback validation and pool-side post-callback balance checks.
- Pendle V2 market callbacks demonstrate the caveat: the market checks post-callback balances, but generic periphery callback handlers still need expected-caller validation.
- Curve Crypto `exchange_extended` supports callback settlement and requires the
  exact input balance delta before finalizing in [`contracts/two/CurveCryptoSwap2.vy:722-837`](https://github.com/curvefi/curve-crypto-contract/blob/d7d04cd9ae038970e40be850df99de8c1ff7241b/contracts/two/CurveCryptoSwap2.vy#L722-L837),
  with callback tests in [`tests/twocrypto/test_callback.py:17-54`](https://github.com/curvefi/curve-crypto-contract/blob/d7d04cd9ae038970e40be850df99de8c1ff7241b/tests/twocrypto/test_callback.py#L17-L54).

## Related Patterns

- [Canonical AMM Pool Factory](./pattern-canonical-amm-pool-factory.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Shared Liquidity Kernel](./pattern-shared-liquidity-kernel.md)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)
