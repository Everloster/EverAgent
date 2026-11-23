#!/usr/bin/env python3
"""Small algebra checks, with invented data. No model training or TRL calls."""
import json
import math


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def add(a, b):
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(a, weight):
    return [[weight * x for x in row] for row in a]


def advantages(rewards):
    # Population standard deviation for this illustrative example only.
    mean = sum(rewards) / len(rewards)
    std = math.sqrt(sum((x - mean) ** 2 for x in rewards) / len(rewards))
    return [(x - mean) / (std + 1e-8) for x in rewards]


def main():
    b1, a1 = [[1], [2]], [[1, 3]]
    b2, a2 = [[4], [1]], [[2, -1]]
    expected = scale(add(matmul(b1, a1), matmul(b2, a2)), 0.5)
    bcat = [left + right for left, right in zip(b1, b2)]
    acat = scale(a1, 0.5) + scale(a2, 0.5)
    exact = matmul(bcat, acat)
    naive = scale(matmul(add(b1, b2), add(a1, a2)), 0.5)
    assert exact == expected and naive != expected
    assert advantages([0, 0, 0, 0]) == [0, 0, 0, 0]
    assert advantages([1, 1, 1, 1]) == [0, 0, 0, 0]
    mixed = advantages([0, 0, 1, 1])
    assert mixed[0] < 0 < mixed[-1]
    signals = [
        {"success_probability": p, "group_size": g,
         "probability_of_mixed_binary_rewards": 1 - p ** g - (1 - p) ** g}
        for p in [0.05, 0.5] for g in [4, 8]
    ]
    print(json.dumps({"scope": "invented matrix and Bernoulli examples; no GPU experiment",
                      "weighted_update_sum": expected, "concatenation": exact,
                      "naive_factor_addition": naive, "mixed_group_advantages": mixed,
                      "signals": signals}, indent=2))


if __name__ == "__main__":
    main()
