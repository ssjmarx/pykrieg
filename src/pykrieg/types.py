"""Type definitions for Pykrieg.

This module contains type hints and TypedDict classes used throughout
the Pykrieg game implementation for better code clarity and type safety.
"""

from typing import TYPE_CHECKING, TypedDict, Tuple, Optional, List

if TYPE_CHECKING:
    from .pieces import Unit


class Piece(TypedDict, total=False):
    """Represents a piece on the board (for backward compatibility).
    
    This is kept for backward compatibility with existing code.
    New code should use Unit objects directly.
    
    Attributes:
        type: The unit type (e.g., 'INFANTRY', 'CAVALRY')
        owner: The player who owns the piece ('NORTH' or 'SOUTH')
    """
    type: str
    owner: str


# Type aliases for common coordinate and board representations
Coordinate = Tuple[int, int]
CoordinateString = str
SquareIndex = int

Player = str  # 'NORTH' or 'SOUTH'
Territory = str  # 'NORTH' or 'SOUTH'

UnitType = str  # 'INFANTRY', 'CAVALRY', 'CANNON', 'ARSENAL', 'RELAY', 'SWIFT_CANNON', 'SWIFT_RELAY'

BoardData = List[List[Optional[Piece]]]
