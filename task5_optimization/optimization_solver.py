"""
Task 5 – Optimization over Reachable Markings
----------------------------------------------
Description:
    Given a linear objective function maximize c^T M, where M belongs
    to the set of reachable markings Reach(M0), determines the marking
    that maximizes the objective function. If no marking satisfies
    the condition, the program reports none.

Input:
    data/reachable_markings.json

Output:
    data/optimization_result.json

Author:
    Thanh Binh
"""
import time
import json
import os


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4)


def optimization(markingArr, c, places):
    best_val = float("-inf")
    best_list = []

    for marking in markingArr:
        # compute c^T M with consistent ordering from places[]
        tmp = sum(c[i] * marking[p] for i, p in enumerate(places))

        if tmp > best_val:
            best_val = tmp
            best_list = [marking]
        elif tmp == best_val:
            best_list.append(marking)

    return best_val, best_list


def main():
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA = os.path.join(ROOT, "data")

    marking_path = os.path.join(DATA, "reachable_markings.json")
    carr_path = os.path.join(DATA, "CArr.json")
    net_path = os.path.join(DATA, "net_structure.json")
    out_path = os.path.join(DATA, "optimization_result.json")

    # Load input data
    markingArr = read(marking_path)
    c = read(carr_path)
    net = read(net_path)

    # FIX: Use consistent place ordering from net_structure.json
    places = net["places"]

    # Optimize
    start = time.perf_counter()
    bestVal, bestMarking = optimization(markingArr, c, places)
    end = time.perf_counter()

    result = {
        "best_marking": bestMarking,
        "max_value": bestVal,
        "time_seconds": end - start
    }

    write(result, out_path)

    # Print output to terminal
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()