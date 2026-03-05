# Experiment Log

A dated index of experiments (spec → code → results → notes).

- 2026-02-24 — Termination proofs / well-founded recursion → cosmological base case: experiments/2026-02-24_termination_well_foundedness_cosmological_base_case/
- 2026-02-25 — 2026-02-25_process_underdetermination

## 2026-02-26 — work_stealing → underdetermination
- Directory: `experiments/2026-02-26_work_stealing_underdetermination/`
- Summary: Toy underdetermination model: scheduling (FIFO vs local vs work-stealing) shifts exploration coverage and which acceptable hypothesis is adopted.

## 2026-02-27 — complexity_classes → belief revision
- Directory: `experiments/2026-02-27_complexity_classes_belief_revision/`
- Summary: Exact Bayes vs budgeted sparse updaters (top‑M/beam-like) over K hypotheses; bounded belief revision can prune truth early and fail to recover as K grows.

## 2026-02-28 — noisy_channel_ecc → revelation preservation
- Directory: `experiments/2026-02-28_noisy_channel_ecc_revelation_preservation/`
- Summary: Binary symmetric channel over generations. Repetition codes (3x/5x) dramatically improve end-to-end fidelity under bit-flip noise; adding parity detects corruption (zero BER when accepted) but lowers acceptance rate (discarding/certification trade-off).

## 2026-03-01 — property_based_testing → belief revision
- Directory: `experiments/2026-03-01_property_based_testing_belief_revision/`
- Summary: Property-based test harness over randomized evidence streams. Exact Bayes satisfies coherence + order-invariance + neutrality under uninformative evidence; greedy MAP collapse frequently violates order-invariance and always collapses under neutral evidence (tie-break artifact), illustrating how update procedures can manufacture certainty.

## 2026-03-02 — separation_of_concerns → epistemic humility
- Directory: `experiments/2026-03-02_separation_of_concerns_epistemic_humility/`
- Summary: Two-signal world (causal + spurious). Monolithic learner looks great in-training but becomes overconfident under distribution shift when the spurious correlation flips. A separated-concerns design that forbids the spurious channel improves calibration (ECE/Brier) and shift accuracy, operationalizing “humility” as an architectural constraint.

- 2026-03-03 — CAP tension → grounding and dependence: partitioned replicas diverge on grounding reachability; availability-first answers induce false certainty; consistency-first withholds disputed queries. (toy model; moderate confidence)
  - 2026-03-03_cap_tension_grounding_and_dependence

- **2026-03-04 (UTC)** — `experiments/2026-03-04_gradient_methods_epistemic_humility/`
  - P: Non-convex / multi-modal landscapes make single-answer procedures overconfident; humility tracks uncertainty.
  - CS: Gradient methods
  - Result: Multi-start GD reaches distinct basins; tempered humility refuses to collapse when spread is high (moderate confidence).
  - Notes: `experiments/2026-03-04_gradient_methods_epistemic_humility/notes.md`

- 2026-03-05 — **event sourcing → evidence aggregation**: preserving an evidence log enables rational reweighting of past testimony under credibility updates; snapshot-only belief cannot fully recover (toy model).
  - Dir: 
