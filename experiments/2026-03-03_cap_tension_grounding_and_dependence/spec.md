# Spec — CAP tension → grounding and dependence

- **Date (UTC):** 2026-03-03
- **CS concept:** CAP tension (consistency vs availability under partition)
- **Theology target (P):** *Grounding and dependence* claims aim to describe an objective dependency structure (what depends on what). The question: under information partitions, can a community maintain globally consistent grounding judgments while remaining responsive?

## Selection

- **Selected pair:** `cap_tension::grounding and dependence`
- **Selection rationale:** least-covered CS slug (min prior coverage), then uniform random unused target for that slug.

## Candidates (E)

We model three explanatory stances about grounding judgments under epistemic partition:

1) **E₁ — Objective + locally accessible grounding:** each local community can answer grounding queries correctly from its local state even under partition.
2) **E₂ — Objective grounding, but access is partition-limited:** the grounding structure may be objective, but globally consistent judgments require cross-community reconciliation; under partition you must either (a) refuse to answer some queries or (b) risk inconsistency.
3) **E₃ — Conventional / locally-defined grounding:** each community’s grounding judgments are defined by its local ledger; divergence is not an error but a feature (at the cost of global disagreement).

## Invariants / axioms (pruning constraints)

- **Non-contradiction:** for any query `depends(a,b)` we should not simultaneously endorse both `depends(a,b)` and `not depends(a,b)` across replicas.
- **Acyclicity (grounding-as-DAG):** grounding is modeled as a DAG; cycles indicate a modeling failure (or a category error).
- **Partition constraint:** during a partition, cross-replica coordination is unavailable.

## Operationalization

- True world: a random DAG over `N` nodes represents the *objective* grounding relation `G`.
- Two replicas start with the same snapshot of `G`.
- A partition occurs. Each replica receives **different noisy “updates”** (edge flips) during the partition, yielding divergent local DAGs `G1`, `G2`.
- We issue reachability queries `depends(a,b)`.

Policies (CAP-style):

- **CP (consistency-first):** answer only if both replicas agree (requires coordination). Under partition: return **UNKNOWN**.
- **AP (availability-first):** always answer from a random local replica’s state (no coordination). Under partition: always returns TRUE/FALSE.

## Metrics

For each policy:

- **availability:** fraction of queries answered (not UNKNOWN).
- **accuracy vs objective G:** fraction of answers that match truth in `G`.
- **cross-replica contradiction rate:** fraction of queries where `G1` and `G2` disagree (a pressure term).
- **false certainty rate:** fraction of AP answers where replicas disagree (i.e., the policy answered despite global disagreement).

## Decision rule

- If AP achieves high accuracy *and* low false-certainty under meaningful divergence, it supports E₁.
- If there is a persistent tradeoff: AP stays available but accumulates false certainty; CP preserves consistency by refusing to answer, it supports E₂.
- If divergence is treated as non-error (local truth), then “accuracy vs objective G” ceases to be binding; the model highlights the cost (global disagreement), relevant to E₃.
