import json
import random
import statistics
from datetime import datetime, timezone


def run_trial(rng, prior, p_true, p_false, observations):
    # H in {0,1}; we track p = P(H=1)
    H = 1 if rng.random() < 0.5 else 0
    p = prior
    for _ in range(observations):
        e = 1 if rng.random() < (p_true if H else p_false) else 0
        if e:
            num = p * p_true
            den = p * p_true + (1 - p) * p_false
        else:
            num = p * (1 - p_true)
            den = p * (1 - p_true) + (1 - p) * (1 - p_false)
        p = num / den

    p_correct = p if H == 1 else (1 - p)
    return p_correct


def simulate(trials=2000, prior=0.5, p_true=0.7, p_false=0.3, observations=30, seed=7):
    rng = random.Random(seed)
    pcs = [run_trial(rng, prior, p_true, p_false, observations) for _ in range(trials)]
    return {
        "trials": trials,
        "prior": prior,
        "p_true": p_true,
        "p_false": p_false,
        "observations": observations,
        "mean_p_correct": statistics.mean(pcs),
        "p_confident_correct": sum(1 for x in pcs if x >= 0.9) / trials,
    }


def main():
    with open("selection.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    results = {
        "neutral_prior": simulate(prior=0.5),
        "skeptical_prior": simulate(prior=0.2),
        "very_skeptical_prior": simulate(prior=0.05),
    }

    out = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "meta": meta,
        "results": results,
    }

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
