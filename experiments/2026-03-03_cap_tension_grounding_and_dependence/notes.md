# Notes — CAP tension → grounding and dependence

## What happened

We modeled a "grounding" relation as an objective DAG `G` (reachability answers `depends(a,b)`), then created two replicas `G1` and `G2` that diverge under a partition by receiving different edge-flip updates.

Policies:
- **AP (availability-first):** always answers from one local replica.
- **CP (consistency-first):** answers only when replicas agree; otherwise UNKNOWN.

## Results

See `results.json`.

## Judgment

Tradeoff observed:
- AP stays available but produces **false certainty** whenever replicas disagree.
- CP preserves consistency by withholding disputed answers (lower availability).

Supports **E₂** (objective grounding may exist, but partition-limited access forces a consistency/availability tradeoff in our judgments).

## Limitations

- Grounding-as-reachability is a simplification.
- Divergence is randomized.
- CP is agreement-only (not full consensus).
