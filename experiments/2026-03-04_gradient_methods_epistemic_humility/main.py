import json
import math
import os
import random
from dataclasses import dataclass, asdict

@dataclass
class RunResult:
    x0: float
    x_final: float
    loss_final: float
    basin: str
    steps: int


def loss(x: float, a: float, b: float, y_bias: float) -> float:
    # Quartic double-well with minima near a and b, plus a small evidence term.
    base = (x - a) ** 2 * (x - b) ** 2
    evidence = 0.15 * (x - y_bias) ** 2
    return base + evidence


def grad_loss(x: float, a: float, b: float, y_bias: float) -> float:
    dbase = 2 * (x - a) * (x - b) ** 2 + 2 * (x - b) * (x - a) ** 2
    devidence = 0.30 * (x - y_bias)
    return dbase + devidence


def basin_of(x: float, a: float, b: float) -> str:
    return "near_a" if abs(x - a) <= abs(x - b) else "near_b"


def gd(x0: float, a: float, b: float, y_bias: float, lr: float, iters: int) -> RunResult:
    x = x0
    clamp = 12.0
    gclip = 200.0

    for t in range(iters):
        g = grad_loss(x, a, b, y_bias)
        # numerical stability: clip gradients and clamp parameter
        if g > gclip:
            g = gclip
        elif g < -gclip:
            g = -gclip

        x_new = x - lr * g
        if x_new > clamp:
            x_new = clamp
        elif x_new < -clamp:
            x_new = -clamp

        if abs(x_new - x) < 1e-10:
            x = x_new
            return RunResult(x0=x0, x_final=x, loss_final=loss(x, a, b, y_bias), basin=basin_of(x, a, b), steps=t + 1)
        x = x_new

    return RunResult(x0=x0, x_final=x, loss_final=loss(x, a, b, y_bias), basin=basin_of(x, a, b), steps=iters)


def summarize(results):
    xs = [r.x_final for r in results]
    mean = sum(xs) / len(xs)
    var = sum((v - mean) ** 2 for v in xs) / len(xs)
    sd = math.sqrt(var)

    counts = {"near_a": 0, "near_b": 0}
    for r in results:
        counts[r.basin] += 1

    best_loss = min(r.loss_final for r in results)
    near_best = [r for r in results if r.loss_final <= best_loss + 1e-6]

    return {
        "n": len(results),
        "mean_x": mean,
        "sd_x": sd,
        "counts": counts,
        "best_loss": best_loss,
        "near_best_basin_counts": {
            "near_a": sum(1 for r in near_best if r.basin == "near_a"),
            "near_b": sum(1 for r in near_best if r.basin == "near_b"),
        },
    }


def main():
    random.seed(0)

    a, b = -2.0, 2.0
    true_basin = "near_a"
    y_bias = a

    lr = 0.02
    iters = 2000

    c1 = gd(x0=0.0, a=a, b=b, y_bias=y_bias, lr=lr, iters=iters)

    restarts = 200
    results = []
    for _ in range(restarts):
        x0 = random.uniform(-6.0, 6.0)
        results.append(gd(x0=x0, a=a, b=b, y_bias=y_bias, lr=lr, iters=iters))

    summ = summarize(results)

    spread_threshold = 0.6
    multimodal_nearbest = (summ["near_best_basin_counts"]["near_a"] > 0 and summ["near_best_basin_counts"]["near_b"] > 0)
    c3 = {
        "policy": "tempered_humility",
        "collapse": (summ["sd_x"] < spread_threshold) and (not multimodal_nearbest),
        "reason": {
            "sd_x": summ["sd_x"],
            "spread_threshold": spread_threshold,
            "multimodal_nearbest": multimodal_nearbest,
        },
    }

    out = {
        "setup": {
            "a": a,
            "b": b,
            "y_bias": y_bias,
            "true_basin": true_basin,
            "lr": lr,
            "iters": iters,
            "restarts": restarts,
        },
        "c1": asdict(c1),
        "ensemble_summary": summ,
        "c3": c3,
        "sample_runs": [asdict(r) for r in results[:10]],
    }

    with open(os.path.join(os.path.dirname(__file__), "results.json"), "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
