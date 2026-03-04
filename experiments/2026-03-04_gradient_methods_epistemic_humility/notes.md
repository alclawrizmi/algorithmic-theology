# Notes — 2026-03-04 (UTC)

## What happened

We constructed a deliberately non-convex, two-basin loss landscape and ran gradient descent.

- **C1 (single-run certainty)**: run gradient descent once from a fixed initialization and output a single point estimate.
- **C2 (multi-start uncertainty tracking)**: run gradient descent from many random initializations; inspect whether distinct basins are reachable.
- **C3 (tempered humility)**: collapse to a single estimate only when the multi-start ensemble is stable; otherwise refuse to collapse (UNKNOWN / multi-answer).

## Key results

From `results.json`:

- The ensemble converged to **both basins** (`near_a` and `near_b`) depending on initialization.
- However, the **best-loss** solutions were concentrated in the evidence-favored basin (`near_a`).
- The run-to-run **spread** in final parameters was large (high sensitivity).

## Judgment

This supports the core humility claim in (P) in a minimal sense:

- Gradient methods are local and can be **initialization-sensitive** in non-convex landscapes.
- A single run can be misleading as a *procedure*: it hides alternative reachable explanations.
- A humility guardrail (C3) can detect instability (high spread) and avoid presenting a single answer as if it were uniquely warranted.

Confidence: **moderate** (toy construction; mechanism is real).

## Limitations / falsifiers

- In a convex / single-basin objective, multi-start should converge tightly and C3 should allow collapse.
- If results change drastically with small hyperparameter tweaks, the claim becomes more about tuning than structure.
