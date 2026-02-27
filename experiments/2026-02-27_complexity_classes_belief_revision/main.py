import json, math, os, random, statistics, time
from dataclasses import dataclass
from typing import List, Tuple, Dict


def normalize_log_weights(logw: List[float]) -> List[float]:
    m = max(logw)
    w = [math.exp(x - m) for x in logw]
    s = sum(w)
    return [x / s for x in w]


def categorical_sample(probs: List[float]) -> int:
    r = random.random()
    c = 0.0
    for i, p in enumerate(probs):
        c += p
        if r <= c:
            return i
    return len(probs) - 1


def kl_divergence(p: List[float], q: List[float], eps: float = 1e-12) -> float:
    # KL(p||q)
    s = 0.0
    for pi, qi in zip(p, q):
        pi = max(pi, eps)
        qi = max(qi, eps)
        s += pi * math.log(pi / qi)
    return s


@dataclass
class Problem:
    K: int
    S: int
    true_h: int
    likelihoods: List[List[float]]  # K x S


def make_problem(K: int, S: int, alpha: float = 0.7) -> Problem:
    """Generate K hypotheses each with a categorical distribution over S symbols.

    alpha controls concentration: larger alpha -> more peaked.
    """
    true_h = random.randrange(K)
    likes = []
    for _ in range(K):
        # Dirichlet via gamma draws (stdlib)
        g = [random.gammavariate(alpha, 1.0) for _ in range(S)]
        tot = sum(g)
        likes.append([x / tot for x in g])
    return Problem(K=K, S=S, true_h=true_h, likelihoods=likes)


def run_exact(problem: Problem, evidence: List[int]) -> Tuple[List[float], List[int], List[float]]:
    K = problem.K
    logp = [-math.log(K)] * K  # uniform prior
    argmaxes = []
    true_masses = []
    for e in evidence:
        for h in range(K):
            logp[h] += math.log(max(problem.likelihoods[h][e], 1e-300))
        p = normalize_log_weights(logp)
        argmaxes.append(max(range(K), key=lambda i: p[i]))
        true_masses.append(p[problem.true_h])
    return p, argmaxes, true_masses


def run_particle(problem: Problem, evidence: List[int], M: int, proposal: int = 16) -> Tuple[List[float], List[int], List[float]]:
    """Budgeted sparse Bayesian updater (beam-like).

    Maintains up to M hypotheses with explicit weights; each step, expands with a small
    number of random proposals, updates, renormalizes, then prunes back to M.
    """
    K = problem.K

    # start with M random hypotheses, uniform mass
    start = random.sample(range(K), k=min(M, K))
    support = {h: 1.0 / len(start) for h in start}

    argmaxes = []
    true_masses = []

    for e in evidence:
        # add proposals
        for h in random.sample(range(K), k=min(proposal, K)):
            support.setdefault(h, 1e-12)

        # update weights by likelihood
        for h in list(support.keys()):
            support[h] *= max(problem.likelihoods[h][e], 1e-300)

        # renormalize
        z = sum(support.values())
        if z == 0.0:
            start = random.sample(range(K), k=min(M, K))
            support = {h: 1.0 / len(start) for h in start}
        else:
            for h in support:
                support[h] /= z

        # prune to top M
        top = sorted(support.items(), key=lambda kv: kv[1], reverse=True)[: min(M, K)]
        support = dict(top)

        # embedded posterior
        est = [1e-12] * K
        for h, p in support.items():
            est[h] = p
        s = sum(est)
        est = [x / s for x in est]

        argmaxes.append(max(range(K), key=lambda i: est[i]))
        true_masses.append(est[problem.true_h])

    return est, argmaxes, true_masses



def run_greedy_challengers(problem: Problem, evidence: List[int], M: int, C: int = 12) -> Tuple[List[float], List[int], List[float]]:
    """Maintain a working set W of size M plus C random challengers per step.

    This approximates a bounded updater that cannot score all hypotheses each timestep.
    """
    K = problem.K
    # start with random working set
    W = set(random.sample(range(K), k=min(M, K)))
    logp = {h: -math.log(K) for h in W}

    argmaxes = []
    true_masses = []

    for e in evidence:
        challengers = set(random.sample(range(K), k=min(C, K)))
        U = W | challengers

        # initialize missing logp with uniform prior
        for h in U:
            if h not in logp:
                logp[h] = -math.log(K)

        # update only the considered set
        for h in U:
            logp[h] += math.log(max(problem.likelihoods[h][e], 1e-300))

        # pick next working set as top-M by current logp among U
        top = sorted(U, key=lambda h: logp[h], reverse=True)[: min(M, K)]
        W = set(top)
        logp = {h: logp[h] for h in W}

        # produce an embedded posterior estimate over K by softmax over W only
        # (everything outside W gets epsilon mass)
        logw = [logp[h] for h in W]
        pw = normalize_log_weights(logw)
        est = [1e-12] * K
        for h, ph in zip(list(W), pw):
            est[h] = ph
        s = sum(est)
        est = [x / s for x in est]

        argmaxes.append(max(range(K), key=lambda i: est[i]))
        true_masses.append(est[problem.true_h])

    return est, argmaxes, true_masses


