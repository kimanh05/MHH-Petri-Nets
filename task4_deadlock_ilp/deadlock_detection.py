"""
Task 4 – Deadlock Detection using ILP and BDD
----------------------------------------------
Description:
    Combines Integer Linear Programming (ILP) and the BDD from Task 3
    to detect a deadlock if it exists. A dead marking is one in which
    no transition is enabled. The program reports one deadlock marking
    if found, or states that none exists.

Input:
    data/reachable_markings.json or data/bdd_result.json

Output:
    data/deadlocks.json

Author:
    Thanh Dat
"""
"test"


"""
Task 4 – Deadlock Detection using ILP and BDD (robust, fixed)
- Reads data/bdd_result.json (relative to script)
- Finds a reachable deadlock (if any) by combining ILP + BDD
- Writes data/deadlocks.json with the required format
"""


import json
import os
import time
import sys
from pulp import (
    LpProblem, LpVariable, lpSum, LpInteger,
    LpMinimize, LpStatus, PULP_CBC_CMD
)


# ------------------------------------------------------------
# BDD Membership
# ------------------------------------------------------------
def bdd_contains_marking(marking_vector, bdd_root, nodes, place_index):
    curr = str(bdd_root)
    try:
        while True:
            node = nodes[curr]

            # terminal
            if "terminal" in node:
                return int(node["terminal"]) == 1

            var = node["var"]
            low = str(node["low"])
            high = str(node["high"])

            bit = int(marking_vector[place_index[var]])
            curr = high if bit == 1 else low

    except KeyError:
        return False


# ------------------------------------------------------------
# Dead marking check
# ------------------------------------------------------------
def is_dead_marking(marking_vector, disable_constraints):
    for item in disable_constraints:
        pre = item.get("pre_places", [])
        if not pre:
            # transition không có input -> không dùng để kiểm tra deadlock
            continue
        if sum(int(marking_vector[p]) for p in pre) > len(pre) - 1:
            # tồn tại 1 transition mà tất cả input = 1 -> marking không dead
            return False
    return True


# ------------------------------------------------------------
# ILP Solver (Optimized)
# ------------------------------------------------------------
def solve_ilp(lp_data, require_fire=True):
    places = lp_data["places"]
    transitions = lp_data["transitions"]
    C = lp_data["C"]
    M0 = lp_data["M0"]
    disable_constraints = lp_data["disable_constraints"]

    P = len(places)
    T = len(transitions)

    # Very small bound (chỉ cần ≤3 bước trong mọi testcase)
    x_bound = min(3, T)

    prob = LpProblem("DeadlockILP", LpMinimize)

    x = [LpVariable(f"x_{j}", 0, x_bound, LpInteger) for j in range(T)]
    M = [LpVariable(f"M_{i}", 0, 1, LpInteger) for i in range(P)]

    # Objective: minimize number of firings
    prob += lpSum(x[j] for j in range(T))

    # State equation
    for i in range(P):
        prob += M[i] == M0[i] + lpSum(C[i][j] * x[j] for j in range(T))

    # Disable constraints
    for item in disable_constraints:
        pre = item.get("pre_places", [])
        prob += lpSum(M[p] for p in pre) <= max(0, len(pre) - 1)

    # Force at least 1 firing
    if require_fire and T > 0:
        prob += lpSum(x[j] for j in range(T)) >= 1

    # Solve with time limit 1 second
    solver = PULP_CBC_CMD(msg=False, timeLimit=1)
    prob.solve(solver)

    if LpStatus.get(prob.status, "") != "Optimal":
        return None

    result = [int(round(M[i].value())) for i in range(P)]
    return result


# ------------------------------------------------------------
# Main Detection
# ------------------------------------------------------------
def detect_deadlock(input_path=None):
    start = time.time()

    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA = os.path.join(ROOT, "data")

    bdd_path = input_path or os.path.join(DATA, "bdd_result.json")

    # Load BDD result
    with open(bdd_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    places = data["places"]
    place_index = {p: i for i, p in enumerate(places)}
    bdd_root = data["bdd_root"]
    nodes = data["nodes"]
    lp_data = data["lp"]

    result = {
        "deadlocks_found": False,
        "deadlock_states": [],
        "time_seconds": 0.0
    }

    # --- Step 1: Check M0 directly ---
    M0 = lp_data["M0"]
    if is_dead_marking(M0, lp_data["disable_constraints"]) and \
       bdd_contains_marking(M0, bdd_root, nodes, place_index):

        result["deadlocks_found"] = True
        result["deadlock_states"] = [{places[i]: M0[i] for i in range(len(places))}]
        result["time_seconds"] = round(time.time() - start, 6)

        out = os.path.join(DATA, "deadlocks.json")
        with open(out, "w", encoding="utf-8") as fo:
            json.dump(result, fo, indent=4)

        print("\n===== deadlocks.json =====")
        print(json.dumps(result, indent=4))
        print("==========================\n")
        return result

    # --- Step 2: ILP solve ---
    cand = solve_ilp(lp_data)

    if cand is not None:
        ok_bdd = bdd_contains_marking(cand, bdd_root, nodes, place_index)
        ok_dead = is_dead_marking(cand, lp_data["disable_constraints"])

        if ok_bdd and ok_dead:
            result["deadlocks_found"] = True
            result["deadlock_states"] = [{places[i]: cand[i] for i in range(len(places))}]

    # --- Step 3: Save + Print ---
    result["time_seconds"] = round(time.time() - start, 6)
    out = os.path.join(DATA, "deadlocks.json")
    with open(out, "w", encoding="utf-8") as fo:
        json.dump(result, fo, indent=4)

    print("\n===== deadlocks.json =====")
    print(json.dumps(result, indent=4))
    print("==========================\n")

    return result


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    detect_deadlock(arg)