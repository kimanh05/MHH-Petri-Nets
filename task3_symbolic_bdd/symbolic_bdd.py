"""
Task 3 – Symbolic Computation of Reachable Markings using BDD
--------------------------------------------------------------
Description:
    Encodes reachable markings symbolically using Binary Decision Diagrams (BDDs).
    Constructs the reachability set iteratively via symbolic image computation.
    Returns a BDD representing the set of all reachable markings and reports
    the total number of markings and BDD nodes.

Input:
    data/reachable_markings.json

Output:
    data/bdd_result.json

Author:
    Kim Anh - Thao Ngoc
                                         
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import os
import argparse
from typing import Dict, List, Optional, Set

# =========================== Utility ===========================

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================== BDD ===========================

class BDD:
    def __init__(self, var_order: List[str]):
        self.var_order = var_order
        self.var_to_idx = {v: i for i, v in enumerate(var_order)}
        self.nodes = [(None, None, None), (None, None, None)]
        self.unique = {}

        self.cache = {}

    def mk(self, var: str, low: int, high: int) -> int:
        if low == high:
            return low
        key = (var, low, high)
        if key in self.unique:
            return self.unique[key]
        idx = len(self.nodes)
        self.unique[key] = idx
        self.nodes.append((self.var_to_idx[var], low, high))
        return idx

    def apply_and(self, u1: int, u2: int) -> int:
        if u1 > u2:
            u1, u2 = u2, u1

        key = ("and", u1, u2)
        if key in self.cache:
            return self.cache[key]

        if u1 == 0 or u2 == 0:
            return 0
        if u1 == 1:
            return u2
        if u2 == 1:
            return u1

        v1, l1, h1 = self.nodes[u1]
        v2, l2, h2 = self.nodes[u2]

        if v1 == v2:
            low = self.apply_and(l1, l2)
            high = self.apply_and(h1, h2)
            res = self.mk(self.var_order[v1], low, high)
        elif v1 < v2:
            low = self.apply_and(l1, u2)
            high = self.apply_and(h1, u2)
            res = self.mk(self.var_order[v1], low, high)
        else:
            low = self.apply_and(u1, l2)
            high = self.apply_and(u1, h2)
            res = self.mk(self.var_order[v2], low, high)

        self.cache[key] = res
        return res

    def apply_or(self, u1: int, u2: int) -> int:
        if u1 > u2:
            u1, u2 = u2, u1

        key = ("or", u1, u2)
        if key in self.cache:
            return self.cache[key]

        if u1 == 1 or u2 == 1:
            return 1
        if u1 == 0:
            return u2
        if u2 == 0:
            return u1

        v1, l1, h1 = self.nodes[u1]
        v2, l2, h2 = self.nodes[u2]

        if v1 == v2:
            low = self.apply_or(l1, l2)
            high = self.apply_or(h1, h2)
            res = self.mk(self.var_order[v1], low, high)
        elif v1 < v2:
            low = self.apply_or(l1, u2)
            high = self.apply_or(h1, u2)
            res = self.mk(self.var_order[v1], low, high)
        else:
            low = self.apply_or(u1, l2)
            high = self.apply_or(u1, h2)
            res = self.mk(self.var_order[v2], low, high)

        self.cache[key] = res
        return res


    def cube_from_marking(self, marking: Dict[str, int], over_vars: List[str]) -> int:
        res = 1
        for v in over_vars:
            if marking.get(v, 0) == 1:
                lit = self.mk(v, 0, 1)
                res = self.apply_and(res, lit)
        return res

    def exists(self, vars_to_eliminate: Set[str], u: int) -> int:
        if u <= 1:
            return u
        var_idx, low, high = self.nodes[u]
        var = self.var_order[var_idx]

        low_ = self.exists(vars_to_eliminate, low)
        high_ = self.exists(vars_to_eliminate, high)

        if var in vars_to_eliminate:
            return self.apply_or(low_, high_)
        return self.mk(var, low_, high_)

    def rename(self, u: int, mapping: Dict[str, str]) -> int:
        if u <= 1:
            return u
        var_idx, low, high = self.nodes[u]
        old_name = self.var_order[var_idx]
        new_name = mapping.get(old_name, old_name)

        low_ = self.rename(low, mapping)
        high_ = self.rename(high, mapping)
        return self.mk(new_name, low_, high_)

    @property
    def stats(self):
        return {
            "num_nodes": len(self.nodes),
            "cache": len(self.cache),
        }

# =========================== Helper Functions ===========================

def choose_var_order_from_markings(markings, user_order):
    if user_order:
        return user_order

    freq = {}
    for m in markings:
        for p, v in m.items():
            if v == 1:
                freq[p] = freq.get(p, 0) + 1

    return sorted(freq.keys(), key=lambda x: -freq[x])

def or_reduce_balanced(bdd, lst):
    if not lst:
        return 0
    while len(lst) > 1:
        new = []
        for i in range(0, len(lst), 2):
            if i + 1 < len(lst):
                new.append(bdd.apply_or(lst[i], lst[i + 1]))
            else:
                new.append(lst[i])
        lst = new
    return lst[0]

def derive_preset_postset(net):
    arcs = net.get("arcs", [])
    pre, post = {}, {}
    for (u, v) in arcs:
        if u in net["places"]:
            pre.setdefault(v, set()).add(u)
        else:
            post.setdefault(u, set()).add(v)
    return {"pre": pre, "post": post}

def build_T_relation(bdd, places, pre, post, next_suffix="'"):
    clauses = []
    for t in pre.keys() | post.keys():
        m = {}
        for p in places:
            if p in pre.get(t, set()):
                m[p] = 0
            elif p in post.get(t, set()):
                m[p + next_suffix] = 1
        clauses.append(bdd.cube_from_marking(m, over_vars=places + [p + next_suffix for p in places]))
    return or_reduce_balanced(bdd, clauses)

# =========================== EXPORT HELPERS ===========================

def export_bdd_nodes_dict(bdd: BDD) -> Dict[str, dict]:
    nodes_dict = {"0": {"terminal": 0}, "1": {"terminal": 1}}
    for nid in range(2, len(bdd.nodes)):
        var_idx, low, high = bdd.nodes[nid]
        vname = bdd.var_order[var_idx]
        nodes_dict[str(nid)] = {"var": vname, "low": low, "high": high}
    return nodes_dict

def build_incidence_and_lp(net_path: str, places_order: list, x_upper: int = 20):
    net = load_json(net_path)
    places = list(places_order)
    p_to_i = {p: i for i, p in enumerate(places)}

    arcs = net.get("arcs", [])
    trans_names = net.get("transitions")
    if not trans_names:
        Tset = set()
        for u, v in arcs:
            if u not in p_to_i:
                Tset.add(u)
            if v not in p_to_i:
                Tset.add(v)
        trans_names = sorted(Tset)

    t_to_j = {t: j for j, t in enumerate(trans_names)}

    pre = {t: set() for t in trans_names}
    post = {t: set() for t in trans_names}
    for u, v in arcs:
        if u in p_to_i and v in t_to_j:
            pre[v].add(u)
        elif u in t_to_j and v in p_to_i:
            post[u].add(v)

    C = [[0 for _ in trans_names] for _ in places]
    for t in trans_names:
        j = t_to_j[t]
        for p in pre[t]:
            C[p_to_i[p]][j] -= 1
        for p in post[t]:
            C[p_to_i[p]][j] += 1

    M0_src = net.get("initial_marking", {})
    M0 = [int(M0_src.get(p, 0)) for p in places]

    disable_constraints = []
    for t in trans_names:
        indices = sorted(p_to_i[p] for p in pre[t])
        disable_constraints.append({"transition": t, "pre_places": indices})

    return {
        "places": places,
        "transitions": trans_names,
        "C": C,
        "M0": M0,
        "x_bounds": {"lower": 0, "upper": x_upper},
        "disable_constraints": disable_constraints
    }

# =========================== MAIN MODES ===========================

def run_union_mode(inp_path: str, order: Optional[str], net_path_for_lp: str):
    markings = load_json(inp_path)

    uniq, seen = [], set()
    for m in markings:
        key = tuple(sorted((k, int(v)) for k, v in m.items()))
        if key not in seen:
            seen.add(key)
            uniq.append({k: int(v) for k, v in m.items()})

    user_order = [v.strip() for v in order.split(",")] if order else None
    var_order = choose_var_order_from_markings(uniq, user_order)

    bdd = BDD(var_order)
    cubes = [bdd.cube_from_marking(m, var_order) for m in uniq]
    F = or_reduce_balanced(bdd, cubes)

    result = {
        "num_markings": len(uniq),
        "bdd_nodes": len(bdd.nodes),
        "places": var_order,
        "build_time_seconds": None,
        "bdd_root": F,
        "nodes": export_bdd_nodes_dict(bdd),
        "lp": build_incidence_and_lp(net_path_for_lp, var_order),
        "mode": "union_only",
        "stats": bdd.stats
    }

    return result

def run_symbolic_mode(net_path: str, order: Optional[str]):
    net = load_json(net_path)
    places = net.get("places") or []
    init = net.get("initial_marking") or {}

    arcs = net.get("arcs") or []
    trans_names = net.get("transitions") or sorted(
        {t for u, t in arcs if isinstance(t, str)} |
        {u for u, v in arcs if isinstance(u, str)}
    )

    user_order = [v.strip() for v in order.split(",")] if order else None
    places_order = user_order + sorted([p for p in places if p not in user_order]) if user_order else sorted(places)

    next_suffix = "'"
    var_order = places_order + [p + next_suffix for p in places_order]
    bdd = BDD(var_order)

    R = bdd.cube_from_marking({p: int(init.get(p, 0)) for p in places_order}, places_order)

    pp = derive_preset_postset(net)
    T = build_T_relation(bdd, places_order, pp["pre"], pp["post"], next_suffix)

    it = 0
    while True:
        it += 1
        RT = bdd.apply_and(R, T)
        Post_next = bdd.exists(set(places_order), RT)
        Post = bdd.rename(Post_next, {p + next_suffix: p for p in places_order})
        R_new = bdd.apply_or(R, Post)
        if R_new == R:
            break
        R = R_new

    return {
        "num_markings": None,
        "bdd_nodes": len(bdd.nodes),
        "places": places_order,
        "build_time_seconds": None,
        "bdd_root": R,
        "nodes": export_bdd_nodes_dict(bdd),
        "lp": build_incidence_and_lp(net_path, places_order),
        "mode": "symbolic",
        "num_transitions": len(trans_names),
        "fixpoint_iterations": it,
        "stats": bdd.stats
    }

# =========================== MAIN ===========================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="input_path", default="data/reachable_markings.json")
    ap.add_argument("--out", dest="output_path", default="data/bdd_result.json")
    ap.add_argument("--order", dest="order", default=None)
    ap.add_argument("--symbolic", action="store_true")
    ap.add_argument("--net", dest="net_path", default="data/net_structure.json")
    args = ap.parse_args()

    t0 = time.perf_counter()

    if args.symbolic:
        result = run_symbolic_mode(args.net_path, args.order)
    else:
        result = run_union_mode(args.input_path, args.order, args.net_path)

    result["build_time_seconds"] = round(time.perf_counter() - t0, 6)

    os.makedirs(os.path.dirname(args.output_path) or ".", exist_ok=True)
    with open(args.output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

