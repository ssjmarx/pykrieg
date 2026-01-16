"""Main game loop for console interface.

This module manages the game loop, user interaction, and command execution.

Classes:
    ConsoleGame: Main game controller

Functions:
    main(): Entry point for console game
"""

import logging
import os
from typing import TYPE_CHECKING, Optional, Tuple

from .parser import Command

if TYPE_CHECKING:
    pass

from ..board import Board
from ..fen import Fen
from .display import BoardDisplay, DisplayMode, clear_screen, render_game_state
from .input_buffer import CommandBuffer, parse_multi_command_input
from .parser import get_help_text, parse_command, validate_command
from .terminal import detect_best_mode


class ConsoleGame:
    """Console game controller."""

    def __init__(self, display_mode: Optional[str] = None):
        """Initialize console game.

        Args:
            display_mode: Display mode ('curses' or 'compat'), auto-detect if None

        NOTE: Display mode is determined ONCE at startup. No mid-game switching
        except via 'mode curses' or 'mode compat' commands.
        """
        # Configure logging
        self._setup_logging()

        # Load board
        self.board = self._load_default_position()

        # Determine display mode (ONE TIME)
        if display_mode is None:
            mode_str = detect_best_mode()
        else:
            mode_str = display_mode

        self.display_mode = (
            DisplayMode.CURSES if mode_str == 'curses' else DisplayMode.COMPATIBILITY
        )
        self.display = BoardDisplay(self.display_mode)

        # Initialize appropriate input handler
        if self.display_mode == DisplayMode.CURSES:
            from .curses_input import CURSES_AVAILABLE, CursesInput
            if not CURSES_AVAILABLE:
                # Fallback to compatibility mode
                self.display_mode = DisplayMode.COMPATIBILITY
                self.display = BoardDisplay(self.display_mode)
                self.curses_input = None
            else:
                self.curses_input = CursesInput(self.board, self.display)
        else:
            self.curses_input = None

        # Initialize command buffer
        self.command_buffer = CommandBuffer()
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.running = True

    def _setup_logging(self) -> None:
        """Configure logging to file for debugging."""
        log_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'pykrieg_debug.log'
        )
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Pykrieg game initialized")

    def run(self) -> None:
        """Run the main game loop."""
        self._display_welcome()
        self._render()

        while self.running:
            self._prompt_for_command()

    def _display_welcome(self) -> None:
        """Display welcome message."""
        lines = [
            "",
            "╔══════════════════════════════════════════════════╗",
            "║                                                  ║",
            "║        PYKRIEG - Console Interface v0.2.1        ║",
            "║         Guy Debord's Le Jeu de la Guerre         ║",
            "║                                                  ║",
            "╚══════════════════════════════════════════════════╝",
            "",
            "Type 'help' for commands, 'quit' to exit.",
            "",
        ]

        print("\n".join(lines))
        input("Press Enter to start...")

    def _render(self) -> None:
        """Render current game state."""
        if self.display_mode == DisplayMode.CURSES:
            # Curses mode: rendering handled by curses_input
            return

        # Compatibility mode: use standard rendering
        self._render_compat_fallback()

        # Display retreat warning if applicable
        self._display_retreat_warning()

        # Display victory message if game over
        if self.board.is_game_over():
            self._display_victory_message()

    def _display_retreat_warning(self) -> None:
        """Display warning for units that must retreat."""
        retreats = self.board.get_units_must_retreat()
        if retreats:
            retreat_units = []
            for row, col in retreats:
                unit = self.board.get_unit(row, col)
                if unit:
                    coord = self.board.tuple_to_spreadsheet(row, col)
                    unit_type = getattr(unit, 'unit_type', 'Unit')
                    retreat_units.append(f"{unit_type} at {coord}")

            retreat_msg = "\nUNITS MUST RETREAT:\n"
            retreat_msg += "   " + ", ".join(retreat_units)
            retreat_msg += "\n   These units must move before other units can move."
            print(retreat_msg)

    def _render_compat_fallback(self) -> None:
        """Render in compatibility mode (ignores current display_mode setting).

        This is used when curses mode falls back to compatibility mode temporarily.
        """
        clear_screen()

        # Render game state info
        state_text = render_game_state(self.board, DisplayMode.COMPATIBILITY)
        print(state_text)

        # Render board using compatibility display
        compat_display = BoardDisplay(DisplayMode.COMPATIBILITY)
        board_text = compat_display.render(self.board)
        print(board_text)
        print()

        # Render selected cell status (if applicable)
        if self.selected_cell:
            row, col = self.selected_cell
            coord = self.board.tuple_to_spreadsheet(row, col)
            print(f"[MOUSE ACTIVE] Selected: {coord} (Click destination or ESC to cancel)")

    def _get_input_curses(self, prompt: str) -> Optional[str]:
        """Get input using curses.

        Args:
            prompt: The prompt string to display

        Returns:
            User input string, or None if quit
        """
        if self.curses_input is None:
            return None
        try:
            return self.curses_input.get_input(prompt)
        except (EOFError, KeyboardInterrupt):
            self._quit()
            return None

    def _prompt_for_command(self) -> None:
        """Prompt user for and execute a command."""
        # Build prompt
        phase = "Movement" if self.board.current_phase == 'M' else "Battle"
        prompt = f"{self.board.turn} [{phase}] > "

        # Get user input
        if self.display_mode == DisplayMode.CURSES and self.curses_input:
            user_input = self._get_input_curses(prompt)
            if user_input is None:
                return
        else:
            user_input = self._get_input_fallback(prompt)

        if user_input is None:
            return

        # Handle ESC key
        if user_input == "ESC":
            self.selected_cell = None
            self.display.clear_highlights()
            return

        # Handle mouse click
        if user_input.startswith("MOUSE_CLICK:"):
            coords = user_input.replace("MOUSE_CLICK:", "")
            row, col = map(int, coords.split(","))
            self._handle_board_click(row, col)
            return

        # Handle multi-line input (copy/paste support)
        if '\n' in user_input or ';' in user_input:
            commands = parse_multi_command_input(user_input)
            for cmd in commands:
                self._process_single_command(cmd)
            return

        # Parse command
        command = parse_command(user_input)

        # Handle invalid command
        if command.command_type.name == "INVALID":
            error = command.args.get("error", "Unknown command")
            message = f"Error: {error}\nType 'help' for available commands."

            # Display message based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(f"Error: {error}")
                print("Type 'help' for available commands.")
                input("Press Enter to continue...")
                self._render()
            return

        # Validate command
        is_valid, error = validate_command(self.board, command)
        if not is_valid:
            # Check if it's an attack in movement phase with moves remaining
            if (command.command_type.name == "ATTACK" and
                self.board.current_phase == "M" and
                self.board.get_moves_this_turn() < 5):
                # Offer confirmation to skip to battle phase
                moves_remaining = 5 - self.board.get_moves_this_turn()
                confirm_msg = (f"You have {moves_remaining} move(s) remaining.\n"
                             f"Attack will end movement phase.\n\n"
                             f"Attack anyway? (y/n)")
                if self._confirm(confirm_msg):
                    # Clear highlights before executing attack
                    self.display.clear_highlights()
                    # Switch to battle phase and execute attack
                    try:
                        self.board.switch_to_battle_phase()
                        if self.curses_input:
                            self.curses_input.update_board(self.board)
                        self._execute_command(command)
                    except ValueError as e:
                        # Cannot switch to battle phase - units must retreat
                        message = f"Error: {e}"
                        if self.display_mode == DisplayMode.CURSES and self.curses_input:
                            self.curses_input.show_message(message)
                        else:
                            print(message)
                            input("Press Enter to continue...")
                            self._render()
                else:
                    # User cancelled - re-render to clear any fallback messages
                    self._render()
                return

            message = f"Error: {error}"

            # Display message based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(f"Error: {error}")
                input("Press Enter to continue...")
                self._render()
            return

        # Execute command
        self._execute_command(command)

    def _handle_board_click(self, row: int, col: int) -> None:
        """Handle a click on the board.

        Args:
            row: Board row (0-19)
            col: Board column (0-24)

        Click behavior by phase:

        **Movement Phase:**
        - 1st click on own unit: Select it (highlight cell)
        - 2nd click on empty square: Execute move
        - 2nd click on own unit: Change selection
        - 2nd click on same unit: Deselect

        **Battle Phase:**
        - Click on enemy unit: Execute attack
        - Click anywhere else: Ignore
        """
        phase = self.board.current_phase
        unit = self.board.get_unit(row, col)

        if phase == 'M':  # Movement phase
            if unit and hasattr(unit, 'owner') and unit.owner == self.board.turn:
                # Check if there are units that must retreat (NEW in 0.1.5)
                must_retreat_units = self.board.get_units_must_retreat()
                if must_retreat_units:
                    # Only allow selecting/moving retreating units
                    if self.selected_cell is None:
                        # Must click on a retreating unit first
                        if (row, col) not in must_retreat_units:
                            # Show error about retreat enforcement
                            retreat_units_str = []
                            for r, c in must_retreat_units:
                                unit_at = self.board.get_unit(r, c)
                                if unit_at:
                                    coord = self.board.tuple_to_spreadsheet(r, c)
                                    unit_type = getattr(unit_at, 'unit_type', 'Unit')
                                    retreat_units_str.append(f"{unit_type} at {coord}")

                            message = "Cannot move! These units must retreat first:\n"
                            message += ", ".join(retreat_units_str)
                            message += "\n   Click on a retreating unit to select its destination."

                            # Display error based on mode
                            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                                self.curses_input.show_message(message)
                            else:
                                print(message)
                                input("Press Enter to continue...")
                                self._render()
                            return

                        # Clicked on a retreating unit - select it
                        self.display.clear_highlights()
                        self.display.set_highlight(row, col, 'selected')
                        self.selected_cell = (row, col)
                        return

                # No pending retreats - normal selection logic
                # Check if unit must retreat (deprecated FEN check,
                # should not happen with new system)
                if self.board.has_pending_retreat(row, col):
                    message = "This unit must retreat before making other moves!"
                    # Display error based on mode
                    if self.display_mode == DisplayMode.CURSES and self.curses_input:
                        self.curses_input.show_message(message)
                    else:
                        print(message)
                        input("Press Enter to continue...")
                    return

                # Click on own unit
                if self.selected_cell is None:
                    # First click: Select unit
                    self.selected_cell = (row, col)
                    self.display.set_highlight(row, col, 'selected')
                elif self.selected_cell == (row, col):
                    # Click same unit again: Deselect
                    self.selected_cell = None
                    self.display.clear_highlights()
                else:
                    # Different unit: Replace selection
                    self.selected_cell = (row, col)
                    self.display.clear_highlights()
                    self.display.set_highlight(row, col, 'selected')
            elif unit and hasattr(unit, 'owner') and unit.owner != self.board.turn:
                # Click on enemy unit: Trigger attack confirmation
                self.display.clear_highlights()
                self.display.set_highlight(row, col, 'attack')

                # Generate attack command
                target_sheet = self.board.tuple_to_spreadsheet(row, col)
                command_str = f"attack {target_sheet}"
                command = parse_command(command_str)

                # Check for early attack in movement phase with confirmation
                if (self.board.get_moves_this_turn() < 5):
                    # Offer confirmation to skip to battle phase
                    moves_remaining = 5 - self.board.get_moves_this_turn()
                    confirm_msg = (f"You have {moves_remaining} move(s) remaining.\n"
                                     f"Attacking will end movement phase.  "
                                     f"Attack anyway? (y/n)")
                    if self._confirm(confirm_msg):
                        # Clear highlights before executing attack
                        self.display.clear_highlights()
                        # Switch to battle phase and execute attack
                        try:
                            self.board.switch_to_battle_phase()
                            if self.curses_input:
                                self.curses_input.update_board(self.board)
                            self._execute_command(command)
                            return
                        except ValueError as e:
                            # Cannot switch to battle phase - units must retreat
                            message = f"Error: {e}"
                            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                                self.curses_input.show_message(message)
                            else:
                                print(message)
                                input("Press Enter to continue...")
                            self._render()

                # If not confirmed, clear highlights and re-render
                self.display.clear_highlights()
                self._render()
                return
            elif self.selected_cell is not None:
                # Have selection - this is destination
                from_row, from_col = self.selected_cell

                # Check if selected unit must retreat (new 0.1.5 system)
                if self.board.is_unit_in_retreat(from_row, from_col):
                    # This is a retreat move
                    self.display.clear_highlights()
                    self.display.set_highlight(from_row, from_col, 'selected')
                    self.display.set_highlight(row, col, 'destination')

                    # Generate and execute move command
                    from_sheet = self.board.tuple_to_spreadsheet(from_row, from_col)
                    to_sheet = self.board.tuple_to_spreadsheet(row, col)
                    command_str = f"{from_sheet} {to_sheet}"

                    # Parse and execute command
                    command = parse_command(command_str)

                    # Validate command
                    is_valid, error = validate_command(self.board, command)
                    if is_valid:
                        # Execute the move
                        self._execute_command(command)
                    else:
                        message = f"Error: {error}"
                        # Display error based on mode
                        if self.display_mode == DisplayMode.CURSES and self.curses_input:
                            self.curses_input.show_message(message)
                        else:
                            print(message)
                            input("Press Enter to continue...")
                else:
                    # Normal movement
                    self.display.clear_highlights()
                    self.display.set_highlight(from_row, from_col, 'selected')
                    self.display.set_highlight(row, col, 'destination')

                    # Generate and execute move command
                    from_sheet = self.board.tuple_to_spreadsheet(from_row, from_col)
                    to_sheet = self.board.tuple_to_spreadsheet(row, col)
                    command_str = f"{from_sheet} {to_sheet}"

                    # Parse and execute command
                    command = parse_command(command_str)

                    # Validate command
                    is_valid, error = validate_command(self.board, command)
                    if is_valid:
                        self._execute_command(command)
                    else:
                        message = f"Error: {error}"
                        # Display error based on mode
                        if self.display_mode == DisplayMode.CURSES and self.curses_input:
                            self.curses_input.show_message(message)
                        else:
                            print(message)
                            input("Press Enter to continue...")

                # Clear selection
                self.selected_cell = None
                self.display.clear_highlights()
            # Click on empty square with no selection: Ignore
            else:
                return

        elif phase == 'B':  # Battle phase
            if unit and hasattr(unit, 'owner') and unit.owner != self.board.turn:
                # Click on enemy: Queue attack
                self.display.clear_highlights()
                self.display.set_highlight(row, col, 'attack')

                # Generate and execute attack command
                target_sheet = self.board.tuple_to_spreadsheet(row, col)
                command_str = f"attack {target_sheet}"

                command = parse_command(command_str)

                # Check for early attack in movement phase with confirmation
                if (command.command_type.name == "ATTACK" and
                    self.board.current_phase == "M" and
                    self.board.get_moves_this_turn() > 0 and
                    self.board.get_moves_this_turn() < 5):
                    # Offer confirmation to skip to battle phase
                    moves_remaining = 5 - self.board.get_moves_this_turn()
                    confirm_msg = (f"You have {moves_remaining} move(s) remaining.\n"
                                     f"Attack will end movement phase.  "
                                     f"Attack anyway? (y/n)")
                    if self._confirm(confirm_msg):
                        # Switch to battle phase and execute attack
                        self.board.switch_to_battle_phase()
                        if self.curses_input:
                            self.curses_input.update_board(self.board)
                        self._execute_command(command)
                        return

                # Validate and execute
                is_valid, error = validate_command(self.board, command)
                if is_valid:
                    self._execute_command(command)
                else:
                    message = f"Error: {error}"
                    # Display error based on mode
                    if self.display_mode == DisplayMode.CURSES and self.curses_input:
                        self.curses_input.show_message(message)
                    else:
                        print(message)
                        input("Press Enter to continue...")

                # Clear highlights
                self.display.clear_highlights()
            # Click on own unit or empty: Ignore
            else:
                return

    def _confirm(self, message: str) -> bool:
        """Get user confirmation.

        Args:
            message: Confirmation message to display

        Returns:
            True if user confirms, False otherwise
        """
        self.logger.debug(f"Confirm dialog: display_mode={self.display_mode.name}")

        if self.display_mode == DisplayMode.CURSES and self.curses_input:
            try:
                result = self.curses_input.get_input(f"{message}\n> ")
                if result is None:
                    return False
                self.logger.debug(f"Confirm result: {result}")

                return bool(result and result.lower() in ['y', 'yes'])
            except Exception as e:
                self.logger.error(f"Curses confirm error: {e}", exc_info=True)
                return False
        else:
            try:
                # Clear screen before showing prompt to prevent accumulation
                clear_screen()

                # Show confirmation prompt
                response = input(f"{message}\n> ").strip().lower()
                self.logger.debug(f"Compat confirm result: {response}")

                # After compat mode input, always re-render to clear any leftover text
                self._render()

                return bool(response in ['y', 'yes'])
            except (EOFError, KeyboardInterrupt):
                self.logger.debug("Compat confirm cancelled")
                return False

    def _get_input_fallback(self, prompt: str) -> Optional[str]:
        """Get input using standard input (fallback).

        Args:
            prompt: The prompt string to display

        Returns:
            User input string, or None if quit
        """
        try:
            user_input = input(prompt).strip()
            return user_input
        except (EOFError, KeyboardInterrupt):
            print("\n")
            self._quit()
            return None

    def _process_single_command(self, command_str: str) -> None:
        """Process a single command string.

        Args:
            command_str: Command string to process
        """
        command = parse_command(command_str)

        # Handle invalid command
        if command.command_type.name == "INVALID":
            error = command.args.get("error", "Unknown command")
            print(f"Error: {error}")
            print("Type 'help' for available commands.")
            input("Press Enter to continue...")
            self._render()
            return

        # Validate command
        is_valid, error = validate_command(self.board, command)
        if not is_valid:
            print(f"Error: {error}")
            input("Press Enter to continue...")
            self._render()
            return

        # Execute command
        self._execute_command(command)

    def _execute_command(self, command: Command) -> None:
        """Execute a parsed command.

        Args:
            command: Parsed command to execute
        """
        cmd_type = command.command_type

        if cmd_type.name == "MOVE":
            self._execute_move(command)
        elif cmd_type.name == "ATTACK":
            self._execute_attack(command)
        elif cmd_type.name == "PASS":
            self._execute_pass(command)
        elif cmd_type.name == "END_TURN":
            self._execute_end_turn(command)
        elif cmd_type.name == "SURRENDER":
            self._execute_surrender(command)
        elif cmd_type.name == "SAVE":
            self._execute_save(command)
        elif cmd_type.name == "LOAD":
            self._execute_load(command)
        elif cmd_type.name == "HELP":
            self._execute_help()
        elif cmd_type.name == "MODE":
            self._execute_mode(command)
        elif cmd_type.name == "PHASE":
            self._execute_phase(command)
        elif cmd_type.name == "QUIT":
            self._quit()

    def _execute_move(self, command: Command) -> None:
        """Execute move command.

        Modified for 0.2.2: Handle enemy arsenal destruction.

        Args:
            command: Move command with from/to coordinates
        """
        from_row: int = command.args.get('from_row')  # type: ignore[assignment]
        from_col: int = command.args.get('from_col')  # type: ignore[assignment]
        to_row: int = command.args.get('to_row')  # type: ignore[assignment]
        to_col: int = command.args.get('to_col')  # type: ignore[assignment]

        # Check if unit is offline before attempting move
        try:
            unit = self.board.get_unit(from_row, from_col)
        except ValueError:
            message = f"Error: Invalid coordinates ({from_row}, {from_col})"
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()
            return
        if unit and hasattr(unit, 'owner'):
            is_online = self.board.is_unit_online(from_row, from_col, unit.owner)
            unit_type = getattr(unit, 'unit_type', '?')

            # Relays and Swift Relays can move even when offline
            is_relay = unit_type in ('RELAY', 'SWIFT_RELAY')

            if not is_online and not is_relay:
                # Unit is offline and cannot move
                coord = self.board.tuple_to_spreadsheet(from_row, from_col)

                if self.display_mode == DisplayMode.CURSES and self.curses_input:
                    message = (
                        f"Cannot move: {unit_type} at {coord} is offline.\n"
                        f"Units require network connection to move.\n"
                        f"Relays can move even when offline."
                    )
                    self.curses_input.show_message(message)
                else:
                    message = (
                        f"Cannot move: {unit_type} at {coord} is OFFLINE.\n"
                        f"Units require network connection to move.\n"
                        f"Check relay placement and line-of-sight from arsenals.\n"
                        f"Relays can move even when offline."
                    )
                    print(message)
                    input("Press Enter to continue...")
                    self._render()
                return

        # Execute move
        try:
            unit, arsenal_destroyed = self.board.make_turn_move(from_row, from_col, to_row, to_col)
            if not hasattr(unit, 'unit_type'):
                raise ValueError("Invalid unit returned from move")
            from .parser import format_move
            move_str = format_move(from_row, from_col, to_row, to_col)
            unit_type = getattr(unit, 'unit_type', 'Unknown')
            message = f"Moved {unit_type} from {move_str}"

            # Check for enemy arsenal destruction
            if arsenal_destroyed:
                message += "\nENEMY ARSENAL DESTROYED!"
                message += "\nThis counts as your attack. Turn ending."

                # End turn immediately
                captured_units = self.board.end_turn()
                message += f"\nTurn ended. Now {self.board.turn}'s turn."

                # Display capture notifications for units with no valid retreat
                if captured_units:
                    for cap_row, cap_col, cap_unit, cap_reason in captured_units:
                        cap_coord = self.board.tuple_to_spreadsheet(cap_row, cap_col)
                        cap_type = getattr(cap_unit, 'unit_type', 'Unit')
                        message += f"\n{cap_type} at {cap_coord} captured ({cap_reason})"

                # Display victory message if game over
                if self.board.is_game_over():
                    message += "\n\n" + self._format_victory_message()

                # Update curses input board reference
                if self.curses_input:
                    self.curses_input.update_board(self.board)

                # Display message based on mode
                if self.display_mode == DisplayMode.CURSES and self.curses_input:
                    self.curses_input.show_message(message)
                else:
                    print(message)
                    input("Press Enter to continue...")
                    self._render()
                return

            # After successful move, recalculate networks for both players
            # Moving units can change line-of-sight for both players
            self.board.calculate_network('NORTH')
            self.board.calculate_network('SOUTH')

            # Check if all moves used - auto-advance to battle phase
            if self.board.get_moves_this_turn() >= 5:
                try:
                    self.board.switch_to_battle_phase()
                    message += "\nAll moves used. Switched to Battle phase."
                    # Update curses input board reference
                    if self.curses_input:
                        self.curses_input.update_board(self.board)
                except ValueError as e:
                    # Cannot switch to battle phase - units must retreat
                    message += f"\n{e}"

            # Display message based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()
        except Exception as e:
            message = f"Error executing move: {e}"

            # Display error based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()

    def _execute_attack(self, command: Command) -> None:
        """Execute attack command.

        Args:
            command: Attack command with target coordinates
        """
        target_row: int = command.args.get('target_row')  # type: ignore[assignment]
        target_col: int = command.args.get('target_col')  # type: ignore[assignment]

        # Validate coordinates first
        if not self.board.is_valid_square(target_row, target_col):
            message = f"Error: Invalid coordinates ({target_row}, {target_col})"
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()
            return

        # Preview battle before executing
        from ..combat import preview_combat

        try:
            preview = preview_combat(self.board, target_row, target_col,
                                 self.board.turn, self._get_opponent())

            # Display battle confirmation dialog
            if not self._show_battle_confirmation(target_row, target_col, preview):
                # User cancelled attack
                self.display.clear_highlights()
                self._render()
                return

            # Execute attack
            result = self.board.make_turn_attack(target_row, target_col)

            # After attack, recalculate networks for both players
            # Capture/retreat removes units, potentially breaking network chains
            self.board.calculate_network('NORTH')
            self.board.calculate_network('SOUTH')

            target = self.board.get_unit(target_row, target_col)
            if target and hasattr(target, 'unit_type'):
                target_type = target.unit_type
            else:
                target_type = "Unknown"

            outcome_value = "UNKNOWN"
            if 'outcome' in result and hasattr(result['outcome'], 'value'):
                outcome_value = result['outcome'].value

            message = f"Attacked {target_type} at {target_row},{target_col}\n"
            message += f"Outcome: {outcome_value}\n"
            message += f"Attack Power: {result['attack_power']}\n"
            message += f"Defense Power: {result['defense_power']}"

            # Auto-advance to next turn after attack
            captured_units = self.board.end_turn()
            message += f"\n\nTurn ended. Now {self.board.turn}'s turn."

            # Display capture notifications for units with no valid retreat
            if captured_units:
                for cap_row, cap_col, cap_unit, cap_reason in captured_units:
                    cap_coord = self.board.tuple_to_spreadsheet(cap_row, cap_col)
                    cap_type = getattr(cap_unit, 'unit_type', 'Unit')
                    message += f"\n{cap_type} at {cap_coord} captured ({cap_reason})"

            # Display victory message if game over
            if self.board.is_game_over():
                message += "\n\n" + self._format_victory_message()

            # Update curses input board reference
            if self.curses_input:
                self.curses_input.update_board(self.board)

            # Display message based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()
        except Exception as e:
            message = f"Error executing attack: {e}"

            # Display error based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()

    def _get_opponent(self) -> str:
        """Get the opponent player.

        Returns:
            Opponent player ('NORTH' or 'SOUTH')
        """
        return 'SOUTH' if self.board.turn == 'NORTH' else 'NORTH'

    def _show_battle_confirmation(self, target_row: int, target_col: int,
                               preview: dict) -> bool:
        """Show battle confirmation dialog with highlights.

        Args:
            target_row: Target row
            target_col: Target column
            preview: Battle preview dictionary from preview_combat()

        Returns:
            True if user confirms attack, False if cancelled
        """
        # Clear any existing highlights
        self.display.clear_highlights()

        # Highlight target square (same color as defenders since it's being attacked)
        self.display.set_highlight(target_row, target_col, 'defense')

        # Highlight attacking units
        for row, col, _unit, _contribution in preview['attack_units']:
            # Check if this cavalry is charging (using positions list from preview)
            if (row, col) in preview['charging_cavalry_positions']:
                self.display.set_highlight(row, col, 'charging')
            else:
                self.display.set_highlight(row, col, 'attack')

        # Highlight defending units (excluding target itself)
        self.board.get_unit(target_row, target_col)
        for row, col, _unit, _contribution in preview['defense_units']:
            # Skip the target unit itself (use position comparison, not object identity)
            if row == target_row and col == target_col:
                continue
            # Defending units all get blue highlight (including cavalry)
            self.display.set_highlight(row, col, 'defense')

        # Re-render with highlights
        self._render()

        # Build confirmation message
        message = self._format_battle_confirmation(target_row, target_col, preview)

        # Get user confirmation
        confirmed = self._confirm(message)

        # Clear highlights after decision
        self.display.clear_highlights()

        return confirmed

    def _format_battle_confirmation(self, target_row: int, target_col: int,
                                   preview: dict) -> str:
        """Format battle confirmation message.

        Args:
            target_row: Target row
            target_col: Target column
            preview: Battle preview dictionary from preview_combat()

        Returns:
            Formatted confirmation message string
        """
        # Single line confirmation
        message = (
            f"Attack Power {preview['attack_power']} vs Defense Power "
            f"{preview['defense_power']}, continue? (y/n)"
        )
        return message

    def _execute_pass(self, command: Command) -> None:
        """Execute pass command.

        Args:
            command: Pass command (unused but for consistency)
        """
        try:
            self.board.pass_attack()
            message = "Attack phase passed."

            # Auto-advance turn after pass
            captured_units = self.board.end_turn()
            message += f"\nTurn ended. Now {self.board.turn}'s turn."

            # Display capture notifications for units with no valid retreat
            if captured_units:
                for cap_row, cap_col, cap_unit, cap_reason in captured_units:
                    cap_coord = self.board.tuple_to_spreadsheet(cap_row, cap_col)
                    cap_type = getattr(cap_unit, 'unit_type', 'Unit')
                    message += f"\n{cap_type} at {cap_coord} captured ({cap_reason})"

            # Display victory message if game over
            if self.board.is_game_over():
                message += "\n\n" + self._format_victory_message()

            # Update curses input board reference
            if self.curses_input:
                self.curses_input.update_board(self.board)

            # Display message based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()
        except Exception as e:
            message = f"Error passing: {e}"

            # Display error based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()

    def _execute_end_turn(self, command: Command) -> None:
        """Execute end turn command.

        Args:
            command: End turn command (unused but for consistency)
        """
        try:
            captured_units = self.board.end_turn()
            message = f"Turn ended. Now {self.board.turn}'s turn."

            # Display capture notifications for units with no valid retreat
            if captured_units:
                for cap_row, cap_col, cap_unit, cap_reason in captured_units:
                    cap_coord = self.board.tuple_to_spreadsheet(cap_row, cap_col)
                    cap_type = getattr(cap_unit, 'unit_type', 'Unit')
                    message += f"\n{cap_type} at {cap_coord} captured ({cap_reason})"

            # Display victory message if game over
            if self.board.is_game_over():
                message += "\n\n" + self._format_victory_message()

            # Display message based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()
        except Exception as e:
            message = f"Error ending turn: {e}"

            # Display error based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()

    def _execute_surrender(self, command: Command) -> None:
        """Execute surrender command.

        Args:
            command: Surrender command (unused but for consistency)
        """
        try:
            # Surrender on behalf of current player
            self.board.handle_surrender(self.board.turn)

            message = f"{self.board.turn} has surrendered!"

            # Display victory message if game over
            if self.board.is_game_over():
                message += "\n\n" + self._format_victory_message()

            # Display message based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()
        except Exception as e:
            message = f"Error surrendering: {e}"

            # Display error based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()

    def _execute_save(self, command: Command) -> None:
        """Execute save command.

        Args:
            command: Save command with optional filename
        """
        filename = command.args.get('filename', 'pykrieg_save.fen')

        try:
            fen = Fen.board_to_fen(self.board)

            with open(filename, 'w') as f:
                f.write(fen)

            message = f"Game saved to {filename}"

            # Display message based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()
        except Exception as e:
            message = f"Error saving game: {e}"

            # Display error based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()

    def _execute_load(self, command: Command) -> None:
        """Execute load command.

        Args:
            command: Load command with optional filename
        """
        filename = command.args.get('filename', 'pykrieg_save.fen')

        try:
            if not os.path.exists(filename):
                message = f"Error: File not found: {filename}"

                # Display error based on mode
                if self.display_mode == DisplayMode.CURSES and self.curses_input:
                    self.curses_input.show_message(message)
                else:
                    print(message)
                    input("Press Enter to continue...")
                    self._render()
                return

            with open(filename) as f:
                fen = f.read()

            self.board = Fen.fen_to_board(fen)

            # After loading, enable networks
            self.board.enable_networks()

            # Update curses input board reference
            if self.curses_input:
                self.curses_input.update_board(self.board)
            message = f"Game loaded from {filename}"

            # Display message based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()
        except Exception as e:
            message = f"Error loading game: {e}"

            # Display error based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()

    def _execute_phase(self, command: Command) -> None:
        """Execute phase command.

        Args:
            command: Phase command with target phase

        Switches between movement and battle phases manually.
        """
        phase_str = command.args.get('phase')

        try:
            if phase_str == 'battle':
                try:
                    self.board.switch_to_battle_phase()
                    message = "Switched to Battle phase"
                except ValueError as e:
                    # Cannot switch to battle phase - units must retreat
                    message = f"Error: {e}"
            else:  # movement
                # Switching back to movement phase resets turn state
                # This allows undoing battle phase changes if needed
                self.board.current_phase = "M"
                # Update curses input board reference (phase changed)
                if self.curses_input:
                    self.curses_input.update_board(self.board)
                message = "Switched to Movement phase"

            # Display message based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()
        except Exception as e:
            message = f"Error switching phase: {e}"

            # Display error based on mode
            if self.display_mode == DisplayMode.CURSES and self.curses_input:
                self.curses_input.show_message(message)
            else:
                print(message)
                input("Press Enter to continue...")
                self._render()

    def _execute_help(self) -> None:
        """Execute help command."""
        # Clear screen before displaying help to prevent accumulation
        clear_screen()

        help_text = get_help_text()

        # Help is always displayed in compatibility mode (too long for curses)
        print(help_text)
        input("Press Enter to continue...")
        self._render()

    def _execute_mode(self, command: Command) -> None:
        """Execute mode command.

        Args:
            command: Mode command with target mode

        NOTE: Switching modes requires reinitializing the display and input handler.
        """
        mode_str = command.args.get('mode')

        if mode_str == 'curses':
            from .curses_input import CURSES_AVAILABLE
            if not CURSES_AVAILABLE:
                print("Error: Curses not available on this system")
                print("Windows: Install 'windows-curses' package")
                print("Linux/macOS: Curses should be built-in")
                input("Press Enter to continue...")
                self._render()
                return

            # Re-check terminal capabilities when switching to curses
            from .terminal import detect_best_mode
            current_best = detect_best_mode()
            if current_best != 'curses':
                print("Warning: Terminal does not currently support curses mode.")
                print("This could be due to:")
                print("  - Terminal too small (requires minimum 30 rows)")
                print("  - Terminal doesn't support colors (requires minimum 8 colors)")
                print("  - Curses library not available")
                print("\nResize terminal or use 'mode compat' instead.")
                input("Press Enter to continue...")
                self._render()
                return

            self.display_mode = DisplayMode.CURSES
            print("Switching to Curses mode...")
        else:
            self.display_mode = DisplayMode.COMPATIBILITY
            print("Switching to Compatibility mode...")

        # Reinitialize display
        self.display = BoardDisplay(self.display_mode)

        # Reinitialize input handler
        if self.display_mode == DisplayMode.CURSES:
            from .curses_input import CursesInput
            self.curses_input = CursesInput(self.board, self.display)
        else:
            self.curses_input = None

        input("Press Enter to apply mode change...")
        self._render()

    def _load_default_position(self) -> Board:
        """Load default starting position from FEN file.

        Returns:
            Board object with default starting position, or empty board if file not found
        """
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_fen_path = os.path.join(current_dir, 'default_starting_position.fen')

        try:
            with open(default_fen_path) as f:
                # Read file and strip whitespace/newlines
                fen_string = f.read().strip()

            # Load board from FEN string
            board = Fen.fen_to_board(fen_string)

            # After loading, enable networks
            board.enable_networks()

            return board
        except FileNotFoundError:
            print("Warning: Default starting position file not found.")
            print("Starting with empty board.")
            return Board()
        except Exception as e:
            print(f"Warning: Failed to load default starting position: {e}")
            print("Starting with empty board.")
            return Board()

    def _format_victory_message(self) -> str:
        """Format victory message for display.

        Returns:
            Formatted victory message string
        """
        result = self.board.victory_result
        if not result:
            return "Game Over!"

        winner = result.get('winner', 'Unknown')
        condition = result.get('victory_condition', 'Unknown')
        details = result.get('details', 'Game ended')

        message = "GAME OVER\n"
        message += f"\nWinner: {winner}"
        message += f"\nCondition: {condition}"
        message += f"\n\n{details}"
        message += "\n\nType 'quit' to exit."

        return message

    def _display_victory_message(self) -> None:
        """Display victory message in compatibility mode."""
        print()
        print("=" * 50)
        print(self._format_victory_message())
        print("=" * 50)
        print()

    def _quit(self) -> None:
        """Quit the game."""
        print("Thanks for playing Pykrieg!")
        self.running = False



def main() -> None:
    """Entry point for console game."""
    import sys

    # Parse command line arguments
    display_mode = None

    for arg in sys.argv[1:]:
        if arg in ['--mode=curses', '--curses', '-c']:
            display_mode = 'curses'
        elif arg in ['--mode=compat', '--compat', '-a', '--ascii']:
            display_mode = 'compatibility'
        elif arg in ['--help', '-h', 'help']:
            print("Pykrieg Console Interface")
            print("")
            print("Usage: python -m pykrieg.console [options]")
            print("")
            print("Options:")
            print("  --mode=curses, --curses, -c    Force curses mode (full UI with mouse)")
            print("  --mode=compat, --compat, -a    Force compatibility mode (ASCII only)")
            print("  --help, -h                      Show this help message")
            print("")
            print("Auto-detection (default):")
            print("  - Uses curses mode if terminal supports colors")
            print("  - Falls back to compatibility mode otherwise")
            sys.exit(0)

    # Create and run game
    game = ConsoleGame(display_mode=display_mode)
    game.run()


if __name__ == "__main__":
    main()
