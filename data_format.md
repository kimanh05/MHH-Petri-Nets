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
    "build_time_seconds": 0.0123
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
