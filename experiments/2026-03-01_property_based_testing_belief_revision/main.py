import json
import math
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple


def normalize(ps: List[float]) -> List[float]:
    s = sum(ps)
    if s <= 0 or any((p < 0 or math.isnan(p) or math.isinf(p)) for p in ps):
        return [float('nan')] * len(ps)
    return [p / s for p in ps]


def l1(a: List[float], b: List[float]) -> float:
    return sum(abs(x - y) for x, y in zip(a, b))


@dataclass
class World:
    # Bernoulli params for each hypothesis
    ps: List[float]  # P(x=1|Hi)


class Updater:
    name: str

    def update(self, prior: List[float], seq: List[int], world: World) -> List[float]:
        raise NotImplementedError


class BayesUpdater(Updater):
    name = "bayes_exact"

    def update(self, prior: List[float], seq: List[int], world: World) -> List[float]:
        post = prior[:]
        for x in seq:
            # multiply by likelihood
            for i, p1 in enumerate(world.ps):
                like = p1 if x == 1 else (1 - p1)
                post[i] *= like
            post = normalize(post)
        return post


class GreedyMAPUpdater(Updater):
    name = "greedy_map_collapse"

    def update(self, prior: List[float], seq: List[int], world: World) -> List[float]:
        post = prior[:]
        for x in seq:
            for i, p1 in enumerate(world.ps):
                like = p1 if x == 1 else (1 - p1)
                post[i] *= like
            post = normalize(post)
            # collapse to MAP with deterministic tie-breaker (lowest index)
            m = max(post)
            j = min(i for i, v in enumerate(post) if abs(v - m) < 1e-18)
            post = [1.0 if i == j else 0.0 for i in range(len(post))]
        return post


class TemperedBayesUpdater(Updater):
    """Bayes in log space, but cap per-step log-likelihood contributions.

    Intended to model bounded trust / bounded rationality.
    Capping breaks strict order invariance because different orders can hit the cap differently.
    """

    def __init__(self, cap: float = 1.0):
        self.cap = float(cap)
        self.name = f"tempered_bayes_cap_{self.cap:g}"

    def update(self, prior: List[float], seq: List[int], world: World) -> List[float]:
        # work in log space for stability
        eps = 1e-15
        logp = [math.log(max(eps, p)) for p in prior]
        for x in seq:
            for i, p1 in enumerate(world.ps):
                like = p1 if x == 1 else (1 - p1)
                ll = math.log(max(eps, like))
                # cap contribution
                ll = max(-self.cap, min(self.cap, ll))
                logp[i] += ll
            # normalize
            m = max(logp)
            exps = [math.exp(lp - m) for lp in logp]
            post = normalize(exps)
            logp = [math.log(max(eps, p)) for p in post]
        # final normalize
        m = max(logp)
        exps = [math.exp(lp - m) for lp in logp]
        return normalize(exps)


def check_coherence(p: List[float], tol: float = 1e-9) -> bool:
    if any(math.isnan(x) or x < -tol or x > 1 + tol for x in p):
        return False
    s = sum(p)
    return abs(s - 1.0) <= 1e-6


def run_property_tests(
    rng: random.Random,
    updater: Updater,
    world: World,
    N: int = 2000,
    L: int = 40,
) -> Dict:
    K = len(world.ps)
    prior = [1.0 / K] * K

    coh_viol = 0
    order_viol = 0
    order_l1s: List[float] = []

    neutral_viol = 0

    for _ in range(N):
        true_h = rng.randrange(K)
        seq = [1 if rng.random() < world.ps[true_h] else 0 for _ in range(L)]

        post = updater.update(prior, seq, world)
        if not check_coherence(post):
            coh_viol += 1

        seq2 = seq[:]
        rng.shuffle(seq2)
        post2 = updater.update(prior, seq2, world)

        d = l1(post, post2) if (all(not math.isnan(x) for x in post + post2)) else float('inf')
        order_l1s.append(d)
        if d > 1e-6:
            order_viol += 1

        # Neutral-evidence stability: make evidence uninformative by setting all likelihoods equal
        p_neutral = rng.uniform(0.1, 0.9)
        neutral_world = World(ps=[p_neutral] * K)
        seqN = [1 if rng.random() < p_neutral else 0 for _ in range(L)]
        postN = updater.update(prior, seqN, neutral_world)
        if not all(abs(x - 1.0 / K) <= 1e-6 for x in postN):
            neutral_viol += 1

    return {
        "updater": updater.name,
        "N": N,
        "L": L,
        "coherence_violation_rate": coh_viol / N,
        "order_invariance_violation_rate": order_viol / N,
        "order_invariance_l1_mean": sum(order_l1s) / len(order_l1s),
        "order_invariance_l1_max": max(order_l1s),
        "neutral_evidence_violation_rate": neutral_viol / N,
    }


def main() -> None:
    rng = random.Random(20260301)  # fixed seed for reproducibility

    # World: intentionally close likelihoods to create near-ties under finite evidence
    world = World(ps=[0.55, 0.50, 0.45])

    updaters: List[Updater] = [
        BayesUpdater(),
        GreedyMAPUpdater(),
        TemperedBayesUpdater(cap=0.7),
    ]

    results = {
        "world": {"ps": world.ps},
        "tests": [run_property_tests(rng, u, world) for u in updaters],
        "notes": {
            "tolerance": {
                "order_invariance_l1": 1e-6,
                "coherence_sum_tol": 1e-6,
            },
            "interpretation_hint": "Higher order-invariance violations suggest procedural sensitivity to evidence ordering.",
        },
    }

    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
