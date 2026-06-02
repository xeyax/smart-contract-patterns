# Move Receipt-Bound Flash Loan

> Bind a Move flash loan to repayment by returning a non-storable receipt that must be consumed in the same transaction.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | move, flash-loan, receipt, linear-type, repayment |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A Move-based lending protocol offers atomic flash liquidity
- The language can enforce resource abilities such as non-drop and non-store
- Repayment should be mandatory before transaction completion
- The loan needs to bind asset, amount, fee, pool, and borrower context

## Avoid When

- Flash liquidity may intentionally convert into open debt
- Repayment can happen in a later transaction or through another account
- The receipt can be dropped, stored, copied, or wrapped in an untrusted container

## Trade-offs

**Pros:**
- Uses the type system to force repayment flow
- Avoids scanning transaction instructions or persisting transient debt state
- Makes repayment context explicit and tamper-resistant

**Cons:**
- Move-only pattern; it does not translate directly to EVM
- Receipt fields and abilities become security-critical API surface
- Composability depends on routers preserving and returning the receipt

## How It Works

The loan function transfers assets and returns a receipt resource with no `drop`,
`store`, or `copy` ability. Repayment consumes the receipt and verifies the
returned asset, pool, borrower, amount, and fee.

```move
struct FlashLoanReceipt has key {
    borrower: address,
    pool_id: ID,
    asset: TypeName,
    amount: u64,
    fee: u64,
}

public fun loan(pool: &mut Pool, amount: u64): (Coin<Asset>, FlashLoanReceipt) {
    let fee = flash_fee(pool, amount);
    (withdraw(pool, amount), FlashLoanReceipt {
        borrower: tx_context::sender(),
        pool_id: object::id(pool),
        asset: type_name::get<Asset>(),
        amount,
        fee,
    })
}

public fun repay(pool: &mut Pool, payment: Coin<Asset>, receipt: FlashLoanReceipt) {
    assert!(receipt.pool_id == object::id(pool), E_WRONG_POOL);
    assert!(coin::value(&payment) >= receipt.amount + receipt.fee, E_UNDERPAID);
    deposit(pool, payment);
    destroy_receipt(receipt);
}
```

## Implementation

- Omit `drop`, `store`, and `copy` abilities from the receipt type.
- Put every repayment-critical field in the receipt, not in caller-provided arguments.
- Consume the receipt exactly once in the repay path.
- Reject repayments to the wrong pool or asset type.
- Test attempts to skip repay, repay the wrong pool, repay too little, and wrap or leak the receipt through router code.

## Source Evidence

- NAVI defines flash-loan receipt flow in `/private/tmp/defillama-source/naviprotocol__navi-smart-contracts/lending_core/sources/flash_loan.move` using `Receipt`, `loan`, `loan_v2`, and `repay`.
- NAVI lending wrappers in `/private/tmp/defillama-source/naviprotocol__navi-smart-contracts/lending_core/sources/lending.move` route flash loans through the receipt contract.
- NAVI flash-loan tests in `/private/tmp/defillama-source/naviprotocol__navi-smart-contracts/lending_core/tests/flash_loan_tests.move` cover repayment behavior.

## Real-World Examples

- NAVI uses receipt-bound flash loans in its Sui lending core.

## Related Patterns

- [Solana Instruction-Paired Flash Loan](./pattern-solana-instruction-paired-flash-loan.md)
- [Debt-Converting Flash Loan](./pattern-debt-converting-flash-loan.md)
- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)

## References

- Move resource abilities and linear asset semantics.
