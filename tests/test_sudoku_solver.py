import logging

import pytest

from src.puzzle_fetcher import fetch_puzzles_with_cache
from src.sudoku_solver import GRID_SIZE, Board, SudokuSolver
from tests.data.puzzles import (
    INCORRECTLY_SOLVED_BOARD,
    INVALID_PUZZLE,
    SOLUTION,
    SOLVABLE_PUZZLE,
    UNSOLVABLE_PUZZLE,
)

# Configure logging for the test file
# logging.basicConfig(level=logging.DEBUG)  # Managed by pytest
test_logger = logging.getLogger(__name__)


def test_load_valid_puzzle():
    solver = SudokuSolver(SOLVABLE_PUZZLE)
    assert solver.board is not None

    test_logger.debug("test_load_valid_puzzle completed.")


def test_load_invalid_puzzle():
    solver = SudokuSolver(INVALID_PUZZLE)
    assert solver.board.is_valid is False
    test_logger.debug("test_load_invalid_puzzle completed.")


def test_solve_valid_puzzle():
    test_logger.debug("Starting test_solve_valid_puzzle.")
    solver = SudokuSolver(SOLVABLE_PUZZLE)
    test_logger.debug("Solver initialized with SOLVABLE_PUZZLE.")
    assert solver.solve() is True
    test_logger.debug("Solver reported success.")
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            assert list(solver.board.grid[r][c])[0] == SOLUTION[r][c]
    test_logger.debug("Solution verified against expected.")
    test_logger.debug("test_solve_valid_puzzle completed.")


def test_solve_unsolvable_puzzle():
    test_logger.debug("Starting test_solve_unsolvable_puzzle.")
    solver = SudokuSolver(UNSOLVABLE_PUZZLE)
    # Log the unsolvable puzzle in a one-line format for easy debugging
    puzzle_str = "".join(
        str(cell) if str(cell) != "0" else "."
        for row in UNSOLVABLE_PUZZLE
        for cell in row
    )
    test_logger.debug(f"Attempting to solve unsolvable puzzle: {puzzle_str}")

    assert solver.solve() is False
    test_logger.debug("test_solve_unsolvable_puzzle completed (expected failure).")


def test_is_solved():
    board = Board(SOLUTION)
    assert board.is_solved() is True
    test_logger.debug("test_is_solved completed.")


def test_is_not_solved():
    board = Board()
    board.grid[0][0] = {1, 2, 3}
    assert board.is_solved() is False
    test_logger.debug("test_is_not_solved completed.")


def test_validate_correct_solution():
    solver = SudokuSolver(SOLUTION)
    assert solver.validate() is True
    test_logger.debug("test_validate_correct_solution completed.")


def test_validate_incorrect_solution():
    # Test case where the board is fully filled but logically incorrect
    solver = SudokuSolver()
    # Manually set the board to simulate a "solved" (all cells have one value) but
    # incorrect state
    incorrect_board = Board()
    incorrect_board.grid = [[{val} for val in row] for row in INCORRECTLY_SOLVED_BOARD]
    solver.board = incorrect_board
    assert solver.board.is_solved() is True  # Now this should pass
    test_logger.debug("Incorrect board set up, checking is_solved.")
    assert solver.validate() is False
    test_logger.debug("test_validate_incorrect_solution completed.")


