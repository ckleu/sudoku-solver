# 🧩 Sudoku Solver

[![Python CI](https://github.com/ckleu/sudoku-solver/actions/workflows/ci.yml/badge.svg)](https://github.com/ckleu/sudoku-solver/actions/workflows/ci.yml)

A command-line and library-based Sudoku solver in Python. This project uses constraint propagation and backtracking search to solve any valid Sudoku puzzle. It can also fetch puzzles of varying difficulty from `websudoku.com`.

## ✨ Features

-   **🧠 Constraint Propagation:** Efficiently reduces the search space before attempting to guess.
-   **🔍 Backtracking Search:** A robust algorithm to find solutions for complex puzzles.
-   **🌐 Puzzle Fetcher:** Can download new puzzles from the web.
-   **💻 Command-Line Interface:** Easy to use from the terminal.
-   **✅ Well-Tested:** Includes a comprehensive test suite using `pytest`.

## 🚀 Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/ckleu/sudoku-solver.git
    cd sudoku-solver
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  Install the project and its dependencies:
    ```bash
    pip install .
    ```
    For development (including test dependencies), use:
    ```bash
    pip install -e ".[test,lint]"
    ```

## 📖 Usage

### As a Command-Line Tool

The solver can be run directly from the command line. You can provide a puzzle as an 81-character string or ask it to download one.

**Solve a puzzle from a string:**

Use `0` or `.` for empty cells.

```bash
sudoku --puzzle "400000805030000000000700000020000060000080400000010000000603070500200000104000000"
```

**Download and solve a puzzle:**

Levels range from 1 (easiest) to 4 (hardest).

```bash
sudoku --download-level 2
```

### As a Library

You can also import the solver into your own Python projects.

```python
from src.sudoku_solver import SudokuSolver, Board

puzzle_list = [list(row) for row in ["400000805", "030000000", "000700000", "020000060", "000080400", "000010000", "000603070", "500200000", "104000000"]]
solver = SudokuSolver(puzzle_list)

if solver.solve():
    print("Solved!")
    print(solver)
else:
    print("Could not solve the puzzle.")
```

## 🧪 Running Tests

To run the test suite, ensure you have installed the test dependencies and then run `pytest`:

```bash
pytest
```

---
*This project is for educational purposes. The puzzle fetcher scrapes websudoku.com and may break if the site's structure changes.*
