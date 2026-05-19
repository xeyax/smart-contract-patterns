# Semi-Fungible Slot Reserve Wrapper

> Wrap ERC-3525 or other slot-scoped semi-fungible positions into one ERC-20 claim token per slot while the pool owns the underlying slot value id.

## Metadata

| Property | Value |
|----------|-------|
| Category | token-integration |
| Tags | token-integration, erc3525, sft, wrapper, reserve |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Underlying positions are semi-fungible by slot
- Each slot should become a fungible ERC-20 claim
- The wrapper can custody one holding value id per supported slot
- Deposits and withdrawals should be gated per slot

## Avoid When

- Slot values are not economically fungible within the slot
- Decimal precision differs between the SFT value and wrapped ERC-20
- The pool cannot prove it owns the holding value id
- The wrapper is expected to prove off-chain reserve backing

## How It Works

Map each supported slot to a wrapped ERC-20 and a pool-owned SFT value id:

```solidity
struct SlotInfo {
    IERC3525 sft;
    uint256 holdingValueId;
    IERC20 wrapped;
    bool depositsAllowed;
    bool withdrawalsAllowed;
}

function deposit(uint256 slot, uint256 fromValueId, uint256 amount) external {
    SlotInfo storage info = slots[slot];
    require(info.depositsAllowed, "deposit disabled");
    info.sft.transferValue(fromValueId, info.holdingValueId, amount);
    info.wrapped.mint(msg.sender, amount);
}

function withdraw(uint256 slot, uint256 amount, uint256 toValueId) external {
    SlotInfo storage info = slots[slot];
    require(info.withdrawalsAllowed, "withdraw disabled");
    info.wrapped.burnFrom(msg.sender, amount);
    info.sft.transferValue(info.holdingValueId, toValueId, amount);
}
```

## Key Points

- Create one wrapped ERC-20 per slot.
- Verify wrapped-token decimals equal the SFT value decimals.
- Keep one pool-owned holding value id per slot.
- Gate deposits and withdrawals independently by slot.
- Do not treat slot custody as proof of external reserve backing.
- Test wrong slot, wrong decimals, disabled deposit/withdraw, and value-id ownership cases.

## Source Evidence

- SolvBTC maps ERC-3525 slots to wrapped ERC-20 tokens and pool-owned value ids, moves SFT value into and out of the holding id, mints and burns wrapped tokens 1:1, verifies decimal equality, and exposes per-slot gates.

## Related Patterns

- [Adapter-Isolated Core Ledger](./pattern-adapter-isolated-core-ledger.md)
- [Balance Delta Transfer Accounting](./pattern-balance-delta-transfer-accounting.md)
