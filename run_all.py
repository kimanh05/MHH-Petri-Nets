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
   Input: reachable_markings.json
   Output: bdd_result.json
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

import os
import subprocess

def run_task(script, description):
    print(f"\n==============================")
    print(f"Running: {description}")
    print("==============================")
    subprocess.run(["python", script], check=True)

if __name__ == "__main__":
    run_task("task1_2_explicit/pnml_parser.py", "Task 1 – PNML Parser")
    run_task("task1_2_explicit/reachable_bfs.py", "Task 2 – Reachable Markings (BFS)")
    run_task("task3_symbolic_bdd/symbolic_bdd.py", "Task 3 – Symbolic BDD")
    run_task("task4_deadlock_ilp/deadlock_detection.py", "Task 4 – Deadlock Detection")
    run_task("task5_optimization/optimization_solver.py", "Task 5 – Optimization")

    print("\n All tasks completed successfully!")

