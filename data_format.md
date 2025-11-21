# 📄 Data Format Specification

This document defines the input and output data formats used between tasks in the Petri Net assignment.

---

## 🟢 Task 1 – PNML Parser
**Input:** `data/example.pnml`  
**Output:** `data/net_structure.json`

```json
{
    "places": ["P0", "P1", "P2"],
    "transitions": ["T1", "T2"],
    "arcs": [
        ["P0", "T1"],
        ["T1", "P1"],
        ["P1", "T2"],
        ["T2", "P2"]
    ],
    "initial_marking": {
        "P0": 1,
        "P1": 0,
        "P2": 0
    }
}

```

## 🟡 Task 2 – Reachable Markings (BFS/DFS)
**Input:** `data/net_structure.json`    
**Output:** `data/reachable_markings.json`

```json
[
    {"P0": 1, "P1": 0, "P2": 0},
    {"P0": 0, "P1": 1, "P2": 0},
    {"P0": 0, "P1": 0, "P2": 1}
]

```

## 🔵 Task 3 – Symbolic BDD
**Input:** `data/reachable_markings.json`    
**Output:** `data/bdd_result.json`

```json
{
    "num_markings": 3,
    "bdd_nodes": 8,
    "places": ["P0", "P1", "P2"],
    "build_time_seconds": 0.0019,

    "bdd_root": 7,

    "nodes": {
        "0": { "terminal": 0 },
        "1": { "terminal": 1 },

        "2": { "var": "P0", "low": 0, "high": 1 },
        "3": { "var": "P1", "low": 0, "high": 1 },
        "4": { "var": "P2", "low": 0, "high": 1 },

        "5": { "var": "P0", "low": 3, "high": 1 },
        "6": { "var": "P1", "low": 4, "high": 1 },
        "7": { "var": "P0", "low": 6, "high": 1 }
    },

    "lp": {
        "places": ["P0", "P1", "P2"],
        "transitions": ["T1", "T2", "T3"],

        "C": [
            [-1, -1,  0],
            [ 1,  0, -1],
            [ 0,  1, -1]
        ],

        "M0": [1, 0, 0],

        "x_bounds": { "lower": 0, "upper": 20 },

        "disable_constraints": [
            { "transition": "T1", "pre_places": [0] },
            { "transition": "T2", "pre_places": [0] },
            { "transition": "T3", "pre_places": [1, 2] }
        ]
    },

    "mode": "union_only",

    "stats": {
        "num_nodes": 8,
        "cache": 3
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
        {"P0": 0, "P1": 1, "P2": 0}
    ],
    "time_seconds": 0.027992
}
```

## 🟣 Task 5 – Optimization
**Input:** `data/reachable_markings.json`    
**Output:** `data/optimization_result.json`

```json
{
    "best_marking": [
        {"P0": 0, "P1": 1, "P2": 0}
    ],
    "max_value": 0.2274393162,
    "time_seconds": 0.000012
}
```
