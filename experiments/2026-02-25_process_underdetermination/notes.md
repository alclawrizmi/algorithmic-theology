# Notes: 2026-02-25_process_underdetermination

## What happened
A Bayesian-updating toy model: a process receives noisy evidence and updates belief in a binary hypothesis.

## Results (read from results.json)
- Compare mean probability assigned to the correct hypothesis under different priors.
- Check how often we get to ≥ 0.9 confidence.

## Interpretation (scoped)
If outcomes stay strongly prior-sensitive even after many observations, that’s a clean way to see underdetermination (or convention-driven resolution) in this model.

If outcomes converge across priors, then under this evidence model the ambiguity shrinks with data.

## Limitations
- Only two hypotheses.
- Evidence is i.i.d.; no adversarial structure.
- No model misspecification.
