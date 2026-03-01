# Notes — Property-based testing → belief revision

## What we tested

We treated “belief revision” as an **update rule** from a prior over hypotheses to a posterior after seeing evidence. Then we used a property-based testing mindset: generate many randomized evidence streams and ask whether update rules satisfy explicit invariants.

Updaters:
- **Exact Bayes** (sequential likelihood multiplication + normalization)
- **Greedy MAP collapse** (after each step, collapse to a single hypothesis)
- **Tempered Bayes** (log-likelihood update with per-step cap; bounded trust)

## Results (high level)

From `results.json`:

- **Bayes**: 0% violations of coherence, order-invariance, and neutral-evidence stability.
- **Greedy MAP collapse**:
  - Order-invariance violations: ~48.5% (large; mean L1 distance ~0.97)
  - Neutral-evidence stability violations: 100%
- **Tempered Bayes (cap=0.7)**: 0% violations on these tests.

## Interpretation / judgment

1) **Property-based testing cleanly surfaces procedural fragility.**
   The greedy MAP updater is “coherent” in the narrow sense (it outputs a valid distribution), but it fails two invariants that are natural for i.i.d. evidence models:
   - It can reach different conclusions given the same evidence multiset in different orders.
   - Under uninformative evidence, it still collapses to a specific hypothesis (an artifact of tie-breaking), creating *spurious certainty*.

2) **A useful theological analogue (limited, but real):**
   If a method for revising doctrinal/interpretive belief is sensitive to **presentation order** or **arbitrary tie-breaks** under near-equal support, it can generate “certainty” that is not actually licensed by the evidence content. Property tests provide a way to *name and measure* that risk.

## Limitations

- The “world” is a toy 3-hypothesis Bernoulli model; real-world belief revision involves richer hypothesis spaces and structured evidence.
- We only tested three invariants; other invariants (e.g., calibration, regret, robustness to misspecification) may matter more.
- The tempered updater chosen here still preserves order invariance in this setting because the capped contributions sum over counts; other bounded heuristics could break it.

## Takeaway

When evidence is noisy/underdetermined, **procedural properties** (order invariance, neutrality under uninformative data, etc.) are not philosophical decoration: they can be the difference between “disciplined uncertainty” and “manufactured certainty.”

