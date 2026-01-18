"""Command parser for console interface.

This module handles parsing and validation of user commands.

Classes:
    CommandType: Enum for command types
    Command: Parsed command structure

Functions:
    parse_command(input_str): Parse user input into command
    validate_command(board, command): Validate command against game state
    format_move(from_row, from_col, to_row, to_col): Format move coordinates
    parse_coordinates(coord_str): Parse coordinate string
"""

from enum import Enum
from typing import Optional, Tuple

from ..board import Board


class CommandType(Enum):
    """Command type enumeration."""
    MOVE = "move"
    ATTACK = "attack"
    PASS = "pass"
    END_TURN = "end"
    SURRENDER = "surrender"
    SAVE = "save"
    LOAD = "load"
    HELP = "help"
    MODE = "mode"
    PHASE = "phase"
    UNDO = "undo"
    REDO = "redo"
    SET_UNDO_LIMIT = "set_undo_limit"
    QUIT = "quit"
    INVALID = "invalid"


class Command:
    """Parsed command structure."""

    def __init__(self, command_type: CommandType, args: Optional[dict] = None):
        """Initialize command.

        Args:
            command_type: Type of command
            args: Command arguments (e.g., coordinates)
        """
        self.command_type = command_type
        self.args = args or {}

    def __repr__(self) -> str:
        return f"Command({self.command_type}, {self.args})"


def parse_command(input_str: str) -> Command:
    """Parse user input into a command.

    Supported command formats:
    - move: "move A1 to B1" or "A1 B1" or "m A1 B1"
    - attack: "attack B1" or "a B1"
    - pass: "pass" or "p"
    - end turn: "end" or "e"
    - save: "save [filename]" or "s [filename]"
    - load: "load [filename]" or "l [filename]"
    - help: "help" or "h" or "?"
    - phase: "phase battle" or "phase movement" or "ph b" or "ph m"
    - mode: "mode curses" or "mode rich" or "mode compat" or "mode ascii"
    - quit: "quit" or "q" or "exit"

    Args:
        input_str: User input string

    Returns:
        Parsed Command object
    """
    if not input_str or not input_str.strip():
        return Command(CommandType.INVALID, {"error": "Empty command"})

    parts = input_str.strip().lower().split()

    if not parts:
        return Command(CommandType.INVALID, {"error": "Empty command"})

    cmd = parts[0]

    # Parse based on command type
    if cmd in ["move", "m"]:
        return _parse_move_command(parts)
    elif cmd in ["attack", "a"]:
        return _parse_attack_command(parts)
    elif cmd in ["pass", "p"]:
        return Command(CommandType.PASS)
    elif cmd in ["end", "e"]:
        return Command(CommandType.END_TURN)
    elif cmd == "surrender":
        return Command(CommandType.SURRENDER)
    elif cmd in ["phase", "ph"]:
        return _parse_phase_command(parts)
    elif cmd in ["save", "s"]:
        return _parse_save_command(parts)
    elif cmd in ["load", "l"]:
        return _parse_load_command(parts)
    elif cmd in ["help", "h", "?"]:
        return Command(CommandType.HELP)
    elif cmd == "mode":
        return _parse_mode_command(parts)
    elif cmd in ["undo", "u"]:
        return _parse_undo_command(parts)
    elif cmd in ["redo", "r"]:
        return _parse_redo_command(parts)
    elif cmd == "set_undo_limit":
        return _parse_set_undo_limit_command(parts)
    elif cmd in ["quit", "q", "exit"]:
        return Command(CommandType.QUIT)
    else:
        # Try to parse as shorthand move (e.g., "A1 B1")
        if len(parts) == 2:
            return _parse_move_shorthand(parts)
        else:
            return Command(CommandType.INVALID, {"error": f"Unknown command: {cmd}"})


def _parse_move_command(parts: list) -> Command:
    """Parse move command.

    Format: "move A1 to B1" or "move A1 B1"

    Args:
        parts: Command parts list

    Returns:
        Parsed Command or INVALID if malformed
    """
    if len(parts) < 3:
        return Command(CommandType.INVALID, {"error": "Move requires source and destination"})

    # Handle "move A1 to B1" format
    if "to" in parts:
        to_idx = parts.index("to")
        if to_idx != 2 or len(parts) < 4:
            return Command(
                CommandType.INVALID,
                {"error": "Invalid move format. Use: move F11 to G11"},
            )

        from_coords = parts[1]
        to_coords = parts[3]
    else:
        # Handle "move A1 B1" format
        from_coords = parts[1]
        to_coords = parts[2]

    # Parse coordinates
    from_result = _parse_coordinates(from_coords)
    to_result = _parse_coordinates(to_coords)

    if not from_result or not to_result:
        msg = "Invalid coordinates. Use: 1A, 10B (spreadsheet) or 5,10 (numeric)"
        return Command(CommandType.INVALID, {"error": msg})

    return Command(CommandType.MOVE, {
        "from_row": from_result[0],
        "from_col": from_result[1],
        "to_row": to_result[0],
        "to_col": to_result[1],
    })


