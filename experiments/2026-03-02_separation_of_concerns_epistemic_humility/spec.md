# Spec — 2026-03-02 (UTC)

## Pair
- **CS concept:** separation_of_concerns — *Separation of concerns*
- **Theology target:** *epistemic humility*
- **Selection rationale:** chosen uniformly at random from the **least-covered** CS concepts (coverage count = 0) with an unused target in `/workspace/memory/theology_map.md`.

## Target proposition (P)
**P:** When evidence is noisy and distribution shift is plausible, epistemic humility is improved by separating (a) *what is observed* from (b) *what is concluded*—i.e., by enforcing modular interfaces that prevent spurious features from directly driving high-confidence belief updates.

Operational reading: “humility” ≈ calibrated confidence + restraint under shift.

## Candidates (E)
We compare three epistemic architectures:

- **E1 — Monolith (end-to-end):** one model consumes all observed features and outputs beliefs/confidence.
- **E2 — Modular / separated concerns:** a constrained interface only passes an explicitly designated “causal” feature forward; spurious features are treated as *out-of-scope* for inference.
- **E3 — Monolith + regularization (partial mitigation):** a monolithic model with shrinkage/temperature scaling to reduce overconfidence.

These are not metaphysical “explanations,” but operational competitors for *how a belief-forming agent should be structured*.

## Invariants / axioms (pruning constraints)
1. **Shift-robustness invariant:** If a feature is known to be non-invariant across environments, treating it as decisive evidence should be penalized.
2. **Calibration preference:** For a fixed accuracy, prefer the system with better probabilistic calibration (lower Brier score / calibration error).
3. **Interface discipline:** A separated module should not have access to out-of-scope signals (prevents silent coupling).

## Operationalization
We simulate a world with:
- a binary latent truth `Y ∈ {0,1}`
- one *causal* feature `Xc` that predicts `Y` similarly in train and test
- one *spurious* feature `Xs` that is correlated with `Y` in training but flips/weakens in test (distribution shift)

Agents learn on training data and are evaluated on both training-like and shifted test data.

## Metrics
- **Accuracy** on train-like and shifted test.
- **Brier score** (mean squared error of predicted probability).
- **ECE (expected calibration error)** using equal-width probability bins.
- **Overconfidence under shift:** mean(predicted p) on wrong predictions in the shifted test.

## Decision rule
Support for P if:
- E2 has **lower calibration error** (Brier + ECE) than E1 on shifted test **without catastrophic accuracy loss**, and
- E1 shows a clear overconfidence increase under shift driven by reliance on `Xs`.

“Inconclusive” if differences are tiny or dominated by randomness.

## Limits
Toy model; “causal vs spurious” is stipulated by the simulator. The point is structural: whether modular interfaces can enforce humility-like behavior under shift.
