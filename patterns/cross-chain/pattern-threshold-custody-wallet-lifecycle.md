# Threshold Custody Wallet Lifecycle

> Manage bridge custody through rotating threshold-signer wallets with explicit states, liveness timeouts, moving-funds transitions, and fraud challenges.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, threshold, custody, wallet, slashing |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A bridge custody account is controlled by a threshold signer group
- Wallets need rotation, retirement, or moving-funds flows
- Signer liveness and dishonest signatures can be challenged on-chain
- The chain cannot directly execute custody actions and must verify evidence

## Avoid When

- A single custodian or multisig is the intended trust model
- The protocol cannot observe enough evidence to distinguish valid from fraudulent signatures
- Timeout and slashing parameters cannot be safely calibrated

## Trade-offs

**Pros:**
- An explicit state machine makes every custody transition enumerable, timeout-bounded, and auditable.
- Public liveness notifications let anyone escalate stuck redemptions or moving-funds flows without privileged roles.
- Fraud challenges with evidence-based defeat paths punish dishonest signers without trusting an external oracle.
- Wallet rotation and retirement limit long-lived key exposure for custody funds.

**Cons:**
- Timeout and slashing calibration is delicate: too short slashes honest-but-slow signer groups, too long strands user funds.
- Defeat logic is subtle — a wallet signature alone does not prove theft, so valid-evidence rules need careful design and testing.
- Moving-funds transitions are operationally heavy and create transient custody risk during every rotation.
- The combined state machine, challenge, notification, and slashing surface is large and expensive to audit.
- The chain can only punish a malicious off-chain spend after the fact via evidence; it cannot prevent one.

## How It Works

Wallets move through explicit states and every custody transition has a timeout or evidence path:

```solidity
enum WalletState { Unknown, Live, MovingFunds, Closing, Closed, Terminated }

function notifyRedemptionTimeout(bytes32 walletId) external {
    require(wallets[walletId].state == WalletState.Live, "bad state");
    require(block.timestamp > redemptionDeadline[walletId], "too early");
    _slashOrMoveFunds(walletId);
}

function challengeFraud(bytes calldata signature, bytes32 walletId) external payable {
    require(_signatureMatchesWallet(signature, walletId), "bad signature");
    challenges[walletId] = FraudChallenge(msg.sender, block.timestamp);
}
```

Valid protocol spends or heartbeat messages can defeat a fraud challenge; unresolved challenges can slash or terminate the wallet.

## Key Points

- Define every wallet state and valid transition before funds can enter the wallet.
- Keep active-wallet selection explicit and resistant to stale or closing wallets.
- Add public liveness notifications for timeouts that affect redemption, moving funds, and closing.
- Let fraud challenges be defeated by valid protocol evidence; a signature alone may not prove theft.
- Keep custody reserve requirements separate from signer-lifecycle mechanics.

## Source Evidence

- tBTC v2 models threshold signer wallets with lifecycle states, active-wallet selection, moving-funds flows, redemption timeouts, fraud challenges, defeat paths, and slashing or reward outcomes.

## Related Patterns

- [Custodial Reserve Backing](./req-custodial-reserve-backing.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)
