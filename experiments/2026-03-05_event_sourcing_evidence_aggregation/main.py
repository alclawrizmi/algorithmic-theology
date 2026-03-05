import json
import math
import os
import random
from dataclasses import dataclass


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def logit(p: float) -> float:
    p = min(max(p, 1e-9), 1 - 1e-9)
    return math.log(p / (1 - p))


@dataclass
class Event:
    t: int
    src: int
    claim: int


def sample_world(rng: random.Random, n_sources: int):
    H = rng.choice([0, 1])
    ps = [0.55 + 0.40 * rng.random() for _ in range(n_sources)]
    return H, ps


def generate_events(rng: random.Random, H: int, ps, n_events: int):
    events = []
    for t in range(n_events):
        src = rng.randrange(len(ps))
        p = ps[src]
        truthful = rng.random() < p
        claim = H if truthful else (1 - H)
        events.append(Event(t=t, src=src, claim=claim))
    return events


def fold_logodds(events, weights):
    lo = 0.0
    for ev in events:
        w = logit(weights[ev.src])
        lo += (w if ev.claim == 1 else -w)
    return lo


def posterior(lo: float) -> float:
    return sigmoid(lo)


def nll_true(H: int, p_h1: float) -> float:
    p = p_h1 if H == 1 else (1 - p_h1)
    p = min(max(p, 1e-12), 1.0)
    return -math.log(p)


def run(seed: int = 0):
    rng = random.Random(seed)

    n_sources = 12
    n_events = 600
    t_change = 300
    W = 80

    H, true_ps = sample_world(rng, n_sources)
    events = generate_events(rng, H, true_ps, n_events)

    q0 = [0.65 for _ in range(n_sources)]
    q1 = list(true_ps)

    log_full = []
    log_window = []
    lo_snapshot = 0.0

    traj = {"ideal": [], "event_sourced": [], "snapshot_only": [], "windowed": []}

    for t, ev in enumerate(events):
        log_full.append(ev)
        log_window.append(ev)
        if len(log_window) > W:
            log_window.pop(0)

        weights_now = q0 if t < t_change else q1

        # snapshot updates irreversibly with weights at the time
        w_now = logit(weights_now[ev.src])
        lo_snapshot += (w_now if ev.claim == 1 else -w_now)

        lo_es = fold_logodds(log_full, weights_now)
        lo_win = fold_logodds(log_window, weights_now)

        # counterfactual ideal: after change, reweight ALL past events with q1
        lo_ideal = fold_logodds(log_full, q0 if t < t_change else q1)

        traj["ideal"].append(posterior(lo_ideal))
        traj["event_sourced"].append(posterior(lo_es))
        traj["snapshot_only"].append(posterior(lo_snapshot))
        traj["windowed"].append(posterior(lo_win))

    idx0 = t_change
    idx1 = n_events - 1

    def summarize(name: str):
        p_star = traj["ideal"][idx1]
        p = traj[name][idx1]
        return {
            "p_final": p,
            "p_star_final": p_star,
            "mae_final": abs(p - p_star),
            "regret_final": nll_true(H, p) - nll_true(H, p_star),
            "acc_final": int((p >= 0.5) == (H == 1)),
            "p_at_change": traj[name][idx0],
            "p_star_at_change": traj["ideal"][idx0],
            "mae_at_change": abs(traj[name][idx0] - traj["ideal"][idx0]),
        }

    out = {
        "seed": seed,
        "setup": {
            "H_true": H,
            "n_sources": n_sources,
            "n_events": n_events,
            "t_change": t_change,
            "W_window": W,
            "q0": 0.65,
            "true_ps": true_ps,
            "mean_abs_weight_shift": sum(abs(p - 0.65) for p in true_ps) / len(true_ps),
        },
        "summary": {
            "event_sourced": summarize("event_sourced"),
            "snapshot_only": summarize("snapshot_only"),
            "windowed": summarize("windowed"),
        },
        "trajectory_sample": {
            "t": list(range(0, n_events, 10)),
            "ideal": traj["ideal"][0:n_events:10],
            "event_sourced": traj["event_sourced"][0:n_events:10],
            "snapshot_only": traj["snapshot_only"][0:n_events:10],
            "windowed": traj["windowed"][0:n_events:10],
        },
    }

    return out


if __name__ == "__main__":
    out = run(seed=0)
    here = os.path.dirname(__file__)
    with open(os.path.join(here, "results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out["summary"], indent=2))
