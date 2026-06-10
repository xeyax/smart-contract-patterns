# Escrow Mint-Burn Refund Fallback

> Pair source escrow or burn with destination validation and automatic refund when bridge settlement cannot safely mint or release.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, escrow, mint-burn, refund, settlement |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Bridge deposits lock or burn assets before destination settlement
- Destination token deployment or peer binding may fail
- The bridge can send a compensating withdrawal or refund message
- Users need liveness even when custom token registration is misconfigured

## Avoid When

- Failed destination settlement cannot be proven or refunded
- Source assets are transferred to an irreversible external custodian
- The protocol cannot distinguish invalid destination state from temporary failure

## Trade-offs

**Pros:**
- Avoids minting wrapped assets into invalid token mappings
- Gives users a recovery path for failed destination settlement
- Makes bridge token deployment failures fail closed

**Cons:**
- Refund paths must be replay-safe and may be delayed
- Partial failures create extra accounting and monitoring burden
- Destination validation must be strict enough to prevent counterfeit peers

## How It Works

On deposit, source-side assets are escrowed or burned. On the destination chain, finalization validates the token contract and peer binding. If validation fails, the bridge sends a refund or withdrawal back instead of minting.

```solidity
function finalizeInbound(address token, address to, uint256 amount) external onlyCounterpart {
    if (!_validDestinationToken(token)) {
        _refundToSource(token, to, amount);
        return;
    }

    _mintOrRelease(token, to, amount);
}
```

## Key Points

- Use balance-delta accounting for source-side escrow transfers.
- Validate destination token code, registered peer, and expected origin token before minting.
- Refund only through authenticated bridge messages.
- Make refund paths available even while new deposits are paused.
- Include failed deployment and wrong-peer tests.
- For async deposit cancellation, bind the reclaim request to the exact message envelope: remote bridge, selector, token, depositor, recipient, amount, payload, and nonce.
- Make delayed reclaim depositor-only and document whether messaging fees are spent and non-refundable.
- Treat cancellation as a race with remote consumption; it is not an instant refund guarantee.
- For failed destination execution, record a transaction-data hash or equivalent proof handle that lets users later prove and reclaim the deposit.
- If the refund handle omits the destination receiver, it must still bind the original depositor, token, amount, and unique destination transaction, and refunds must return only to that depositor.
- For signer-mediated withdrawals, lock the requested amount plus maximum fee, then make signer acceptance burn the locked amount and refund unused fee while signer rejection unlocks the escrow.
- For auto-call bridge settlement, make failed external calls fall back to the original receiver or fallback address instead of leaving approved tokens or native value in the executor.
- When the bridge offers destination native drops, separate recipient principal, relayer/native-drop funding, relayer fee, and refund of excess native value.
- For escrowed token bridge flows, test failed destination handling and wrong-counterpart messages separately from ordinary mint/burn success cases.

## Source Evidence

- Arbitrum token bridge escrow transfer paths release only from authenticated counterpart messages.
- L2 gateway finalization validates deployed tokens and `l1Address()` bindings.
- Gateway fallback handlers trigger refund withdrawals when token deployment or peer validation fails.
- StarkGate deposit cancellation binds the exact L1-to-L2 message envelope, delays depositor-only reclaim, and leaves messaging fees spent even when escrowed principal is reclaimed.
- zkSync Era bridge documentation and integration tests show failed L2 deposit recovery through recorded transaction data hashes and proof paths in [`docs/src/specs/contracts/bridging/overview.md`](https://github.com/matter-labs/zksync-era/blob/3f99eb0d62eb7dba159b78b7e842b9c73f5cf3d0/docs/src/specs/contracts/bridging/overview.md) and `core/tests/ts-integration/tests/l2-erc20.test.ts`.
- Sophon's custom USDC bridge records an L2 transaction hash to source-side deposit-data hash mapping, requires a canonical failed-transaction proof, deletes the record before transfer, and refunds the original depositor in [`src/L1USDCBridge.sol`](https://github.com/sophon-org/custom-usdc-bridge/blob/72b36f11fb6c901380836043a43c738c434d5c12/src/L1USDCBridge.sol).
- Stacks sBTC withdrawal escrow locks `amount + max-fee`, burns on signer acceptance with fee refund, and unlocks on signer rejection in [`contracts/contracts/sbtc-withdrawal.clar`](https://github.com/stacks-network/sbtc/blob/a97172e25e6e255f6a973629505d400ee5d8bebf/contracts/contracts/sbtc-withdrawal.clar), with tests in `contracts/tests/sbtc-withdrawal.test.ts`.
- deBridge auto-call settlement sends leftovers back to reserve, clears approvals, and pays execution fees only around the call proxy frame in [`contracts/periphery/CallProxy.sol`](https://github.com/debridge-finance/debridge-contracts-v1/blob/2e9f9c73438738310b5293cec4cffe25741e9b1f/contracts/periphery/CallProxy.sol) and [`contracts/transfers/DeBridgeGate.sol`](https://github.com/debridge-finance/debridge-contracts-v1/blob/2e9f9c73438738310b5293cec4cffe25741e9b1f/contracts/transfers/DeBridgeGate.sol).
- LI.FI destination receivers catch failed compose swaps and route remaining funds to receiver or refund/fallback handling in [`src/Periphery/ReceiverStargateV2.sol`](https://github.com/lifinance/contracts/blob/7aeb2419d52d6bf834bf2c47e54dd8ea470a57bd/src/Periphery/ReceiverStargateV2.sol) and `src/Periphery/ReceiverAcrossV4.sol`.
- Wormhole's example token bridge relayer separates self-redemption, relayer-funded native drops, fee recipient payout, and recipient token balance in [`evm/src/token-bridge-relayer/TokenBridgeRelayer.sol`](https://github.com/wormhole-foundation/example-token-bridge-relayer/blob/b8ac43d008f9867193e8d08bc54211ae4f5803df/evm/src/token-bridge-relayer/TokenBridgeRelayer.sol).
- Velodrome Superchain escrow bridges lock and release assets through root and leaf escrow bridge contracts in [`src/root/bridge/RootEscrowTokenBridge.sol`](https://github.com/velodrome-finance/superchain-contracts/blob/c93c466a2fcd1fd9dc79ba569f6b81c42bb50d61/src/root/bridge/RootEscrowTokenBridge.sol) and [`src/bridge/LeafEscrowTokenBridge.sol`](https://github.com/velodrome-finance/superchain-contracts/blob/c93c466a2fcd1fd9dc79ba569f6b81c42bb50d61/src/bridge/LeafEscrowTokenBridge.sol).

## Related Patterns

- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Relayer-Funded Native Drop Accounting](./pattern-relayer-funded-native-drop-accounting.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
