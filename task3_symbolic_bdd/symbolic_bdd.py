"""
Task 3 – Symbolic Computation of Reachable Markings using BDD
--------------------------------------------------------------
Description:
    Encodes reachable markings symbolically using Binary Decision Diagrams (BDDs).
    Also builds LP information for Task 4 (deadlock analysis).

Input:
    data/net_structure.json      (symbolic)
Output:
    data/bdd_result.json

Author:
    Kim Anh - Thao Ngoc
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, time, os, argparse
from typing import Dict, List, Set

# ============================================================
# BDD / ROBDD ENGINE
# ============================================================

class BDD:
    """
    Minimal implementation of a Reduced Ordered Binary Decision Diagram (ROBDD).

    Features:
        - Unique table ensuring canonical form.
        - Apply-cache to memoize AND/OR operations.
        - Existential quantification (used in Post-image computation).
        - Variable renaming (map s' → s).
        - Cube construction for initial markings.
        - Symbolic model counting (SATCOUNT) to count reachable markings.
    """

    def __init__(self, var_order: List[str]):
        # Global variable ordering for all BDD nodes
        self.var_order = var_order
        self.var_to_idx = {v:i for i,v in enumerate(var_order)}

        # Terminal nodes: index 0 = False, index 1 = True
        self.nodes = [(None,None,None), (None,None,None)]

        # Unique-table stores canonical nodes: (var,low,high) → index
        self.unique = {}

        # Cache for repeated AND/OR operations
        self.cache = {}

    # --------------------------------------------------------
    def mk(self, var: str, low: int, high: int) -> int:
        """Create a BDD node or reuse an existing one."""
        # Reduction rule: if low == high, skip node
        if low == high:
            return low

        key = (var, low, high)
        if key in self.unique:
            return self.unique[key]

        idx = len(self.nodes)
        self.unique[key] = idx
        self.nodes.append((self.var_to_idx[var], low, high))
        return idx

    # --------------------------------------------------------
    def apply_and(self, u1: int, u2: int) -> int:
        """Apply logical AND to two BDD nodes."""
        if u1 > u2:
            u1,u2 = u2,u1
        key = ("and", u1, u2)

        if key in self.cache:
            return self.cache[key]

        # Terminal cases
        if u1 == 0 or u2 == 0:
            res = 0
        elif u1 == 1:
            res = u2
        elif u2 == 1:
            res = u1
        else:
            v1,l1,h1 = self.nodes[u1]
            v2,l2,h2 = self.nodes[u2]

            if v1 == v2:
                low  = self.apply_and(l1, l2)
                high = self.apply_and(h1, h2)
                res = self.mk(self.var_order[v1], low, high)

            elif v1 < v2:
                low  = self.apply_and(l1, u2)
                high = self.apply_and(h1, u2)
                res = self.mk(self.var_order[v1], low, high)

            else:
                low  = self.apply_and(u1, l2)
                high = self.apply_and(u1, h2)
                res = self.mk(self.var_order[v2], low, high)

        self.cache[key] = res
        return res

    # --------------------------------------------------------
    def apply_or(self, u1: int, u2: int) -> int:
        """Apply logical OR to two nodes."""
        if u1 > u2:
            u1,u2 = u2,u1
        key = ("or",u1,u2)

        if key in self.cache:
            return self.cache[key]

        if u1 == 1 or u2 == 1:
            res = 1
        elif u1 == 0:
            res = u2
        elif u2 == 0:
            res = u1
        else:
            v1,l1,h1 = self.nodes[u1]
            v2,l2,h2 = self.nodes[u2]

            if v1 == v2:
                low  = self.apply_or(l1, l2)
                high = self.apply_or(h1, h2)
                res = self.mk(self.var_order[v1], low, high)

            elif v1 < v2:
                low  = self.apply_or(l1, u2)
                high = self.apply_or(h1, u2)
                res = self.mk(self.var_order[v1], low, high)

            else:
                low  = self.apply_or(u1, l2)
                high = self.apply_or(u1, h2)
                res = self.mk(self.var_order[v2], low, high)

        self.cache[key] = res
        return res

    # --------------------------------------------------------
    def exists(self, vars_to_eliminate: Set[str], u: int) -> int:
        """
        Existential quantification: ∃x. f
        Used during Post-image computation to remove old-state variables.
        """
        if u <= 1:
            return u

        var_idx, low, high = self.nodes[u]
        name = self.var_order[var_idx]

        low2  = self.exists(vars_to_eliminate, low)
        high2 = self.exists(vars_to_eliminate, high)

        if name in vars_to_eliminate:
            return self.apply_or(low2, high2)
        return self.mk(name, low2, high2)

    # --------------------------------------------------------
    def rename(self, u: int, mapping: Dict[str,str]) -> int:
        """Rename variables according to mapping, e.g., p' → p."""
        if u <= 1:
            return u

        var_idx, low, high = self.nodes[u]
        old = self.var_order[var_idx]
        new = mapping.get(old, old)

        low2  = self.rename(low,  mapping)
        high2 = self.rename(high, mapping)
        return self.mk(new, low2, high2)

    # --------------------------------------------------------
    def cube_from_marking(self, marking:Dict[str,int], vars_list:List[str]) -> int:
        """Construct a Boolean cube representing the marking."""
        res = 1
        for v in vars_list:
            if marking.get(v,0) == 1:
                lit = self.mk(v, 0, 1)
            else:
                lit = self.mk(v, 1, 0)
            res = self.apply_and(res, lit)
        return res

    # --------------------------------------------------------
    def count_solutions(self, root:int, vars_list:List[str]) -> int:
        """
        Count the number of satisfying assignments over vars_list.
        Standard SATCOUNT using BDD recursion.
        """
        memo = {}

        def dfs(u, pos):
            if (u,pos) in memo:
                return memo[(u,pos)]

            if u == 0:
                return 0
            if u == 1:
                rem = len(vars_list) - pos
                return 1 << rem

            v_idx, low, high = self.nodes[u]
            name = self.var_order[v_idx]

            while pos < len(vars_list) and vars_list[pos] != name:
                pos += 1

            c_low  = dfs(low,  pos+1)
            c_high = dfs(high, pos+1)

            memo[(u,pos)] = c_low + c_high
            return memo[(u,pos)]

        return dfs(root, 0)

# ============================================================
# Helper functions
# ============================================================

def load_json(path):
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)

