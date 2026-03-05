# Spec — Event sourcing → evidence aggregation

- **Date (UTC):** 2026-03-05
- **Selected pair:** \
- **Selection rationale:** least-covered CS slug among unused pairs (uniform random within the min-coverage set).

## Target proposition (P)
When later information changes how we should weight earlier testimony (credibility updates, new priors, detection of bias), a method that preserves the **history of evidence** enables more rational aggregation than a method that stores only the current belief state.

## CS concept
**Event sourcing:** represent state as a fold/reduction over an append-only log of events; allow recomputation under new reducers/weights.

## Candidates (E)
- **E1 — Event-sourced aggregator:** store every testimony event ; belief is computed by folding the log with current source weights.
- **E2 — Snapshot-only aggregator:** store only current belief state (log-odds) and do not retain the event log. When weights change, past contributions cannot be reweighted.
- **E3 — Windowed log (bounded event sourcing):** store only the last  events; recompute only within the window.

## Invariants/axioms
- **Revision invariance:** if only the weighting function changes over the same evidence, belief should track the recomputed aggregate.
- **Auditability:** divergences should be explainable by a witness trail (which events/sources drove the state).
- **Resource constraint:** bounded memory can force lossy summaries.

## Operationalization
- Hidden binary hypothesis .
-  sources with true reliabilities .
- Events: .
- Agent starts with wrong uniform weights  and later learns corrected weights .

## Metrics
- Mean absolute error of posterior  vs the counterfactual ideal (reweight all past events by  after the change).
- Regret in negative log-likelihood of the true  vs the ideal.
- Accuracy of the final favored hypothesis.
- Immediate recovery at the weight-change step.

## Decision rule
Support for P if event-sourced recomputation converges to the counterfactual ideal after the weight update, while snapshot-only remains persistently off.
