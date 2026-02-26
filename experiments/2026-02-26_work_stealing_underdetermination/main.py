import json, math, random, statistics
from collections import Counter, deque

def shannon_entropy(counter: Counter):
    total = sum(counter.values())
    if total == 0:
        return 0.0
    ent = 0.0
    for c in counter.values():
        p = c / total
        ent -= p * math.log(p + 1e-18, 2)
    return ent

def gini_from_counts(counter: Counter):
    xs = sorted(counter.values())
    n = len(xs)
    if n == 0:
        return 0.0
    s = sum(xs)
    if s == 0:
        return 0.0
    cum = 0
    for i, x in enumerate(xs, 1):
        cum += i * x
    return (2 * cum) / (n * s) - (n + 1) / n

class RNG:
    def __init__(self, seed: int):
        self.r = random.Random(seed)
    def fit(self):
        return self.r.random()
    def eval_time(self):
        u = self.r.random()
        return 0.2 + (u ** -0.7) * 0.02


def simulate_trial(policy: str, *, seed: int, H: int, W: int, T: float, epsilon: float):
    rng = RNG(seed)
    fits = [rng.fit() for _ in range(H)]

    if policy == "fifo":
        global_q = deque(range(H))
        local = [None] * W
    elif policy in ("local_no_steal", "work_steal"):
        local = [deque() for _ in range(W)]
        for i, h in enumerate(range(H)):
            local[i % W].append(h)
        global_q = None
    else:
        raise ValueError(policy)

    t = 0.0
    evaluated = []
    evals_by_worker = [0] * W

    while t < T:
        progressed = False
        for w in range(W):
            if t >= T:
                break

            h = None
            if policy == "fifo":
                if global_q:
                    h = global_q.popleft()
            elif policy == "local_no_steal":
                if local[w]:
                    h = local[w].popleft()
            elif policy == "work_steal":
                if local[w]:
                    h = local[w].pop()
                else:
                    victims = list(range(W))
                    rng.r.shuffle(victims)
                    for v in victims:
                        if v != w and local[v]:
                            h = local[v].popleft()
                            break
            if h is None:
                continue

            dt = rng.eval_time()
            if t + dt > T:
                t = T
                break
            t += dt
            evaluated.append((h, fits[h]))
            evals_by_worker[w] += 1
            progressed = True

        if not progressed:
            break

    if not evaluated:
        return {"winner": None, "acceptable_count": 0, "evaluated": 0, "coverage_skew": 0.0}

    best = max(f for _, f in evaluated)
    acceptable = [h for (h, f) in evaluated if best - f <= epsilon]

    winner = None
    for h, f in evaluated:
        if best - f <= epsilon:
            winner = h
            break

    skew = statistics.pstdev(evals_by_worker) if W > 1 else 0.0
    return {
        "winner": winner,
        "acceptable_count": len(set(acceptable)),
        "evaluated": len(evaluated),
        "coverage_skew": skew,
    }


def run(*, trials: int, H: int, W: int, T: float, epsilon: float, seed: int):
    policies = ["fifo", "local_no_steal", "work_steal"]
    out = {}
    for p in policies:
        winners = Counter()
        acceptable_counts = []
        evaluated_counts = []
        skews = []
        for i in range(trials):
            r = simulate_trial(p, seed=seed + 100000 * policies.index(p) + i, H=H, W=W, T=T, epsilon=epsilon)
            if r["winner"] is not None:
                winners[r["winner"]] += 1
            acceptable_counts.append(r["acceptable_count"])
            evaluated_counts.append(r["evaluated"])
            skews.append(r["coverage_skew"])

        out[p] = {
            "trials": trials,
            "winner_support": len(winners),
            "winner_entropy_bits": shannon_entropy(winners),
            "winner_gini": gini_from_counts(winners),
            "avg_acceptable_count": sum(acceptable_counts) / len(acceptable_counts),
            "avg_evaluated": sum(evaluated_counts) / len(evaluated_counts),
            "avg_coverage_skew": sum(skews) / len(skews),
        }
    return out


def main():
    cfg = {"trials": 2000, "H": 400, "W": 8, "T": 25.0, "epsilon": 0.01, "seed": 260226}
    results = run(**cfg)
    payload = {"config": cfg, "results": results}
    print(json.dumps(payload, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