@pytest.mark.timeout(30)  # Set a 30-second timeout for this test
def test_solve_cached_puzzles_comprehensive():
    """
    Fetches a large number of puzzles from the cache (or downloads if not present)
    across different difficulty levels and attempts to solve and validate each one.
    """
    levels_to_test = [1, 2, 3, 4]
    num_puzzles_per_level = (
        100  # Test 100 puzzles per level (for comprehensive testing)
    )

    test_logger.debug("--- Starting comprehensive puzzle solving test ---")
    total_puzzles_solved = 0
    total_puzzles_failed = 0

    for level in levels_to_test:
        test_logger.debug(
            f"--- Starting test for Level {level} "
            f"(fetching {num_puzzles_per_level} puzzles) ---"
        )
        test_logger.debug(f"Calling fetch_puzzles_with_cache for Level {level}...")
        puzzles_data = fetch_puzzles_with_cache(
            level=level, num_puzzles=num_puzzles_per_level
        )

        if not puzzles_data:
            test_logger.warning(
                f"No puzzles fetched or found in cache for Level {level}. "
                "Skipping this level."
            )
            continue
        test_logger.debug(f"Fetched {len(puzzles_data)} puzzles for Level {level}.")

        test_logger.debug(f"Fetched {len(puzzles_data)} puzzles for Level {level}.")

        for puzzle_entry in puzzles_data:
            puzzle_id = puzzle_entry["id"]
            puzzle_list = puzzle_entry["data"]["puzzle"]
            expected_solution_list = puzzle_entry["data"]["solution"]

            log_prefix = f"L{level} P{puzzle_id}"
            test_logger.debug(f"Progress: Attempting to solve {log_prefix}...")
            test_logger.debug(f"Puzzle {log_prefix} data: {puzzle_list}")

            try:
                solver = SudokuSolver(puzzle_list)
                test_logger.debug(f"{log_prefix}: Loading puzzle into solver.")
                if not solver.board.is_valid:
                    test_logger.error(
                        f"{log_prefix}: Failed to load initial puzzle configuration "
                        "(contradiction detected)."
                    )
                    # Log the puzzle that caused the load failure
                    test_logger.debug(
                        f"{log_prefix}: Puzzle data that failed to load: {puzzle_list}"
                    )

                    total_puzzles_failed += 1
                    continue  # Move to next puzzle

                if not solver.solve():
                    test_logger.error(
                        f"{log_prefix}: Solver failed to find a solution."
                    )
                    total_puzzles_failed += 1
                    continue  # Move to next puzzle
                test_logger.debug(f"{log_prefix}: Solver found a solution.")

                if not solver.validate():
                    test_logger.error(
                        f"{log_prefix}: Solved board is not valid according to "
                        "internal validation."
                    )
                    total_puzzles_failed += 1
                    test_logger.debug(
                        f"{log_prefix}: Invalid solved board: {solver.board}"
                    )
                    continue  # Move to next puzzle

                # Verify against the expected solution
                mismatch_found = False
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        solved_val = list(solver.board.grid[r][c])[0]
                        expected_val = int(expected_solution_list[r][c])
                        if solved_val != expected_val:
                            # Log the specific mismatch and the full
                            # expected/actual solutions
                            test_logger.error(
                                f"{log_prefix}: Mismatch at ({r},{c}): "
                                f"Expected {expected_val}, Got {solved_val}"
                            )
                            mismatch_found = True
                            break
                    if mismatch_found:
                        break

                if mismatch_found:
                    test_logger.error(f"{log_prefix}: Solution mismatch detected.")
                    test_logger.debug(
                        f"{log_prefix}: Expected: {Board(expected_solution_list)}"
                    )
                    test_logger.debug(
                        f"{log_prefix}: Solver's solution: {solver.board}"
                    )
                    total_puzzles_failed += 1
                else:
                    test_logger.debug(
                        f"Successfully solved and validated: {log_prefix}"
                    )
                    total_puzzles_solved += 1
                    test_logger.debug(
                        f"{log_prefix}: Final solved board: {solver.board}"
                    )

            except Exception:
                test_logger.exception(
                    f"{log_prefix}: An unexpected error occurred during solving."
                )
                total_puzzles_failed += 1
                continue

    test_logger.info("--- Comprehensive Test Summary ---")
    test_logger.info(
        f"Total puzzles attempted: {total_puzzles_solved + total_puzzles_failed}"
    )
    test_logger.info(f"Total puzzles solved and validated: {total_puzzles_solved}")
    test_logger.info(f"Total puzzles failed: {total_puzzles_failed}")

    # Assert that all puzzles were solved successfully
    assert total_puzzles_failed == 0, (
        f"Comprehensive test failed: {total_puzzles_failed} puzzles were not "
        "solved or validated correctly."
    )
    test_logger.debug(
        "--- Comprehensive puzzle solving test completed successfully ---"
    )
