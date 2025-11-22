"""
This module defines common constants used across the Sudoku solver project.
"""

from typing import FrozenSet

GRID_SIZE = 9
BOX_DIM = 3
ALL_POSSIBILITIES: FrozenSet[int] = frozenset(range(1, GRID_SIZE + 1))
