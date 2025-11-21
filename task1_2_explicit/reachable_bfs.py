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
        self.initial_marking = data["initial_marking"]

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def get_inputs(self, transition):
        """Return list of input places for a transition."""
        return [src for src, tgt in self.arcs if tgt == transition and src in self.places]

    def get_outputs(self, transition):
        """Return list of output places for a transition."""
        return [tgt for src, tgt in self.arcs if src == transition and tgt in self.places]

    # --------------------------------------------------
    # Firing rules
    # --------------------------------------------------
    def is_enabled(self, transition, marking):
        """
        Fix quan trọng:
        - Transition KHÔNG CÓ INPUT thì không thể enabled trong 1-safe PN.
        """
        inputs = self.get_inputs(transition)
        if len(inputs) == 0:
            return False  # dead transition

        for p in inputs:
            if marking.get(p, 0) == 0:
                return False
        return True

    def fire(self, transition, marking):
        new_marking = marking.copy()

        for p in self.get_inputs(transition):
            new_marking[p] -= 1

        for p in self.get_outputs(transition):
            new_marking[p] += 1

        return new_marking


# ------------------------------------------------------
# BFS enumeration
# ------------------------------------------------------
def bfs_reachability(net: PetriNet):

    start = net.initial_marking
    visited = set()
    queue = deque([start])
    reachable = []

    def marking_to_tuple(m):
        return tuple(m[p] for p in net.places)  # stable order

    while queue:
        current = queue.popleft()
        key = marking_to_tuple(current)

        if key in visited:
            continue

        visited.add(key)
        reachable.append(current)

        for t in net.transitions:
            if net.is_enabled(t, current):
                new_marking = net.fire(t, current)
                new_key = marking_to_tuple(new_marking)

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

    # Write JSON file manually for stable formatting
    lines = ['[']
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