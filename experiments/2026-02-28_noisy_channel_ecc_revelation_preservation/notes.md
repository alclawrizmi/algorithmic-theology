# Notes — 2026-02-28

Quick intuition check:
- Raw copying accumulates errors roughly linearly with generations.
- Repetition (majority vote) converts bit-level noise into much smaller effective noise as long as `p < 0.5` and `r` is odd.
- Adding parity is only **detection**, not correction: it can give *very low BER when accepted*, but the probability that **all** blocks pass declines quickly as `p` and the number of generations rise.

The interesting theological analogy is the *trade-off knob*:
- more redundancy/cross-checking → fewer undetected corruptions
- but also higher cost and, in strict regimes, more discarding of imperfect copies