def derive_preset_postset(net):
    """
    Construct Pre(t) and Post(t) sets from arc structure.
    """
    places = set(net["places"])
    pre, post = {}, {}
    for u,v in net["arcs"]:
        if u in places:
            pre.setdefault(v,set()).add(u)
        else:
            post.setdefault(u,set()).add(v)
    return {"pre":pre,"post":post}

def or_reduce(bdd, lst):
    """Balanced OR-reduction for a list of BDD nodes."""
    if not lst:
        return 0
    s = lst
    while len(s) > 1:
        nxt=[]
        for i in range(0,len(s),2):
            if i+1 < len(s):
                nxt.append(bdd.apply_or(s[i], s[i+1]))
            else:
                nxt.append(s[i])
        s = nxt
    return s[0]

# ============================================================
# Transition relation encoding
# ============================================================

def build_T_relation(bdd, places, pre, post, nxt="'"):
    """
    Encode the transition relation T(s,s') as an ROBDD.
    For each transition t, we encode:
        • Pre-places must be 1
        • Post-places become 1 in next state
        • Pre-places become 0 (token consumed)
        • Unchanged places satisfy (p' == p)
    """

    clauses = []

    for t in sorted(pre.keys() | post.keys()):
        lits = []
        pre_t  = pre.get(t, set())
        post_t = post.get(t, set())

        # BEFORE firing: all pre-places must be 1
        for p in pre_t:
            lits.append(bdd.mk(p, 0, 1))

        # AFTER firing: determine next-state value for each place
        for p in places:
            if p in pre_t:
                lits.append(bdd.mk(p+nxt, 1, 0))     # consumed → 0
            elif p in post_t:
                lits.append(bdd.mk(p+nxt, 0, 1))     # produced → 1
            else:
                # unchanged: encode equality p' = p
                eq = bdd.mk(
                    p,
                    bdd.mk(p+nxt, 1,0),   # p=0 → p'=0
                    bdd.mk(p+nxt, 0,1)    # p=1 → p'=1
                )
                lits.append(eq)

        # AND all literals of this transition
        clause = 1
        for lit in lits:
            clause = bdd.apply_and(clause, lit)
        clauses.append(clause)

    return or_reduce(bdd, clauses)

# ============================================================
# LP builder (Task 4)
# ============================================================

def build_incidence_and_lp(net_path, places_order):
    """
    Construct incidence matrix C, initial marking M0,
    and disabling constraints for ILP deadlock detection (Task 4).
    """
    net = load_json(net_path)
    places = places_order
    pidx = {p:i for i,p in enumerate(places)}

    arcs = net["arcs"]
    trans = net.get("transitions")

    # infer transition list if missing
    if not trans:
        T=set()
        for u,v in arcs:
            if u not in pidx: T.add(u)
            if v not in pidx: T.add(v)
        trans = sorted(T)

    tidx = {t:i for i,t in enumerate(trans)}

    pre={t:set() for t in trans}
    post={t:set() for t in trans}

    for u,v in arcs:
        if u in pidx and v in tidx:
            pre[v].add(u)
        elif u in tidx and v in pidx:
            post[u].add(v)

    C=[[0]*len(trans) for _ in places]

    for t in trans:
        j=tidx[t]
        for p in pre[t]:
            C[pidx[p]][j] -= 1
        for p in post[t]:
            C[pidx[p]][j] += 1

    M0src = net["initial_marking"]
    M0=[int(M0src.get(p,0)) for p in places]

    disable=[]
    for t in trans:
        disable.append({
            "transition":t,
            "pre_places":sorted(pidx[p] for p in pre[t])
        })

    return {
        "places":places,
        "transitions":trans,
        "C":C,
        "M0":M0,
        "x_bounds":{"lower":0,"upper":20},
        "disable_constraints":disable
    }

