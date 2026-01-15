"""Board display system for console interface.

This module provides board visualization in two modes:
- Curses Mode: Full UI with mouse support and native colors
- Compatibility Mode: ASCII characters without colors

Classes:
    DisplayMode: Enum for display modes (CURSES, COMPATIBILITY)
    BoardDisplay: Main class for rendering board state

Functions:
    render_board(board, mode): Render board in specified mode
    render_game_state(board): Render current game state information
    clear_screen(): Clear terminal screen
"""

import logging
from enum import Enum
from typing import TYPE_CHECKING, Optional, Tuple

from ..board import Board

# Setup logger for display module
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import _curses

try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False
    curses = None  # type: ignore[assignment]


class DisplayMode(Enum):
    """Display mode enumeration - ALL OR NOTHING approach."""
    CURSES = "curses"               # Full curses mode with mouse support and colors
    COMPATIBILITY = "compatibility"  # ASCII-only mode without colors


class BoardDisplay:
    """Board display renderer supporting multiple visualization modes."""

    def __init__(self, mode: DisplayMode = DisplayMode.CURSES):
        """Initialize board display.

        Args:
            mode: Display mode (CURSES or COMPATIBILITY) - set ONCE at startup

        NOTE: No dual-mode rendering. Mode determines entire rendering pipeline.
        """
        self.mode = mode

        # Track render state for mouse coordinate mapping (both modes)
        self.render_state: dict = {
            'header_height': 0,           # Lines before board starts
            'row_header_width': 3,        # Width of row number labels (e.g., "1 ")
            'cell_width': 2,               # Width of each cell (char + space)
            'cell_positions': {},        # Maps (row, col) -> (screen_x, screen_y)
            'highlights': {},             # Maps (row, col) -> highlight_type
        }

        # Curses color pairs (only initialized in CURSES mode)
        if self.mode == DisplayMode.CURSES:
            self.COLOR_NORTH = 1      # Magenta for North units
            self.COLOR_SOUTH = 2      # Cyan for South units
            self.COLOR_WHITE = 3        # White for column headers
            self.COLOR_GRAY = 4        # Gray for alternating column headers
            self.COLOR_SELECTED_BG = 5 # Magenta background for selection
            self.COLOR_DEST_BG = 6     # Cyan background for destination
            self.COLOR_ATTACK_BG = 7   # Red background for attack
            self.COLOR_TERRAIN_DARK = 8   # Dark green for empty terrain outside LOC
            self.COLOR_TERRAIN_LIGHT = 9  # Light green for empty terrain inside LOC

    def render(self, board: Board, stdscr: Optional["_curses.window"] = None) -> Optional[str]:
        """Render the complete board display.

        Args:
            board: The game board to render
            stdscr: curses window (only used in CURSES mode)

        Returns:
            String representation (COMPAT mode) or None (CURSES mode renders directly)
        """
        # Calculate cell positions before rendering for mouse mapping
        self._calculate_cell_positions(board)

        if self.mode == DisplayMode.CURSES:
            # Curses mode: render directly to curses window
            if stdscr:
                self._render_curses(board, stdscr)
            return None
        else:
            # Compatibility mode: return ASCII string
            return self._render_compatibility(board)

    def _render_curses(
        self,
        board: Board,
        stdscr: "_curses.window",
        y_offset: int = 0
    ) -> None:
        """Render board directly to curses window.

        Args:
            board: The game board to render
            stdscr: curses window object
            y_offset: Y position offset (default 0, used in curses_input to avoid
                overwriting game state)
        """
        # Render column headers with alternating colors to avoid overlap
        self._render_column_headers_curses(board, stdscr, y_offset)

        # Render board rows with colors
        for row in range(board.rows):
            self._render_curses_row(board, stdscr, row, y_offset)

        # Render bottom column headers
        self._render_column_headers_curses(board, stdscr, y_offset + board.rows + 1)

    def _render_curses_row(
        self,
        board: Board,
        stdscr: "_curses.window",
        row: int,
        y_offset: int = 0
    ) -> None:
        """Render a single row in curses mode.

        Args:
            board: The game board
            stdscr: curses window object
            row: Row number to render (0-19)
            y_offset: Y position offset
        """
        y_pos = y_offset + row + 1  # +1 for header

        # Row letter (Debord's convention: rows as letters)
        row_letter = chr(ord('A') + row)
        logger.debug(f"Rendering row {row} (0-indexed), row_letter='{row_letter}', y_pos={y_pos}")

        # Explicitly erase the row number area before writing (to clear any terminal artifacts)
        # This prevents stray characters from appearing at the row number position
        stdscr.move(y_pos, 0)
        stdscr.clrtoeol()

        logger.debug(
            f"About to write row_num at (y={y_pos}, x=0) with color pair {self.COLOR_GRAY}"
        )
        stdscr.addstr(y_pos, 0, row_letter, curses.color_pair(self.COLOR_GRAY))
        logger.debug("Successfully wrote row_num")

        # Cells
        for col in range(board.cols):
            x_pos = 3 + (col * 2)
            unit = board.get_unit(row, col)

            highlights: dict = self.render_state.get('highlights', {})
            highlight = highlights.get((row, col))

            if highlight:
                # Render with background color
                self._render_curses_cell_highlight(stdscr, x_pos, y_pos, unit, highlight, board)
            elif unit is None:
                # Empty cell (terrain) - color based on LOC status
                in_loc = board.is_unit_online(row, col, board.turn)
                color = self.COLOR_TERRAIN_LIGHT if in_loc else self.COLOR_TERRAIN_DARK
                stdscr.addstr(y_pos, x_pos, "·", curses.color_pair(color))
            else:
                # Unit with player color
                owner = getattr(unit, 'owner', None)
                color = self.COLOR_NORTH if owner == "NORTH" else self.COLOR_SOUTH

                # Check if unit is online (for curses mode)
                if owner is None:
                    is_online = True  # Fallback if no owner
                else:
                    is_online = board.is_unit_online(row, col, owner)

                # Get appropriate glyph based on online status
                char = self._get_unit_glyph(unit, is_online)
                stdscr.addstr(y_pos, x_pos, char, curses.color_pair(color))

            # Space after cell - check if this is a swift unit and add star
            unit_type = getattr(unit, 'unit_type', '').upper() if unit else ''
            is_swift_unit = unit_type in ('SWIFT_CANNON', 'SWIFT_RELAY')

            if is_swift_unit:
                owner = getattr(unit, 'owner', None) if unit else None
                color = self.COLOR_NORTH if owner == "NORTH" else self.COLOR_SOUTH
                # Render star in the space position
                stdscr.addstr(y_pos, x_pos + 1, "★", curses.color_pair(color))
            else:
                # Regular space for non-swift units
                stdscr.addstr(y_pos, x_pos + 1, " ")

        # Right row letter
        right_row_x = 3 + (board.cols * 2) + 1
        stdscr.addstr(y_pos, right_row_x, row_letter, curses.color_pair(self.COLOR_GRAY))

    def _render_curses_cell_highlight(
        self,
        stdscr: "_curses.window",
        x: int,
        y: int,
        unit: Optional[object],
        highlight_type: str,
        board: Optional[Board] = None,
    ) -> None:
        """Render cell with highlight background.

        Args:
            stdscr: curses window object
            x: X position
            y: Y position
            unit: Unit at cell (or None)
            highlight_type: Type of highlight
        """
        # Get background color pair
        if highlight_type == 'selected':
            bg_pair = self.COLOR_SELECTED_BG
        elif highlight_type == 'destination':
            bg_pair = self.COLOR_DEST_BG
        elif highlight_type == 'attack':
            bg_pair = self.COLOR_ATTACK_BG
        else:
            return

        # Get cell content
        if unit is None:
            text = "·"
        elif board:
            # Check if unit is online (for curses mode) using board's method
            owner = getattr(unit, 'owner', None)
            # Find unit position from board state
            is_online = True
            if owner is None:
                # No owner - assume online
                pass
            else:
                for row in range(board.rows):
                    for col in range(board.cols):
                        if board.get_unit(row, col) == unit:
                            is_online = board.is_unit_online(row, col, owner)
                            break
                    if not is_online:  # Found unit and it's offline
                        break
            text = self._get_unit_glyph(unit, is_online)
        else:
            # Fallback if no board provided
            text = self._get_unit_glyph(unit, online=True)

        # Render with background color
        stdscr.addstr(y, x, text, curses.color_pair(bg_pair))

        # Check if this is a swift unit and add star after the cell
        unit_type = getattr(unit, 'unit_type', '').upper() if unit else ''
        is_swift_unit = unit_type in ('SWIFT_CANNON', 'SWIFT_RELAY')

        if is_swift_unit:
            owner = getattr(unit, 'owner', None) if unit else None
            color = self.COLOR_NORTH if owner == "NORTH" else self.COLOR_SOUTH
            # Render star in the space position with same color as unit
            stdscr.addstr(y, x + 1, "★", curses.color_pair(color))
        else:
            # Regular space for non-swift units
            stdscr.addstr(y, x + 1, " ")

    def _get_column_headers_text(self) -> str:
        """Get column headers as plain text.

        Returns:
            String of column numbers (spreadsheet style: columns as numbers)
        """
        headers = ["  "]  # Space for row letter (2 chars to match row letters)

        for col in range(25):
            # Column numbers 1-25 (Debord's convention: columns as numbers)
            # Right-justify to 2 chars
            col_num = str(col + 1).rjust(2)
            headers.append(col_num)

        headers.append("  ")  # Space for row letter

        return "".join(headers)

    def _render_column_headers_curses(
        self,
        board: Board,
        stdscr: "_curses.window",
        y_offset: int = 0
    ) -> None:
        """Render column headers with alternating colors to avoid visual overlap.

        Args:
            board: The game board
            stdscr: curses window object
            y_offset: Y position offset
        """
        # Space for row letter
        stdscr.addstr(y_offset, 0, "  ", curses.color_pair(self.COLOR_WHITE))

        for col in range(board.cols):
            # Column numbers 1-25
            col_num = str(col + 1).rjust(2)

            # Alternate between white and gray for subtle pattern
            color = self.COLOR_WHITE if col % 2 == 0 else self.COLOR_GRAY
            # Position after row header space
            x_pos = 2 + (col * 2)

            # Apply dim attribute for gray color to create subtle difference
            attrs = curses.A_DIM if color == self.COLOR_GRAY else 0
            stdscr.addstr(y_offset, x_pos, col_num, curses.color_pair(color) | attrs)

        # Space for row letter
        stdscr.addstr(y_offset, 2 + (board.cols * 2), "  ", curses.color_pair(self.COLOR_WHITE))

    def _get_unit_glyph(self, unit: object, online: bool = True) -> str:
        """Get the visual glyph for a unit based on type and online status.

        NOTE: Stars for Swift units are added separately in rendering logic,
        not in this glyph method. This method only returns the base glyph.

        Args:
            unit: The unit to get glyph for
            online: Whether the unit is online (default True)

        Returns:
            Character representing the unit (solid/hollow based on online status)
        """
        unit_type = getattr(unit, 'unit_type', '?').upper()

        # Unicode characters for curses mode
        if self.mode == DisplayMode.CURSES:
            # Network units (Arsenal, Relay, Swift Relay) - ALWAYS solid
            if unit_type == 'ARSENAL':
                return '☗'
            elif unit_type == 'RELAY':
                return '♝'
            elif unit_type == 'SWIFT_RELAY':
                return '♝'  # Star added separately

            # Combat units - Solid when online, Hollow when offline
            if online:
                # Online (solid) unicode characters
                chars_online = {
                    "INFANTRY": "♟",        # Pawn
                    "CAVALRY": "♞",         # Knight
                    "CANNON": "♜",          # Rook
                    "SWIFT_CANNON": "♜",    # Same as cannon (star added separately)
                }
                return chars_online.get(unit_type, "?")
            else:
                # Offline (hollow) unicode characters
                chars_offline = {
                    "INFANTRY": "♙",        # Hollow Pawn
                    "CAVALRY": "♘",         # Hollow Knight
                    "CANNON": "♖",          # Hollow Rook
                    "SWIFT_CANNON": "♖",    # Same as cannon (star added separately)
                }
                return chars_offline.get(unit_type, "?")

        else:
            # ASCII characters for compatibility mode
            # Online/Offline status is NOT displayed in compatibility mode
            chars_north = {
                "INFANTRY": "I",
                "CAVALRY": "C",
                "CANNON": "K",
                "SWIFT_CANNON": "W",
                "RELAY": "R",
                "SWIFT_RELAY": "X",
                "ARSENAL": "A",
            }

            char = chars_north.get(unit_type, "?")

            # Lowercase for South player
            owner = getattr(unit, 'owner', None)
            if owner == "SOUTH":
                char = char.lower()

            return char

    def _get_unit_char(self, unit: object) -> str:
        """Get character for unit (unicode in curses mode, ASCII in compat mode).

        Args:
            unit: The unit to get character for

        Returns:
            Character representing the unit (uppercase/unicode for North, lowercase for South)

        DEPRECATED: This method is kept for backward compatibility.
        New code should use _get_unit_glyph() with online status.
        """
        # Default to online for backward compatibility
        return self._get_unit_glyph(unit, online=True)

    def _render_compatibility(self, board: Board) -> str:
        """Render board in compatibility mode (ASCII).

        Args:
            board: The game board to render

        Returns:
            String representation (ASCII only)
        """
        lines = []

        # Column headers
        lines.append(self._get_column_headers_text())

        # Board rows
        for row in range(board.rows):
            lines.append(self._render_row_compat(board, row))

        # Column headers (bottom)
        lines.append(self._get_column_headers_text())

        return "\n".join(lines)

    def _render_row_compat(self, board: Board, row: int) -> str:
        """Render a single row in compatibility mode.

        Args:
            board: The game board
            row: Row number to render (0-19)

        Returns:
            String representation of row (ASCII)
        """
        cells = []

        # Row letter (Debord's convention: rows as letters)
        row_letter = chr(ord('A') + row)
        cells.append(row_letter.rjust(2))

        for col in range(board.cols):
            cell = self._render_cell_compat(board, row, col)
            cells.append(cell)

        # Row letter (right)
        cells.append(row_letter.rjust(2))

        return " ".join(cells)

    def _render_cell_compat(self, board: Board, row: int, col: int) -> str:
        """Render a single cell in compatibility mode.

        Args:
            board: The game board
            row: Row number (0-19)
            col: Column number (0-24)

        Returns:
            String representation of the cell (ASCII)
        """
        unit = board.get_unit(row, col)

        if unit is None:
            # Render terrain only
            return "_"
        else:
            # Render unit
            return self._get_unit_char(unit)

    def _calculate_cell_positions(self, board: Board) -> None:
        """Calculate screen positions for all board cells.

        Args:
            board: The game board to render

        This method calculates where each board cell appears on screen
        for mouse coordinate mapping.
        """
        # Get header lines (column headers) - use text version for both modes
        header_lines = [self._get_column_headers_text()]
        self.render_state['header_height'] = len(header_lines)

        # Row header width: "1 " = 3 characters
        self.render_state['row_header_width'] = 3

        # Cell width: char + space = 2 characters
        self.render_state['cell_width'] = 2

        # Calculate positions for each cell
        cell_positions: dict = self.render_state.get('cell_positions', {})
        row_header_width = self.render_state['row_header_width']
        cell_width = self.render_state['cell_width']
        header_height = self.render_state['header_height']

        for row in range(board.rows):
            for col in range(board.cols):
                # Calculate screen position
                screen_x = row_header_width + (col * cell_width)
                screen_y = header_height + row

                cell_positions[(row, col)] = (screen_x, screen_y)
        self.render_state['cell_positions'] = cell_positions

    def screen_to_board(self, screen_x: int, screen_y: int) -> Optional[Tuple[int, int]]:
        """Convert screen coordinates to board coordinates.

        Args:
            screen_x: Screen column position (0-based)
            screen_y: Screen row position (0-based)

        Returns:
            Tuple of (row, col) or None if outside board

        Note: This performs a simple lookup. The screen coordinates
        should match the calculated positions from _calculate_cell_positions.
        """
        # Check each cell's position for match
        cell_positions: dict = self.render_state.get('cell_positions', {})
        for (row, col), (bx, by) in cell_positions.items():
            # Check if click is within cell bounds
            # Cell occupies 2 characters (glyph + space)
            if bx <= screen_x < bx + 1 and by == screen_y:
                return (row, col)

        # No matching cell found
        return None

    def set_highlight(self, row: int, col: int, highlight_type: str) -> None:
        """Set highlight for a specific cell.

        Args:
            row: Board row (0-19)
            col: Board column (0-24)
            highlight_type: Type of highlight ('selected', 'destination', 'attack')
        """
        highlights: dict = self.render_state.get('highlights', {})
        highlights[(row, col)] = highlight_type
        self.render_state['highlights'] = highlights

    def clear_highlights(self) -> None:
        """Clear all cell highlights."""
        highlights: dict = self.render_state.get('highlights', {})
        highlights.clear()
        self.render_state['highlights'] = highlights


