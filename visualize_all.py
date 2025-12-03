"""
visualize_all.py
----------------
Generate various Graphviz DOT visualizations for the Petri net project,
EXCEPT BDD VISUALIZATION (REMOVED FOR SAFETY).

Outputs (all into visualization/):
- petrinet.dot           : Petri net structure
- reachable_graph.dot    : State space graph
- incidence.dot          : Incidence matrix C
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

# ------------------------------------------------------
# Helper to support both old/new Task 2 formats
# ------------------------------------------------------
def extract_reachable(data):
    if isinstance(data, dict) and "reachable_markings" in data:
        return data["reachable_markings"]
    return data

# ------------------------------------------------------
# 1. Petri net structure visualization
# ------------------------------------------------------
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

    for p in places:
        tokens = init_marking.get(p, 0)
        label = f"{p}" + (f" ({tokens})" if tokens else "")
        lines.append(f'    "{p}" [shape=circle, label="{label}"];')

    for t in transitions:
        lines.append(f'    "{t}" [shape=box, style=filled, fillcolor="#eeeeee"];')

    for src, tgt in arcs:
        lines.append(f'    "{src}" -> "{tgt}";')

    lines.append("}")

    out_path = os.path.join(VIZ, "petrinet.dot")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[PetriNet] DOT written to {out_path}")

# ------------------------------------------------------
# Helper class for reachable graph
# ------------------------------------------------------
class PetriNetSemantics:
    def __init__(self, net):
        self.places = net["places"]
        self.transitions = net["transitions"]
        self.arcs = net["arcs"]

    def get_inputs(self, t):
        return [p for p, x in self.arcs if x == t]

    def get_outputs(self, t):
        return [x for p, x in self.arcs if p == t]

    def is_enabled(self, t, marking):
        return all(marking.get(p, 0) == 1 for p in self.get_inputs(t))

    def fire(self, t, marking):
        m2 = dict(marking)
        for p in self.get_inputs(t):
            m2[p] -= 1
        for q in self.get_outputs(t):
            m2[q] += 1
        return m2

def marking_key(m, places):
    return tuple(m.get(p, 0) for p in places)

# ------------------------------------------------------
# 2. Reachable graph visualization
# ------------------------------------------------------
def visualize_reachable_graph():
    net_path = os.path.join(DATA, "net_structure.json")
    reach_path = os.path.join(DATA, "reachable_markings.json")

    if not (os.path.exists(net_path) and os.path.exists(reach_path)):
        print("[Reachable] required files missing, skip.")
        return

    net = jload(net_path)
    reachable = extract_reachable(jload(reach_path))

    places = net["places"]
    sem = PetriNetSemantics(net)

    key_to_id = {}
    id_to_mark = {}

    for idx, m in enumerate(reachable):
        key = marking_key(m, places)
        key_to_id[key] = f"M{idx}"
        id_to_mark[f"M{idx}"] = m

    edges = []
    for m in reachable:
        src = key_to_id[marking_key(m, places)]
        for t in net["transitions"]:
            if sem.is_enabled(t, m):
                m2 = sem.fire(t, m)
                key2 = marking_key(m2, places)
                if key2 in key_to_id:
                    edges.append((src, key_to_id[key2], t))

    lines = []
    lines.append("digraph Reachable {")
    lines.append("    rankdir=LR;")

    for nid, m in id_to_mark.items():
        label = f"{nid}\\n" + ", ".join(f"{p}={m[p]}" for p in places)
        style = 'style=filled, fillcolor="#ccffcc"' if nid == "M0" else ""
        lines.append(f'    {nid} [label="{label}" {style}];')

    for s, t, tr in edges:
        lines.append(f'    {s} -> {t} [label="{tr}"];')

    lines.append("}")

    out_path = os.path.join(VIZ, "reachable_graph.dot")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[Reachable] DOT written to {out_path}")

# ------------------------------------------------------
# 3. Incidence Matrix Visualization
# ------------------------------------------------------
def visualize_incidence():
    bdd_path = os.path.join(DATA, "bdd_result.json")
    if not os.path.exists(bdd_path):
        print("[Incidence] bdd_result.json not found, skip.")
        return

    bdd = jload(bdd_path)
    lp = bdd["lp"]
    places = lp["places"]
    transitions = lp["transitions"]
    C = lp["C"]

    lines = []
    lines.append("digraph Incidence {")
    lines.append("    node [shape=plaintext];")
    lines.append("    incidence_table [label=<")
    lines.append("    <table border='1' cellborder='1' cellspacing='0'>")

    header = "<tr><td></td>" + "".join(f"<td>{t}</td>" for t in transitions) + "</tr>"
    lines.append(header)

    for i, p in enumerate(places):
        row = f"<tr><td>{p}</td>" + "".join(f"<td>{C[i][j]}</td>" for j in range(len(transitions))) + "</tr>"
        lines.append(row)

    lines.append("    </table>")
    lines.append("    >];")
    lines.append("}")

    out_path = os.path.join(VIZ, "incidence.dot")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[Incidence] DOT written to {out_path}")

# ------------------------------------------------------
# 4. Deadlock visualization
# ------------------------------------------------------
def visualize_deadlock_graph():
    net_path = os.path.join(DATA, "net_structure.json")
    reach_path = os.path.join(DATA, "reachable_markings.json")
    dead_path = os.path.join(DATA, "deadlocks.json")

    if not (os.path.exists(net_path) and os.path.exists(reach_path) and os.path.exists(dead_path)):
        print("[Deadlock] required files missing, skip.")
        return

    net = jload(net_path)
    reachable = extract_reachable(jload(reach_path))
    deadlocks = jload(dead_path)

    places = net["places"]
    sem = PetriNetSemantics(net)

    key_to_id = {}
    id_to_mark = {}
    for idx, m in enumerate(reachable):
        key = marking_key(m, places)
        nid = f"M{idx}"
        key_to_id[key] = nid
        id_to_mark[nid] = m

    dead_keys = {marking_key(m, places) for m in deadlocks.get("deadlock_states", [])}
    dead_ids = {key_to_id[k] for k in dead_keys if k in key_to_id}

    edges = []
    for m in reachable:
        src = key_to_id[marking_key(m, places)]
        for t in net["transitions"]:
            if sem.is_enabled(t, m):
                m2 = sem.fire(t, m)
                k2 = marking_key(m2, places)
                if k2 in key_to_id:
                    edges.append((src, key_to_id[k2], t))

    lines = []
    lines.append("digraph Deadlocks {")
    lines.append("    rankdir=LR;")

    for nid, m in id_to_mark.items():
        label = f"{nid}\\n" + ", ".join(f"{p}={m[p]}" for p in places)
        if nid in dead_ids:
            style = 'style=filled, fillcolor="#ffcccc"'
        elif nid == "M0":
            style = 'style=filled, fillcolor="#ccffcc"'
        else:
            style = ""
        lines.append(f'    {nid} [label="{label}" {style}];')

    for s, t, tr in edges:
        lines.append(f'    {s} -> {t} [label="{tr}"];')

    lines.append("}")

    out_path = os.path.join(VIZ, "deadlock_graph.dot")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[Deadlock] DOT written to {out_path}")

# ------------------------------------------------------
# 5. Optimization visualization
# ------------------------------------------------------
def visualize_optimization():
    net_path = os.path.join(DATA, "net_structure.json")
    reach_path = os.path.join(DATA, "reachable_markings.json")
    opt_path = os.path.join(DATA, "optimization_result.json")

    if not (os.path.exists(net_path) and os.path.exists(reach_path) and os.path.exists(opt_path)):
        print("[Optimization] required files missing, skip.")
        return

    net = jload(net_path)
    reachable = extract_reachable(jload(reach_path))
    opt = jload(opt_path)

    places = net["places"]
    best_keys = {marking_key(m, places) for m in opt.get("best_marking", [])}

    key_to_id = {marking_key(m, places): f"M{i}" for i, m in enumerate(reachable)}

    lines = []
    lines.append("digraph Optimization {")
    lines.append("    rankdir=LR;")

    for key, nid in key_to_id.items():
        m = reachable[int(nid[1:])]
        label = f"{nid}\\n" + ", ".join(f"{p}={m[p]}" for p in places)
        if key in best_keys:
            style = 'style=filled, fillcolor="#fff2a8"'
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

# ------------------------------------------------------
# Main (NO BDD VISUALIZATION)
# ------------------------------------------------------
if __name__ == "__main__":
    print("=== Generating visualizations (without BDD) ===")
    visualize_petrinet()
    visualize_reachable_graph()
    visualize_incidence()
    # visualize_bdd_basic_and_path()   <-- REMOVED
    visualize_deadlock_graph()
    visualize_optimization()
    print("=== Done. ===")
