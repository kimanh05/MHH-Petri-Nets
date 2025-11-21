"""
visualize_all.py
----------------
Generate various Graphviz DOT visualizations for the Petri net project.

Requires that the pipeline has already produced:
- data/net_structure.json
- data/reachable_markings.json
- data/bdd_result.json
- data/deadlocks.json         (from Task 4, if any)
- data/optimization_result.json (from Task 5)

Outputs (all into visualization/):
- petrinet.dot           : Petri net structure
- reachable_graph.dot    : State space / reachable markings graph
- incidence.dot          : Incidence matrix C
- bdd.dot                : Raw BDD
- bdd_path_M0.dot        : BDD with highlighted path for M0
- deadlock_graph.dot     : Reachable graph with deadlocks highlighted
- optimization.dot       : Reachable graph with best markings highlighted
"""

import json
import os


ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
VIZ = os.path.join(ROOT, "visualization")
os.makedirs(VIZ, exist_ok=True)


def jload(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 1. Petri net structure visualization
# ---------------------------------------------------------------------------
def visualize_petrinet():
    net_path = os.path.join(DATA, "net_structure.json")
    if not os.path.exists(net_path):
        print("[PetriNet] net_structure.json not found, skip.")
        return

    net = jload(net_path)
    places = net["places"]
    transitions = net["transitions"]
    arcs = net["arcs"]
    init_marking = net.get("initial_marking", {})

    lines = []
    lines.append("digraph PetriNet {")
    lines.append("    rankdir=LR;")
    lines.append("    node [fontsize=12];")

    # Places as circles
    for p in places:
        tokens = init_marking.get(p, 0)
        label = f"{p}"
        if tokens != 0:
            label += f" ({tokens})"
        lines.append(f'    "{p}" [shape=circle, label="{label}"];')

    # Transitions as boxes
    for t in transitions:
        lines.append(f'    "{t}" [shape=box, style=filled, fillcolor="#eeeeee"];')

    # Arcs
    for src, tgt in arcs:
        lines.append(f'    "{src}" -> "{tgt}";')

    lines.append("}")

    out_path = os.path.join(VIZ, "petrinet.dot")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[PetriNet] DOT written to {out_path}")


# ---------------------------------------------------------------------------
# Helper: Petri net firing semantics for reachable graph
# ---------------------------------------------------------------------------
class PetriNetSemantics:
    def __init__(self, net_data):
        self.places = net_data["places"]
        self.transitions = net_data["transitions"]
        self.arcs = net_data["arcs"]
        self.initial_marking = net_data["initial_marking"]

    def get_inputs(self, t):
        return [src for src, tgt in self.arcs
                if tgt == t and src in self.places]

    def get_outputs(self, t):
        return [tgt for src, tgt in self.arcs
                if src == t and tgt in self.places]

    def is_enabled(self, t, marking):
        for p in self.get_inputs(t):
            if marking.get(p, 0) == 0:
                return False
        return True

    def fire(self, t, marking):
        new_marking = dict(marking)
        for p in self.get_inputs(t):
            new_marking[p] -= 1
        for p in self.get_outputs(t):
            new_marking[p] += 1
        return new_marking


def marking_key(m, places):
    """Convert marking dict -> tuple in fixed order (for dict keys)."""
    return tuple(m.get(p, 0) for p in places)


# ---------------------------------------------------------------------------
# 2. Reachable graph (state space)
# ---------------------------------------------------------------------------
def visualize_reachable_graph():
    net_path = os.path.join(DATA, "net_structure.json")
    reach_path = os.path.join(DATA, "reachable_markings.json")
    if not (os.path.exists(net_path) and os.path.exists(reach_path)):
        print("[Reachable] net_structure or reachable_markings missing, skip.")
        return

    net_data = jload(net_path)
    reachable = jload(reach_path)
    pn = PetriNetSemantics(net_data)
    places = pn.places

    # Map marking -> node id
    key_to_id = {}
    id_to_mark = {}
    for idx, m in enumerate(reachable):
        key = marking_key(m, places)
        nid = f"M{idx}"
        key_to_id[key] = nid
        id_to_mark[nid] = m

    # Build edges by trying to fire transitions
    edges = []
    for idx, m in enumerate(reachable):
        key = marking_key(m, places)
        src_id = key_to_id[key]
        for t in pn.transitions:
            if pn.is_enabled(t, m):
                m2 = pn.fire(t, m)
                k2 = marking_key(m2, places)
                if k2 in key_to_id:
                    dst_id = key_to_id[k2]
                    edges.append((src_id, dst_id, t))

    # Write DOT
    lines = []
    lines.append("digraph Reachable {")
    lines.append("    rankdir=LR;")
    lines.append("    node [shape=ellipse, fontsize=10];")

    # Nodes with marking labels
    for nid, m in id_to_mark.items():
        label_parts = [f"{p}={m.get(p,0)}" for p in places]
        label = f"{nid}\\n" + ", ".join(label_parts)
        # initial marking = green
        style = 'style=filled, fillcolor="#ccffcc"' if nid == "M0" else ""
        lines.append(f'    {nid} [label="{label}" {style}];')

    # Edges with transition labels
    for src, dst, t in edges:
        lines.append(f'    {src} -> {dst} [label="{t}"];')

    lines.append("}")

    out_path = os.path.join(VIZ, "reachable_graph.dot")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[Reachable] DOT written to {out_path}")


# ---------------------------------------------------------------------------
# 3. Incidence matrix visualization (from BDD lp.C)
# ---------------------------------------------------------------------------
def visualize_incidence():
    bdd_path = os.path.join(DATA, "bdd_result.json")
    if not os.path.exists(bdd_path):
        print("[Incidence] bdd_result.json not found, skip.")
        return

    bdd = jload(bdd_path)
    lp = bdd.get("lp", {})
    places = lp.get("places", [])
    transitions = lp.get("transitions", [])
    C = lp.get("C", [])

    lines = []
    lines.append("digraph Incidence {")
    lines.append('    node [shape=plaintext];')
    lines.append('    incidence_table [label=<')
    lines.append('    <table border="1" cellborder="1" cellspacing="0" cellpadding="4">')

    # Header row
    header = "      <tr><td></td>"
    for t in transitions:
        header += f"<td><b>{t}</b></td>"
    header += "</tr>"
    lines.append(header)

    # Rows
    for i, p in enumerate(places):
        row = f"      <tr><td><b>{p}</b></td>"
        for j in range(len(transitions)):
            val = C[i][j] if i < len(C) and j < len(C[i]) else 0
            row += f"<td>{val}</td>"
        row += "</tr>"
        lines.append(row)

    lines.append("    </table>")
    lines.append("    >];")
    lines.append("}")

    out_path = os.path.join(VIZ, "incidence.dot")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[Incidence] DOT written to {out_path}")


# ---------------------------------------------------------------------------
# 4. BDD visualization (basic + path for M0)
# ---------------------------------------------------------------------------
def visualize_bdd_basic_and_path():
    bdd_path = os.path.join(DATA, "bdd_result.json")
    if not os.path.exists(bdd_path):
        print("[BDD] bdd_result.json not found, skip.")
        return

    data = jload(bdd_path)
    nodes = data["nodes"]
    root = str(data["bdd_root"])
    lp = data.get("lp", {})
    M0 = lp.get("M0", [])
    places = lp.get("places", [])

    # -------- basic BDD --------
    lines = []
    lines.append("digraph BDD {")
    lines.append("    rankdir=TB;")
    lines.append("    node [shape=circle, fontsize=12];")

    for nid, node in nodes.items():
        if "terminal" in node:
            label = node["terminal"]
            lines.append(f'    {nid} [label="{label}", shape=box];')
        else:
            label = node["var"]
            lines.append(f'    {nid} [label="{label}"];')

    for nid, node in nodes.items():
        if "terminal" in node:
            continue
        low = node["low"]
        high = node["high"]
        lines.append(f'    {nid} -> {low} [label="0", color="blue"];')
        lines.append(f'    {nid} -> {high} [label="1", color="red"];')

    lines.append("}")
    out_basic = os.path.join(VIZ, "bdd.dot")
    with open(out_basic, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[BDD] Basic DOT written to {out_basic}")

    # -------- path for M0 --------
    if not M0 or not places:
        print("[BDD] No M0/places in lp, skip path highlight.")
        return

    # compute marking bits dict: place -> 0/1
    bits = {places[i]: int(M0[i]) for i in range(len(places))}

    path_edges = set()
    current = root
    visited = set()
    while True:
        if current in visited:
            break  # avoid cycles if malformed
        visited.add(current)
        node = nodes[str(current)]
        if "terminal" in node:
            break
        var = node["var"]
        bit = bits.get(var, 0)
        low = str(node["low"])
        high = str(node["high"])
        nxt = high if bit == 1 else low
        path_edges.add((str(current), nxt))
        current = nxt

    lines = []
    lines.append("digraph BDD_M0 {")
    lines.append("    rankdir=TB;")
    lines.append("    node [shape=circle, fontsize=12];")

    for nid, node in nodes.items():
        if "terminal" in node:
            label = node["terminal"]
            lines.append(f'    {nid} [label="{label}", shape=box];')
        else:
            label = node["var"]
            lines.append(f'    {nid} [label="{label}"];')

    for nid, node in nodes.items():
        if "terminal" in node:
            continue
        low = str(node["low"])
        high = str(node["high"])

        e_low = (nid, low)
        e_high = (nid, high)

        if e_low in path_edges:
            attr = 'color="blue", penwidth=3'
        else:
            attr = 'color="blue"'
        lines.append(f'    {nid} -> {low} [label="0", {attr}];')

        if e_high in path_edges:
            attr = 'color="red", penwidth=3'
        else:
            attr = 'color="red"'
        lines.append(f'    {nid} -> {high} [label="1", {attr}];')

    lines.append("}")
    out_path = os.path.join(VIZ, "bdd_path_M0.dot")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[BDD] M0-path DOT written to {out_path}")


# ---------------------------------------------------------------------------
# 5. Deadlock visualization on reachable graph
# ---------------------------------------------------------------------------
def visualize_deadlock_graph():
    net_path = os.path.join(DATA, "net_structure.json")
    reach_path = os.path.join(DATA, "reachable_markings.json")
    dead_path = os.path.join(DATA, "deadlocks.json")

    if not (os.path.exists(net_path) and os.path.exists(reach_path) and os.path.exists(dead_path)):
        print("[Deadlock] Required files missing, skip.")
        return

    net_data = jload(net_path)
    reachable = jload(reach_path)
    deadlocks = jload(dead_path)

    pn = PetriNetSemantics(net_data)
    places = pn.places

    key_to_id = {}
    id_to_mark = {}
    for idx, m in enumerate(reachable):
        key = marking_key(m, places)
        nid = f"M{idx}"
        key_to_id[key] = nid
        id_to_mark[nid] = m

    # build edges
    edges = []
    for idx, m in enumerate(reachable):
        key = marking_key(m, places)
        src_id = key_to_id[key]
        for t in pn.transitions:
            if pn.is_enabled(t, m):
                m2 = pn.fire(t, m)
                k2 = marking_key(m2, places)
                if k2 in key_to_id:
                    dst_id = key_to_id[k2]
                    edges.append((src_id, dst_id, t))

    # set of deadlock markings
    dead_states = set()
    for dm in deadlocks.get("deadlock_states", []):
        key = marking_key(dm, places)
        if key in key_to_id:
            dead_states.add(key_to_id[key])

    lines = []
    lines.append("digraph Deadlocks {")
    lines.append("    rankdir=LR;")
    lines.append("    node [shape=ellipse, fontsize=10];")

    for nid, m in id_to_mark.items():
        label_parts = [f"{p}={m.get(p,0)}" for p in places]
        label = f"{nid}\\n" + ", ".join(label_parts)

        if nid == "M0":
            style = 'style=filled, fillcolor="#ccffcc"'
        elif nid in dead_states:
            style = 'style=filled, fillcolor="#ffcccc"'
        else:
            style = ""

        lines.append(f'    {nid} [label="{label}" {style}];')

    for src, dst, t in edges:
        lines.append(f'    {src} -> {dst} [label="{t}"];')

    lines.append("}")
    out_path = os.path.join(VIZ, "deadlock_graph.dot")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[Deadlock] DOT written to {out_path}")


# ---------------------------------------------------------------------------
# 6. Optimization result visualization
# ---------------------------------------------------------------------------
def visualize_optimization():
    net_path = os.path.join(DATA, "net_structure.json")
    reach_path = os.path.join(DATA, "reachable_markings.json")
    opt_path = os.path.join(DATA, "optimization_result.json")

    if not (os.path.exists(net_path) and os.path.exists(reach_path) and os.path.exists(opt_path)):
        print("[Optimization] Required files missing, skip.")
        return

    net_data = jload(net_path)
    reachable = jload(reach_path)
    opt = jload(opt_path)

    places = net_data["places"]
    best_list = opt.get("best_marking", [])
    best_keys = set(marking_key(m, places) for m in best_list)

    # Map markings to IDs
    key_to_id = {}
    id_to_mark = {}
    for idx, m in enumerate(reachable):
        key = marking_key(m, places)
        nid = f"M{idx}"
        key_to_id[key] = nid
        id_to_mark[nid] = m

    lines = []
    lines.append("digraph Optimization {")
    lines.append("    rankdir=LR;")
    lines.append("    node [shape=ellipse, fontsize=10];")

    for nid, m in id_to_mark.items():
        label_parts = [f"{p}={m.get(p,0)}" for p in places]
        label = f"{nid}\\n" + ", ".join(label_parts)

        key = marking_key(m, places)
        if key in best_keys:
            style = 'style=filled, fillcolor="#fff2a8"'   # yellow-ish
        elif nid == "M0":
            style = 'style=filled, fillcolor="#ccffcc"'
        else:
            style = ""

        lines.append(f'    {nid} [label="{label}" {style}];')

    lines.append("}")
    out_path = os.path.join(VIZ, "optimization.dot")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[Optimization] DOT written to {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Generating all visualizations into /visualization ===")
    visualize_petrinet()
    visualize_reachable_graph()
    visualize_incidence()
    visualize_bdd_basic_and_path()
    visualize_deadlock_graph()
    visualize_optimization()
    print("=== Done. Open .dot files with Graphviz Interactive Preview in VSCode. ===")
