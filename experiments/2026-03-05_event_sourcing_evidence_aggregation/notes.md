# Notes — Event sourcing → evidence aggregation

## Judgment
Supports the proposition (P) **in this toy model**.

We intentionally included *adversarial* sources (reliability `< 0.5`). The agent initially mis-modeled all sources as moderately truthful. When it later learned corrected reliabilities, **only systems that retained the evidence log** could re-interpret earlier testimony (treat adversarial testimony as *negative* evidence).

## What this illustrates
- **Event-sourced aggregation** can recompute belief with new weights and jump toward the counterfactual “ideal” posterior.
- **Snapshot-only belief** cannot fully recover because earlier misweighted updates are irreversible summaries.
- **Windowed logs** offer partial recovery limited by the window size.

## Limitations
- Evidence is simplified to independent binary claims.
- The credibility update is unrealistically clean (we reveal true reliabilities).
- Real religious evidence includes interpretation, dependence, and institutional incentives.
