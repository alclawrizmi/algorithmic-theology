# Spec — Termination / well‑foundedness → cosmological base case

- **Date (UTC):** 2026-02-24
- **CS concept:** Termination proofs / well‑founded recursion (well‑founded order + base case)

## Theological target proposition (P)
A cosmological explanation that is *complete* must include a **grounding/base case** (a terminus) rather than an infinite regress of dependent explanations.

## Candidates (E)
We model “explanation” as a procedure that reduces a query to sub‑queries (“what explains X?” → “what explains cause(X)?”).

1) **E1 — Well‑founded base case (terminating recursion):**
   - There exists a base case B such that queries eventually reduce to B.
   - Operationally: each step has some chance to hit a base case.

2) **E2 — Infinite regress (non‑terminating recursion):**
   - For every query there is a further dependent query; no base case.
   - Operationally: never hits a base case.

3) **E3 — Cyclic dependence (loop):**
   - Explanation graph contains a cycle; queries revisit earlier states.
   - Operationally: chain returns to a previous node (cycle detected).

## Invariants / axioms (pruning constraints)
- **Termination requirement:** a “complete explanation” must return an answer in finite steps.
- **No silent truncation:** capping steps is a measurement convenience, not a genuine explanation.
- **Cycle is not grounding:** detecting a loop is not the same as providing a base case.

## Operationalization
We simulate an “explanation chase” as a walk that starts at a query node and repeatedly requests a prior cause.
- **E1:** at each step, with probability `p_base`, return BASE (terminate); otherwise extend the chain.
- **E2:** always extend the chain (never terminate).
- **E3:** extend the chain, but with probability `p_cycle` jump back to an earlier node (forming a cycle).

We run many trials and record whether the process:
- terminates in a base case,
- falls into a cycle,
- or fails to terminate within `max_steps`.

## Metrics
- `terminate_rate` (BASE reached)
- `cycle_rate` (cycle detected)
- `timeout_rate` (max_steps reached without BASE/cycle)
- `avg_steps_to_event` (mean steps to BASE or cycle)

## Decision rule
- If a candidate systematically yields **non‑termination** (or only termination by external truncation), it fails the “complete explanation” invariant.
- Cycles count as *non‑grounding*: they may be finite to detect, but they do not provide an explanatory base case.
- This experiment cannot identify *what* the base case is; it tests the structural requirement that some base case exists if completeness implies termination.
