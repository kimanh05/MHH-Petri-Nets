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


# -------- JSON Helpers --------
def jload(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def jwrite(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4)


# -------- Optimization Logic --------
def optimize(reachable_markings, c, places):
    """
    reachable_markings: list of marking dicts
    c: vector of weights (list of int)
    places: fixed ordering of places
    """
    best_val = float("-inf")
    best_list = []

    for marking in reachable_markings:
        # Compute c^T M with respect to given place ordering
        value = sum(c[i] * marking.get(p, 0) for i, p in enumerate(places))

        if value > best_val:
            best_val = value
            best_list = [marking]
        elif value == best_val:
            best_list.append(marking)

    return best_val, best_list


# -------- Main --------
def main():
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA = os.path.join(ROOT, "data")

    # Input paths
    reach_path = os.path.join(DATA, "reachable_markings.json")
    carr_path = os.path.join(DATA, "CArr.json")
    net_path = os.path.join(DATA, "net_structure.json")

    # Output path
    out_path = os.path.join(DATA, "optimization_result.json")

    # ---- Load files ----
    reach_data = jload(reach_path)
    reachable_markings = reach_data.get("reachable_markings", [])

    c = jload(carr_path)
    net = jload(net_path)

    # Use consistent place ordering from net_structure.json
    places = net["places"]

    # ---- Optimize ----
    start = time.perf_counter()
    max_val, best_markings = optimize(reachable_markings, c, places)
    end = time.perf_counter()

    result = {
        "best_marking": best_markings,
        "max_value": max_val,
        "time_seconds": round(end - start, 6)
    }

    # Save
    jwrite(result, out_path)

    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()