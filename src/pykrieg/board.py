"""
Board class for Pykrieg - representing the 20×25 game board.

This module implements the Board class with territory divisions,
coordinate validation, and piece management.
"""

import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from . import constants

if TYPE_CHECKING:
    pass


class Board:
    """
    Represents the 20×25 game board with territory divisions.

    The board has:
    - 20 rows (0-19)
    - 25 columns (0-24)
    - Total 500 squares
    - Territory division at row 10 (North: 0-9, South: 10-19)
    """

    TERRITORY_BOUNDARY = constants.TERRITORY_BOUNDARY  # Row 10 is the boundary

    def __init__(self) -> None:
        """Initialize empty board with territory boundaries."""
        self._rows = constants.BOARD_ROWS
        self._cols = constants.BOARD_COLS
        # Use Any to handle both None and Unit objects due to circular imports
        self._board: List[List[Any]] = [[None for _ in range(self._cols)]
                                        for _ in range(self._rows)]
        self._turn = constants.PLAYER_NORTH  # Starting player
        self._turn_number = 1  # Track turn number
        self._current_phase = constants.PHASE_MOVEMENT  # Track current phase
        self._pending_retreats: List[Tuple[int, int]] = []  # Track pending retreats

    @property
    def rows(self) -> int:
        """Return number of rows."""
        return self._rows

    @property
    def cols(self) -> int:
        """Return number of columns."""
        return self._cols

    @property
    def turn(self) -> str:
        """Return current player."""
        return self._turn

    def turn_side(self) -> str:
        """Return current turn side (NORTH/SOUTH)."""
        return self._turn

    @property
    def territory_boundary(self) -> int:
        """Return row number that separates territories."""
        return self.TERRITORY_BOUNDARY

    def is_valid_square(self, row: int, col: int) -> bool:
        """Check if coordinates are within board bounds."""
        return (0 <= row < self._rows) and (0 <= col < self._cols)

    def get_piece(self, row: int, col: int) -> Optional[object]:
        """Get piece at given coordinates.

        .. deprecated:: 0.1.2
            Use :meth:`get_unit` instead. Will be removed in version 0.3.0.
        """
        warnings.warn(
            "get_piece() is deprecated and will be removed in version 0.3.0. "
            "Use get_unit() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        if not self.is_valid_square(row, col):
            raise ValueError(f"Invalid coordinates: ({row}, {col})")
        return self._board[row][col]  # type: ignore[no-any-return]

    def set_piece(self, row: int, col: int, piece: object) -> None:
        """Set piece at given coordinates.

        .. deprecated:: 0.1.2
            Use :meth:`place_unit` instead. Will be removed in version 0.3.0.
        """
        warnings.warn(
            "set_piece() is deprecated and will be removed in version 0.3.0. "
            "Use place_unit() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        if not self.is_valid_square(row, col):
            raise ValueError(f"Invalid coordinates: ({row}, {col})")
        self._board[row][col] = piece

    def clear_square(self, row: int, col: int) -> None:
        """Remove piece from square."""
        if not self.is_valid_square(row, col):
            raise ValueError(f"Invalid coordinates: ({row}, {col})")
        self._board[row][col] = None

    # Unit placement methods

    def place_unit(self, row: int, col: int, unit: object) -> None:
        """Place a Unit object on the board.

        Args:
            row: Row coordinate (0-19)
            col: Column coordinate (0-24)
            unit: Unit object to place

        Raises:
            ValueError: If coordinates are invalid
        """
        if not self.is_valid_square(row, col):
            raise ValueError(f"Invalid coordinates: ({row}, {col})")
        self._board[row][col] = unit

    def create_and_place_unit(self, row: int, col: int,
                             unit_type: str, owner: str) -> object:
        """Create and place a unit on the board in one step.

        Args:
            row: Row coordinate (0-19)
            col: Column coordinate (0-24)
            unit_type: Unit type string
            owner: 'NORTH' or 'SOUTH'

        Returns:
            The created Unit object

        Raises:
            ValueError: If coordinates, unit_type, or owner are invalid
        """
        from .pieces import create_piece
        unit = create_piece(unit_type, owner)
        self.place_unit(row, col, unit)
        return unit

    # Unit query methods

    def get_unit(self, row: int, col: int) -> Optional[object]:
        """Get Unit object at given coordinates.

        Args:
            row: Row coordinate (0-19)
            col: Column coordinate (0-24)

        Returns:
            Unit object or None if square is empty

        Raises:
            ValueError: If coordinates are invalid
        """
        if not self.is_valid_square(row, col):
            raise ValueError(f"Invalid coordinates: ({row}, {col})")
        return self._board[row][col]  # type: ignore[no-any-return]

    def get_unit_type(self, row: int, col: int) -> Optional[str]:
        """Get unit type string at given coordinates.

        Returns unit type string or None if square is empty.
        """
        unit = self.get_unit(row, col)
        if unit is None:
            return None
        # Use getattr to avoid circular imports with Unit type
        return getattr(unit, 'unit_type', None)

    def get_unit_owner(self, row: int, col: int) -> Optional[str]:
        """Get unit owner at given coordinates.

        Returns 'NORTH', 'SOUTH', or None if square is empty.
        """
        unit = self.get_unit(row, col)
        if unit is None:
            return None
        # Use getattr to avoid circular imports with Unit type
        return getattr(unit, 'owner', None)

    def count_units(self, unit_type: Optional[str] = None,
                   owner: Optional[str] = None) -> int:
        """Count units on the board with optional filters.

        Args:
            unit_type: Unit type to count, or None for all types
            owner: Owner to count, or None for all owners

        Returns:
            Number of matching units
        """
        count = 0
        for row in range(self._rows):
            for col in range(self._cols):
                unit = self._board[row][col]
                if unit:
                    if unit_type is None or unit.unit_type == unit_type:
                        if owner is None or unit.owner == owner:
                            count += 1
        return count

    def get_units_by_type(self, unit_type: str) -> List[Tuple[int, int]]:
        """Get all coordinates containing a specific unit type.

        Args:
            unit_type: Unit type string

        Returns:
            List of (row, col) tuples containing unit type
        """
        units: List[Tuple[int, int]] = []
        for row in range(self._rows):
            for col in range(self._cols):
                unit = self._board[row][col]
                if unit and unit.unit_type == unit_type:
                    units.append((row, col))
        return units

    def get_units_by_owner(self, owner: str) -> List[Tuple[int, int]]:
        """Get all coordinates containing units owned by a player.

        Args:
            owner: 'NORTH' or 'SOUTH'

        Returns:
            List of (row, col) tuples containing player's units
        """
        units: List[Tuple[int, int]] = []
        for row in range(self._rows):
            for col in range(self._cols):
                unit = self._board[row][col]
                if unit and unit.owner == owner:
                    units.append((row, col))
        return units

    def get_all_units(self) -> Dict[Tuple[int, int], object]:
        """Get all units on the board.

        Returns:
            Dictionary mapping (row, col) tuples to Unit objects
        """
        units: Dict[Tuple[int, int], object] = {}
        for row in range(self._rows):
            for col in range(self._cols):
                unit = self._board[row][col]
                if unit:
                    units[(row, col)] = unit
        return units

    # Validation methods

    def is_valid_unit_type(self, unit_type: str) -> bool:
        """Check if unit type is valid.

        Returns True if unit_type is in ALL_UNIT_TYPES.
        """
        return unit_type in constants.ALL_UNIT_TYPES

    def is_valid_owner(self, owner: str) -> bool:
        """Check if owner is valid.

        Returns True if owner is NORTH or SOUTH.
        """
        return owner in (constants.PLAYER_NORTH, constants.PLAYER_SOUTH)

    def get_territory(self, row: int, col: int) -> str:
        """
        Determine which territory a square belongs to.

        Returns:
            'NORTH' if row < TERRITORY_BOUNDARY
            'SOUTH' if row >= TERRITORY_BOUNDARY
        """
        if not self.is_valid_square(row, col):
            raise ValueError(f"Invalid coordinates: ({row}, {col})")

        return constants.PLAYER_NORTH if row < self.TERRITORY_BOUNDARY else constants.PLAYER_SOUTH

    def is_north_territory(self, row: int, col: int) -> bool:
        """Check if square is in North territory."""
        return self.get_territory(row, col) == constants.PLAYER_NORTH

    def is_south_territory(self, row: int, col: int) -> bool:
        """Check if square is in South territory."""
        return self.get_territory(row, col) == constants.PLAYER_SOUTH

    def get_territory_squares(self, territory: str) -> List[Tuple[int, int]]:
        """
        Get all squares belonging to a territory.

        Args:
            territory: 'NORTH' or 'SOUTH'

        Returns:
            List of (row, col) tuples
        """
        if territory not in [constants.PLAYER_NORTH, constants.PLAYER_SOUTH]:
            raise ValueError(f"Invalid territory: {territory}")

        squares = []
        for row in range(self._rows):
            for col in range(self._cols):
                if self.get_territory(row, col) == territory:
                    squares.append((row, col))
        return squares

    @staticmethod
    def spreadsheet_to_tuple(coord: str) -> Tuple[int, int]:
        """
        Convert spreadsheet-style coordinate to internal (row, col) tuple.

        Args:
            coord: String in spreadsheet format (e.g., "A1", "AA10", "Y25")

        Returns:
            Tuple (row, col) where:
            - row: 0-based from top
            - col: 0-based from left

        Note: Coordinate origin is top-left (A1 = top-left corner)
              No flipping needed - direct mapping with 1-based → 0-based conversion

        Example:
            "A1" -> (0, 0)      (top-left corner)
            "Y25" -> (24, 24)   (bottom-right on 25-col board)
            "AA10" -> (9, 26)   (10th row, 27th column)
            "AB1" -> (0, 27)     (top row, 28th column)
        """
        if not isinstance(coord, str):
            raise TypeError(f"Coord must be string, got {type(coord)}")

        # Check for empty or whitespace-only string
        if not coord or coord.isspace():
            raise ValueError(f"Invalid coord format: {coord}")

        # Check for spaces in the string
        if ' ' in coord:
            raise ValueError(f"Invalid coord format: {coord}")

        # Separate letters (column) and numbers (row)
        i = 0
        while i < len(coord) and coord[i].isalpha():
            i += 1

        col_letters = coord[:i]
        row_number = coord[i:]

        if not col_letters or not row_number:
            raise ValueError(f"Invalid coord format: {coord}")

        # Parse row (direct conversion, no flip needed)
        row_index = int(row_number) - 1  # Convert 1-based to 0-based

        # Validate row index (must be >= 0 after conversion)
        if row_index < 0:
            raise ValueError(f"Invalid coord format: {coord} (row must be >= 1)")

        # Parse column (A=0, Z=25, AA=26, AZ=51, BA=52, etc.)
        col_index = 0
        for char in col_letters:
            col_index = col_index * 26 + (ord(char.upper()) - ord('A') + 1)
        col_index -= 1  # Convert to 0-based

        return (row_index, col_index)

    @staticmethod
    def tuple_to_spreadsheet(row: int, col: int) -> str:
        """
        Convert internal (row, col) tuple to spreadsheet-style coordinate.

        Args:
            row: Row number (0-19, 0-based from top)
            col: Column number (0-24, 0-based from left)

        Returns:
            String in spreadsheet format (e.g., "A1", "AA10", "Y25")

        Note: Coordinate origin is top-left (A1 = top-left corner)
              No flipping needed - direct mapping with 0-based → 1-based conversion

        Example:
            (0, 0) -> "A1"      (top-left corner)
            (24, 24) -> "Y25"   (bottom-right on 25-col board)
            (9, 26) -> "AA10"   (10th row, 27th column)
            (0, 27) -> "AB1"     (top row, 28th column)
        """
        if not isinstance(row, int) or not isinstance(col, int):
            raise TypeError("Row and col must be integers")

        # Format column (0=A, 1=B, 25=Z, 26=AA, etc.)
        col_index = col + 1  # Convert to 1-based
        col_letters: List[str] = []
        while col_index > 0:
            col_index -= 1
            col_letters.insert(0, chr(ord('A') + col_index % 26))
            col_index //= 26

        # Format row (direct conversion, no flip needed)
        row_number = row + 1  # Convert to 1-based

        return f"{''.join(col_letters)}{row_number}"

    @staticmethod
    def tuple_to_index(row: int, col: int, board_cols: int = 25) -> int:
        """
        Convert row, col to square index (row-major order).

        Args:
            row: Row number (0-19)
            col: Column number (0-24)
            board_cols: Number of columns (default 25)

        Returns:
            Integer index (0-499)

        Example:
            (0, 0) -> 0
            (0, 1) -> 1
            (1, 0) -> 25
        """
        if row < 0 or col < 0:
            raise ValueError(f"Invalid coordinates: ({row}, {col})")

        return row * board_cols + col

    @staticmethod
    def index_to_tuple(index: int, board_cols: int = 25, board_rows: int = 20) -> Tuple[int, int]:
        """
        Convert square index to row, col tuple.

        Args:
            index: Integer index (0-499)
            board_cols: Number of columns (default 25)
            board_rows: Number of rows (default 20)

        Returns:
            Tuple (row, col)

        Example:
            0 -> (0, 0)
            1 -> (0, 1)
            25 -> (1, 0)
        """
        if not isinstance(index, int):
            raise TypeError(f"Index must be integer, got {type(index)}")

        max_index = board_cols * board_rows - 1
        if not (0 <= index <= max_index):
            raise ValueError(f"Invalid index: {index} (max: {max_index})")

        row = index // board_cols
        col = index % board_cols
        return (row, col)

    # Movement convenience methods

    def get_legal_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get all legal moves for unit at given position.

        Convenience method that wraps movement.generate_moves.

        Args:
            row: Row of unit (0-19)
            col: Column of unit (0-24)

        Returns:
            List of (to_row, to_col) tuples

        Raises:
            ValueError: If no unit at position
        """
        from .movement import generate_moves
        return generate_moves(self, row, col)

    def is_legal_move(self, from_row: int, from_col: int,
                      to_row: int, to_col: int) -> bool:
        """Check if a move is legal.

        Convenience method that wraps movement.is_valid_move.

        Args:
            from_row: Source row (0-19)
            from_col: Source column (0-24)
            to_row: Target row (0-19)
            to_col: Target column (0-24)

        Returns:
            True if move is legal, False otherwise
        """
        from .movement import is_valid_move
        return is_valid_move(self, from_row, from_col, to_row, to_col)

    def make_move(self, from_row: int, from_col: int,
                  to_row: int, to_col: int) -> object:
        """Make a move on the board.

        Convenience method that wraps movement.execute_move.

        Args:
            from_row: Source row (0-19)
            from_col: Source column (0-24)
            to_row: Target row (0-19)
            to_col: Target column (0-24)

        Returns:
            The Unit object that was moved

        Raises:
            ValueError: If move is invalid
        """
        from .movement import execute_move
        return execute_move(self, from_row, from_col, to_row, to_col)

    # Combat convenience methods

    def calculate_combat(self, target_row: int, target_col: int,
                        attacker: str, defender: str) -> Dict[str, object]:
        """Calculate complete combat scenario.

        Convenience method that wraps combat.calculate_combat.

        Args:
            target_row: Target row (0-19)
            target_col: Target column (0-24)
            attacker: 'NORTH' or 'SOUTH'
            defender: 'NORTH' or 'SOUTH'

        Returns:
            Dictionary with combat results
        """
        from .combat import calculate_combat
        return calculate_combat(self, target_row, target_col, attacker, defender)

    def execute_capture(self, target_row: int, target_col: int) -> object:
        """Execute a capture (remove target unit from board).

        Convenience method that wraps combat.execute_capture.

        Args:
            target_row: Target row (0-19)
            target_col: Target column (0-24)

        Returns:
            The captured Unit object
        """
        from .combat import execute_capture
        return execute_capture(self, target_row, target_col)

    # Retreat tracking methods

    def add_pending_retreat(self, row: int, col: int) -> None:
        """Add unit to pending retreats.

        This is called when combat resolves to RETREAT outcome.
        The actual retreat execution happens at the start of the defender's
        next turn (enforced by turn management in 0.1.4).

        Note: Retreats are tracked in-memory and not persisted in KFEN format.
        They are resolved each turn by turn management system.

        Args:
            row: Row of unit that must retreat
            col: Column of unit that must retreat

        Raises:
            ValueError: If no unit at position
        """
        if not self.is_valid_square(row, col):
            raise ValueError(f"Invalid coordinates: ({row}, {col})")

        unit = self.get_unit(row, col)
        if unit is None:
            raise ValueError(f"No unit at ({row}, {col}) to mark for retreat")

        # Check if already in retreat list to avoid duplicates
        if (row, col) not in self._pending_retreats:
            self._pending_retreats.append((row, col))

    def get_pending_retreats(self) -> List[Tuple[int, int]]:
        """Get all pending retreats.

        Returns:
            List of (row, col) tuples for units that must retreat
        """
        return list(self._pending_retreats)

    def clear_pending_retreats(self) -> None:
        """Clear all pending retreats after resolution.

        This should be called after all retreats have been processed
        at the start of a turn.
        """
        self._pending_retreats.clear()

    def has_pending_retreat(self, row: int, col: int) -> bool:
        """Check if unit at position must retreat.

        Args:
            row: Row of unit to check
            col: Column of unit to check

        Returns:
            True if unit at (row, col) must retreat, False otherwise
        """
        return (row, col) in self._pending_retreats

    # Turn tracking methods

    @property
    def turn_number(self) -> int:
        """Return current turn number."""
        return self._turn_number

    @turn_number.setter
    def turn_number(self, value: int) -> None:
        """Set turn number."""
        self._turn_number = value

    @property
    def current_phase(self) -> str:
        """Return current turn phase."""
        return self._current_phase

    @current_phase.setter
    def current_phase(self, value: str) -> None:
        """Set current turn phase."""
        self._current_phase = value

    def increment_turn(self) -> None:
        """Increment turn number and switch player."""
        self._turn_number += 1
        self._turn = (
            constants.PLAYER_SOUTH
            if self._turn == constants.PLAYER_NORTH
            else constants.PLAYER_NORTH
        )
        self._current_phase = constants.PHASE_MOVEMENT  # Reset to movement phase
