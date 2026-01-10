"""
Pykrieg - A Pythonic wargame engine for Guy Debord's Le Jeu de la Guerre.

This package is currently in early development. Check back soon for updates!
"""

__version__ = "0.1.2"
__author__ = "ssjmarx"
__license__ = "GPL-3.0"

from . import board
from . import constants
from . import fen
from . import types
from . import movement
from .board import Board
from .fen import Fen
from .pieces import (
    Unit,
    Infantry,
    Cavalry,
    Cannon,
    Arsenal,
    Relay,
    SwiftCannon,
    SwiftRelay,
    create_piece,
)
from .movement import (
    generate_moves,
    is_valid_move,
    execute_move,
    get_movement_range,
    can_move,
)

__all__ = [
    'board',
    'constants',
    'fen',
    'types',
    'movement',
    'Board',
    'Fen',
    'Unit',
    'Infantry',
    'Cavalry',
    'Cannon',
    'Arsenal',
    'Relay',
    'SwiftCannon',
    'SwiftRelay',
    'create_piece',
    'generate_moves',
    'is_valid_move',
    'execute_move',
    'get_movement_range',
    'can_move',
]
