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
from collections import deque
import os


class PetriNet:
    def __init__(self, data):
        self.places = data["places"]
        self.transitions = data["transitions"]
        self.arcs = data["arcs"]

        # FIX: convert marking to int (critical!)
        self.initial_marking = {k: int(v) for k, v in data["initial_marking"].items()}

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def get_inputs(self, transition):
        """List of input places for transition."""
        return [src for src, tgt in self.arcs if tgt == transition and src in self.places]

    def get_outputs(self, transition):
        """List of output places for transition."""
        return [tgt for src, tgt in self.arcs if src == transition and tgt in self.places]

    # --------------------------------------------------
    # 1-SAFE FIRING RULE
    # --------------------------------------------------
    def is_enabled(self, transition, marking):
        """
        1-safe firing rules:
        ✔ Transition must have at least 1 input
        ✔ All input places must contain token = 1
        ✔ All output places must be empty (0)
        """

        inputs = self.get_inputs(transition)
        outputs = self.get_outputs(transition)

        # Rule 1: Must have input
        if len(inputs) == 0:
            return False

        # Rule 2: All input places must contain token
        for p in inputs:
            if int(marking.get(p, 0)) == 0:
                return False

        # Rule 3: All output places must be empty
        for p in outputs:
            if int(marking.get(p, 0)) == 1:
                return False

        return True

    def fire(self, transition, marking):
        """Fire transition under 1-safe assumption."""
        new_marking = marking.copy()

        # Consume tokens
        for p in self.get_inputs(transition):
            new_marking[p] = 0

        # Produce tokens (always safe)
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
    reachable = bfs_reachability(net)

    # Write JSON with stable formatting
    lines = ["["]
    for i, m in enumerate(reachable):
        line = "{" + ", ".join(f'"{k}": {v}' for k, v in m.items()) + "}"
        if i < len(reachable) - 1:
            lines.append(f"    {line},")
        else:
            lines.append(f"    {line}")
    lines.append("]")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n".join(lines))