def render_game_state(board: Board, display_mode: DisplayMode) -> str:
    """Render current game state information.

    Args:
        board: The game board
        display_mode: Display mode for coloring

    Returns:
        String with game state information
    """
    lines = []

    lines.append("=" * 50)
    lines.append("PYKRIEG - Guy Debord's Le Jeu de la Guerre")
    lines.append("=" * 50)
    lines.append("")

    # Turn information
    lines.append(f"Turn: {board.turn_number}")
    lines.append(f"Current Player: {board.turn}")
    lines.append(f"Phase: {'Movement' if board.current_phase == 'M' else 'Battle'}")
    lines.append("")

    # Movement phase info
    if board.current_phase == 'M':
        moves_made = board.get_moves_this_turn()
        moves_remaining = 5 - moves_made
        lines.append(f"Moves: {moves_made}/5 (Remaining: {moves_remaining})")
        lines.append("")

    # Battle phase info
    if board.current_phase == 'B':
        attacks_made = board.get_attacks_this_turn()
        attacks_remaining = 1 - attacks_made
        lines.append(f"Attacks: {attacks_made}/1 (Remaining: {attacks_remaining})")
        lines.append("")

    # Display mode
    mode_str = (
        "Curses (Full UI with Mouse)"
        if display_mode == DisplayMode.CURSES
        else "Compatibility (ASCII only)"
    )
    lines.append(f"Display Mode: {mode_str}")
    lines.append("")

    return "\n".join(lines)


def clear_screen() -> None:
    """Clear terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')
