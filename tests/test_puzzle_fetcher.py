import unittest
from unittest.mock import MagicMock, patch

from src.puzzle_fetcher import PuzzleFetchError, fetch_puzzle_from_websudoku


class TestPuzzleFetcher(unittest.TestCase):
    @patch("src.puzzle_fetcher.requests.get")
    def test_fetch_puzzle_success(self, mock_get):
        """Test successful puzzle fetch."""
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <table id="puzzle_grid">
                <tr><td><input value="1"></td><td><input></td></tr>
            </table>
            <input name="cheat" value="12">
        </html>
        """
        # Mocking a 2x1 grid for simplicity, though the code expects 9x9.
        # We need to mock a full 9x9 grid to pass the length check.
        # Let's just mock the find_all result directly or provide full HTML.
        # Providing full HTML is safer but verbose.
        # Let's mock the soup parsing if possible, or just provide enough HTML.

        # Actually, let's just mock the response text with enough TDs.
        # 9x9 = 81 cells.
        tds = "".join(["<td><input></td>"] * 81)
        cheat_value = "1" * 81

        mock_response.text = f"""
        <html>
            <table id="puzzle_grid">
                {tds}
            </table>
            <input name="cheat" value="{cheat_value}">
        </html>
        """
        mock_get.return_value = mock_response

        result = fetch_puzzle_from_websudoku(level=1)
        self.assertIsNotNone(result)
        self.assertIn("puzzle", result)
        self.assertIn("solution", result)

    @patch("src.puzzle_fetcher.requests.get")
    def test_fetch_puzzle_failure_no_table(self, mock_get):
        """Test fetch failure when table is missing."""
        mock_response = MagicMock()
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response

        with self.assertRaises(PuzzleFetchError):
            fetch_puzzle_from_websudoku(level=1)

    @patch("src.puzzle_fetcher.requests.get")
    def test_fetch_puzzle_failure_request_exception(self, mock_get):
        """Test fetch failure on request exception."""
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        with self.assertRaises(PuzzleFetchError):
            fetch_puzzle_from_websudoku(level=1)
