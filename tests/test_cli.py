import sys
import unittest
from io import StringIO
from unittest.mock import patch

from src.sudoku_solver import main


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_cli_puzzle_argument(self):
        """Test the CLI with a puzzle string."""
        puzzle = (
            "400000805030000000000700000020000060"
            "000080400000010000000603070500200000104000000"
        )
        with patch.object(sys, "argv", ["sudoku", "--puzzle", puzzle]):
            main()

        output = self.held_output.getvalue()
        self.assertIn("Solved board:", output)
        self.assertIn("Solution is valid.", output)

    def test_cli_invalid_puzzle_length(self):
        """Test the CLI with an invalid puzzle string length."""
        with patch.object(sys, "argv", ["sudoku", "--puzzle", "123"]):
            with self.assertRaises(ValueError):
                main()

    @patch("src.sudoku_solver._handle_downloaded_puzzle")
    def test_cli_download_level(self, mock_handle):
        """Test the CLI with the download-level argument."""
        with patch.object(sys, "argv", ["sudoku", "--download-level", "1"]):
            main()
        mock_handle.assert_called_once_with(1)

    def test_cli_no_args(self):
        """Test the CLI with no arguments (should exit)."""
        with patch.object(sys, "argv", ["sudoku"]):
            with self.assertRaises(SystemExit):
                main()
