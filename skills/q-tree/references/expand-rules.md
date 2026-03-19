# Expand Rules

Detailed rules for the orchestrator's EXPAND phase — how to present batches, collect answers, and handle user responses.

## Present batch

Take the batch from the generator's output (already ordered, limited to 5, formatted). Add the round header and accept prompt:

```
[Round 5] 5 questions (2 previous, 3 new — decomposing "Async withdraw"):

[batch from generator]

Accept all? [Y / numbers to change / "details N"]
```

Rule: **Show EVERY new node** (including `~` auto). Nothing becomes ✓ without the user seeing it first.

## Collect answers — single loop with depth-first decomposition

The loop processes unanswered questions until all are resolved or skipped, then exits to CHECK. On every user response:

1. **Parse** the response as a whole. A single message may contain answers to some questions AND a request to dig into another.
2. **Write immediately.** Every answer, override, or skip → write to tree file now. Never hold confirmed answers in memory across exchanges. Record rejected variants and discovered constraints in the Details section of the question, not as tree nodes.
3. **Route:**
   - All questions answered or skipped → exit to CHECK.
   - User wants to dig into a question (details, question, pushback, "dig into N") → **decompose** that question into sub-questions, present them. If the user asks about multiple questions, dig into the **first** one mentioned — the rest wait.
   - Otherwise (some answered, no dig-in request, remaining > 0) → show remaining unanswered.

## What triggers decomposition

- "details N" — user wants reasoning; show it, then if unresolved, decompose into sub-questions
- Asks a question about N / "tell me about N" — user needs more info to decide
- Pushback on N — user rejects the answer ("why not X?", "I think this should be...")
- "let's dig into N" / "N подробнее" — explicit request
- Partial acceptance of N — user accepts part, rejects part ("claim не нравится, остальное ок")

## What does NOT trigger decomposition

- Simple override ("2 aave") — this is an answer, write it
- "skip N" / "postpone N" — write the skip, continue with remaining

## Decomposition

The question becomes a parent node, sub-questions become children. The same collect loop runs on the children. When all children are resolved → parent auto-closes → re-read tree → show remaining unanswered at the parent level.

## Partial acceptance

User accepts part of a suggested answer and rejects part. The accepted part becomes the answer on the node. The rejected part with reasoning goes into Details. If the accepted part has sub-decisions, those become child questions.
```
Before: → ERC-7540? → adopt for async vault [d:erc7540]
User: "claim не нравится, остальное подходит"
After:
✓ ERC-7540 → adopt request interface, no claim — shares sent directly [d:erc7540]

In Details [d:erc7540]:
Rejected: claim pattern (claimDeposit/claimRedeem) — unnecessary step,
shares and USDC sent directly to users at finalize.
```

## Answering user questions

If the user asks a factual question instead of giving an answer — answer it inline. If you can't answer from context/knowledge, tell the user: "I'd need to check [what]. Research this, or do you already know?"

## Recording after extended discussion

After any extended discussion (more than one exchange on a question), show what you're about to record before writing:
```
Recording from our discussion:
1. ✓ Share pricing → delta NAV (depositor bears swap costs)
2. Updated Details [d:share-pricing]: rejected flat fee (not aligned with vault performance)
Confirm? [Y / numbers to change]
```

## Stall detection

After 3 exchanges on the same question without progress (no new answers, no narrowing of options), suggest: `"Confirm what we have, postpone, or reframe?"`

## General rules

- **Agent NEVER goes silent for minutes.** If external data is needed, ask user first.
- **Narrow the space** when digging in. Ask what properties matter, what's unacceptable — don't present menus of options.
- **Re-read tree** after returning from a decomposed branch. Do not rely on conversation memory for the state of other questions.
- **Auto-close** after writing — apply auto-close rules from `references/tree-format.md`. Recurse up.
