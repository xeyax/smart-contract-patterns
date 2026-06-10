# Custodian-Attested Mint/Burn

> Mint and burn wrapped assets through merchant requests that are approved and reconciled by a trusted custodian.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, custodian, wrapped-asset, mint, burn, attestation |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- The source asset is not trustlessly verifiable on the destination chain
- A regulated or operational custodian is an explicit trust assumption
- Merchants or operators intermediate mint and burn requests
- Public reserve verification can support the custody model

## Avoid When

- The bridge can verify source-chain finality and messages on-chain
- Users expect trustless redemption
- The custodian cannot publish reserves or settlement identifiers

## Trade-offs

**Pros:**
- Works for assets that lack direct on-chain verification
- Separates merchant request flow from custodian approval
- Gives an auditable mint/burn ledger

**Cons:**
- Custodian solvency and honesty are core trust assumptions
- Redemption can depend on off-chain settlement and operating hours
- Small redemptions can create operational DoS or external fee pressure
- Pauses or admin actions can trap exits if not carefully scoped

## How It Works

```solidity
function requestMint(uint256 amount, bytes32 depositTxId) external onlyMerchant returns (uint256 id) {
    id = ++nextRequestId;
    mintRequests[id] = MintRequest(msg.sender, amount, depositTxId, false);
}

function approveMint(uint256 id) external onlyCustodian {
    MintRequest storage request = mintRequests[id];
    require(!request.approved, "approved");
    request.approved = true;
    token.mint(request.merchant, request.amount);
}

function burn(uint256 amount, string calldata withdrawalAddress) external onlyMerchant returns (uint256 id) {
    token.burnFrom(msg.sender, amount);
    id = ++nextRequestId;
    burnRequests[id] = BurnRequest(msg.sender, amount, withdrawalAddress, "");
}

function recordSettlement(uint256 id, string calldata settlementTxId) external onlyCustodian {
    burnRequests[id].settlementTxId = settlementTxId;
}
```

## Key Points

- Track mint and burn request ids with external settlement identifiers.
- Publish or verify reserves so `custody balance >= token totalSupply`.
- Enforce minimum redemption amounts or batching where external settlement has fixed costs.
- Scope pauses so successful burns have a refund or settlement path.
- Do not describe this as trustless bridging; document custodian and merchant trust explicitly.
- If an on-chain exit only burns representation and emits an external destination, state clearly that off-chain settlement remains a custody obligation until the source-chain payout is proven.

### Sequenced Custodian Instruction Queue

For custodian systems that emit off-chain transfer instructions, keep separate
ledgers for confirmed funds, pending requests, escrowed funds, and emitted
instructions. A request should be admitted only when confirmed plus escrowed
funds can cover the requested amount and fees, and each emitted instruction
should carry a sequence number or payment reference that off-chain operators can
execute and later reconcile.

## Source Evidence

- WBTC uses merchant mint requests approved by a custodian and merchant burn requests reconciled with settlement transaction ids.
- WBTC documentation and audit materials emphasize public reserve verification and custodian backing.
- Lorenzo enzoBTC withdrawal requests burn or mark on-chain representation and emit BTC destination data for off-chain custody release in [`src/modules/WithdrawalRequest.sol`](https://github.com/Lorenzo-Protocol/enzoBTC_contract/blob/5951bff2cd51a3ac91a239ed6ca73aca095986dd/src/modules/WithdrawalRequest.sol) and [`x/btcstaking/keeper/msg_server.go`](https://github.com/Lorenzo-Protocol/lorenzo/blob/ee65c41e485ad7b57f4e40d0230c029354610a7d/x/btcstaking/keeper/msg_server.go).
- Flare FAssets CoreVaultManager confirms incoming custody payments once per transaction id, admits transfer requests only against available plus escrowed funds, emits sequenced off-chain payment instructions, and bounds escrow processing in [`contracts/coreVaultManager/implementation/CoreVaultManager.sol`](https://github.com/flare-foundation/fassets/blob/37c1be508a33c0d0ce31216aef45958fd4e5281e/contracts/coreVaultManager/implementation/CoreVaultManager.sol).

## Related Patterns

- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md) - trustless bridge replay domain pattern
- [Signed Custody-Routed Mint](./pattern-signed-custody-routed-mint.md) - typed signed order flow for routed custody settlement
- [Custodial Reserve Backing](./req-custodial-reserve-backing.md)
- [Value-Tiered Source Finality](./pattern-value-tiered-source-finality.md)
- [Bridge Custodian Concentration](../../ANTIPATTERNS.md#bridge-custodian-concentration)
