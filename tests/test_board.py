from src.sudoku_constants import ALL_POSSIBILITIES, GRID_SIZE
from src.sudoku_solver import Board


def test_board_initialization_empty():
    """Test that a new, empty board has all possibilities in every cell."""
    board = Board()
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            assert board.grid[r][c] == set(ALL_POSSIBILITIES)


def test_load_from_list_and_assign():
    """Test loading a board from a list and check constraint propagation."""
    # A simple puzzle with one number placed at the top-left.
    puzzle_list = [
        ["1", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["0", "0", "0", "0", "0", "0", "0", "0", "0"],
    ]
    board = Board(puzzle_list)

    # Check that the top-left cell has only '1'
    assert board.grid[0][0] == {1}

    # Check that a peer (in the same row) does not have '1' as a possibility
    assert 1 not in board.grid[0][1], "Peer in same row was not updated."
    # Check that a peer (in the same column) does not have '1' as a possibility
    assert 1 not in board.grid[1][0], "Peer in same column was not updated."
    # Check that a peer (in the same box) does not have '1' as a possibility
    assert 1 not in board.grid[1][1], "Peer in same box was not updated."

    # Check that a non-peer cell still has '1' as a possibility
    assert 1 in board.grid[3][3], "Non-peer cell incorrectly had '1' removed."


def test_contradiction_assigning_same_value_in_unit():
    """Test that assigning a value that's already in a peer unit fails."""
    board = Board()
    # Assign '5' to the top-left cell
    assert board.assign(0, 0, 5) is True
    # Attempting to assign '5' to another cell in the same row should fail
    # The 'assign' method should return False, indicating a contradiction.
    assert board.assign(0, 1, 5) is False


def test_eliminate_rule_1_naked_single():
    """Test that eliminating a value, leaving one possibility, propagates to peers."""
    board = Board()
    # Reduce cell (0,0) to two possibilities: {1, 2}
    for i in range(3, 10):
        board.grid[0][0].remove(i)

    # Now, eliminating 1 from (0,0) should leave only 2.
    # This should trigger rule 1, eliminating 2 from all of (0,0)'s peers.
    assert board.eliminate(0, 0, 1) is True
    assert board.grid[0][0] == {2}

    # Check a peer in the same row, column, and box
    assert 2 not in board.grid[0][5]  # Row peer
    assert 2 not in board.grid[5][0]  # Column peer
    assert 2 not in board.grid[1][1]  # Box peer


def test_eliminate_rule_2_hidden_single():
    """Test that if a value has only one possible spot in a unit, it gets assigned."""
    board = Board()
    # For the first row (unit), remove 7 as a possibility from all cells except (0, 5)
    for c in range(GRID_SIZE):
        if c != 5:
            board.eliminate(0, c, 7)

    # At this point, (0, 5) is the only place in the row that can be 7.
    # The board should have automatically assigned 7 to (0, 5).
    assert board.grid[0][5] == {7}


def test_board_copy():
    """Test that Board.copy creates a deep copy."""
    board = Board()
    board.assign(0, 0, 1)
    board_copy = board.copy()

    # Modify the copy
    board_copy.assign(0, 1, 2)

    # Check that the original board is unaffected
    assert 2 in board.grid[0][1]
    assert board_copy.grid[0][1] == {2}
