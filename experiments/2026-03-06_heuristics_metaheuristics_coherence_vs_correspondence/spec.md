# Spec — 2026-03-06 (UTC)

## Pair
- **CS concept:** heuristics / metaheuristics
- **Theology target:** coherence vs correspondence
- **Selection rationale:** chosen by the runner’s *least-covered CS concept* policy (uniform random among CS slugs with minimal prior usage).

## Target proposition (P)
**P:** “High internal coherence of a belief-set is reliable evidence that the belief-set corresponds to reality.”

We test a narrow, operational version: when we search for a belief-set using heuristic optimization of a *coherence proxy*, do we reliably recover the hidden ground-truth state?

## Candidates (E) — mutually competing explanations
Let the “belief-set” be an assignment of truth values to propositions.

- **E1 (Correspondence-tracking):** In typical conditions, maximizing coherence (plus fitting observations) tends to recover the ground truth; coherence is a good proxy for truth.
- **E2 (Proxy Goodhart / coherence trap):** Coherence is an optimizing target that can be decoupled from truth; heuristic search can converge to highly coherent yet false belief-sets when constraints/observations are noisy or misspecified.
- **E3 (Underdetermination plateau):** Many distinct belief-sets score similarly on coherence and observation-fit; heuristic dynamics select arbitrarily among near-ties, so correspondence is unstable.

## Invariants / axioms (pruning rules)
- **Non-contradiction (operationalized):** higher coherence score means satisfying more constraints (but constraints may be wrong).
- **Bounded resources:** the agent uses heuristic/metaheuristic search rather than exhaustive search in large spaces.
- **Fallibility of inputs:** some fraction of constraints and observations may be corrupted (noise / mis-specification).

## Operationalization
We simulate:
- A hidden **true world state** `t ∈ {0,1}^N`.
- **Observations**: a subset of bits of `t`, flipped with probability `p_obs_noise`.
- **Constraints** (a “coherence fabric”): pairwise relations of the form `x_i == x_j` or `x_i != x_j`.
  - A fraction `p_constraint_corrupt` are flipped (the relation is wrong), modeling doctrinal/interpretive mistakes or invalid harmonization rules.

A candidate belief-set `b` is scored by a **coherence proxy**:
- `score(b) = w_c * (# satisfied constraints) + w_o * (# matched observations)`

The agent attempts to find a high-scoring `b` using:
- greedy hill-climbing (heuristic)
- simulated annealing (metaheuristic)

We then measure **correspondence** to reality as: `corr(b,t) = fraction of bits where b_i == t_i`.

## Metrics
Across many random trials and several regimes:
- best **proxy score** achieved by each method
- resulting **correspondence** to truth
- correlation between proxy score and correspondence
- frequency of “coherence traps”: cases where method A achieves higher proxy score than method B but lower correspondence.

## Decision rule
- Evidence for **E2/E3** if, under plausible noise/misspecification, proxy coherence is *weakly correlated* with correspondence and heuristic/metaheuristic search frequently produces belief-sets with **high coherence score but low correspondence**.
- Evidence for **E1** if correspondence remains high and robust across noise regimes, and proxy score tracks correspondence strongly.

## Scope / limitations
This is a toy model: “coherence” is reduced to satisfiable pairwise constraints + observation-fit. It does not model semantics, lived practice, or richer explanatory virtues.
