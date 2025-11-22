"""
This script implements a Sudoku solver using a combination of constraint propagation
and backtracking search. It's designed to be both a command-line tool and a library.
"""

import argparse
import logging
from typing import Dict, List, Optional, Set, Tuple, Union

from .puzzle_fetcher import PuzzleFetchError, fetch_puzzle_from_websudoku
from .sudoku_constants import ALL_POSSIBILITIES, BOX_DIM, GRID_SIZE

# --- Type Aliases ---
Cell = Tuple[int, int]
Unit = List[Cell]

# --- Pre-computed Grid Information ---
SQUARES: List[Cell] = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]

UNIT_LIST: List[Unit] = (
    [[(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]  # Rows
    + [[(r, c) for r in range(GRID_SIZE)] for c in range(GRID_SIZE)]  # Columns
    + [
        [(r, c) for r in range(br, br + BOX_DIM) for c in range(bc, bc + BOX_DIM)]
        for br in range(0, GRID_SIZE, BOX_DIM)
        for bc in range(0, GRID_SIZE, BOX_DIM)
    ]  # 3x3 Boxes
)

UNITS: Dict[Cell, List[Unit]] = {s: [u for u in UNIT_LIST if s in u] for s in SQUARES}
PEERS: Dict[Cell, Set[Cell]] = {s: set(sum(UNITS[s], [])) - {s} for s in SQUARES}

# --- Logger Setup ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class Board:
    """Represents the Sudoku board and its state."""

    def __init__(self, board_repr: Optional[List[List[Union[str, int]]]] = None):
        self.grid: List[List[Set[int]]] = [
            [set(ALL_POSSIBILITIES) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)
        ]
        self.is_valid = True
        if board_repr:
            if not self.load_from_list(board_repr):
                self.is_valid = False

    def load_from_list(self, board_list: List[List[Union[str, int]]]) -> bool:
        """Initializes the board from a 2D list. Returns False on contradiction."""
        for r, row in enumerate(board_list):
            for c, val in enumerate(row):
                if str(val) in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}:
                    if not self.assign(r, c, int(val)):
                        return False
        return True

    def assign(self, r: int, c: int, val: int) -> bool:
        """Assigns a value to a cell and propagates constraints."""
        other_values = self.grid[r][c] - {val}
        for other_val in other_values:
            if not self.eliminate(r, c, other_val):
                return False
        return True

    def eliminate(self, r: int, c: int, val: int) -> bool:
        """Eliminates a value from a cell and propagates constraints."""
        if val not in self.grid[r][c]:
            return True  # Already eliminated

        self.grid[r][c].remove(val)

        if not self.grid[r][c]:
            return False  # Contradiction

        # (1) If a cell is reduced to one value, eliminate it from peers.
        if len(self.grid[r][c]) == 1:
            the_one_val = list(self.grid[r][c])[0]
            for peer_r, peer_c in PEERS[(r, c)]:
                if not self.eliminate(peer_r, peer_c, the_one_val):
                    return False

        # (2) If a unit has only one place for a value, assign it there.
        for unit in UNITS[(r, c)]:
            dplaces = [s for s in unit if val in self.grid[s[0]][s[1]]]
            if not dplaces:
                return False  # Contradiction
            if len(dplaces) == 1:
                if not self.assign(dplaces[0][0], dplaces[0][1], val):
                    return False
        return True

    def is_solved(self) -> bool:
        """Checks if the board is fully solved."""
        return all(len(self.grid[r][c]) == 1 for r, c in SQUARES)

    def copy(self) -> "Board":
        """Creates a deep copy of the board."""
        new_board = Board()
        new_board.grid = [[s.copy() for s in row] for row in self.grid]
        return new_board

    def __str__(self) -> str:
        """Returns a string representation of the board."""
        width = 2  # Each cell is a digit plus a space
        line_separator = "-" * (width * GRID_SIZE + BOX_DIM - 1)
        lines = []
        for r, row in enumerate(self.grid):
            if r > 0 and r % BOX_DIM == 0:
                lines.append(line_separator)
            line = []
            for c, possibilities in enumerate(row):
                if c > 0 and c % BOX_DIM == 0:
                    line.append("|")
                val = str(list(possibilities)[0]) if len(possibilities) == 1 else "."
                line.append(val.center(width))
            lines.append("".join(line))
        return "\n".join(lines)


class SudokuSolver:
    """A class to represent and solve a Sudoku puzzle."""

    def __init__(self, board_repr: Optional[List[List[Union[str, int]]]] = None):
        self.board: Optional[Board] = Board(board_repr) if board_repr else None

    def solve(self) -> bool:
        """Solves the loaded puzzle, returns True on success."""
        if not self.board:
            logging.error("No puzzle loaded to solve.")
            return False

        if not self.board.is_valid:
            logging.debug("Board is invalid from the start, cannot solve.")
            return False

        solved_board = self._search(self.board)
        if solved_board:
            self.board = solved_board
            return True
        return False

    def _search(self, board: Board) -> Optional[Board]:
        """Recursive backtracking search to find a solution."""
        if board.is_solved():
            return board

        min_len = float("inf")
        best_cell = None

        for r, c in SQUARES:
            num_possibilities = len(board.grid[r][c])
            if num_possibilities > 1 and num_possibilities < min_len:
                min_len = num_possibilities
                best_cell = (r, c)

        if best_cell is None:
            return None

        r, c = best_cell
        for val in sorted(list(board.grid[r][c])):
            new_board = board.copy()
            if new_board.assign(r, c, val):
                result = self._search(new_board)
                if result:
                    return result
        return None

    def validate(self) -> bool:
        """Validates if the board is a correct Sudoku solution."""
        if not self.board or not self.board.is_solved():
            return False
        for unit in UNIT_LIST:
            if {list(self.board.grid[r][c])[0] for r, c in unit} != set(
                ALL_POSSIBILITIES
            ):
                return False
        return True

    def __str__(self) -> str:
        """Returns a string representation of the board."""
        if not self.board:
            return "No board loaded."
        return str(self.board)


def _handle_downloaded_puzzle(level: int):
    """Fetches, displays, and solves a puzzle from websudoku.com."""
    logging.info(f"Attempting to download a puzzle of level {level}...")
    try:
        puzzle_data = fetch_puzzle_from_websudoku(level)
    except PuzzleFetchError as e:
        logging.error(f"Failed to download puzzle for level {level}: {e}")
        return

    puzzle_list = puzzle_data["puzzle"]
    solution_list = puzzle_data["solution"]

    puzzle_one_liner = "".join(
        val if val != "" else "0" for row in puzzle_list for val in row
    )
    print(f"\nDownloaded Puzzle (One-liner): {puzzle_one_liner}")

    # Display the initial puzzle and its known solution
    print("\nDownloaded Puzzle (Pre-filled Grid):")
    print(Board(puzzle_list))
    print("\nKnown Solution (from websudoku.com):")
    print(Board(solution_list))

    # Solve the downloaded puzzle to demonstrate the solver
    print("\n--- Attempting to solve the downloaded puzzle with the solver ---")
    solver = SudokuSolver(puzzle_list)
    if solver.solve():
        print("\nSolver's Solution:")
        print(solver)
        if solver.validate():
            print("\nSolver's solution is valid.")
        else:
            print("\nSolver's solution is INVALID.")
    else:
        print("\nSolver could not find a solution for the downloaded puzzle.")


def main():
    """Main function to run the Sudoku solver from the command line."""
    parser = argparse.ArgumentParser(description="Sudoku Solver CLI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--puzzle",
        type=str,
        help=(
            "A string of 81 characters representing the puzzle (0 or '.' for empty "
            "cells)."
        ),
    )
    group.add_argument(
        "--download-level",
        type=int,
        choices=[1, 2, 3, 4],
        help=(
            "Download a puzzle of a specific difficulty level (1-4) from websudoku.com."
        ),
    )
    args = parser.parse_args()

    if args.download_level:
        _handle_downloaded_puzzle(args.download_level)
    elif args.puzzle:
        if len(args.puzzle) != 81:
            raise ValueError("Puzzle string must be 81 characters long.")
        puzzle_list = [
            list(args.puzzle[i : i + GRID_SIZE])
            for i in range(0, len(args.puzzle), GRID_SIZE)
        ]

        # Create and print a representation of the initial board state
        # without triggering the solver's constraint propagation.
        initial_display_board = Board()
        for r, row in enumerate(puzzle_list):
            for c, val in enumerate(row):
                if str(val) in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}:
                    initial_display_board.grid[r][c] = {int(val)}

        print("Initial board:")
        print(initial_display_board)

        # Now, create the actual solver which will run constraint propagation.
        solver = SudokuSolver(puzzle_list)
        if solver.solve():
            print("\nSolved board:")
            print(solver)
            if solver.validate():
                print("\nSolution is valid.")
            else:
                print("\nSolution is INVALID.")
        else:
            print("\nCould not solve the puzzle.")


if __name__ == "__main__":
    main()
