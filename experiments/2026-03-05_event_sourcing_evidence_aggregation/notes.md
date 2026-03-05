# Notes — Event sourcing → evidence aggregation

## Judgment
Supports the proposition (P) **in this toy model**: preserving an evidence log enables immediate, rational reweighting of past testimony when credibility estimates change; snapshot-only belief cannot fully recover.

## Key observation
At the credibility-update moment, event-sourced recomputation jumps close to the counterfactual posterior (reweighted over all prior events). Snapshot-only remains offset because its earlier updates are irreversible summaries.

## Limitations
- Binary, independent testimony; real-world evidence is correlated and semantic.
- We model an oracle credibility update (learning true reliabilities), which overstates how clean revisions are in practice.
- Institutional “event sourcing” (archives, isnāds, citations) has its own incentives and failure modes.
