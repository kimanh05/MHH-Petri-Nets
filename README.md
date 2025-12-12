# 🧮 Bài tập lớn Mô hình hóa Toán học – Petri Nets
### Trường Đại học Bách Khoa – ĐHQG TP.HCM  
### Khoa Khoa học & Kỹ thuật Máy tính  

---

## 👥 Nhóm 33
| Thành viên | MSSV | Lớp | Nhiệm vụ |
|:---------------------------|:-----------:|:------:|:--------|
| **Phạm Thảo Ngọc** | 2312318 | TN02 | Task 3 |
| **Nguyễn Thị Kim Anh** | 2310123 | TN02 | Task 3 |
| **Nguyễn Thành Đạt** | 2410709 | L03 | Task 4 |
| **Lương Hoàng Vĩnh Tiến** | 2413477 | TN02 | Task 1 + 2 |
| **Nguyễn Thanh Bình** | 2410355 | L03 | Task 5 |

---

## 📘 Giới thiệu
Petri Net là mô hình toán học dùng để mô tả hành vi của các hệ thống song song và dựa trên sự kiện thông qua **place, transition và token**.  

Trong bài tập lớn này, nhóm hiện thực **pipeline gồm 5 nhiệm vụ**:

1. **Task 1:** Phân tích file PNML và sinh cấu trúc mạng.  
2. **Task 2:** Tính reachable markings bằng BFS/DFS.  
3. **Task 3:** Phân tích reachability bằng BDD.  
4. **Task 4:** Phát hiện deadlock bằng BDD + ILP.  
5. **Task 5:** Tối ưu hóa tuyến tính trên tập reachable.

Báo cáo tập trung vào thiết kế cài đặt, kết quả thực nghiệm và so sánh hai phương pháp **explicit** và **symbolic**.

---

## 🗂 Cấu trúc thư mục
```
BTL_MHH/
│
├── data/
│ ├── example.pnml
│ ├── net_structure.json
│ ├── reachable_markings.json
│ ├── bdd_result.json
│ ├── deadlocks.json
│ ├── optimization_result.json
│ └── ...
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
├── run_testcase.py
├── run_all_testcases.py
├── validate_testcase.py
└── README.md
```

---

## ⚙️ Cách chạy chương trình

### 1️⃣ Cài đặt môi trường
Yêu cầu Python **≥ 3.10**  
Cài đặt thư viện:

```bash
pip install -r requirements.txt
```
2️⃣ Chạy toàn bộ pipeline

```
python run_all.py
```

Tất cả kết quả sẽ sinh trong thư mục data/.
📈 Workflow
```
Task 1 (Parser)
   Input : example.pnml
   Output: net_structure.json
        ↓
Task 2 (BFS Reachability)
   Input : net_structure.json
   Output: reachable_markings.json
        ↓
Task 3 (Symbolic BDD)
   Input : net_structure.json
   Output: bdd_result.json
        ↓
Task 4 (Deadlock Detection)
   Input : reachable_markings.json + bdd_result.json
   Output: deadlocks.json
        ↓
Task 5 (Optimization)
   Input : reachable_markings.json
   Output: optimization_result.json
```
🔗 Tham khảo

PNML Standard – https://www.pnml.org/
BDD package: dd
ILP solver: PuLP
CO2011 – Mathematical Modeling, HK251