def _parse_move_shorthand(parts: list) -> Command:
    """Parse shorthand move command (e.g., "A1 B1").

    Args:
        parts: Command parts list

    Returns:
        Parsed Command or INVALID if malformed
    """
    from_result = _parse_coordinates(parts[0])
    to_result = _parse_coordinates(parts[1])

    if not from_result or not to_result:
        msg = "Invalid coordinates. Use: 1A, 10B (spreadsheet) or 5,10 (numeric)"
        return Command(CommandType.INVALID, {"error": msg})

    return Command(CommandType.MOVE, {
        "from_row": from_result[0],
        "from_col": from_result[1],
        "to_row": to_result[0],
        "to_col": to_result[1],
    })


def _parse_attack_command(parts: list) -> Command:
    """Parse attack command.

    Format: "attack B1" or "a B1"

    Args:
        parts: Command parts list

    Returns:
        Parsed Command or INVALID if malformed
    """
    if len(parts) < 2:
        return Command(CommandType.INVALID, {"error": "Attack requires target coordinates"})

    target_coords = parts[1]
    result = _parse_coordinates(target_coords)

    if not result:
        msg = "Invalid coordinates. Use: 12G (spreadsheet) or 5,12 (numeric)"
        return Command(CommandType.INVALID, {"error": msg})

    return Command(CommandType.ATTACK, {
        "target_row": result[0],
        "target_col": result[1],
    })


def _parse_save_command(parts: list) -> Command:
    """Parse save command.

    Format: "save [filename]" or "save"

    Args:
        parts: Command parts list

    Returns:
        Parsed Command
    """
    if len(parts) > 1:
        filename = parts[1]
    else:
        # Default filename (now uses KFEN format)
        filename = "pykrieg_save.kfen"

    return Command(CommandType.SAVE, {"filename": filename})


def _parse_load_command(parts: list) -> Command:
    """Parse load command.

    Format: "load [filename]" or "load"

    Args:
        parts: Command parts list

    Returns:
        Parsed Command
    """
    if len(parts) > 1:
        filename = parts[1]
    else:
        # Default filename (now uses KFEN format)
        filename = "pykrieg_save.kfen"

    return Command(CommandType.LOAD, {"filename": filename})


def _parse_mode_command(parts: list) -> Command:
    """Parse mode command.

    Format: "mode curses", "mode rich", or "mode compat" or "mode ascii"

    Args:
        parts: Command parts list

    Returns:
        Parsed Command or INVALID if malformed
    """
    if len(parts) < 2:
        return Command(CommandType.INVALID, {"error": "Mode requires 'curses' or 'compat'"})

    mode_str = parts[1]

    if mode_str in ["curses", "rich", "unicode", "color"]:
        mode = "curses"
    elif mode_str in ["compat", "ascii", "plain"]:
        mode = "compatibility"
    else:
        return Command(CommandType.INVALID, {"error": "Invalid mode. Use 'curses' or 'compat'"})

    return Command(CommandType.MODE, {"mode": mode})


def _parse_phase_command(parts: list) -> Command:
    """Parse phase command.

    Format: "phase battle" or "phase movement" or "ph b" or "ph m"

    Args:
        parts: Command parts list

    Returns:
        Parsed Command or INVALID if malformed
    """
    if len(parts) < 2:
        return Command(CommandType.INVALID, {"error": "Phase requires 'battle' or 'movement'"})

    phase_str = parts[1]

    if phase_str in ["battle", "b"]:
        phase = "battle"
    elif phase_str in ["movement", "m"]:
        phase = "movement"
    else:
        return Command(CommandType.INVALID, {"error": "Invalid phase. Use 'battle' or 'movement'"})

    return Command(CommandType.PHASE, {"phase": phase})


def _parse_undo_command(parts: list) -> Command:
    """Parse undo command.

    Format: "undo [count]" or "undo"

    Args:
        parts: Command parts list

    Returns:
        Parsed Command
    """
    if len(parts) > 1:
        try:
            count = int(parts[1])
            if count < 1:
                return Command(CommandType.INVALID, {"error": "Undo count must be at least 1"})
        except ValueError:
            return Command(CommandType.INVALID, {"error": "Invalid undo count. Must be a number."})
    else:
        count = 1

    return Command(CommandType.UNDO, {"count": count})


