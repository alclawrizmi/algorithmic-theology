# Notes — work stealing under underdetermination

## What happened
We simulated “hypothesis evaluation under a fixed wall-clock budget” where many hypotheses are **evidentially near-tied** (within `epsilon` of the best evaluated fit). We compared three scheduling policies:

- global FIFO queue
- local queues without stealing
- work stealing

The adoption rule deliberately picks the **first** acceptable hypothesis encountered (a caricature of narrative lock-in / early commitment).

## Judgment
This toy model targets a procedural claim:

> When evidence underdetermines theory choice, the *search/scheduling procedure* can influence which theory is adopted.

Scheduling changes (i) how much of the hypothesis space gets evaluated under a fixed budget and (ii) which “good-enough” hypotheses are encountered early, so the adopted outcome can shift even with the same evidence model.

**Conclusion:** supports the procedural sensitivity version of underdetermination (P) in this simplified setting.

## Limitations / falsifiers
- If we switch the adoption rule to “choose the best evaluated” (instead of first acceptable) and differences vanish, the effect is mainly about **early commitment**.
- If structured hypothesis spaces remove the effect, this may be an i.i.d. artifact.
