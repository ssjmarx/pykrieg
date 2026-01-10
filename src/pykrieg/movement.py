"""Movement system for Pykrieg.

This module implements movement patterns for all unit types, generating
pseudo-legal moves without considering terrain or lines of communication.
Terrain restrictions and LOC will be added in 0.2.x series.

Movement uses Chebyshev distance (king moves in chess):
- Movement range 1: 8 adjacent squares
- Movement range 2: Up to 24 squares (3x3 area × 3x3 area minus corners)
- Movement range 0: No movement (Arsenals only)
"""

from typing import TYPE_CHECKING, List, Tuple

from .board import Board

if TYPE_CHECKING:
    pass


def generate_moves(board: Board, from_row: int, from_col: int) -> List[Tuple[int, int]]:
    """Generate pseudo-legal moves for a unit at given position.

    Pseudo-legal means:
    - Within movement range (Chebyshev distance)
    - Within board boundaries
    - Not occupied by any unit

    Terrain and lines of communication are NOT considered (0.2.x feature).

    Args:
        board: The game board
        from_row: Row of unit to move (0-19)
        from_col: Column of unit to move (0-24)

    Returns:
        List of (to_row, to_col) tuples representing legal moves

    Raises:
        ValueError: If position is invalid or no unit at position

    Examples:
        >>> board = Board()
        >>> board.create_and_place_unit(5, 10, "INFANTRY", "NORTH")
        >>> moves = generate_moves(board, 5, 10)
        >>> len(moves)
        8  # Infantry has range 1, up to 8 moves
    """
    # Get unit at position
    unit = board.get_unit(from_row, from_col)
    if unit is None:
        raise ValueError(f"No unit at position ({from_row}, {from_col})")

    # Check if unit can move - use getattr to avoid type checking issues
    movement_range = getattr(unit, 'movement', 0)
    if movement_range == 0:
        return []

    # Generate all squares within movement range
    moves = []

    # Iterate through all possible target squares
    for row_offset in range(-movement_range, movement_range + 1):
        for col_offset in range(-movement_range, movement_range + 1):
            # Skip the starting position
            if row_offset == 0 and col_offset == 0:
                continue

            to_row = from_row + row_offset
            to_col = from_col + col_offset

            # Check if target square is valid
            if is_valid_move(board, from_row, from_col, to_row, to_col):
                moves.append((to_row, to_col))

    return moves


def is_valid_move(board: Board, from_row: int, from_col: int,
                  to_row: int, to_col: int) -> bool:
    """Check if a move is valid (pseudo-legal).

    A move is pseudo-legal if:
    1. Source square has a unit
    2. Target square is within board boundaries
    3. Target square is within movement range (Chebyshev distance)
    4. Target square is not occupied by any unit
    5. Source unit has movement > 0

    Args:
        board: The game board
        from_row: Source row (0-19)
        from_col: Source column (0-24)
        to_row: Target row (0-19)
        to_col: Target column (0-24)

    Returns:
        True if move is pseudo-legal, False otherwise

    Examples:
        >>> board = Board()
        >>> board.create_and_place_unit(5, 10, "INFANTRY", "NORTH")
        >>> is_valid_move(board, 5, 10, 6, 11)
        True  # Valid diagonal move
        >>> is_valid_move(board, 5, 10, 5, 10)
        False  # Cannot move to same square
    """
    # Check source has unit
    unit = board.get_unit(from_row, from_col)
    if unit is None:
        return False

    # Check unit can move - use getattr to avoid type checking issues
    movement_range = getattr(unit, 'movement', 0)
    if movement_range == 0:
        return False

    # Check target within board boundaries
    if not board.is_valid_square(to_row, to_col):
        return False

    # Check movement range (Chebyshev distance)
    distance = max(abs(to_row - from_row), abs(to_col - from_col))
    if distance > movement_range:
        return False

    # Check target not occupied
    if board.get_unit(to_row, to_col) is not None:
        return False

    return True


def execute_move(board: Board, from_row: int, from_col: int,
                to_row: int, to_col: int) -> object:
    """Execute a move on the board.

    This function:
    1. Validates the move is legal
    2. Moves the unit from source to target
    3. Clears the source square
    4. Returns the moved unit

    Args:
        board: The game board
        from_row: Source row (0-19)
        from_col: Source column (0-24)
        to_row: Target row (0-19)
        to_col: Target column (0-24)

    Returns:
        The Unit object that was moved

    Raises:
        ValueError: If move is invalid

    Examples:
        >>> board = Board()
        >>> board.create_and_place_unit(5, 10, "INFANTRY", "NORTH")
        >>> moved_unit = execute_move(board, 5, 10, 6, 11)
        >>> moved_unit.unit_type
        'INFANTRY'
        >>> board.get_unit(6, 11) is not None
        True
        >>> board.get_unit(5, 10) is None
        True
    """
    # Validate move
    if not is_valid_move(board, from_row, from_col, to_row, to_col):
        raise ValueError(f"Invalid move from ({from_row}, {from_col}) to ({to_row}, {to_col})")

    # Get unit
    unit = board.get_unit(from_row, from_col)

    # Move unit
    board.clear_square(from_row, from_col)
    board.place_unit(to_row, to_col, unit)

    return unit


def get_movement_range(unit: object) -> int:
    """Get the movement range of a unit.

    Args:
        unit: Unit object

    Returns:
        Movement range (0, 1, or 2)

    Examples:
        >>> from pykrieg import create_piece
        >>> infantry = create_piece("INFANTRY", "NORTH")
        >>> get_movement_range(infantry)
        1
        >>> cavalry = create_piece("CAVALRY", "NORTH")
        >>> get_movement_range(cavalry)
        2
        >>> arsenal = create_piece("ARSENAL", "NORTH")
        >>> get_movement_range(arsenal)
        0
    """
    return getattr(unit, 'movement', 0)


def can_move(unit: object) -> bool:
    """Check if a unit can move.

    Args:
        unit: Unit object

    Returns:
        True if unit has movement > 0, False otherwise

    Examples:
        >>> from pykrieg import create_piece
        >>> infantry = create_piece("INFANTRY", "NORTH")
        >>> can_move(infantry)
        True
        >>> arsenal = create_piece("ARSENAL", "NORTH")
        >>> can_move(arsenal)
        False
    """
    return getattr(unit, 'movement', 0) > 0
