"""
Board class for Pykrieg - representing the 20×25 game board.

This module implements the Board class with territory divisions,
coordinate validation, and piece management.
"""

from . import constants


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
    
    def __init__(self):
        """Initialize empty board with territory boundaries."""
        self._rows = constants.BOARD_ROWS
        self._cols = constants.BOARD_COLS
        self._board = [[None for _ in range(self._cols)] 
                      for _ in range(self._rows)]
        self._turn = constants.PLAYER_NORTH  # Starting player
    
    @property
    def rows(self):
        """Return number of rows."""
        return self._rows
    
    @property
    def cols(self):
        """Return number of columns."""
        return self._cols
    
    @property
    def turn(self):
        """Return current player."""
        return self._turn
    
    def turn_side(self):
        """Return current turn side (NORTH/SOUTH)."""
        return self._turn
    
    @property
    def territory_boundary(self):
        """Return the row number that separates territories."""
        return self.TERRITORY_BOUNDARY
    
    def is_valid_square(self, row, col):
        """Check if coordinates are within board bounds."""
        return (0 <= row < self._rows) and (0 <= col < self._cols)
    
    def get_piece(self, row, col):
        """Get piece at given coordinates."""
        if not self.is_valid_square(row, col):
            raise ValueError(f"Invalid coordinates: ({row}, {col})")
        return self._board[row][col]
    
    def set_piece(self, row, col, piece):
        """Set piece at given coordinates."""
        if not self.is_valid_square(row, col):
            raise ValueError(f"Invalid coordinates: ({row}, {col})")
        self._board[row][col] = piece
    
    def clear_square(self, row, col):
        """Remove piece from square."""
        if not self.is_valid_square(row, col):
            raise ValueError(f"Invalid coordinates: ({row}, {col})")
        self._board[row][col] = None
    
    def get_territory(self, row, col):
        """
        Determine which territory a square belongs to.
        
        Returns:
            'NORTH' if row < TERRITORY_BOUNDARY
            'SOUTH' if row >= TERRITORY_BOUNDARY
        """
        if not self.is_valid_square(row, col):
            raise ValueError(f"Invalid coordinates: ({row}, {col})")
        
        return constants.PLAYER_NORTH if row < self.TERRITORY_BOUNDARY else constants.PLAYER_SOUTH
    
    def is_north_territory(self, row, col):
        """Check if square is in North territory."""
        return self.get_territory(row, col) == constants.PLAYER_NORTH
    
    def is_south_territory(self, row, col):
        """Check if square is in South territory."""
        return self.get_territory(row, col) == constants.PLAYER_SOUTH
    
    def get_territory_squares(self, territory):
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
    def spreadsheet_to_tuple(coord):
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
    def tuple_to_spreadsheet(row, col):
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
        col_letters = []
        while col_index > 0:
            col_index -= 1
            col_letters.insert(0, chr(ord('A') + col_index % 26))
            col_index //= 26
        
        # Format row (direct conversion, no flip needed)
        row_number = row + 1  # Convert to 1-based
        
        return f"{''.join(col_letters)}{row_number}"
    
    @staticmethod
    def tuple_to_index(row, col, board_cols=25):
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
    def index_to_tuple(index, board_cols=25, board_rows=20):
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
