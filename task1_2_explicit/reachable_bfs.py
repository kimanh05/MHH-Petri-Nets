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


class PetriNet:
    def __init__(self, data):
        self.places = data["places"]
        self.transitions = data["transitions"]
        self.arcs = data["arcs"]
        self.initial_marking = data["initial_marking"]

    # --- structure helpers ---
    def get_inputs(self, transition):
        """Return list of input places for a given transition."""
        return [src for src, tgt in self.arcs if tgt == transition and src in self.places]

    def get_outputs(self, transition):
        """Return list of output places for a given transition."""
        return [tgt for src, tgt in self.arcs if src == transition and tgt in self.places]

    # --- firing logic ---
    def is_enabled(self, transition, marking):
        """Return True if transition is enabled under given marking."""
        for p in self.get_inputs(transition):
            if marking.get(p, 0) == 0:
                return False
        return True

    def fire(self, transition, marking):
        """Fire transition and return new marking."""
        new_marking = marking.copy()
        for p in self.get_inputs(transition):
            new_marking[p] -= 1
        for p in self.get_outputs(transition):
            new_marking[p] += 1
        return new_marking


def bfs_reachability(net: PetriNet):
    """Enumerate all reachable markings via BFS."""
    start = net.initial_marking
    visited = set()
    queue = deque([start])
    reachable = []

    def marking_to_tuple(m):
        return tuple(m[p] for p in net.places)

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


if __name__ == "__main__":
    input_file = "net_structure.json"
    output_file = "reachable_markings.json"

    # --- read Petri net structure ---
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    net = PetriNet(data)

    # --- compute reachable markings ---
    reachable = bfs_reachability(net)

    # --- write output ---
    with open(output_file, "w", encoding="utf-8") as f:
        f.write('[\n')
        for i, m in enumerate(reachable):
            # convert dict -> "key: value" join lại thành 1 dòng
            one_line = "{" + ", ".join(f'"{k}": {v}' for k, v in m.items()) + "}"

            # thêm dấu phẩy nếu chưa phải phần tử cuối
            if i < len(reachable) - 1:
                f.write(f"    {one_line},\n")
            else:
                f.write(f"    {one_line}\n")
        f.write("]")

    print(f"Reachability analysis done! {len(reachable)} markings written to '{output_file}'.")

# run: python "C:\Users\ADMIN\Documents\Learning\UniDocs\Documents\HK251\MHH\Assigment 251\MHH-Petri-Nets-main\task1_2_explicit\reachable_bfs.py"