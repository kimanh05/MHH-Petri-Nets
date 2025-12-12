"""
run_all.py – Master Script
--------------------------
Chạy toàn bộ pipeline của Assignment:

Task 1 (Parser)
   Input: example.pnml
   Output: net_structure.json
        ↓
Task 2 (BFS Reachability)
   Input: net_structure.json
   Output: reachable_markings.json
        ↓
Task 3 (Symbolic BDD)
   Input: net_structure.json
        ↓
Task 4 (Deadlock Detection)
   Input: reachable_markings.json + bdd_result.json
   Output: deadlocks.json
        ↓
Task 5 (Optimization)
   Input: reachable_markings.json
   Output: optimization_result.json

Kết quả đầu ra lưu trong thư mục `data/`.
"""

"""
run_all.py – Full Pipeline for 5 Tasks
"""
"""
run_all.py – Full Pipeline for 5 Tasks
--------------------------------------
Chạy toàn bộ assignment theo đúng thứ tự:

Task 1 – Parse PNML
Task 2 – BFS Reachability (không dùng cho Task 3 nhưng vẫn phải chạy)
Task 3 – SYMBOLIC BDD (đã FIX chạy symbolic mode)
Task 4 – Deadlock Detection
Task 5 – Optimization
"""

import os
import subprocess
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")


def run_task(script_path, description, extra_args=None):
    print("\n===================================")
    print(f"[RUN] {description}")
    print("===================================")

    cmd = ["python", script_path]
    if extra_args:
        cmd += extra_args

    subprocess.run(cmd, check=True)


if __name__ == "__main__":

    # ------------------------------------------------------------
    # Ensure data/ directory exists
    # ------------------------------------------------------------
    os.makedirs(DATA, exist_ok=True)

    # ------------------------------------------------------------
    # (Optional) Auto-generate CArr.json if missing
    # ------------------------------------------------------------
    carr_path = os.path.join(DATA, "CArr.json")
    if not os.path.exists(carr_path):
        print("Generating CArr.json (default example)...")
        with open(carr_path, "w") as f:
            json.dump([1, -1], f)

    # ------------------------------------------------------------
    # TASK 1 – PNML PARSER
    # ------------------------------------------------------------
    run_task(
        os.path.join(ROOT, "task1_2_explicit", "pnml_parser.py"),
        "Task 1 – PNML Parser"
    )

    # ------------------------------------------------------------
    # TASK 2 – BFS REACHABILITY
    # ------------------------------------------------------------
    run_task(
        os.path.join(ROOT, "task1_2_explicit", "reachable_bfs.py"),
        "Task 2 – Explicit Reachability BFS"
    )

    # ------------------------------------------------------------
    # TASK 3 – SYMBOLIC BDD (NEW VERSION)
    #   symbolic_bdd.py does NOT use --symbolic anymore
    # ------------------------------------------------------------
    run_task(
        os.path.join(ROOT, "task3_symbolic_bdd", "symbolic_bdd.py"),
        "Task 3 – Symbolic BDD",
        extra_args=[
            "--net", os.path.join(DATA, "net_structure.json"),
            "--out", os.path.join(DATA, "bdd_result.json"),
            "--order", ""    # or custom variable ordering
        ]
    )

    # ------------------------------------------------------------
    # TASK 4 – DEADLOCK DETECTION (uses bdd_result.json)
    # ------------------------------------------------------------
    run_task(
        os.path.join(ROOT, "task4_deadlock_ilp", "deadlock_detection.py"),
        "Task 4 – Deadlock Detection",
        extra_args=[os.path.join(DATA, "bdd_result.json")]
    )

    # ------------------------------------------------------------
    # TASK 5 – OPTIMIZATION
    # ------------------------------------------------------------
    run_task(
        os.path.join(ROOT, "task5_optimization", "optimization_solver.py"),
        "Task 5 – Optimization"
    )

    print("\n===================================")
    print(" ALL TASKS COMPLETED SUCCESSFULLY! ")
    print("===================================\n")