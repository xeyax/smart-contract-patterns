# Participant Permission Bitmap

> Encode participant eligibility as compact policy bits so deposits, borrows, transfers, and exits can enforce both account-level and pool-level access.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, permissions, allowlist, bitmap, transfer-policy |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- A pool has private, public, pool-level, or function-level participation modes
- Transfers must verify both sender and receiver eligibility
- Eligibility needs to be updated without migrating pool state
- Permission checks are hot-path and need compact storage

## Avoid When

- All participants are fully permissionless
- Eligibility depends on complex off-chain terms that cannot be represented on-chain
- Policy bits are undocumented or overloaded across unrelated meanings

## Trade-offs

**Pros:**
- Efficient storage and transfer checks
- Makes policy transitions explicit
- Supports private markets without bespoke code per pool

**Cons:**
- Bit semantics can become hard to audit if not named clearly
- Off-chain onboarding still remains a trust boundary
- Transfer restrictions reduce token composability

## How It Works

Represent pool and participant policy as bitsets:

```solidity
uint256 constant PUBLIC = 1 << 0;
uint256 constant POOL_LEVEL = 1 << 1;
uint256 constant FUNCTION_LEVEL = 1 << 2;

mapping(address => uint256) public poolPolicy;
mapping(address => mapping(address => uint256)) public participantBits;

function hasPermission(address pool, address account, uint256 requiredBit) public view returns (bool) {
    uint256 policy = poolPolicy[pool];
    if (policy & PUBLIC != 0) return true;
    return participantBits[pool][account] & requiredBit != 0;
}
```

For transfers, check both endpoints:

```solidity
require(hasPermission(pool, from, SEND_BIT), "sender not allowed");
require(hasPermission(pool, to, RECEIVE_BIT), "receiver not allowed");
```

### Registry Or Role-Backed Variant

Eligibility can also be delegated to a permission manager that stores named roles instead of compact bits:

```solidity
require(permissionManager.hasRole(WHITELISTED_ROLE, from), "from");
require(permissionManager.hasRole(WHITELISTED_ROLE, to), "to");
```

This is easier to inspect for regulated tokens, but it still needs the same endpoint coverage and admin controls. Role changes should be evented, and role admins are part of the transfer-policy trust boundary.

### Regulated Vault Share Variant

For redeemable or claim-bearing vault shares, endpoint checks must cover the caller, owner/from account, receiver/to account, and any delegated spender. If a holder is frozen or blocklisted, rescue paths should move specific share balances or claim-ledger entries, emit the affected periods and amounts, and document who can redirect custody.

## Key Points

- Name every bit and keep a policy table in docs or deployment artifacts.
- Check both sides of transfers when secondary market eligibility matters.
- Distinguish pool-level allowlists from function-level permissions.
- If roles or registries replace bitmaps, keep the same sender, receiver, delegated-spender, and redemption-contract coverage.
- Emit events for bit changes so off-chain compliance and monitoring can reconstruct state.
- Fuzz policy combinations, not only the happy-path private/public modes.
- For regulated or permissioned shares, check the delegated transfer initiator as well as `from` and `to`; a non-eligible spender should not move eligible users' tokens through `transferFrom`.
- If transfer rights intentionally inherit from the `from` account through normal ERC20 approval, document that delegation as a business requirement and test approved spenders explicitly.
- Permission bits may include expiry timestamps, freeze bits, and endorsed system escrow/router bypasses, but bypasses should be narrow and documented.
- For regulated vault shares, rescue frozen accounts through specific entitlements rather than broad operator custody.

## Source Evidence

- Maple uses participant permission modes and pool/lender bitmaps, with tests covering private, function-level, pool-level, public, and transfer eligibility checks.
- Centrifuge liquidity pools use time-bounded membership, freeze state, sender/receiver checks, endorsed escrow/router paths, and authorized settlement transfers for permissioned tranche tokens.
- An Ondo audit-contest snapshot checks KYC/sanctions status for `from`, `to`, and delegated transfer initiator on regulated rebasing share transfers.
- Spiko's Stellar token delegates mint, transfer, redeem, and redemption-contract eligibility to a permission manager with admin-controlled whitelist roles.
- Karpatkey's KPK token intentionally lets an allowlisted sender delegate transfers through ERC20 approval, illustrating that delegated-spender checks are policy-dependent and must be explicit.
- Firelight's regulated vault-share flow checks transfer endpoints and includes frozen-account rescue mechanics for claim-ledger periods and amounts.

## Related Patterns

- [Selector-Scoped Authority](./pattern-selector-scoped-authority.md)
- [Unvalidated External Contract](../../ANTIPATTERNS.md#unvalidated-external-contract)
- [Permissioned Exit Custody](../../ANTIPATTERNS.md#permissioned-exit-custody)
