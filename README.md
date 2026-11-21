# Student Performance Analysis System
**Course**: Computational Thinking and Programming (`2026CSAE100`)  
**Institution**: School of Computer Science Engineering and Technology, Bennett University  
**Academic Year**: 2026–27 | **Batch / Section**: 56, S28  

---

## 📌 Project Overview

The **Student Performance Analysis System** is a pure Python application built to track, evaluate, benchmark, and report student marks across subjects and terms. It strictly adheres to foundational programming principles—file handling, recursion, lambda functions, lists, and dictionaries—without any external web frameworks or advanced libraries.

---

## 👥 Team Members & Responsibilities

| S.No. | Student Name | Enrollment No. | Assigned Role & Module |
| :---: | :--- | :--- | :--- |
| 1 | **Harshul Yadav** | `1956` | **Phase 1: Data Management** (`modules/data_management.py`) |
| 2 | **Rohil Maurya** | `1936` | **Phase 2, 5, 6, 7: Grades, Averages, Integration & Output** (`modules/grades_and_averages.py`, `modules/summary_and_output.py`, `main.py`) |
| 3 | **Priyansh Rathi** | `1909` | **Phase 3: Weak Area Detection** (`modules/weak_areas.py`) |
| 4 | **Akshit Kumar** | `1918` | **Phase 4: Multi-Term Trend Detection** (`modules/trend_detection.py`) |

---

## 📂 Project Directory Structure

```
edumatircs/
├── data/
│   └── students_data.csv            # Multi-term academic marks database
├── modules/
│   ├── __init__.py                  # Package initializer
│   ├── data_management.py          # Phase 1: Data Management (Harshul Yadav - 1956)
│   ├── grades_and_averages.py      # Phase 2: Grades & Averages (Rohil Maurya - 1936)
│   ├── weak_areas.py               # Phase 3: Weak Area Detection (Priyansh Rathi - 1909)
│   ├── trend_detection.py          # Phase 4: Multi-Term Trend Detection (Akshit Kumar - 1918)
│   └── summary_and_output.py       # Phase 5-7: Summary & Output Generation (Rohil Maurya - 1936)
├── tests/
│   └── test_modules.py             # Phase 6: Pytest verification suite (7/7 pass)
├── main.py                         # Interactive Terminal CLI Application
├── .gitignore                      # Git ignore rules
└── README.md                       # Project documentation
```

---



## 🚀 How to Run the Program

### 1. Launch Interactive CLI Menu
```bash
python main.py
```

### 2. Run Automated Pytest Suite
```bash
pytest tests/test_modules.py -v
```

---

## 🧠 Python Concepts Used
- **File Handling**: Pure Python `open()` with `csv.reader` and `csv.writer` for `data/students_data.csv`.
- **Recursion**:
  - `find_student_recursive(records, student_id, index=0)` in `data_management.py`.
  - `recursive_sum(numbers, index=0)` in `grades_and_averages.py`.
- **Lambda Functions**:
  - `sorted(records, key=lambda s: s["Overall_Average"], reverse=True)` for rankings.
  - `list(filter(lambda r: r["Student_ID"] == sid, records))` for filtering.
- **Data Structures**: Dictionaries and Lists for modular data representation.
