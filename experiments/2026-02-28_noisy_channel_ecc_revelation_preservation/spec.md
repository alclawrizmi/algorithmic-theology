# Spec — noisy_channel_ecc → revelation preservation (toy model)

## Target proposition (P)
In a setting where a message is repeatedly copied/transmitted with random errors, **redundancy and verification** can preserve high end-to-end fidelity even when individual transmissions are noisy — at the cost of extra bandwidth and/or rejecting corrupted copies.

## Model choices
- Message: a fixed-length bitstring.
- Channel: binary symmetric channel (each bit flips with probability `p`).
- Generations: repeated copying over `G` steps.

## Schemes compared
1) **Raw**: transmit bits directly.
2) **Repetition code**: repeat each bit `r` times; decode by majority vote.
3) **Repetition + parity**: add a parity bit per block (detection), then apply repetition; reject if any block fails parity.

## What would count as support
- Lower final bit error rate and higher exact-match rate under redundancy.
- For detection, near-zero error among accepted transmissions, with an acceptance-rate trade-off.

## Non-goals / disclaimers
This is **not** a manuscript-stemmatics model and does not represent language, meaning drift, social dynamics, or deliberate corruption.
