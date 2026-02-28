"""Noisy channel + error-correcting codes -> revelation preservation (toy model).

We model "revelation" as a message (bits) sent across generations through a
binary symmetric channel (each bit flips with probability p).

We compare:
- raw transmission (no redundancy)
- repetition code with majority vote (r copies per bit)
- repetition + checksum (detect-and-reject corrupted blocks)

This is not a model of real manuscript traditions; it's a didactic simulation
showing how redundancy + verification can convert high per-copy noise into high
end-to-end fidelity, at a cost in bandwidth and/or discarding.
"""

from __future__ import annotations

import json
import math
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple


def flip(bit: int, p: float) -> int:
    return bit ^ (1 if random.random() < p else 0)


def transmit_bits(bits: List[int], p: float) -> List[int]:
    return [flip(b, p) for b in bits]


def repetition_encode(bits: List[int], r: int) -> List[int]:
    return [b for b in bits for _ in range(r)]


def repetition_decode_majority(bits_rep: List[int], r: int) -> List[int]:
    assert len(bits_rep) % r == 0
    out = []
    for i in range(0, len(bits_rep), r):
        chunk = bits_rep[i : i + r]
        ones = sum(chunk)
        out.append(1 if ones > r / 2 else 0)  # ties break to 0
    return out


def parity(bits: List[int]) -> int:
    x = 0
    for b in bits:
        x ^= (b & 1)
    return x


def block_with_parity(bits: List[int], block_size: int) -> List[int]:
    """Append 1 parity bit per block."""
    out = []
    for i in range(0, len(bits), block_size):
        blk = bits[i : i + block_size]
        out.extend(blk)
        out.append(parity(blk))
    return out


def verify_and_strip_parity(bits_with_parity: List[int], block_size: int) -> Tuple[bool, List[int]]:
    out = []
    i = 0
    while i < len(bits_with_parity):
        blk = bits_with_parity[i : i + block_size]
        if len(blk) < block_size:
            # last partial block; treat similarly
            payload = blk
            i += len(blk)
            if i >= len(bits_with_parity):
                return False, []  # malformed
            check = bits_with_parity[i]
            i += 1
        else:
            payload = blk
            i += block_size
            if i >= len(bits_with_parity):
                return False, []
            check = bits_with_parity[i]
            i += 1

        if parity(payload) != check:
            return False, []
        out.extend(payload)

    return True, out


@dataclass
class Config:
    name: str
    p: float
    generations: int
    n_bits: int
    trials: int
    repetition_r: int | None = None
    parity_block: int | None = None


def hamming_distance(a: List[int], b: List[int]) -> int:
    return sum(x != y for x, y in zip(a, b))


def run_trial(cfg: Config) -> Dict:
    msg = [random.getrandbits(1) for _ in range(cfg.n_bits)]

    # choose codec
    if cfg.repetition_r is None:
        def encode(x):
            return x

        def decode(x):
            return x
    else:
        r = cfg.repetition_r

        if cfg.parity_block is None:
            def encode(x):
                return repetition_encode(x, r)

            def decode(x):
                return repetition_decode_majority(x, r)
        else:
            B = cfg.parity_block

            def encode(x):
                return repetition_encode(block_with_parity(x, B), r)

            def decode(x):
                decoded = repetition_decode_majority(x, r)
                ok, stripped = verify_and_strip_parity(decoded, B)
                return stripped if ok else None

    current = msg
    accepted = True

    for _ in range(cfg.generations):
        wire = encode(current)
        noisy = transmit_bits(wire, cfg.p)
        nxt = decode(noisy)
        if nxt is None:
            accepted = False
            break
        current = nxt

    if not accepted:
        return {
            "accepted": 0,
            "bit_error_rate": None,
            "exact_match": 0,
            "final_hamming": None,
        }

    ham = hamming_distance(msg, current)
    ber = ham / cfg.n_bits
    return {
        "accepted": 1,
        "bit_error_rate": ber,
        "exact_match": int(ham == 0),
        "final_hamming": ham,
    }


def summarize(rows: List[Dict]) -> Dict:
    acc = sum(r["accepted"] for r in rows) / len(rows)
    exact = sum(r["exact_match"] for r in rows) / len(rows)

    bers = [r["bit_error_rate"] for r in rows if r["bit_error_rate"] is not None]
    mean_ber = sum(bers) / len(bers) if bers else None

    return {
        "accept_rate": acc,
        "exact_match_rate": exact,
        "mean_bit_error_rate_given_accept": mean_ber,
    }


def main():
    random.seed(0)

    meta = {
        "cs_slug": "noisy_channel_ecc",
        "cs_master_label": "Noisy channel + error-correcting codes",
        "theology_target": "revelation preservation",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "note": "Toy simulation: redundancy + verification can preserve messages under noise; not a manuscript-history model.",
    }

    base = {
        "generations": 20,
        "n_bits": 256,
        "trials": 200,
    }

    configs: List[Config] = []
    for p in [0.001, 0.005, 0.01, 0.02]:
        configs.append(Config(name="raw", p=p, **base))
        configs.append(Config(name="rep3", p=p, repetition_r=3, **base))
        configs.append(Config(name="rep5", p=p, repetition_r=5, **base))
        configs.append(Config(name="rep3+parity32", p=p, repetition_r=3, parity_block=32, **base))

    out = {"meta": meta, "base": base, "results": []}

    for cfg in configs:
        rows = [run_trial(cfg) for _ in range(cfg.trials)]
        out["results"].append(
            {
                "name": cfg.name,
                "p": cfg.p,
                "repetition_r": cfg.repetition_r,
                "parity_block": cfg.parity_block,
                "summary": summarize(rows),
            }
        )

    here = os.path.dirname(__file__)
    with open(os.path.join(here, "results.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
