"""
Task 2 – Explicit Computation of Reachable Markings
---------------------------------------------------
Description:
    Reads a Petri net from net_structure.json (output of Task 1)
    and performs a breadth-first search (BFS) to enumerate all
    reachable markings from the initial marking.

Input:
    net_structure.json
Output:
    reachable_markings.json
Author:
    Vinh Tien
"""

import json
import time
from collections import deque
import os


class PetriNet:
    def __init__(self, data):
        self.places = data["places"]
        self.transitions = data["transitions"]
        self.arcs = data["arcs"]

        # Convert marking values to int
        self.initial_marking = {k: int(v) for k, v in data["initial_marking"].items()}

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def get_inputs(self, transition):
        return [src for src, tgt in self.arcs if tgt == transition and src in self.places]

    def get_outputs(self, transition):
        return [tgt for src, tgt in self.arcs if src == transition and tgt in self.places]

    # --------------------------------------------------
    # 1-SAFE FIRING RULE
    # --------------------------------------------------
    def is_enabled(self, transition, marking):
        inputs = self.get_inputs(transition)
        outputs = self.get_outputs(transition)

        if len(inputs) == 0:
            return False

        for p in inputs:
            if int(marking.get(p, 0)) == 0:
                return False

        for p in outputs:
            if int(marking.get(p, 0)) == 1:
                return False

        return True

    def fire(self, transition, marking):
        new_marking = marking.copy()

        for p in self.get_inputs(transition):
            new_marking[p] = 0

        for p in self.get_outputs(transition):
            new_marking[p] = 1

        return new_marking


# ------------------------------------------------------
# BFS enumeration
# ------------------------------------------------------
def bfs_reachability(net: PetriNet):

    start = net.initial_marking
    visited = set()
    queue = deque([start])
    reachable = []

    def marking_key(m):
        return tuple(m[p] for p in net.places)

    while queue:
        current = queue.popleft()
        key = marking_key(current)

        if key in visited:
            continue

        visited.add(key)
        reachable.append(current)

        for t in net.transitions:
            if net.is_enabled(t, current):
                new_marking = net.fire(t, current)
                new_key = marking_key(new_marking)

                if new_key not in visited:
                    queue.append(new_marking)

    return reachable


# ------------------------------------------------------
# Main script
# ------------------------------------------------------
if __name__ == "__main__":

    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA = os.path.join(ROOT, "data")

    input_file = os.path.join(DATA, "net_structure.json")
    output_file = os.path.join(DATA, "reachable_markings.json")

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    net = PetriNet(data)

    # === Measure time ===
    t0 = time.perf_counter()
    reachable = bfs_reachability(net)
    build_time = round(time.perf_counter() - t0, 6)

    # Prepare final output dictionary
    output_data = {
        "reachable_markings": reachable,
        "num_markings": len(reachable),
        "build_time_seconds": build_time
    }

    # Write JSON nicely
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    print(json.dumps(output_data, indent=4))
