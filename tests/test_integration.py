import sys
import unittest
from io import StringIO
from unittest.mock import patch

from src.sudoku_solver import PuzzleFetchError, _handle_downloaded_puzzle


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        sys.stdout = self.original_stdout

    @patch("src.sudoku_solver.fetch_puzzle_from_websudoku")
    def test_handle_downloaded_puzzle_success(self, mock_fetch):
        """Test successful download and solve flow."""
        # Mock a simple solvable puzzle
        # 0 0 1 ...
        # 0 0 0 ...
        # ...
        # Let's just use a valid grid structure but simple content
        # To avoid complex solving, let's mock a solved board?
        # Or just a very simple one.
        # Use the puzzle from test_board.py or just a full one.

        # 9x9 grid
        puzzle_list = [["0"] * 9 for _ in range(9)]
        # Make it valid but empty-ish.
        # If we return a puzzle that is unsolvable or takes too long, that's bad.
        # Let's return a puzzle that is already solved or nearly solved.

        # A solved row 1: 1 2 3 4 5 6 7 8 9
        solved_row = [str(i) for i in range(1, 10)]
        solution_list = [
            solved_row
        ] * 9  # Not a valid sudoku but valid structure for lists

        # Let's just mock the return value structure.
        # If we give it an empty board, it might take a while.
        # An empty board is solvable.

        mock_fetch.return_value = {"puzzle": puzzle_list, "solution": solution_list}

        # Mock solver's solve method to avoid actual computation
        # but this is an integration test, so maybe we SHOULD run the solver?
        # But running a full solve on an empty board is slow (backtracking).
        # Let's mock the solver to return True immediately to test the glue code.

        with patch("src.sudoku_solver.SudokuSolver.solve", return_value=True):
            with patch("src.sudoku_solver.SudokuSolver.validate", return_value=True):
                _handle_downloaded_puzzle(1)

        output = self.held_output.getvalue()
        self.assertIn("Downloaded Puzzle (One-liner):", output)
        self.assertIn("Solver's Solution:", output)
        self.assertIn("Solver's solution is valid.", output)

    @patch("src.sudoku_solver.fetch_puzzle_from_websudoku")
    def test_handle_downloaded_puzzle_fetch_error(self, mock_fetch):
        """Test handling of fetch error."""
        mock_fetch.side_effect = PuzzleFetchError("Network down")

        _handle_downloaded_puzzle(1)

        # Should log error but not crash.
        # Can't easily check logs with just stdout capture
        # But we can check that it didn't print the success messages.
        output = self.held_output.getvalue()
        self.assertNotIn("Downloaded Puzzle", output)

    @patch("src.sudoku_solver.fetch_puzzle_from_websudoku")
    def test_handle_downloaded_puzzle_unsolvable(self, mock_fetch):
        """Test handling of unsolvable puzzle (from solver perspective)."""
        puzzle_list = [["0"] * 9 for _ in range(9)]
        solution_list = [["0"] * 9 for _ in range(9)]

        mock_fetch.return_value = {"puzzle": puzzle_list, "solution": solution_list}

        with patch("src.sudoku_solver.SudokuSolver.solve", return_value=False):
            _handle_downloaded_puzzle(1)

        output = self.held_output.getvalue()
        self.assertIn("Solver could not find a solution", output)