def _parse_redo_command(parts: list) -> Command:
    """Parse redo command.

    Format: "redo [count]" or "redo"

    Args:
        parts: Command parts list

    Returns:
        Parsed Command
    """
    if len(parts) > 1:
        try:
            count = int(parts[1])
            if count < 1:
                return Command(CommandType.INVALID, {"error": "Redo count must be at least 1"})
        except ValueError:
            return Command(CommandType.INVALID, {"error": "Invalid redo count. Must be a number."})
    else:
        count = 1

    return Command(CommandType.REDO, {"count": count})


def _parse_set_undo_limit_command(parts: list) -> Command:
    """Parse set_undo_limit command.

    Format: "set_undo_limit <number>"

    Args:
        parts: Command parts list

    Returns:
        Parsed Command or INVALID if malformed
    """
    if len(parts) < 2:
        return Command(CommandType.INVALID, {"error": "set_undo_limit requires a number"})

    try:
        limit = int(parts[1])
        if limit < 0:
            msg = "Undo limit must be 0 or greater (0 = unlimited)"
            return Command(CommandType.INVALID, {"error": msg})
    except ValueError:
        return Command(CommandType.INVALID, {"error": "Invalid undo limit. Must be a number."})

    return Command(CommandType.SET_UNDO_LIMIT, {"limit": limit})


def _parse_coordinates(coord_str: str) -> Optional[Tuple[int, int]]:
    """Parse coordinate string.

    Formats:
    - Spreadsheet: "1A", "10B", "25T" (numbers + letters)
    - Tuple numeric: "5,10", "5 10" (row, col)

    Args:
        coord_str: Coordinate string (e.g., "1A", "5,10", "5 10")

    Returns:
        Tuple of (row, col) or None if invalid
    """
    from ..board import Board

    # Try spreadsheet-style first (e.g., "1A", "10B", "25T")
    try:
        row, col = Board.spreadsheet_to_tuple(coord_str)
        if 0 <= row < 20 and 0 <= col < 25:
            return (row, col)
    except (ValueError, TypeError):
        pass

    # Try comma-separated numeric (e.g., "5,10")
    if ',' in coord_str:
        parts = coord_str.split(',')
    else:
        # Try space-separated numeric (e.g., "5 10")
        parts = coord_str.split()

    if len(parts) != 2:
        return None

    try:
        row = int(parts[0])
        col = int(parts[1])

        # Validate bounds
        if not (0 <= row < 20 and 0 <= col < 25):
            return None

        return (row, col)
    except ValueError:
        return None


def validate_command(board: Board, command: Command) -> Tuple[bool, Optional[str]]:
    """Validate command against current game state.

    Args:
        board: The game board
        command: Parsed command to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if command.command_type == CommandType.MOVE:
        return _validate_move(board, command)
    elif command.command_type == CommandType.ATTACK:
        return _validate_attack(board, command)
    elif command.command_type == CommandType.PASS:
        return _validate_pass(board)
    elif command.command_type == CommandType.END_TURN:
        return _validate_end_turn(board)
    elif command.command_type == CommandType.SAVE:
        return True, None
    elif command.command_type == CommandType.LOAD:
        return True, None
    elif command.command_type == CommandType.HELP:
        return True, None
    elif command.command_type == CommandType.MODE:
        return True, None
    elif command.command_type == CommandType.QUIT:
        return True, None
    elif command.command_type == CommandType.PHASE:
        return _validate_phase(board, command)
    elif command.command_type == CommandType.UNDO:
        return True, None
    elif command.command_type == CommandType.REDO:
        return True, None
    elif command.command_type == CommandType.SET_UNDO_LIMIT:
        return True, None
    else:
        return False, "Invalid command"


def _validate_move(board: Board, command: Command) -> Tuple[bool, Optional[str]]:
    """Validate move command.

    Args:
        board: The game board
        command: Move command to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    from_row = command.args.get('from_row')
    from_col = command.args.get('from_col')
    to_row = command.args.get('to_row')
    to_col = command.args.get('to_col')

    # Use board's validation
    if from_row is None or from_col is None or to_row is None or to_col is None:
        return False, "Invalid move"

    if not board.validate_move(from_row, from_col, to_row, to_col):
        return False, "Invalid move"

    return True, None


