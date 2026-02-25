# Experiment: 2026-02-25_process_underdetermination

- Date (UTC): 2026-02-25
- Run (UTC): 2026-02-25T07:23:20Z
- CS concept: **Process** (process)
- Theological target: **underdetermination**
- Selection rationale: least-covered random (fresh CS concepts prioritized)

## Target proposition (P)
Underdetermination: multiple hypotheses can fit the same observations. Question: does repeated evidence tend to collapse uncertainty, or does ambiguity persist (or get “resolved” mostly by priors/conventions)?

## Candidates (E)
- **E1: Convergent world** — evidence eventually dominates and the correct hypothesis becomes strongly favored.
- **E2: Persistently underdetermined world** — evidence is too noisy/weak; multiple hypotheses remain plausible.
- **E3: Convention/authority truncation** — apparent resolution mostly reflects priors/thresholds rather than evidence.

## Operationalization
A toy “process” receives a stream of noisy observations and performs Bayesian updates.

Simulation family: **belief_revision**

## Metrics
- Mean probability assigned to the correct hypothesis after N observations
- Fraction of trials highly confident (≥ 0.9) in the correct hypothesis
- Sensitivity to skeptical vs neutral priors

## Decision rule
- Robust convergence across priors → supports E1 (in this model)
- Prior-dominated outcomes / weak convergence → supports E2 or E3
