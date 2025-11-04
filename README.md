# 🧮 Mathematical Modeling Assignment – Petri Nets
### HCMC University of Technology - Faculty of Computer Science & Engineering

---

## 👥 Group Information
| Member | Student ID | Class | Task |
|:---------------------------|:-----------:|:------:|:--------|
| **Phạm Thảo Ngọc** | 2312318 | TN02 | Task 3 |
| **Nguyễn Thị Kim Anh** | 2310123 | TN02 | Task 3 |
| **Nguyễn Thành Đạt** | 2410709 | L03 | Task 4 |
| **Lương Hoàng Vĩnh Tiến** | 2413477 | TN02 | Task 1 + 2 |
| **Nguyễn Thanh Bình** | 2410355 | L03 | Task 5 |

---

## 📘 Project Overview
This project implements Petri Net analysis methods as part of the **Mathematical Modeling (CO2011 / CSE251)** course.  
It consists of five main tasks:

1. **PNML Parser** – Reads a 1-safe Petri Net from a PNML file and constructs its internal representation.  
2. **Reachable Markings (BFS/DFS)** – Enumerates all reachable markings from the initial marking.  
3. **Symbolic BDD Computation** – Uses Binary Decision Diagrams to represent and compute reachable markings symbolically.  
4. **Deadlock Detection (ILP + BDD)** – Combines ILP formulation and symbolic BDD to detect reachable deadlocks.  
5. **Optimization** – Finds a reachable marking that maximizes a given linear objective function \( c^T M \).

All intermediate data between tasks are stored in JSON format for clarity and reusability.

---

## 🗂 Folder Structure
```
Assignment-CO2011-CSE251/
├── data/
│ ├── example.pnml
│ ├── net_structure.json
│ ├── reachable_markings.json
│ ├── bdd_result.json
│ ├── deadlocks.json
│ └── optimization_result.json
│
├── task1_2_explicit/
│ ├── pnml_parser.py
│ └── reachable_bfs.py
│
├── task3_symbolic_bdd/
│ └── symbolic_bdd.py
│
├── task4_deadlock_ilp/
│ └── deadlock_detection.py
│
├── task5_optimization/
│ └── optimization_solver.py
│
├── run_all.py
├── requirements.txt
├── data_format.md
├── .gitignore
└── README.md
```
---

## ⚙️ Setup & Run

### 1️⃣ Installation
Make sure you have **Python ≥ 3.10** installed.  
Then install all required libraries:
```bash
pip install -r requirements.txt
```
2️⃣ Run Full Pipeline
To execute all five tasks sequentially:

```bash
python run_all.py
```
Each step will generate its corresponding output JSON file under the data/ directory.

📊 Input / Output Summary
```
Task	Input	Output	Description
1	example.pnml	net_structure.json	Parse PNML and extract Petri Net structure
2	net_structure.json	reachable_markings.json	Compute all reachable markings (BFS/DFS)
3	reachable_markings.json	bdd_result.json	Build symbolic BDD and count reachable states
4	reachable_markings.json, bdd_result.json	deadlocks.json	Detect deadlocks via ILP + BDD
5	reachable_markings.json	optimization_result.json	Maximize linear objective function over reachable markings
📈 Example Workflow
example.pnml
   ↓ (Task 1)
net_structure.json
   ↓ (Task 2)
reachable_markings.json
   ↓ (Task 3)
bdd_result.json
   ↓ (Task 4)
deadlocks.json
   ↓ (Task 5)
optimization_result.json
```
🔗 References

PNML Standard: https://www.pnml.org/

BDD Library: dd

ILP Solver: PuLP

Mathematical Modeling Course Material – HCMUT, 2025–2026

📍 Semester 1, 2025–2026 — CO2011 Mathematical Modeling

