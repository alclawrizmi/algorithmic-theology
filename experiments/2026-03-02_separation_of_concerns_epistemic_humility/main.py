import json
import math
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple


def sigmoid(z: float) -> float:
    # numerically safe-ish sigmoid
    if z >= 0:
        ez = math.exp(-z)
        return 1.0 / (1.0 + ez)
    else:
        ez = math.exp(z)
        return ez / (1.0 + ez)


def dot(w: List[float], x: List[float]) -> float:
    return sum(wi * xi for wi, xi in zip(w, x))


@dataclass
class Dataset:
    X: List[List[float]]
    y: List[int]


def make_dataset(n: int, seed: int, spurious_corr: float) -> Dataset:
    """Generate data.

    - y ~ Bernoulli(0.5)
    - causal feature Xc: y + Gaussian noise
    - spurious feature Xs: correlated with y by flipping label with prob (1 - spurious_corr)

    spurious_corr in [0,1]: 1.0 means perfectly aligned with y, 0.0 means perfectly anti-aligned.
    """
    rnd = random.Random(seed)

    X, y = [], []
    for _ in range(n):
        yi = 1 if rnd.random() < 0.5 else 0
        y.append(yi)

        # causal: centered around +/-1 with noise
        xc = (1.0 if yi == 1 else -1.0) + rnd.gauss(0.0, 1.0)

        # spurious: match y with probability spurious_corr, else flip
        matches = rnd.random() < spurious_corr
        ys = yi if matches else 1 - yi
        xs = (1.0 if ys == 1 else -1.0) + rnd.gauss(0.0, 1.0)

        # bias term included in features
        X.append([1.0, xc, xs])

    return Dataset(X=X, y=y)


def fit_logreg_gd(ds: Dataset, steps: int, lr: float, l2: float, seed: int) -> List[float]:
    """Simple logistic regression with SGD (one pass per step over random sample)."""
    rnd = random.Random(seed)
    d = len(ds.X[0])
    w = [rnd.uniform(-0.1, 0.1) for _ in range(d)]

    n = len(ds.X)
    for _ in range(steps):
        i = rnd.randrange(n)
        x = ds.X[i]
        yi = ds.y[i]
        p = sigmoid(dot(w, x))

        # gradient of log loss + L2
        # loss = -[y log p + (1-y) log(1-p)] + (l2/2)||w||^2
        for j in range(d):
            grad = (p - yi) * x[j] + l2 * w[j]
            w[j] -= lr * grad

    return w


def predict_proba(w: List[float], X: List[List[float]]) -> List[float]:
    return [sigmoid(dot(w, x)) for x in X]


def brier(probs: List[float], y: List[int]) -> float:
    return sum((p - yi) ** 2 for p, yi in zip(probs, y)) / len(y)


def accuracy(probs: List[float], y: List[int], threshold: float = 0.5) -> float:
    correct = 0
    for p, yi in zip(probs, y):
        pred = 1 if p >= threshold else 0
        correct += 1 if pred == yi else 0
    return correct / len(y)


def ece(probs: List[float], y: List[int], bins: int = 10) -> float:
    # equal-width bins in [0,1]
    n = len(y)
    ece_val = 0.0
    for b in range(bins):
        lo = b / bins
        hi = (b + 1) / bins
        idx = [i for i, p in enumerate(probs) if (p >= lo and (p < hi or (b == bins - 1 and p <= hi)))]
        if not idx:
            continue
        avg_p = sum(probs[i] for i in idx) / len(idx)
        avg_y = sum(y[i] for i in idx) / len(idx)
        ece_val += (len(idx) / n) * abs(avg_p - avg_y)
    return ece_val


def mean_confidence_on_errors(probs: List[float], y: List[int]) -> float:
    errs = []
    for p, yi in zip(probs, y):
        pred = 1 if p >= 0.5 else 0
        if pred != yi:
            errs.append(p if pred == 1 else (1 - p))
    return sum(errs) / len(errs) if errs else 0.0


def temperature_scale(probs: List[float], T: float) -> List[float]:
    # Apply temperature scaling in logit space.
    out = []
    for p in probs:
        p = min(max(p, 1e-9), 1 - 1e-9)
        logit = math.log(p / (1 - p))
        out.append(sigmoid(logit / T))
    return out


