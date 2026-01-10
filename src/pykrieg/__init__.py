"""
Pykrieg - A Pythonic wargame engine for Guy Debord's Le Jeu de la Guerre.

This package is currently in early development. Check back soon for updates!
"""

__version__ = "0.1.0"
__author__ = "ssjmarx"
__license__ = "GPL-3.0"

from . import board
from . import constants
from . import fen
from . import types
from .board import Board
from .fen import Fen

__all__ = [
    'board',
    'constants',
    'fen',
    'types',
    'Board',
    'Fen',
]
