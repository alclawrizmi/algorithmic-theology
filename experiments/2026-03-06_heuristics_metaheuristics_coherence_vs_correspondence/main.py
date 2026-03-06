import json, math, random, statistics
from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class Constraint:
    i: int
    j: int
    eq: bool  # True => x_i == x_j, False => x_i != x_j


def rand_bits(n: int) -> List[int]:
    return [random.getrandbits(1) for _ in range(n)]


def gen_observations(truth: List[int], m_obs: int, p_obs_noise: float) -> List[Tuple[int, int]]:
    n = len(truth)
    idxs = random.sample(range(n), k=m_obs)
    obs = []
    for i in idxs:
        v = truth[i]
        if random.random() < p_obs_noise:
            v ^= 1
        obs.append((i, v))
    return obs


def gen_constraints(truth: List[int], m_cons: int, p_constraint_corrupt: float) -> List[Constraint]:
    n = len(truth)
    cons: List[Constraint] = []
    for _ in range(m_cons):
        i, j = random.sample(range(n), 2)
        eq_true = (truth[i] == truth[j])
        eq = eq_true
        if random.random() < p_constraint_corrupt:
            eq = not eq
        cons.append(Constraint(i=i, j=j, eq=eq))
    return cons


def score(b: List[int], obs: List[Tuple[int, int]], cons: List[Constraint], w_c: float, w_o: float) -> float:
    sat = 0
    for c in cons:
        if (b[c.i] == b[c.j]) == c.eq:
            sat += 1
    match = 0
    for i, v in obs:
        if b[i] == v:
            match += 1
    return w_c * sat + w_o * match


def correspondence(b: List[int], truth: List[int]) -> float:
    return sum(1 for x, t in zip(b, truth) if x == t) / len(truth)


def hill_climb(n: int, obs, cons, w_c, w_o, steps: int) -> Tuple[List[int], float]:
    b = rand_bits(n)
    best_s = score(b, obs, cons, w_c, w_o)
    for _ in range(steps):
        i = random.randrange(n)
        b[i] ^= 1
        s = score(b, obs, cons, w_c, w_o)
        if s >= best_s:
            best_s = s
        else:
            b[i] ^= 1
    return b, best_s


def simulated_annealing(n: int, obs, cons, w_c, w_o, steps: int, t0: float, t1: float) -> Tuple[List[int], float]:
    b = rand_bits(n)
    s = score(b, obs, cons, w_c, w_o)
    best_b = b[:]
    best_s = s
    for k in range(steps):
        # exponential cooling
        if steps <= 1:
            T = t1
        else:
            frac = k / (steps - 1)
            T = t0 * (t1 / t0) ** frac
        i = random.randrange(n)
        b[i] ^= 1
        s_new = score(b, obs, cons, w_c, w_o)
        delta = s_new - s
        accept = delta >= 0
        if not accept:
            # metropolis
            if T > 1e-12:
                accept = random.random() < math.exp(delta / T)
        if accept:
            s = s_new
            if s > best_s:
                best_s = s
                best_b = b[:]
        else:
            b[i] ^= 1
    return best_b, best_s


def pearson(xs: List[float], ys: List[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return float('nan')
    mx, my = statistics.mean(xs), statistics.mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return float('nan')
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return cov / math.sqrt(vx * vy)


def run_regime(seed: int, n: int, trials: int, m_obs: int, m_cons: int,
               p_obs_noise: float, p_constraint_corrupt: float,
               w_c: float, w_o: float,
               hc_steps: int, sa_steps: int) -> Dict:
    random.seed(seed)

    rows = []
    traps = 0

    scores_hc = []
    scores_sa = []
    corr_hc = []
    corr_sa = []

    for t in range(trials):
        truth = rand_bits(n)
        obs = gen_observations(truth, m_obs=m_obs, p_obs_noise=p_obs_noise)
        cons = gen_constraints(truth, m_cons=m_cons, p_constraint_corrupt=p_constraint_corrupt)

        b_hc, s_hc = hill_climb(n, obs, cons, w_c, w_o, steps=hc_steps)
        b_sa, s_sa = simulated_annealing(n, obs, cons, w_c, w_o, steps=sa_steps, t0=2.0, t1=0.01)

        c_hc = correspondence(b_hc, truth)
        c_sa = correspondence(b_sa, truth)

        scores_hc.append(s_hc)
        scores_sa.append(s_sa)
        corr_hc.append(c_hc)
        corr_sa.append(c_sa)

        # coherence trap: higher proxy score but lower correspondence
        if (s_sa > s_hc) and (c_sa < c_hc):
            traps += 1

        rows.append({
            "trial": t,
            "score_hill_climb": s_hc,
            "score_sim_anneal": s_sa,
            "corr_hill_climb": c_hc,
            "corr_sim_anneal": c_sa,
        })

    out = {
        "params": {
            "seed": seed,
            "n": n,
            "trials": trials,
            "m_obs": m_obs,
            "m_cons": m_cons,
            "p_obs_noise": p_obs_noise,
            "p_constraint_corrupt": p_constraint_corrupt,
            "w_c": w_c,
            "w_o": w_o,
            "hc_steps": hc_steps,
            "sa_steps": sa_steps,
        },
        "summary": {
            "mean_score_hill_climb": statistics.mean(scores_hc),
            "mean_score_sim_anneal": statistics.mean(scores_sa),
            "mean_corr_hill_climb": statistics.mean(corr_hc),
            "mean_corr_sim_anneal": statistics.mean(corr_sa),
            "pearson_score_vs_corr_hc": pearson(scores_hc, corr_hc),
            "pearson_score_vs_corr_sa": pearson(scores_sa, corr_sa),
            "coherence_trap_rate_sa_vs_hc": traps / trials,
        },
        "rows": rows,
    }
    return out


def main():
    # Keep runtime modest and deterministic across runs.
    seed0 = 20260306

    n = 40
    trials = 200
    m_obs = 12
    m_cons = 120
    w_c, w_o = 1.0, 3.0
    hc_steps = 2500
    sa_steps = 2500

    regimes = [
        # (obs_noise, constraint_corrupt)
        (0.00, 0.00),
        (0.10, 0.00),
        (0.00, 0.20),
        (0.10, 0.20),
        (0.20, 0.35),
    ]

    results = {
        "experiment": "heuristics_metaheuristics_coherence_vs_correspondence",
        "regimes": [],
        "notes": {
            "interpretation_hint": "Coherence proxy mixes constraint satisfaction with observation-fit; correspondence is measured against hidden truth.",
        },
    }

    for k, (p_obs_noise, p_constraint_corrupt) in enumerate(regimes):
        res = run_regime(
            seed=seed0 + k,
            n=n,
            trials=trials,
            m_obs=m_obs,
            m_cons=m_cons,
            p_obs_noise=p_obs_noise,
            p_constraint_corrupt=p_constraint_corrupt,
            w_c=w_c,
            w_o=w_o,
            hc_steps=hc_steps,
            sa_steps=sa_steps,
        )
        results["regimes"].append(res)

    print(json.dumps({
        "high_level": {
            "n": n,
            "trials": trials,
            "regime_summaries": [r["summary"] | {"p_obs_noise": r["params"]["p_obs_noise"], "p_constraint_corrupt": r["params"]["p_constraint_corrupt"]} for r in results["regimes"]]
        }
    }, indent=2))

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
