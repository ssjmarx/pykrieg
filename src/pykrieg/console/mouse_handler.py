"""Mouse input handler for console interface.

This module handles mouse events for click-to-coordinate entry,
allowing players to click squares to queue commands.

Classes:
    MouseHandler: Main class for mouse input handling

Functions:
    detect_mouse_support(): Check if terminal supports mouse input
"""

from typing import List, Optional, Tuple


class MouseHandler:
    """Handle mouse input for click-to-coordinate entry.

    Mouse Interaction Design:
    - Click on unit: Queue as source for move
    - Click on destination: Queue as target, complete move
    - Click on enemy in battle phase: Queue as attack target
    - Visual feedback: Highlight selected squares
    - Click outside board: Ignore or clear selection
    """

    def __init__(self, board, display) -> None:  # type: ignore[no-untyped-def]
        """Initialize mouse handler.

        Args:
            board: The game board
            display: BoardDisplay instance
        """
        self.board = board
        self.display = display

        # State tracking
        self.selected_square: Optional[Tuple[int, int]] = None
        self.command_queue: List[str] = []

        # Mouse support detection
        self.mouse_available = self._detect_mouse_support()

    def _detect_mouse_support(self) -> bool:
        """Detect if mouse support is available.

        Returns:
            True if mouse support available, False otherwise
        """
        # Check for prompt_toolkit availability
        try:
            import importlib.util
            return importlib.util.find_spec("prompt_toolkit") is not None
        except ImportError:
            return False

    def handle_mouse_click(self, row: int, col: int) -> Optional[str]:
        """Handle a mouse click on a board square.

        Args:
            row: Row number (0-19)
            col: Column number (0-24)

        Returns:
            Command string to append to buffer, or None to ignore
        """
        # Validate coordinates
        if not (0 <= row < 20 and 0 <= col < 25):
            return None

        phase = self.board.current_phase

        if phase == 'M':
            return self._handle_movement_phase_click(row, col)
        elif phase == 'B':
            return self._handle_battle_phase_click(row, col)
        else:
            return None

    def _handle_movement_phase_click(self, row: int, col: int) -> Optional[str]:
        """Handle click during movement phase.

        Args:
            row: Row number
            col: Column number

        Returns:
            Command string or None (spreadsheet-style coordinates: numbers + letters)
        """
        unit = self.board.get_unit(row, col)

        # Click on empty square
        if unit is None:
            # If we have a selected unit, this is destination
            if self.selected_square is not None:
                from_row, from_col = self.selected_square
                from_sheet = self.board.tuple_to_spreadsheet(from_row, from_col)
                to_sheet = self.board.tuple_to_spreadsheet(row, col)
                self.selected_square = None  # Clear selection
                return f"{from_sheet} {to_sheet}"
            return None

        # Click on unit
        if unit.owner == self.board.turn:
            if self.selected_square is None:
                # First click: Select this unit as source
                self.selected_square = (row, col)
                return None
            elif self.selected_square == (row, col):
                # Click same unit again: Deselect
                self.selected_square = None
                return None
            else:
                # Different unit selected: Replace selection
                self.selected_square = (row, col)
                return None

        # Click on opponent's unit: Ignore
        return None

    def _handle_battle_phase_click(self, row: int, col: int) -> Optional[str]:
        """Handle click during battle phase.

        Args:
            row: Row number
            col: Column number

        Returns:
            Command string or None (spreadsheet-style coordinates: numbers + letters)
        """
        unit = self.board.get_unit(row, col)

        # Click on enemy unit: Queue attack
        if unit is not None and unit.owner != self.board.turn:
            target_sheet = self.board.tuple_to_spreadsheet(row, col)
            self.selected_square = None
            return f"attack {target_sheet}"

        # Click anywhere else: Ignore
        return None

    def clear_selection(self) -> None:
        """Clear current selection."""
        self.selected_square = None

    def get_status_display(self) -> str:
        """Get display string showing current mouse status.

        Returns:
            Status string for display (spreadsheet-style coordinates: numbers + letters)
        """
        if not self.mouse_available:
            return "[MOUSE DISABLED] Keyboard input only"

        if self.selected_square:
            row, col = self.selected_square
            coord = self.board.tuple_to_spreadsheet(row, col)
            return f"[MOUSE ACTIVE] Selected: {coord} (Click destination or ESC to cancel)"
        else:
            return "[MOUSE ACTIVE] Click a unit to select"

    def get_buffer_display(self) -> str:
        """Get display string showing queued commands.

        Returns:
            Buffer display string
        """
        if not self.command_queue:
            return "Queued Commands: (None)"

        lines = ["Queued Commands:"]
        for i, cmd in enumerate(self.command_queue):
            lines.append(f"  {i+1}. {cmd}")

        if self.selected_square:
            row, col = self.selected_square
            lines.append(f"  → Next: {row},{col}")

        return "\n".join(lines)


def detect_mouse_support() -> bool:
    """Detect if terminal supports mouse input.

    Returns:
        True if mouse support available, False otherwise
    """
    try:
        import importlib.util
        return importlib.util.find_spec("prompt_toolkit") is not None
    except ImportError:
        return False
