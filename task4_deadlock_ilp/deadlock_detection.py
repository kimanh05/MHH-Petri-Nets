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
from pulp import LpProblem, LpVariable, lpSum, LpInteger, LpMinimize, LpStatus

# -------------------------
# BDD membership evaluator
# -------------------------
def bdd_contains_marking(marking_vector, bdd_root, nodes, place_index):
    """Return True if marking_vector (list of 0/1) maps to terminal 1 in the ROBDD."""
    current = str(bdd_root)
    try:
        while True:
            node = nodes[current]
            if "terminal" in node:
                return int(node["terminal"]) == 1
            var = node["var"]
            low = str(node["low"])
            high = str(node["high"])
            # ensure bit is int 0/1
            bit = int(marking_vector[place_index[var]])
            current = high if bit == 1 else low
    except KeyError:
        # malformed BDD or mapping — treat as not contained
        return False

# -------------------------
# Deadness predicate
# -------------------------
def is_dead_marking(marking_vector, disable_constraints):
    """A marking is dead iff for every transition, at least one pre-place is 0."""
    for item in disable_constraints:
        pre = item.get("pre_places", [])
        if sum(int(marking_vector[p]) for p in pre) > len(pre) - 1:
            return False
    return True

# -------------------------
# ILP solver (improved)
# -------------------------
def solve_ILP_dead_marking(lp_data, require_fire=True):
    """
    Solve ILP:
      M = M0 + C*x
      M in {0,1}
      disable constraints (for each transition)
      optionally require sum(x) >= 1
    Objective: minimize sum(x)
    Returns: list<int> marking or None
    """
    places = lp_data["places"]
    transitions = lp_data["transitions"]
    C = lp_data["C"]
    M0 = lp_data["M0"]
    x_low = lp_data["x_bounds"]["lower"]
    x_up = lp_data["x_bounds"]["upper"]
    disable_constraints = lp_data["disable_constraints"]

    P = len(places)
    T = len(transitions)

    prob = LpProblem("DeadlockDetection", LpMinimize)

    # Variables
    x = [LpVariable(f"x_{j}", lowBound=x_low, upBound=x_up, cat=LpInteger) for j in range(T)]
    M = [LpVariable(f"M_{i}", lowBound=0, upBound=1, cat=LpInteger) for i in range(P)]

    # Objective: prefer small firing sequences
    prob += lpSum(x[j] for j in range(T))

    # State equations
    for i in range(P):
        prob += M[i] == M0[i] + lpSum((C[i][j] if j < len(C[i]) else 0) * x[j] for j in range(T))

    # Disable constraints
    for item in disable_constraints:
        pre_places = item.get("pre_places", [])
        prob += lpSum(M[p] for p in pre_places) <= max(0, len(pre_places) - 1)

    # Force at least one transition fired if requested (avoid trivial zero solution)
    if require_fire and T > 0:
        prob += lpSum(x[j] for j in range(T)) >= 1

    status_code = prob.solve()
    # robust status check
    if LpStatus.get(prob.status, "Unknown") != "Optimal":
        return None

    # Extract integer marking values safely
    marking = []
    for i in range(P):
        val = M[i].value()
        if val is None:
            return None
        marking.append(int(round(val)))
    return marking

# -------------------------
# Main detection logic
# -------------------------
def detect_deadlock(input_path=None):
    start_time = time.time()

    # resolve paths relative to script dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if input_path is None:
        bdd_path = os.path.join(script_dir, "data", "bdd_result.json")
    else:
        bdd_path = input_path

    if not os.path.exists(bdd_path):
        raise FileNotFoundError(f"Input file not found: {bdd_path}")

    with open(bdd_path, "r") as f:
        data = json.load(f)

    places = data.get("places", [])
    place_index = {p: i for i, p in enumerate(places)}
    bdd_root = data.get("bdd_root")
    nodes = data.get("nodes", {})
    lp_data = data.get("lp", {})

    result = {"deadlocks_found": False, "deadlock_states": [], "time_seconds": 0.0}

    # Fast path: if M0 is dead and reachable -> return it
    M0 = lp_data.get("M0", [])
    if M0 and is_dead_marking(M0, lp_data.get("disable_constraints", [])):
        if bdd_contains_marking(M0, bdd_root, nodes, place_index):
            result["deadlocks_found"] = True
            result["deadlock_states"].append({places[i]: int(M0[i]) for i in range(len(places))})
            result["time_seconds"] = round(time.time() - start_time, 6)
            out_path = os.path.join(script_dir, "data", "deadlocks.json")
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w") as fo:
                json.dump(result, fo, indent=4)
            print("Initial marking is reachable deadlock -> saved:", out_path)
            return result

    # Otherwise solve ILP requiring at least one firing to find a reachable dead marking
    candidate = solve_ILP_dead_marking(lp_data, require_fire=True)
    if candidate is None:
        result["deadlocks_found"] = False
    else:
        if bdd_contains_marking(candidate, bdd_root, nodes, place_index) and is_dead_marking(candidate, lp_data.get("disable_constraints", [])):
            result["deadlocks_found"] = True
            result["deadlock_states"].append({places[i]: int(candidate[i]) for i in range(len(places))})
        else:
            result["deadlocks_found"] = False

    result["time_seconds"] = round(time.time() - start_time, 6)
    out_path = os.path.join(script_dir, "data", "deadlocks.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as fo:
        json.dump(result, fo, indent=4)

    print("Task 4 completed ->", out_path)
    return result

if __name__ == "__main__":
    # optional CLI arg: path to bdd_result.json
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    detect_deadlock(arg)
