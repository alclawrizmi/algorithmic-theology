# Spec — Event sourcing → evidence aggregation

- **Date (UTC):** 2026-03-05
- **Selected pair:** `event_sourcing::evidence aggregation`
- **Selection rationale:** least-covered CS slug among unused pairs (uniform random within the min-coverage set).

## Target proposition (P)
When later information changes how we should weight earlier testimony (credibility updates, new priors, detection of bias), a method that preserves the **history of evidence** enables more rational aggregation than a method that stores only the current belief state.

## CS concept
**Event sourcing:** represent state as a fold/reduction over an append-only log of events; allow recomputation under new reducers/weights.

## Candidates (E)
- **E1 — Event-sourced aggregator:** store every testimony event `(source_id, claim)`; belief is computed by folding the log with current source weights.
- **E2 — Snapshot-only aggregator:** store only current belief state (log-odds) and do not retain the event log. When weights change, past contributions cannot be reweighted.
- **E3 — Windowed log (bounded event sourcing):** store only the last `W` events; recompute only within the window.

## Invariants/axioms
- **Revision invariance:** if only the weighting function changes over the same evidence, belief should track the recomputed aggregate.
- **Auditability:** divergences should be explainable by a witness trail (which events/sources drove the state).
- **Resource constraint:** bounded memory can force lossy summaries.

## Operationalization
- Hidden binary hypothesis `H ∈ {0,1}`.
- `N` sources with true reliabilities `p_i = P(claim == H)`; allow adversarial sources with `p_i < 0.5`.
- Events: `(source i, claim c)`.
- Agent starts with wrong uniform weights `q0` and later learns corrected weights `q1`.

## Metrics
- Mean absolute error of posterior `P(H=1)` vs the counterfactual ideal (reweight all past events by `q1` after the change).
- Regret in negative log-likelihood of the true `H` vs the ideal.
- Accuracy of the final favored hypothesis.
- Immediate recovery at the weight-change step.

## Decision rule
Support for P if event-sourced recomputation converges to the counterfactual ideal after the weight update, while snapshot-only remains persistently off.
