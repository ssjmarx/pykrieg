"""
FEN (Forsyth-Edwards Notation) for Pykrieg board serialization.

This module implements FEN serialization/deserialization for the
0.1.0 version of Pykrieg, supporting basic board state representation.
"""

from typing import TYPE_CHECKING

from . import constants

if TYPE_CHECKING:
    from .board import Board


class Fen:
    """FEN (Forsyth-Edwards Notation) for Pykrieg board serialization.

    This is 0.1.0 basic implementation supporting:
    - Board serialization/deserialization
    - Basic piece representation
    - Turn tracking

    FEN Format (0.1.4 - With Turn State):
    <board_data>/<turn>/<phase>/<actions>/<turn_number>/<retreats>

    Where:
    - board_data: Row-by-row representation of pieces (20 rows separated by '/')
    - turn: Current player ('N' or 'S')
    - phase: Turn phase ('M' for movement, 'B' for battle)
    - actions: Move pairs or attack target (empty list in 0.1.4)
    - turn_number: Current turn number (1, 2, 3, ...)
    - retreats: List of retreat positions [row1,col1,row2,col2,...]

    Note: Retreats are tracked in-memory and may be lost on FEN serialization.

    Board Data Format:
    - Each row separated by '/'
    - Pieces: unit_type (e.g., 'I', 'C', 'K', 'A', 'R', 'W', 'X')
    - Uppercase: North pieces
    - Lowercase: South pieces
    - Empty squares: '_'

    Example FEN:
    ___________________________/.../_________________________/N/M/[]
    """

    # Use piece symbols from constants
    PIECE_SYMBOLS = constants.FEN_SYMBOLS
    SYMBOL_TO_PIECE = constants.SYMBOL_TO_UNIT

    @staticmethod
    def board_to_fen(board: 'Board') -> str:
        """
        Convert Board object to FEN string (0.1.4 with turn state).

        Args:
            board: Board object

        Returns:
            FEN string representation

        Example:
            Empty board: "_________________________/.../N/M/[]/1/[]"
        """
        # Build board data section
        rows_fen = []
        for row in range(board.rows):
            row_fen = []
            for col in range(board.cols):
                piece = board.get_piece(row, col)
                if piece is None:
                    row_fen.append('_')
                else:
                    # Handle both Unit objects and dict-style pieces for backward compatibility
                    if hasattr(piece, 'unit_type'):
                        unit_type = getattr(piece, 'unit_type', None)
                        owner = getattr(piece, 'owner', None)
                    else:
                        # Dict-style pieces use dict access, not getattr
                        unit_type = piece.get('type') if isinstance(piece, dict) else None
                        owner = piece.get('owner') if isinstance(piece, dict) else None

                    if unit_type is None:
                        raise ValueError("Piece has no unit_type attribute")
                    symbol = Fen.PIECE_SYMBOLS[unit_type]
                    # Convert to lowercase for South
                    if owner == 'SOUTH':
                        symbol = symbol.lower()
                    row_fen.append(symbol)
            rows_fen.append(''.join(row_fen))

        board_data = '/'.join(rows_fen)

        # Build turn info
        turn_char = 'N' if board.turn == constants.PLAYER_NORTH else 'S'
        phase = board.current_phase
        actions = '[]'  # No actions in 0.1.4
        turn_number = str(board.turn_number)

        # Build retreats list: [row1,col1,row2,col2,...]
        retreats = board.get_pending_retreats()
        retreat_list = []
        for row, col in retreats:
            retreat_list.extend([str(row), str(col)])
        retreats_str = f"[{','.join(retreat_list)}]"

        # Assemble FEN (0.1.4 format)
        fen = f"{board_data}/{turn_char}/{phase}/{actions}/{turn_number}/{retreats_str}"
        return fen

    @staticmethod
    def fen_to_board(fen_string: str) -> 'Board':
        """
        Convert FEN string to Board object (0.1.4 with turn state).

        Args:
            fen_string: FEN string

        Returns:
            Board object

        Example:
            "_________________________/.../N/M/[]/1/[]" -> Board
        """
        if not isinstance(fen_string, str):
            raise TypeError(f"FEN must be string, got {type(fen_string)}")

        # Remove newlines to handle user formatting
        fen_string = fen_string.replace('\n', '')

        parts = fen_string.split('/')
        if len(parts) not in [23, 25]:  # 0.1.0 format (23) or 0.1.4 format (25)
            raise ValueError(f"Invalid FEN: expected 23 or 25 parts, got {len(parts)}")

        # Parse board data (first 20 parts)
        board_data = parts[:20]
        turn_char = parts[20]

        # Create board
        from .board import Board
        board = Board()

        # Set turn
        if turn_char not in ['N', 'S']:
            raise ValueError(f"Invalid turn character: {turn_char}")
        board._turn = constants.PLAYER_NORTH if turn_char == 'N' else constants.PLAYER_SOUTH

        # Parse board rows
        for row, row_data in enumerate(board_data):
            if len(row_data) != 25:
                raise ValueError(f"Invalid FEN row {row}: expected 25 chars, got {len(row_data)}")

            for col, char in enumerate(row_data):
                if char == '_':
                    board.clear_square(row, col)
                else:
                    # Determine piece type and owner
                    is_south = char.islower()
                    symbol = char.upper()

                    if symbol not in Fen.SYMBOL_TO_PIECE:
                        raise ValueError(f"Invalid piece symbol: {symbol}")

                    piece_type = Fen.SYMBOL_TO_PIECE[symbol]
                    owner = constants.PLAYER_SOUTH if is_south else constants.PLAYER_NORTH

                    # Create Unit object using factory function
                    from .pieces import create_piece
                    piece = create_piece(piece_type, owner)
                    board.place_unit(row, col, piece)

        # Parse 0.1.4 turn state if present
        if len(parts) == 25:
            phase = parts[21]
            # actions = parts[22]  # Not used in 0.1.4
            turn_number = parts[23]
            retreats_str = parts[24]

            # Set phase
            if phase in [constants.PHASE_MOVEMENT, constants.PHASE_BATTLE]:
                board._current_phase = phase

            # Set turn number
            try:
                board._turn_number = int(turn_number)
            except ValueError as err:
                raise ValueError(f"Invalid turn number: {turn_number}") from err

            # Parse retreats: [row1,col1,row2,col2,...]
            if retreats_str != '[]':
                retreats_str = retreats_str.strip('[]')
                if retreats_str:
                    retreat_parts = retreats_str.split(',')
                    if len(retreat_parts) % 2 != 0:
                        raise ValueError(f"Invalid retreats format: {retreats_str}")

                    for i in range(0, len(retreat_parts), 2):
                        try:
                            row = int(retreat_parts[i])
                            col = int(retreat_parts[i + 1])
                            board.add_pending_retreat(row, col)
                        except (ValueError, IndexError) as err:
                            raise ValueError(f"Invalid retreat position: {retreats_str}") from err

        # Network recalculation is now lazy - networks will be calculated on-demand
        # when needed via _ensure_network_calculated()

        return board