def switches(seq: List[int]) -> int:
    if not seq:
        return 0
    s = 0
    prev = seq[0]
    for x in seq[1:]:
        if x != prev:
            s += 1
            prev = x
    return s


def trial(K: int, S: int, T: int, M: int) -> Dict:
    problem = make_problem(K=K, S=S)
    evidence = [categorical_sample(problem.likelihoods[problem.true_h]) for _ in range(T)]

    exact_p, exact_arg, exact_true = run_exact(problem, evidence)
    part_p, part_arg, part_true = run_particle(problem, evidence, M=M)
    greedy_p, greedy_arg, greedy_true = run_greedy_challengers(problem, evidence, M=M)

    # embed particle posterior already K-length
    eps = 1e-12
    part_emb = [max(x, eps) for x in part_p]
    s = sum(part_emb)
    part_emb = [x / s for x in part_emb]

    return {
        "true_h": problem.true_h,
        "final": {
            "exact_true_mass": exact_p[problem.true_h],
            "particle_true_mass": part_emb[problem.true_h],
            "greedy_true_mass": greedy_p[problem.true_h],
            "exact_correct": int(max(range(K), key=lambda i: exact_p[i]) == problem.true_h),
            "particle_correct": int(max(range(K), key=lambda i: part_emb[i]) == problem.true_h),
            "greedy_correct": int(max(range(K), key=lambda i: greedy_p[i]) == problem.true_h),
            "kl_exact_particle": kl_divergence(exact_p, part_emb),
            "kl_exact_greedy": kl_divergence(exact_p, greedy_p),
        },
        "instability": {
            "exact_switches": switches(exact_arg),
            "particle_switches": switches(part_arg),
            "greedy_switches": switches(greedy_arg),
        },
    }


def summarize(vals: List[float]) -> Dict:
    return {
        "mean": statistics.fmean(vals) if vals else None,
        "median": statistics.median(vals) if vals else None,
        "p25": statistics.quantiles(vals, n=4)[0] if len(vals) >= 4 else None,
        "p75": statistics.quantiles(vals, n=4)[2] if len(vals) >= 4 else None,
        "min": min(vals) if vals else None,
        "max": max(vals) if vals else None,
    }


def main():
    random.seed(0)
    S = 8
    T = 40
    trials = 200

    configs = [
        {"K": 50, "M": 8},
        {"K": 200, "M": 8},
        {"K": 800, "M": 8},
        {"K": 800, "M": 32},
    ]

    out = {
        "meta": {
            "cs_slug": "complexity_classes",
            "theology_target": "belief revision",
            "seed": 0,
            "S": S,
            "T": T,
            "trials": trials,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "configs": [],
    }

    for cfg in configs:
        K, M = cfg["K"], cfg["M"]
        rows = [trial(K=K, S=S, T=T, M=M) for _ in range(trials)]

        exact_tm = [r["final"]["exact_true_mass"] for r in rows]
        part_tm = [r["final"]["particle_true_mass"] for r in rows]
        greedy_tm = [r["final"]["greedy_true_mass"] for r in rows]

        out["configs"].append(
            {
                "K": K,
                "M": M,
                "final_true_mass": {
                    "exact": summarize(exact_tm),
                    "particle": summarize(part_tm),
                    "greedy": summarize(greedy_tm),
                    "regret_exact_minus_particle": summarize([a - b for a, b in zip(exact_tm, part_tm)]),
                    "regret_exact_minus_greedy": summarize([a - b for a, b in zip(exact_tm, greedy_tm)]),
                },
                "accuracy": {
                    "exact": statistics.fmean(r["final"]["exact_correct"] for r in rows),
                    "particle": statistics.fmean(r["final"]["particle_correct"] for r in rows),
                    "greedy": statistics.fmean(r["final"]["greedy_correct"] for r in rows),
                },
                "kl": {
                    "exact_particle": summarize([r["final"]["kl_exact_particle"] for r in rows]),
                    "exact_greedy": summarize([r["final"]["kl_exact_greedy"] for r in rows]),
                },
                "instability_switches": {
                    "exact": summarize([r["instability"]["exact_switches"] for r in rows]),
                    "particle": summarize([r["instability"]["particle_switches"] for r in rows]),
                    "greedy": summarize([r["instability"]["greedy_switches"] for r in rows]),
                },
            }
        )

    here = os.path.dirname(__file__)
    with open(os.path.join(here, "results.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
