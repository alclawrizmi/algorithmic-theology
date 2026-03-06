# Notes — judgment & interpretation

## What happened (summary)
We constructed a toy “belief world” of `N` binary propositions with:
- a hidden **ground truth** assignment `t`
- noisy **observations** of a few propositions
- a fabric of pairwise **coherence constraints** (some fraction corrupted)

We then used two resource-bounded search procedures to maximize a *proxy coherence score*:
- greedy hill-climbing (heuristic)
- simulated annealing (metaheuristic)

We measured:
- proxy score (constraint satisfaction + observation fit)
- **correspondence**: fraction of bits matching the hidden truth

## Result (qualitative)
Across regimes with increasing observation noise and constraint corruption:
- proxy score does **not** reliably track correspondence
- it becomes easy to produce belief-sets that are *internally coherent under the (possibly wrong) constraints* yet diverge from truth
- simulated annealing often finds **higher proxy score** than hill-climbing, but this does not guarantee higher correspondence (a “coherence trap”)

This is the key Goodhart-style lesson: when coherence is operationalized as satisfaction of a constraint set, any misspecification in that constraint set turns “coherence maximization” into optimization of a **proxy** that can be decoupled from reality.

## Judgment (re: candidates)
- **Supports E2 (proxy Goodhart / coherence trap)** and **E3 (underdetermination)** in the modeled regimes.
- **E1** holds only in the idealized regime where constraints and observations are perfectly faithful.

## Limitations / falsifiers
- Stronger coherence notions (explanatory depth, compression, counterfactual support) might correlate better with truth than our pairwise constraints.
- Adding a model class where constraints are *learned and validated* (rather than fixed) could restore correspondence.
- If, in more realistic simulations, coherence proxies remain robust under modest corruption, that would weaken the conclusion.