# ============================================================
# SYMBOLIC REACHABILITY
# ============================================================

def run_symbolic(net_path, order):
    """
    Full symbolic reachability computation:

        R0 = cube(M0)
        Iteratively:
            RT = R ∧ T
            Post = ∃P (RT)
            rename p'→p
            R_new = R ∪ Post
        until fixed point

    Finally, compute SATCOUNT to count the number of reachable markings.
    """

    net = load_json(net_path)
    places = net["places"]
    init   = net["initial_marking"]

    # Determine variable ordering
    if order:
        user = [v.strip() for v in order.split(",")]
        places_order = user + [p for p in places if p not in user]
    else:
        places_order = sorted(places)

    # Interleaved ordering: p, p', q, q', ...
    var_order=[]
    nxt="'"
    for p in places_order:
        var_order.append(p)
        var_order.append(p+nxt)

    bdd = BDD(var_order)

    # Initial marking as BDD cube
    R = bdd.cube_from_marking(
        {p:int(init.get(p,0)) for p in places_order},
        places_order
    )

    # Build transition relation T(s,s')
    pp = derive_preset_postset(net)
    T = build_T_relation(bdd, places_order, pp["pre"], pp["post"], nxt)

    curr_vars = set(places_order)
    rename_map = {p+nxt:p for p in places_order}

    it=0
    while True:
        it+=1

        RT = bdd.apply_and(R, T)                 # Combine R with T
        Post_next = bdd.exists(curr_vars, RT)    # ∃ eliminate current-state vars
        Post = bdd.rename(Post_next, rename_map) # rename p'→p

        R_new = bdd.apply_or(R, Post)

        if R_new == R:
            break
        R = R_new

    # Symbolic SATCOUNT of reachable states
    num_markings = bdd.count_solutions(R, places_order)

    return {
        "num_markings": num_markings,
        "bdd_root": R,
        "bdd_nodes": len(bdd.nodes),
        "places": places_order,
        "iterations": it,
        "stats": {
            "num_nodes": len(bdd.nodes),
            "cache": len(bdd.cache)
        },
        "bdd": bdd
    }

# ============================================================
# JSON Export Helpers
# ============================================================

def export_nodes(bdd):
    """Export ROBDD node table to JSON."""
    out={}
    out["0"]={"terminal":0}
    out["1"]={"terminal":1}

    for i in range(2,len(bdd.nodes)):
        vidx,low,high = bdd.nodes[i]
        out[str(i)] = {
            "var": bdd.var_order[vidx],
            "low": low,
            "high": high
        }
    return out

# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--net", default="data/net_structure.json")
    parser.add_argument("--out", default="data/bdd_result.json")
    parser.add_argument("--order", default=None)
    args = parser.parse_args()

    t0 = time.perf_counter()
    result = run_symbolic(args.net, args.order)
    build_time = round(time.perf_counter() - t0, 6)

    bdd = result["bdd"]
    num_nodes = result["bdd_nodes"]
    cache_entries = result["stats"]["cache"]

    # Rough memory estimate (ROBDD nodes + cache entries)
    memory_bytes = num_nodes * 32 + cache_entries * 48
    memory_mb = memory_bytes / (1024 * 1024)

    # Console output
    print("=== Symbolic Reachability using BDD ===")
    print("Reachable markings:", result["num_markings"])
    print("BDD nodes:", num_nodes)
    print("Iterations:", result["iterations"])
    print("Build time (sec):", build_time)
    print(f"Memory usage: {memory_mb:.4f} MB")

    out_json = {
        "num_markings": result["num_markings"],
        "bdd_nodes": num_nodes,
        "places": result["places"],
        "build_time_seconds": build_time,
        "memory_usage_mb": round(memory_mb, 6),
        "bdd_root": result["bdd_root"],
        "nodes": export_nodes(bdd),
        "lp": build_incidence_and_lp(args.net, result["places"]),
        "stats": result["stats"]
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out_json, f, indent=4, ensure_ascii=False)

if __name__=="__main__":
    main()