def _validate_attack(board: Board, command: Command) -> Tuple[bool, Optional[str]]:
    """Validate attack command.

    Args:
        board: The game board
        command: Attack command to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    target_row = command.args.get('target_row')
    target_col = command.args.get('target_col')

    # Use board's validation
    if target_row is None or target_col is None:
        return False, "Invalid attack"

    # Check phase
    if board.current_phase != "B":
        return False, "Can only attack in battle phase. Use 'phase battle' to switch."

    # Check attack limit
    if board.get_attacks_this_turn() > 0:
        return False, "Already attacked this turn. Use 'pass' or 'end' to continue."

    # Use board's validation
    if not board.validate_attack(target_row, target_col):
        # Check if there's a target unit
        target = board.get_unit(target_row, target_col)
        if target is None:
            return False, "No unit at target coordinates"
        elif hasattr(target, 'owner') and target.owner == board.turn:
            return False, "Cannot attack your own units"
        else:
            return False, "No attacking units in line with target"

    return True, None


def _validate_pass(board: Board) -> Tuple[bool, Optional[str]]:
    """Validate pass command.

    Args:
        board: The game board

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Can only pass in battle phase
    if board.current_phase != "B":
        return False, "Can only pass in battle phase"

    # Can only pass if haven't attacked yet
    if board.get_attacks_this_turn() > 0:
        return False, "Already attacked this turn"

    return True, None


def _validate_phase(board: Board, command: Command) -> Tuple[bool, Optional[str]]:
    """Validate phase command.

    Args:
        board: The game board
        command: Phase command to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    phase = command.args.get('phase')

    if phase == 'movement':
        # Can only switch to movement from battle phase
        if board.current_phase != "B":
            return False, "Already in movement phase"
        # Must have attacked or passed before switching back
        if board.get_attacks_this_turn() == 0:
            return False, "Must attack or pass before switching to movement"
    elif phase == 'battle':
        # Can only switch to battle from movement phase
        if board.current_phase != "M":
            return False, "Already in battle phase"

    return True, None


def _validate_end_turn(board: Board) -> Tuple[bool, Optional[str]]:
    """Validate end turn command.

    Args:
        board: The game board

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Must have attacked or passed in battle phase
    if board.current_phase == "B" and board.get_attacks_this_turn() == 0:
        return False, "Must attack or pass before ending turn"

    return True, None


def format_move(from_row: int, from_col: int, to_row: int, to_col: int) -> str:
    """Format move coordinates for display.

    Args:
        from_row: Source row
        from_col: Source column
        to_row: Target row
        to_col: Target column

    Returns:
        Formatted string (spreadsheet-style, e.g., "F11 → G11")
    """
    from_coord = Board.tuple_to_spreadsheet(from_row, from_col)
    to_coord = Board.tuple_to_spreadsheet(to_row, to_col)
    return f"{from_coord} → {to_coord}"


def get_help_text() -> str:
    """Get help text for commands.

    Returns:
        String with command documentation
    """
    lines = [
        "PYKRIEG COMMANDS",
        "================",
        "",
        "Movement Phase:",
        "  move <from> to <to>  Move a unit (e.g., 'move F11 to G11')",
        "  move <from> <to>     Move a unit (shorthand, e.g., 'F11 G11')",
        "  m <from> <to>        Move a unit (abbreviated)",
        "  <from> <to>          Move a unit (ultra-shorthand)",
        "",
        "Battle Phase:",
        "  attack <target>      Attack a unit (e.g., 'attack G12')",
        "  a <target>           Attack a unit (abbreviated)",
        "  pass                 Pass attack phase",
        "  p                    Pass (abbreviated)",
        "",
        "Turn Management:",
        "  end                  End current turn",
        "  e                    End turn (abbreviated)",
        "  phase battle         Switch to battle phase",
        "  phase movement       Switch to movement phase",
        "  ph b                 Switch to battle phase (abbreviated)",
        "  ph m                 Switch to movement phase (abbreviated)",
        "",
        "Game Management:",
        "  surrender             Surrender to game (concede defeat)",
        "  save [filename]      Save game to KFEN file (.kfen)",
        "                        (default: pykrieg_save.kfen)",
        "  load [filename]      Load game from KFEN or FEN file",
        "                        (default: pykrieg_save.kfen)",
        "  undo [count]         Undo last action(s)",
        "  u [count]            Undo (abbreviated)",
        "  redo [count]         Redo last undone action(s)",
        "  r [count]            Redo (abbreviated)",
        "  set_undo_limit <n>   Set max undo history (0 = unlimited)",
        "",
        "Display:",
        "  mode curses          Switch to curses mode (full UI with mouse)",
        "  mode compat         Switch to compatibility mode (ASCII)",
        "",
        "Other:",
        "  help, h, ?           Show this help",
        "  quit, q, exit        Quit game",
        "",
        "Coordinate Formats:",
        "  Spreadsheet:1A, 10B, 25T (numbers + letters)",
        "  Numeric: 5,10 or 5 10 (row, column)",
        "  Rows: A-T (top to bottom, 0-19)",
        "  Columns: 1-25 (left to right, 0-24)",
    ]

    return "\n".join(lines)
