"""
This module provides functionalities to fetch Sudoku puzzles from online sources,
with a caching mechanism to avoid repeated downloads.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from .sudoku_constants import GRID_SIZE

# --- Constants ---
CACHE_DIR = "puzzle_cache"
DOWNLOAD_DELAY_SECONDS = 1.1

# --- Logger Setup ---
fetch_logger = logging.getLogger(__name__)


class PuzzleFetchError(Exception):
    """Raised when fetching a puzzle fails."""

    pass


def fetch_puzzle_from_websudoku(
    level: int = 1, timeout: int = 15
) -> Dict[str, List[List[str]]]:
    """
    Fetches a single puzzle from en2.websudoku.com.

    Args:
        level: The difficulty level (1-4).
        timeout: Request timeout in seconds.

    Returns:
        A dictionary with 'puzzle' and 'solution' lists.

    Raises:
        PuzzleFetchError: If the puzzle cannot be fetched or parsed.
    """
    url = f"https://en2.websudoku.com/?level={level}"
    fetch_logger.debug(f"Fetching puzzle from: {url}")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html5lib")

        table = soup.find("table", id="puzzle_grid")
        if not table:
            raise PuzzleFetchError(f"Could not find 'puzzle_grid' at {url}.")

        cheat_input = soup.find("input", {"name": "cheat"})
        if not cheat_input or "value" not in cheat_input.attrs:
            raise PuzzleFetchError(f"Could not find solution 'cheat' field at {url}.")
        solution_str = cheat_input["value"]

        td_elements = table.find_all("td")
        if len(td_elements) != GRID_SIZE**2:
            raise PuzzleFetchError(
                f"Expected {GRID_SIZE**2} cells, found {len(td_elements)}."
            )

        puzzle_list = [["" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        solution_list = [["" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        for idx, td in enumerate(td_elements):
            row, col = divmod(idx, GRID_SIZE)
            solution_list[row][col] = solution_str[idx]
            input_tag = td.find("input")
            if input_tag and "value" in input_tag.attrs:
                puzzle_list[row][col] = input_tag["value"]

        return {"puzzle": puzzle_list, "solution": solution_list}

    except requests.exceptions.RequestException as e:
        raise PuzzleFetchError(f"RequestException fetching {url}: {e}") from e
    except Exception as e:
        if isinstance(e, PuzzleFetchError):
            raise
        raise PuzzleFetchError(f"Unexpected error fetching {url}: {e}") from e


def get_cached_puzzle(level: int, puzzle_id: int) -> Optional[Dict[str, Any]]:
    """Loads a puzzle from the cache if it exists."""
    file_path = os.path.join(CACHE_DIR, f"level_{level}_puzzle_{puzzle_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            fetch_logger.debug(f"Cache hit for L{level} P{puzzle_id}.")
            return json.load(f)
    fetch_logger.debug(f"Cache miss for L{level} P{puzzle_id}.")
    return None


def save_puzzle_to_cache(level: int, puzzle_id: int, data: Dict[str, Any]) -> None:
    """Saves a puzzle to the cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    file_path = os.path.join(CACHE_DIR, f"level_{level}_puzzle_{puzzle_id}.json")
    with open(file_path, "w") as f:
        json.dump(data, f)
    fetch_logger.debug(f"Saved L{level} P{puzzle_id} to cache.")


def fetch_puzzles_with_cache(level: int, num_puzzles: int) -> List[Dict[str, Any]]:
    """
    Fetches a number of puzzles, using cache and rate limiting.
    """
    fetch_logger.info(f"Fetching {num_puzzles} puzzles for level {level}...")
    puzzles = []
    for i in range(num_puzzles):
        puzzle_data = get_cached_puzzle(level, i)
        if not puzzle_data:
            fetch_logger.info(f"Downloading L{level} P{i + 1} (cache miss)...")
            try:
                puzzle_data = fetch_puzzle_from_websudoku(level)
                save_puzzle_to_cache(level, i, puzzle_data)
                time.sleep(DOWNLOAD_DELAY_SECONDS)
            except PuzzleFetchError as e:
                fetch_logger.warning(f"Failed to download L{level} P{i + 1}: {e}")
                continue
        puzzles.append({"id": i, "level": level, "data": puzzle_data})
    fetch_logger.info(
        f"Finished fetching for level {level}. Got {len(puzzles)} puzzles."
    )
    return puzzles
