import json
import random
from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Dict


def random_dag(n: int, edge_p: float, rng: random.Random) -> List[List[int]]:
    """Generate a DAG by only allowing edges i->j with i<j."""
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < edge_p:
                adj[i].append(j)
    return adj


def flip_edges(adj: List[List[int]], flips: int, rng: random.Random) -> None:
    """Randomly add/remove edges while maintaining i<j constraint."""
    n = len(adj)
    edge_set = set()
    for i in range(n):
        for j in adj[i]:
            edge_set.add((i, j))

    for _ in range(flips):
        i = rng.randrange(n)
        j = rng.randrange(n)
        if i == j:
            continue
        if i > j:
            i, j = j, i
        e = (i, j)
        if e in edge_set:
            edge_set.remove(e)
        else:
            edge_set.add(e)

    for i in range(n):
        adj[i].clear()
    for i, j in sorted(edge_set):
        adj[i].append(j)


def reachable(adj: List[List[int]], a: int, b: int) -> bool:
    if a == b:
        return True
    n = len(adj)
    seen = [False] * n
    q = deque([a])
    seen[a] = True
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v == b:
                return True
            if not seen[v]:
                seen[v] = True
                q.append(v)
    return False


@dataclass
class Query:
    a: int
    b: int


def sample_queries(n: int, q: int, rng: random.Random):
    out = []
    for _ in range(q):
        a = rng.randrange(n)
        b = rng.randrange(n)
        while b == a:
            b = rng.randrange(n)
        out.append(Query(a, b))
    return out


def policy_AP(adj1, adj2, query: Query, rng: random.Random) -> bool:
    if rng.random() < 0.5:
        return reachable(adj1, query.a, query.b)
    else:
        return reachable(adj2, query.a, query.b)


def policy_CP(adj1, adj2, query: Query) -> Optional[bool]:
    r1 = reachable(adj1, query.a, query.b)
    r2 = reachable(adj2, query.a, query.b)
    if r1 == r2:
        return r1
    return None


def run(seed: int = 0) -> Dict:
    rng = random.Random(seed)

    N = 30
    EDGE_P = 0.08
    FLIPS_DURING_PARTITION = 40
    Q = 2000

    G = random_dag(N, EDGE_P, rng)
    G1 = [lst[:] for lst in G]
    G2 = [lst[:] for lst in G]

    flip_edges(G1, FLIPS_DURING_PARTITION, random.Random(seed + 1))
    flip_edges(G2, FLIPS_DURING_PARTITION, random.Random(seed + 2))

    queries = sample_queries(N, Q, rng)

    truth = [reachable(G, qu.a, qu.b) for qu in queries]
    r1 = [reachable(G1, qu.a, qu.b) for qu in queries]
    r2 = [reachable(G2, qu.a, qu.b) for qu in queries]

    disagree = [x != y for x, y in zip(r1, r2)]
    contradiction_rate = sum(disagree) / Q

    ap_answers = [policy_AP(G1, G2, qu, rng) for qu in queries]
    ap_accuracy = sum(int(a == t) for a, t in zip(ap_answers, truth)) / Q
    ap_false_certainty = sum(int(d) for d in disagree) / Q

    cp_answers = [policy_CP(G1, G2, qu) for qu in queries]
    cp_answered = [a for a in cp_answers if a is not None]
    cp_availability = len(cp_answered) / Q
    cp_accuracy = (
        sum(int(a == t) for a, t in zip(cp_answers, truth) if a is not None) / len(cp_answered)
        if cp_answered
        else None
    )

    return {
        "seed": seed,
        "params": {
            "N": N,
            "EDGE_P": EDGE_P,
            "FLIPS_DURING_PARTITION": FLIPS_DURING_PARTITION,
            "Q": Q,
        },
        "replica_disagreement_rate": contradiction_rate,
        "AP": {
            "availability": 1.0,
            "accuracy_vs_objective": ap_accuracy,
            "false_certainty_rate": ap_false_certainty,
        },
        "CP": {
            "availability": cp_availability,
            "accuracy_vs_objective": cp_accuracy,
        },
    }


if __name__ == "__main__":
    results = run(seed=0)
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    print(json.dumps(results, indent=2, sort_keys=True))
