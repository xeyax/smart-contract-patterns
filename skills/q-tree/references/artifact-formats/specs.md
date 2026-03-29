# Spec Formatting Rules

Rules for `specs/*.t.sol` artifacts.

## Section titles

Include source artifact reference in all section titles:

```solidity
//  SECTION 1: INVARIANTS (from invariants.md)
//  SECTION 2: ACCESS CONTROL (from access-control.md)
//  SECTION 3: POSTCONDITIONS (from call-diagrams.md)
//  SECTION 4: STATE MACHINE (from state-machines.md)
//  SECTION 5: MATHEMATICAL PROPERTIES
```

## Traceability comments

Reference source as `artifact.md ID` before each test function:

```solidity
/// invariants.md I1 -- no shares without assets
function invariant_noSharesWithoutAssets() public view { ... }

/// access-control.md -- rebalance: keeper only
function testFail_rebalanceByNonKeeper() public { ... }

/// call-diagrams.md POST: deposit -- shares minted proportional to NAV
function check_depositMintsProportionalShares() public { ... }
```

Never use `d:tag` references in specs — always reference the artifact file and specific item.

## Naming conventions

- `invariant_*` — Foundry fuzzer calls these after random call sequences.
- `testFail_*` — must revert (negative cases: unauthorized access, invalid transitions).
- `check_*` — postcondition checks, called from unit tests or stateful fuzzing handlers.

## Section scope notes

**SECTION 2 (Access Control):** Not just `onlyOwner` — every guard gets a `testFail_*`: nonReentrant, bound checks, input validation, ERC-20 allowance requirements. For nonReentrant, test with a reentrant callback contract if the interface allows it.

**SECTION 3 (Postconditions):** For compound operations (function internally calls another), verify ALL side-effects, not just the caller's return value. Example: if `redeem` calls `_accruePerformanceFee` internally, check user assets AND feeReceiver balance AND HWM. For token-moving functions, assert BOTH sender and receiver balance deltas with exact amounts.

**SECTION 4 (State Machine):** Not just transitions — also verify that functions NOT mentioned in the state machine continue working in each state. If pause blocks deposits, explicitly test that admin setters, redeem, and accrual still work when paused.

## SECTION 5: Mathematical Properties

System-wide properties that aren't tied to a single call diagram. These verify correctness of core math — the most critical checks for financial contracts.

Generate these by analyzing token-flows, invariants, and the domain model. Common categories:

- **Proportionality** — deposit X% of totalAssets → receive X% of totalSupply
- **Round-trip** — deposit → immediate redeem returns ≈ original (minus fees, rounding)
- **Linearity** — two deposits of N ≈ one deposit of 2N
- **Fee math** — exact fee formula produces expected feeShares for known inputs
- **Conservation** — total value in = total value out + fees (no value created/destroyed)
- **Rounding direction** — always favors the vault (protocol) over the user, or vice versa per design
- **Entry point equivalence** — multiple functions doing the same thing must produce same result (e.g. deposit vs depositWithReferral → same shares). Also verify the simple path does NOT trigger rich path side-effects (deposit() must not set referrer).
- **Recovery scenarios** — behavior after adverse conditions: drawdown (no fee until PPS exceeds previous HWM), recovery from pause, zero-supply edge cases

Example:

```solidity
/// mathematical -- proportional share minting
function check_depositProportionality(uint256 assets) public {
    _depositAs(user1, 10e18); // seed
    uint256 totalAssetsBefore = _totalAssets();
    uint256 totalSupplyBefore = _totalSupply();
    _depositAs(user2, assets);
    uint256 shares = _wrapperShareBalance(user2);
    assertEq(shares, assets * totalSupplyBefore / totalAssetsBefore);
}

/// mathematical -- deposit/redeem round-trip
function check_roundTrip(uint256 assets) public {
    _depositAs(user1, assets);
    uint256 shares = _wrapperShareBalance(user1);
    _redeemAs(user1, shares);
    // user gets back ≈ assets (minus rounding, no fee if no yield)
    assertApproxEqAbs(asset.balanceOf(user1), startBalance, 1);
}
```

Only generate properties where the architecture defines the math. If the formula is a `[GAP]` — note it in the traceability matrix.

## Cross-file consistency

- All spec files use identical section separator style: `// ===============================================================`
- All spec files have a traceability matrix comment block at the top.
