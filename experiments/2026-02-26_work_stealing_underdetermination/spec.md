# Experiment spec — work_stealing → underdetermination

- **Date (UTC):** 2026-02-26
- **Selected pair:** `work_stealing::underdetermination`
- **Selection rationale:** chosen uniformly at random from the **least-covered** CS concepts with unused theology targets.

## Target proposition (P)
In epistemically underdetermined settings (multiple hypotheses fit the evidence), **the search/scheduling algorithm** can materially shape which hypothesis is selected, even when each hypothesis is equally compatible with the data.

## CS concept
**Work stealing**: multiple workers process tasks from local deques; idle workers steal from others to balance load and reduce tail latency.

## Candidates (E)
We model “hypothesis search” as exploring a fixed set of candidate models with indistinguishable evidential support.

- **E1 — Central queue (FIFO):** all workers draw tasks from a single global FIFO queue.
- **E2 — Local queues, no stealing:** each worker gets an initial chunk; when done, it stops (captures fragmented inquiry communities).
- **E3 — Work stealing:** each worker uses a local deque; idle workers steal to keep global exploration going.

## Invariants / axioms (pruning constraints)
- Evidence does **not** privilege any single hypothesis: all candidates have the same likelihood model.
- A hypothesis is “acceptable” if its simulated fit score is within an **indistinguishability band** of the best score found (captures underdetermination).
- A selection procedure must return **one** hypothesis as the “adopted” one.

## Operationalization
- There are `H` hypotheses. Each hypothesis has a latent “fit score” drawn i.i.d. from a continuous distribution. This is **not** treated as real evidence; it represents micro-contingencies / modeling choices / researcher degrees of freedom.
- Workers “evaluate” hypotheses; evaluation time is random (heterogeneous cost).
- After a fixed wall-clock budget `T`, we adopt the **best-scoring evaluated** hypothesis; additionally we record the **set of acceptable hypotheses** within `epsilon` of best.

## Metrics
Across many trials:
- **winner_entropy:** entropy of the winner distribution (higher = less lock-in / less path dependence)
- **winner_gini:** concentration of winner distribution (higher = more lock-in)
- **avg_acceptable_count:** how many hypotheses were acceptable at adoption time
- **avg_evaluated:** how many hypotheses were evaluated within the budget
- **coverage_skew:** stddev of evaluations per worker (load balance proxy)

## Decision rule
- If different scheduling policies produce materially different **winner concentration** (entropy/gini) while keeping the underdetermination band fixed, that supports P: procedure affects outcomes under underdetermination.
- If outcomes are statistically indistinguishable, this run is inconclusive about P (at least for this toy model).

## Limitations (known up front)
- This is a toy model: real underdetermination involves structured hypothesis spaces and non-i.i.d. evidence.
- The “fit score” stands in for researcher degrees of freedom; interpret cautiously.
