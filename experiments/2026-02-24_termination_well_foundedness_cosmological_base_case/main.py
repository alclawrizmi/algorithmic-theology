import json
import random
from dataclasses import dataclass


@dataclass
class TrialResult:
    outcome: str  # "base", "cycle", "timeout"
    steps: int


def run_trial(model: str, *, p_base: float, p_cycle: float, max_steps: int, rng: random.Random) -> TrialResult:
    """Simulate an explanation-chase process.

    model:
      - "E1_base": hits BASE with probability p_base each step
      - "E2_regress": never hits BASE
      - "E3_cycle": may jump back to an earlier node with probability p_cycle

    A cycle is detected when we revisit a node id.
    """
    visited = set()
    current = 0
    visited.add(current)

    for step in range(1, max_steps + 1):
        if model == "E1_base":
            if rng.random() < p_base:
                return TrialResult("base", step)
            current += 1

        elif model == "E2_regress":
            current += 1

        elif model == "E3_cycle":
            if rng.random() < p_cycle and visited:
                current = rng.choice(tuple(visited))
            else:
                current += 1

        else:
            raise ValueError(f"unknown model: {model}")

        if current in visited:
            return TrialResult("cycle", step)
        visited.add(current)

    return TrialResult("timeout", max_steps)


def summarize(results):
    n = len(results)
    counts = {"base": 0, "cycle": 0, "timeout": 0}
    steps_sum = {"base": 0, "cycle": 0, "timeout": 0}

    for r in results:
        counts[r.outcome] += 1
        steps_sum[r.outcome] += r.steps

    def rate(k):
        return counts[k] / n if n else 0.0

    def avg_steps(k):
        return (steps_sum[k] / counts[k]) if counts[k] else None

    return {
        "n_trials": n,
        "terminate_rate": rate("base"),
        "cycle_rate": rate("cycle"),
        "timeout_rate": rate("timeout"),
        "avg_steps_to_base": avg_steps("base"),
        "avg_steps_to_cycle": avg_steps("cycle"),
        "avg_steps_to_timeout": avg_steps("timeout"),
        "counts": counts,
    }


def main():
    rng = random.Random(0)

    config = {
        "n_trials": 20000,
        "max_steps": 200,
        "p_base": 0.05,
        "p_cycle": 0.02,
    }

    out = {"config": config, "models": {}}

    for model in ["E1_base", "E2_regress", "E3_cycle"]:
        results = [
            run_trial(
                model,
                p_base=config["p_base"],
                p_cycle=config["p_cycle"],
                max_steps=config["max_steps"],
                rng=rng,
            )
            for _ in range(config["n_trials"])
        ]
        out["models"][model] = summarize(results)

    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
