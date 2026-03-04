# Spec — ${DATE} (UTC)

## Target proposition (P)

When evidence/optimization landscapes are **multi-modal or non-convex**, any procedure that must output a single determinate answer can become **overconfident by construction**; epistemic humility is the policy of **tracking uncertainty** (e.g., multiple plausible explanations) rather than collapsing early to one.

## CS concept

**Gradient methods** (gradient descent): iterative local optimization; sensitivity to initialization, step size, and non-convexity.

## Candidates (E)

1) **Single-run certainty (C1)**: run gradient descent once from a default initialization; treat the obtained optimum as *the* explanation.
2) **Multi-start uncertainty tracking (C2)**: run gradient descent from many random initializations; treat the set of found optima as the hypothesis family and report uncertainty (spread / multimodality).
3) **Tempered humility (C3)**: like C2, but if the optima cluster tightly (low spread) then it is safe to collapse to a single estimate; otherwise return UNKNOWN / multi-answer.

## Invariants / axioms (pruning constraints)

- **Non-contradiction**: mutually incompatible optima cannot all be "the" true explanation.
- **Calibration constraint**: when a method is empirically sensitive (high run-to-run variability with similar loss), it must not output extreme certainty.
- **Termination**: all candidates must terminate under a fixed iteration budget.

## Operationalization (mapping)

We model "explanation" as the **argmin** of a loss function.

- Landscape: a simple **two-basin non-convex** objective where two separated parameter values fit data almost equally well.
- Evidence: noisy observations generated from one basin.

Policies:
- C1 returns one point estimate from a fixed init.
- C2 returns an ensemble of point estimates from many inits.
- C3 returns a point estimate only when the ensemble is stable; otherwise returns UNKNOWN.

Preserved:
- Locality of gradient updates.
- Initialization sensitivity in non-convex settings.

Ignored:
- Second-order methods; global optimization.
- Real-world model misspecification beyond the toy landscape.

Known limitations:
- This is didactic: the objective is constructed to have multiple basins.

## Metrics

- **Multimodality rate**: fraction of runs that converge to each basin.
- **Spread**: standard deviation of final parameters across restarts.
- **Loss gap**: difference in achieved loss between basins.
- **Overconfidence indicator**: if |mean estimate − true| is large while loss is near-optimal.

## Decision rule

Support for (P) if:
- Multiple distinct optima are reached from different initializations with **similar losses** (small loss gap), and
- A single-run policy (C1) frequently returns the "wrong" basin depending on init, while
- C3 correctly refuses to collapse (returns UNKNOWN) when spread is high.

Disconfirm if:
- Restarts nearly always converge to the same solution (low spread) or loss gap strongly distinguishes basins.

Inconclusive if:
- Results depend heavily on arbitrary hyperparameters without a robust pattern.