def run_once(seed: int) -> Dict:
    # training environment: spurious feature aligns with y strongly
    train = make_dataset(n=5000, seed=seed, spurious_corr=0.9)

    # test (shift): spurious flips (anti-correlated)
    test_shift = make_dataset(n=5000, seed=seed + 1, spurious_corr=0.1)

    # E1: monolith uses both features (bias, xc, xs)
    w_mono = fit_logreg_gd(train, steps=20000, lr=0.05, l2=1e-4, seed=seed + 2)

    # E2: separated concerns: forbid access to spurious feature by zeroing its column
    # equivalent to training on [bias, xc] only.
    train_sep = Dataset(X=[[x[0], x[1], 0.0] for x in train.X], y=train.y)
    test_sep = Dataset(X=[[x[0], x[1], 0.0] for x in test_shift.X], y=test_shift.y)
    w_sep = fit_logreg_gd(train_sep, steps=20000, lr=0.05, l2=1e-4, seed=seed + 3)

    # E3: monolith + temperature scaling (post-hoc humility knob)
    probs_mono_train = predict_proba(w_mono, train.X)
    probs_mono_test = predict_proba(w_mono, test_shift.X)

    # pick a simple temperature by searching a small grid to minimize train ECE
    best_T, best_ece = 1.0, float("inf")
    for T in [0.7, 0.9, 1.0, 1.2, 1.5, 2.0, 3.0]:
        e = ece(temperature_scale(probs_mono_train, T), train.y, bins=15)
        if e < best_ece:
            best_ece, best_T = e, T

    probs_mono_T_train = temperature_scale(probs_mono_train, best_T)
    probs_mono_T_test = temperature_scale(probs_mono_test, best_T)

    # E2 probs
    probs_sep_train = predict_proba(w_sep, train_sep.X)
    probs_sep_test = predict_proba(w_sep, test_sep.X)

    def metrics(name: str, probs_tr: List[float], probs_te: List[float]) -> Dict:
        return {
            "name": name,
            "train": {
                "accuracy": accuracy(probs_tr, train.y),
                "brier": brier(probs_tr, train.y),
                "ece": ece(probs_tr, train.y, bins=15),
            },
            "shift_test": {
                "accuracy": accuracy(probs_te, test_shift.y),
                "brier": brier(probs_te, test_shift.y),
                "ece": ece(probs_te, test_shift.y, bins=15),
                "mean_confidence_on_errors": mean_confidence_on_errors(probs_te, test_shift.y),
            },
        }

    return {
        "seed": seed,
        "temperatures": {"mono_best_T": best_T, "mono_best_train_ece": best_ece},
        "models": [
            metrics("E1_monolith", probs_mono_train, probs_mono_test),
            metrics("E2_separated_concerns", probs_sep_train, probs_sep_test),
            metrics("E3_monolith_temp_scaled", probs_mono_T_train, probs_mono_T_test),
        ],
        "weights": {
            "monolith": {"bias": w_mono[0], "xc": w_mono[1], "xs": w_mono[2]},
            "separated": {"bias": w_sep[0], "xc": w_sep[1], "xs_forced_zero": w_sep[2]},
        },
    }


def summarize(runs: List[Dict]) -> Dict:
    # average metrics across runs
    by_name = {}
    for r in runs:
        for m in r["models"]:
            by_name.setdefault(m["name"], []).append(m)

    def avg(vals: List[float]) -> float:
        return sum(vals) / len(vals)

    out = {"models": {}}
    for name, ms in by_name.items():
        out["models"][name] = {
            "train": {
                "accuracy": avg([m["train"]["accuracy"] for m in ms]),
                "brier": avg([m["train"]["brier"] for m in ms]),
                "ece": avg([m["train"]["ece"] for m in ms]),
            },
            "shift_test": {
                "accuracy": avg([m["shift_test"]["accuracy"] for m in ms]),
                "brier": avg([m["shift_test"]["brier"] for m in ms]),
                "ece": avg([m["shift_test"]["ece"] for m in ms]),
                "mean_confidence_on_errors": avg([m["shift_test"]["mean_confidence_on_errors"] for m in ms]),
            },
        }

    out["temperatures"] = {
        "mono_best_T_avg": avg([r["temperatures"]["mono_best_T"] for r in runs]),
    }
    return out


def main() -> None:
    seeds = [0, 1, 2, 3, 4]
    runs = [run_once(s) for s in seeds]
    summary = summarize(runs)

    results = {
        "meta": {
            "experiment_id": os.path.basename(os.path.dirname(os.path.abspath(__file__))),
            "date_utc": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "seeds": seeds,
            "train_spurious_corr": 0.9,
            "shift_test_spurious_corr": 0.1,
        },
        "summary": summary,
        "runs": runs,
    }

    out_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)

    # minimal console summary
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
