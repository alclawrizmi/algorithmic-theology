# Spec — Property-based testing → belief revision

- Date (UTC): 2026-03-01
- Pair: `property_based_testing::belief revision`
- Selection rationale: chosen uniformly at random from the **least-covered** CS concepts in `theology_map.md` (coverage tracked in `/workspace/memory/at_runner_state.json`).

## Target proposition (P)

**P:** A belief-revision procedure can be evaluated (and sometimes falsified) by checking whether it satisfies simple *invariants* across many randomized evidence streams; violations indicate procedural fragility that matters under underdetermination.

This is not claiming “theology is Bayes” or that any invariant is mandatory; it claims we can *make invariants explicit* and then stress-test update rules.

## CS concept

**Property-based testing:** instead of verifying a few hand-picked examples, generate many randomized inputs and assert that key properties/invariants hold.

## Candidates (E)

We compare three competing belief-update models under the same generative world:

- **E1: Exact Bayes (sequential log-likelihood update).**
- **E2: Greedy MAP collapse.** After each observation, keep only the current argmax hypothesis (probability 1.0), discard the rest.
- **E3: Capped/tempered update (“inertia”).** Apply Bayes but cap per-step log-odds change (models bounded rationality / limited trust in new evidence).

## Invariants / axioms (pruning constraints)

We test the following properties:

- **I1 — Coherence:** probabilities remain non-negative and sum to 1.
- **I2 — Order invariance (multiset evidence):** if two evidence sequences contain the same multiset of observations, the final posterior should be (approximately) the same.
  - Rationale: for i.i.d. evidence models, Bayes depends only on counts, not order.
- **I3 — Neutral-evidence stability:** if the evidence likelihoods are identical across hypotheses (uninformative evidence), the posterior should not change (up to floating error).

## Operationalization / model

- Hypotheses: 3 discrete hypotheses `H0,H1,H2`.
- Evidence: binary observations `x ∈ {0,1}`.
- Each hypothesis defines a Bernoulli likelihood `P(x=1|Hi)=pi`.
- Generate evidence by sampling a “true” hypothesis uniformly at random, then sampling a length-`L` sequence from its Bernoulli.

For order-invariance tests, we compare updating on `seq` vs `shuffle(seq)`.

## Metrics

For each updater and each property:

- **Violation rate** over `N` randomized test cases.
- For order invariance: **mean/max L1 distance** between posteriors for `seq` vs `shuffle(seq)`.

## Decision rule

- If an updater violates **I1** at all → it is rejected as incoherent.
- If an updater violates **I2** frequently (e.g., >1%) → it is flagged as **procedurally sensitive** (its conclusions can depend on evidence ordering rather than evidence content).
- **I3** violations indicate miscalibration or implementation error; frequent I3 failures are a red flag.

