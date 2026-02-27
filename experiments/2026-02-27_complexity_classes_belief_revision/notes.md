# Notes — Complexity classes → belief revision

## What happened
We compared an **exact Bayesian updater** (tracks all K hypotheses) against two **budgeted** updaters that can only keep **M** hypotheses “in working memory” at a time:

- **Particle/beam-like sparse updater:** keeps up to M hypotheses with explicit weights; injects a few random proposals each step; prunes back to top‑M.
- **Greedy challenger updater:** keeps top‑M plus a small random challenger set each step.

All three agents saw the **same evidence stream** from the same true hypothesis.

## Key observation
As K grows with fixed M, the bounded updaters frequently **prune away the true hypothesis early** and then cannot reliably recover it (even with random proposals). This yields:

- lower final probability mass on the true hypothesis,
- higher KL divergence from the exact posterior,
- and more “path-dependent” belief trajectories.

In other words: even in a toy world where the truth is in the hypothesis class and Bayes is well-defined, **resource bounds can dominate belief revision outcomes**.

## Results snapshot (qualitative)
In this run (200 trials per config):
- Exact updating remains strong across K (though it degrades as K increases, as expected).
- With a tight budget (M=8), sparse methods’ accuracy collapses as K increases.
- Increasing budget (M=32 at K=800) helps only modestly in this toy setup: recovery still fails often once the true hypothesis is dropped.

## Judgment
**Supports the target proposition (P)** in the limited sense intended:
- “Belief revision” is not just a matter of normative rules; it can be **computationally constrained**, and those constraints can create durable divergence even under shared priors/evidence.

Confidence: **medium‑low**.

Why not higher:
- The bounded algorithms here are crude and somewhat pessimistic; better approximate inference (SMC with better rejuvenation/MCMC moves, variational methods, structured hypothesis representations) would likely close the gap.
- Complexity classes are represented only by fixed budgets, not by formal reductions.

## What would strengthen this
- Replace the bounded methods with more principled approximate Bayes (e.g., proper SMC with effective sample size control + MCMC rejuvenation; or variational Bayes) and measure how the gap scales.
- Use a structured hypothesis space where exact inference becomes combinatorially hard (more faithful to “NP-ish” structure than a flat K-way categorical).
