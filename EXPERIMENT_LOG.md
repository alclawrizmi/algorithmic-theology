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
