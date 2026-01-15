"""Curses-based input handler for console interface.

This module provides full curses integration with mouse support,
replacing the prompt_toolkit-based approach.

Classes:
    CursesInput: Main class for curses input handling

Functions:
    detect_curses_support(): Check if curses is available
"""

import curses
import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import _curses

# Setup logger for curses module
logger = logging.getLogger(__name__)

# Try to import curses
try:
    import curses
    from curses import wrapper
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False


class CursesInput:
    """Handle curses-based input with mouse support."""

    def __init__(self, board, display) -> None:  # type: ignore[no-untyped-def]
        """Initialize curses input handler.

        Args:
            board: The game board
            display: BoardDisplay instance
        """
        self.board = board
        self.display = display

        # Color pair indices (1-based for curses)
        self.COLOR_NORTH = 1      # Magenta for North units
        self.COLOR_SOUTH = 2      # Cyan for South units
        self.COLOR_WHITE = 3       # White for column headers
        self.COLOR_GRAY = 4        # Gray for alternating column headers
        self.COLOR_SELECTED_BG = 5 # Magenta background for selection
        self.COLOR_DEST_BG = 6     # Cyan background for destination
        self.COLOR_ATTACK_BG = 7   # Red background for attack
        self.COLOR_DEFENSE_BG = 8  # Blue background for defense
        self.COLOR_BLOCKED_BG = 9   # Gray background for blocked units
        self.COLOR_CHARGING_BG = 10  # Gold background for charging cavalry
        self.COLOR_TERRAIN_DARK = 11   # Dark green for empty terrain outside LOC
        self.COLOR_TERRAIN_LIGHT = 12  # Light green for empty terrain inside LOC

    def _init_colors(self, stdscr: "_curses.window") -> None:
        """Initialize curses color pairs.

        Args:
            stdscr: curses window object
        """
        curses.start_color()
        curses.use_default_colors()

        # Initialize color pairs (foreground, background)
        curses.init_pair(self.COLOR_NORTH, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_SOUTH, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_WHITE, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_GRAY, curses.COLOR_WHITE, curses.COLOR_BLACK)

        # Background colors for highlights
        curses.init_pair(self.COLOR_SELECTED_BG, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        curses.init_pair(self.COLOR_DEST_BG, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(self.COLOR_ATTACK_BG, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(self.COLOR_DEFENSE_BG, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(self.COLOR_BLOCKED_BG, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(self.COLOR_CHARGING_BG, curses.COLOR_WHITE, curses.COLOR_YELLOW)

        # Terrain colors for empty squares
        curses.init_pair(self.COLOR_TERRAIN_DARK, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_TERRAIN_LIGHT, curses.COLOR_CYAN, curses.COLOR_BLACK)

    def get_input(self, prompt: str) -> Optional[str]:
        """Get input using curses with mouse support.

        Args:
            prompt: The prompt string to display

        Returns:
            User input string, or None if quit
        """
        logger.debug(f"get_input called with prompt: {prompt[:50]}...")
        try:
            result = wrapper(self._curses_main_loop, prompt)
            logger.debug(f"get_input returned: {result}")

            # If wrapper returned None (terminal too small), fall back to compat
            if result is None:
                logger.debug("Curses wrapper returned None, falling back to compat mode")
                # Clear screen before printing fallback messages
                self._clear_screen()
                print("Terminal too small for curses mode.")
                print("Falling back to compatibility mode...")
                # Get user input and prefix with marker so game.py knows we're in fallback mode
                user_response = input(prompt)
                return f"__FALLBACK_TO_COMPAT__{user_response}"

            return result
        except Exception as e:
            logger.error(f"get_input error: {e}", exc_info=True)
            # Clear screen before printing fallback messages
            self._clear_screen()
            print(f"Curses error: {e}")
            print("Falling back to compatibility mode...")
            # Get user input and prefix with marker
            user_response = input(prompt)
            return f"__FALLBACK_TO_COMPAT__{user_response}"

    def _clear_screen(self) -> None:
        """Clear terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def update_board(self, board) -> None:  # type: ignore[no-untyped-def]
        """Update the board reference after loading or phase changes.

        Args:
            board: The new board object
        """
        self.board = board

    def show_message(self, message: str) -> None:
        """Display a message in curses mode with board visible.

        Args:
            message: The message to display

        This is used for move confirmations, attack results, etc.
        """
        try:
            wrapper(self._curses_message_loop, message)
        except Exception:
            # Clear terminal before printing fallback message to prevent accumulation
            self._clear_screen()
            print(message)
            input("Press Enter to continue...")

    def _curses_main_loop(self, stdscr: "_curses.window", prompt: str) -> Optional[str]:
        """Main curses event loop.

        Args:
            stdscr: curses window object
            prompt: The prompt string

        Returns:
            User input string
        """
        # Initialize colors first (this ensures curses is fully set up)
        self._init_colors(stdscr)

        # Initialize curses
        curses.curs_set(1)  # Show cursor
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        stdscr.nodelay(False)  # Blocking input

        # Input buffer
        input_buffer = ""

        while True:
            # Clear and render
            self._render_curses(stdscr, prompt, input_buffer)

            # Get input
            ch = stdscr.getch()

            # Handle mouse events
            if ch == curses.KEY_MOUSE:
                try:
                    _, mouse_x, mouse_y, _, mouse_state = curses.getmouse()
                    if mouse_state & curses.BUTTON1_CLICKED:
                        # Left click
                        board_coords = self._screen_to_board(mouse_x, mouse_y)
                        if board_coords:
                            row, col = board_coords
                            # Return a special marker for mouse clicks
                            return f"MOUSE_CLICK:{row},{col}"
                except Exception:
                    pass

            # Handle keyboard input
            elif ch == curses.KEY_ENTER or ch == 10:
                # Enter key
                return input_buffer if input_buffer else None
            elif ch == curses.KEY_BACKSPACE or ch == 127 or ch == 8:
                # Backspace
                if input_buffer:
                    input_buffer = input_buffer[:-1]
            elif ch == 27:  # ESC key
                # ESC - will be handled by game to clear selection
                return "ESC"
            elif ch == curses.KEY_RESIZE:
                # Terminal resize - re-render
                continue
            elif 32 <= ch <= 126:  # Printable characters
                input_buffer += chr(ch)
            # Ignore other keys

    def _render_curses(self, stdscr: "_curses.window", prompt: str, input_buffer: str) -> None:
        """Render game state and board in curses mode.

        Args:
            stdscr: curses window object
            prompt: The prompt string (may contain newlines)
            input_buffer: Current input buffer
        """
        logger.debug(
            f"_render_curses called - prompt='{prompt[:50]}...', "
            f"input_buffer='{input_buffer}'"
        )
        stdscr.clear()
        logger.debug("Screen cleared")

        # Render game state info
        self._render_game_state(stdscr)

        # Render board with Y offset to avoid overwriting game state info
        # Game state has base 8 lines + 2-4 more lines for phase info and display mode
        # We'll calculate the actual offset after rendering
        game_state_lines = self._get_game_state_line_count()
        self.display._render_curses(self.board, stdscr, y_offset=game_state_lines)

        # Render prompt and input
        # Handle multi-line prompts by splitting on newlines
        prompt_lines = prompt.split('\n')
        board_height = self.board.rows + 2  # Board rows + top and bottom headers
        y_pos = game_state_lines + board_height + 1  # Game state + board + spacing

        # Render each line of the prompt
        for line in prompt_lines:
            stdscr.addstr(y_pos, 0, line, curses.color_pair(self.COLOR_GRAY))
            y_pos += 1

        # Render input buffer on the next line
        stdscr.addstr(y_pos, 0, "> " + input_buffer, curses.color_pair(self.COLOR_GRAY))

        # Refresh
        stdscr.refresh()

    def _get_game_state_line_count(self) -> int:
        """Calculate the number of lines in game state display.

        Returns:
            Number of lines used for game state display
        """
        # Optimized compact display:
        # Line 1: Turn info header with turn/player/phase/moves all combined
        # Line 2: Divider
        return 2

    def _render_game_state(self, stdscr: "_curses.window") -> None:
        """Render game state information.

        Args:
            stdscr: curses window object
        """
        lines = []

        # Compact single-line game header with turn info
        phase_str = 'M' if self.board.current_phase == 'M' else 'B'
        if self.board.current_phase == 'M':
            moves_made = self.board.get_moves_this_turn()
            moves_remaining = 5 - moves_made
            lines.append(
                f"Turn: {self.board.turn_number} {self.board.turn} {phase_str} "
                f"Moves: {moves_made}/5 ({moves_remaining})"
            )
        else:
            attacks_made = self.board.get_attacks_this_turn()
            attacks_remaining = 1 - attacks_made
            lines.append(
                f"Turn: {self.board.turn_number} {self.board.turn} {phase_str} "
                f"Attack: {attacks_made}/1 ({attacks_remaining})"
            )

        # Divider before board
        lines.append("=" * 54)

        logger.debug(f"Rendering game state: {len(lines)} lines")
        for i, line in enumerate(lines):
            logger.debug(f"Line {i}: {line}")
            stdscr.addstr(i, 0, line, curses.color_pair(self.COLOR_GRAY))
        logger.debug("Finished rendering game state")

    def _curses_message_loop(self, stdscr: "_curses.window", message: str) -> None:
        """Display a message with board visible.

        Args:
            stdscr: curses window object
            message: The message to display (may contain newlines)

        Shows the board with game state, then displays the message
        below of board, waiting for user to press Enter.
        """
        # Initialize colors
        self._init_colors(stdscr)

        # Clear screen completely to avoid overwriting
        stdscr.clear()

        # Render game state and board
        self._render_game_state(stdscr)
        game_state_lines = self._get_game_state_line_count()
        self.display._render_curses(self.board, stdscr, y_offset=game_state_lines)

        # Calculate message position
        board_height = self.board.rows + 2  # Board rows + top and bottom headers
        message_y = game_state_lines + board_height + 2  # Game state + board + spacing

        # Render message (handle multi-line messages)
        message_lines = message.split('\n')
        for i, line in enumerate(message_lines):
            stdscr.addstr(message_y + i, 0, line, curses.color_pair(self.COLOR_GRAY))

        # Render "Press Enter to continue" below message
        prompt_y = message_y + len(message_lines)
        stdscr.addstr(prompt_y, 0, "Press Enter to continue...", curses.color_pair(self.COLOR_GRAY))

        # Refresh
        stdscr.refresh()

        # Wait for Enter key
        while True:
            ch = stdscr.getch()
            if ch == curses.KEY_ENTER or ch == 10:
                break

    def _screen_to_board(self, screen_x: int, screen_y: int) -> Optional[tuple]:
        """Convert screen coordinates to board coordinates.

        Args:
            screen_x: Screen column position
            screen_y: Screen row position

        Returns:
            Tuple of (row, col) or None if outside board

        Note: Board is rendered with Y offset based on game state lines.
        Game state lines vary based on phase info and display mode.
        """
        # Get actual game state line count
        game_state_lines = self._get_game_state_line_count()

        # Check if click is in game state area
        if screen_y < game_state_lines:
            return None

        # Adjust for game state offset
        adjusted_y = screen_y - game_state_lines

        # Check top header line (column headers)
        if adjusted_y == 0:
            return None

        # Check bottom header line (column headers)
        if adjusted_y == self.board.rows + 1:
            return None

        # Adjust for header
        board_y = adjusted_y - 1

        # Check row bounds
        if board_y < 0 or board_y >= self.board.rows:
            return None

        # Check row number column (first 3 chars)
        if screen_x < 3:
            return None

        # Calculate column
        board_x = (screen_x - 3) // 2

        # Check column bounds
        if board_x < 0 or board_x >= self.board.cols:
            return None

        return (board_y, board_x)


def detect_curses_support() -> bool:
    """Detect if curses is available.

    Returns:
        True if curses support available, False otherwise
    """
    return CURSES_AVAILABLE
