"""
Pykrieg - A Pythonic wargame engine for Guy Debord's Le Jeu de la Guerre.

This package is currently in early development. Check back soon for updates!
"""

__version__ = "0.2.0"
__author__ = "ssjmarx"
__license__ = "GPL-3.0"

from . import board, combat, constants, fen, movement, types
from .board import Board
from .combat import (
    CombatOutcome,
    calculate_attack_power,
    calculate_combat,
    calculate_defense_power,
    can_attack,
    execute_capture,
    get_directions,
    get_line_units,
    is_adjacent,
    resolve_combat,
)
from .fen import Fen
from .movement import (
    can_move,
    execute_move,
    generate_moves,
    get_movement_range,
    is_valid_move,
)
from .pieces import (
    Cannon,
    Cavalry,
    Infantry,
    Relay,
    SwiftCannon,
    SwiftRelay,
    Unit,
    create_piece,
)
from .turn import (
    TurnState,
    TurnValidationError,
    can_end_turn,
    get_turn_state,
    get_turn_summary,
    validate_turn_action,
)

__all__ = [
    'board',
    'combat',
    'constants',
    'fen',
    'types',
    'movement',
    'turn',
    'Board',
    'Fen',
    'Unit',
    'Infantry',
    'Cavalry',
    'Cannon',
    'Relay',
    'SwiftCannon',
    'SwiftRelay',
    'create_piece',
    'generate_moves',
    'is_valid_move',
    'execute_move',
    'get_movement_range',
    'can_move',
    'CombatOutcome',
    'calculate_attack_power',
    'calculate_defense_power',
    'calculate_combat',
    'resolve_combat',
    'execute_capture',
    'can_attack',
    'get_directions',
    'get_line_units',
    'is_adjacent',
    'TurnState',
    'TurnValidationError',
    'get_turn_state',
    'validate_turn_action',
    'can_end_turn',
    'get_turn_summary',
]
