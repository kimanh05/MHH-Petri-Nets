# 📄 Data Format Specification

This document defines the input and output data formats used between tasks in the Petri Net assignment.

---

## 🟢 Task 1 – PNML Parser
**Input:** `data/example.pnml`  
**Output:** `data/net_structure.json`

```json
{
    "places": ["p1", "p2", "p3"],
    "transitions": ["t1", "t2"],
    "arcs": [
        ["p1", "t1"],
        ["t1", "p2"],
        ["p2", "t2"],
        ["t2", "p3"]
    ],
    "initial_marking": {"p1": 1, "p2": 0, "p3": 0}
}
```

## 🟡 Task 2 – Reachable Markings (BFS/DFS)
**Input:** `data/net_structure.json`    
**Output:** `data/reachable_markings.json`

```json
[
    {"p1": 1, "p2": 0, "p3": 0},
    {"p1": 0, "p2": 1, "p3": 0},
    {"p1": 0, "p2": 0, "p3": 1}
]
```

## 🔵 Task 3 – Symbolic BDD
**Input:** `data/reachable_markings.json`    
**Output:** `data/bdd_result.json`

```json
{
    "num_markings": 3,
    "bdd_nodes": 10,
    "places": ["p1", "p2", "p3"],
    "build_time_seconds": 0.0123,

    "bdd_root": 8,

    "nodes": {
        "0": {"terminal": 0},
        "1": {"terminal": 1},
        "2": {"var": "p1", "low": 0, "high": 3},
        "3": {"var": "p2", "low": 1, "high": 0},
        "4": {"var": "p1", "low": 0, "high": 3}
    },

    "lp": {
        "places": ["p1", "p2", "p3"],
        "transitions": ["t1", "t2"],

        "C": [
            [-1, 0],
            [1, -1],
            [0, 1]
        ],

        "M0": [1, 0, 0],

        "x_bounds": {"lower": 0, "upper": 20},

        "disable_constraints": [
            {"transition": "t1", "pre_places": [0]},
            {"transition": "t2", "pre_places": [1]}
        ]
    },

    "mode": "union_only",
    "stats": {
        "num_nodes": 10,
        "cache": 20
    }
}
```

## ⚫ Task 4 – Deadlock Detection
**Input:** `data/reachable_markings.json, data/bdd_result.json`    
**Output** `data/deadlocks.json`

```json
{
    "deadlocks_found": true,
    "deadlock_states": [
        {"p1": 0, "p2": 0, "p3": 1}
    ],
    "time_seconds": 0.004
}
```

## 🟣 Task 5 – Optimization
**Input:** `data/reachable_markings.json`    
**Output:** `data/optimization_result.json`

```json
{
    "best_marking": {"p1": 1, "p2": 0, "p3": 0},
    "max_value": 3,
    "time_seconds": 0.001
}
