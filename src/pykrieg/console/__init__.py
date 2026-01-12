"""Console interface module for Pykrieg.

This module provides a text-based console interface for playing Pykrieg
games from the terminal, supporting both rich (Unicode + colors) and
compatibility (ASCII) display modes.

Key Features:
- Board visualization in Rich (Unicode/ANSI) and Compatibility (ASCII) modes
- Mouse support for click-to-coordinate entry
- Command buffer for queuing multiple moves
- Enhanced input handling with copy/paste support
- Save/load functionality using FEN format
- Auto-detection of terminal capabilities
"""

from .display import (
    BoardDisplay,
    DisplayMode,
    clear_screen,
    render_game_state,
)
from .game import (
    ConsoleGame,
    main,
)
from .input_buffer import (
    CommandBuffer,
    parse_multi_command_input,
)
from .mouse_handler import (
    MouseHandler,
    detect_mouse_support,
)
from .parser import (
    Command,
    CommandType,
    format_move,
    get_help_text,
    parse_command,
    validate_command,
)
from .terminal import (
    detect_best_mode,
    get_terminal_width,
    has_color_support,
    has_unicode_support,
)

__all__ = [
    # Display
    'BoardDisplay',
    'DisplayMode',
    'render_game_state',
    'clear_screen',

    # Terminal
    'has_unicode_support',
    'has_color_support',
    'get_terminal_width',
    'detect_best_mode',

    # Parser
    'CommandType',
    'Command',
    'parse_command',
    'validate_command',
    'format_move',
    'get_help_text',

    # Mouse Handler
    'MouseHandler',
    'detect_mouse_support',

    # Input Buffer
    'CommandBuffer',
    'parse_multi_command_input',

    # Main Game
    'ConsoleGame',
    'main',
]
