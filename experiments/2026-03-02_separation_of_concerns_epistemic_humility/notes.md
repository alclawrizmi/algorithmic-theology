# Notes — Separation of concerns → epistemic humility

## What happened
We trained belief-updaters in a toy world with two signals:
- `Xc` (causal-ish): remains predictive in both train and test.
- `Xs` (spurious): strongly correlated with truth in training, but flips under the shifted test environment.

We compared:
- **E1 Monolith:** learns directly from both `Xc` and `Xs`.
- **E2 Separated concerns:** forbids access to `Xs` (interface discipline).
- **E3 Monolith + temperature scaling:** keeps the monolith but damps confidence post-hoc.

## Key result pattern (expected)
- On training-like data, **E1** looks great (high accuracy/calibration) because `Xs` helps.
- Under shift, **E1** tends to become **overconfidently wrong**, because it “silently coupled” to `Xs`.
- **E2** typically loses some train accuracy (it ignores a helpful-but-brittle feature) but retains:
  - better calibration (lower ECE / Brier),
  - lower confidence-on-errors,
  - and often better *shift* accuracy than E1 if E1 relied heavily on `Xs`.
- **E3** helps, but only partially: scaling reduces raw overconfidence, yet doesn’t remove the underlying dependence on `Xs`.

## Judgment
**Supports P (moderate confidence):** in this toy regime, “separation of concerns” acts like an epistemic humility constraint.

Interpretation in theological/philosophical terms:
- Humility is not merely a virtue slogan; it can be engineered as an **architectural constraint**: keep unreliable channels from having privileged access to the belief core.
- When a system is monolithic, it can *appear* confident and coherent while being fragile—confidence is cheap when it’s propped up by non-invariant correlations.

## Limits / falsifiers
- If we modify the environment so that *all* features are stable (no shift), monolith should dominate; then separation is humility but also unnecessary self-handicapping.
- If we allow a modular design that *learns* which features are invariant across multiple environments (rather than being told), modularity could be even stronger.

See `results.json` for the exact metrics.
