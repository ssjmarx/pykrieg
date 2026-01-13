"""Combat system for Pykrieg.

This module implements vector-based combat calculation for all unit types.
Combat is calculated by comparing power numbers along straight lines
(horizontal, vertical, diagonal).

Combat resolution:
- Attack ≤ Defense: FAIL (nothing happens)
- Attack = Defense + 1: RETREAT (defender must move next turn)
- Attack ≥ Defense + 2: CAPTURE (defender destroyed)

Scope for 0.1.3:
- Vector-based line detection (8 directions)
- Attack power calculation with cavalry charge bonus
- Defense power calculation
- Capture/retreat resolution logic
- Terrain-independent (terrain modifiers added in 0.2.1)
- Range-independent (range validation added in 0.2.0)
- Lines of communication not considered (added in 0.2.0)
"""

from enum import Enum
from typing import Dict, List, Tuple

from .board import Board


class CombatOutcome(Enum):
    """Result of a combat calculation."""
    FAIL = "FAIL"
    RETREAT = "RETREAT"
    CAPTURE = "CAPTURE"


def get_directions() -> List[Tuple[int, int]]:
    """Get all 8 cardinal and diagonal directions.

    Returns:
        List of (row_offset, col_offset) tuples for each direction:
        - (-1, 0): Up
        - (1, 0): Down
        - (0, -1): Left
        - (0, 1): Right
        - (-1, -1): Up-Left
        - (-1, 1): Up-Right
        - (1, -1): Down-Left
        - (1, 1): Down-Right
    """
    return [
        (-1, 0),  # Up
        (1, 0),  # Down
        (0, -1),  # Left
        (0, 1),  # Right
        (-1, -1),  # Up-Left
        (-1, 1),  # Up-Right
        (1, -1),  # Down-Left
        (1, 1),  # Down-Right
    ]


def get_line_units(board: Board, target_row: int, target_col: int,
                direction: Tuple[int, int], owner: str) -> List[Tuple[int, int, object]]:
    """Get all units of a given owner in a specific direction from target.

    This function enumerates all squares in a straight line from the target
    in specified direction, collecting all units owned by the specified player.

    Args:
        board: The game board
        target_row: Target row (0-19)
        target_col: Target column (0-24)
        direction: (row_offset, col_offset) tuple
        owner: 'NORTH' or 'SOUTH' - units to collect

    Returns:
        List of (row, col, unit) tuples for matching units in the line
    """
    row_offset, col_offset = direction
    units = []

    # Start from target square and move in direction
    current_row = target_row + row_offset
    current_col = target_col + col_offset

    while board.is_valid_square(current_row, current_col):
        unit = board.get_unit(current_row, current_col)
        if unit is not None:
            if getattr(unit, 'owner', None) == owner:
                units.append((current_row, current_col, unit))

        # Move to next square in line
        current_row += row_offset
        current_col += col_offset

    return units


def calculate_attack_power(board: Board, target_row: int, target_col: int,
                      attacker: str) -> int:
    """Calculate total attack power against a target square.

    Attack power is sum of effective Attack stats of all attacker's units
    in direct lines with target, plus Cavalry charge bonuses.

    Cavalry Charge Rules:
    - Cavalry adjacent to target gets +3 bonus (triggers charge)
    - Cavalry can join charge stack if on same attack vector as charging cavalry
    - Charge stack requires unbroken line, up to 4 squares from target
    - Stacking cavalry also get +3 bonus even if not adjacent
    - Each attack vector calculated separately
    - If first cavalry not adjacent, no charge in that direction
    - Gaps break charge stacking chain

    Note: Effective attack considers online/offline status (0.2.0)
    - Offline units have 0 attack (except relays, which have 0 anyway)
    - Only online units contribute to attack power

    Args:
        board: The game board
        target_row: Target row (0-19)
        target_col: Target column (0-24)
        attacker: 'NORTH' or 'SOUTH' - player making of attack

    Returns:
        Total attack power (integer)
    """
    total_attack = 0

    for direction in get_directions():
        units = get_line_units(board, target_row, target_col, direction, attacker)

        # Check if charge is active for this direction
        charging = False

        # Build full list of squares in this direction
        # to check for gaps between units
        row_offset, col_offset = direction
        squares_in_line = []
        current_row = target_row + row_offset
        current_col = target_col + col_offset
        while board.is_valid_square(current_row, current_col):
            squares_in_line.append((current_row, current_col))
            current_row += row_offset
            current_col += col_offset

        for i, (row, col, unit) in enumerate(units):
            # Use effective attack (0.2.0) to account for online/offline status
            if hasattr(unit, 'get_effective_attack'):
                base_attack = unit.get_effective_attack(board)
            else:
                base_attack = getattr(unit, 'attack', 0)

            unit_type = getattr(unit, 'unit_type', None)

            # Check for Cavalry charge bonus
            if unit_type == 'CAVALRY':
                # First cavalry in direction
                if i == 0:
                    # Check if adjacent (orthogonal/diagonal)
                    if is_adjacent(row, col, target_row, target_col):
                        charging = True  # Trigger charge
                    else:
                        # First cavalry not adjacent, no charge in this direction
                        # Continue but no bonus for this or subsequent units
                        total_attack += base_attack
                        continue
                # Subsequent cavalry - check if charge is still active
                elif not charging:
                    total_attack += base_attack
                    continue
                else:
                    # Charge is active, check for gap between previous unit and this one
                    prev_unit = units[i - 1]
                    prev_row, prev_col = prev_unit[0], prev_unit[1]

                    # Check if there's a gap between prev_unit and current unit
                    # by checking squares_in_line
                    prev_index = squares_in_line.index((prev_row, prev_col))
                    current_index = squares_in_line.index((row, col))

                    # If units are not consecutive, there's a gap
                    if current_index - prev_index > 1:
                        # Gap found, breaks charge stack
                        charging = False
                        total_attack += base_attack
                        continue

                # Apply bonus if charging (either adjacent or stacking)
                total_attack += base_attack + 3
            else:
                # Non-cavalry units contribute normally
                total_attack += base_attack

    return total_attack


def calculate_defense_power(board: Board, target_row: int, target_col: int,
                        defender: str) -> int:
    """Calculate total defense power for a target square.

    Defense power is sum of effective Defense stats of all defender's units
    in direct lines supporting the target, including the unit at the target itself.

    Note: Effective defense considers online/offline status (0.2.0)
    - Offline units have 0 defense (except relays, which always have defense)
    - Only online units contribute to defense power

    Args:
        board: The game board
        target_row: Target row (0-19)
        target_col: Target column (0-24)
        defender: 'NORTH' or 'SOUTH' - player being attacked

    Returns:
        Total defense power (integer)
    """
    total_defense = 0

    # First, check if there's a unit at the target square that belongs to defender
    target_unit = board.get_unit(target_row, target_col)
    if target_unit is not None and getattr(target_unit, 'owner', None) == defender:
        # Use effective defense (0.2.0) to account for online/offline status
        if hasattr(target_unit, 'get_effective_defense'):
            total_defense += target_unit.get_effective_defense(board)
        else:
            total_defense += getattr(target_unit, 'defense', 0)

    # Then add defense from units in all 8 directions supporting the target
    for direction in get_directions():
        units = get_line_units(board, target_row, target_col, direction, defender)

        for _row, _col, unit in units:
            # Use effective defense (0.2.0) to account for online/offline status
            if hasattr(unit, 'get_effective_defense'):
                total_defense += unit.get_effective_defense(board)
            else:
                total_defense += getattr(unit, 'defense', 0)

    return total_defense


def is_adjacent(row1: int, col1: int, row2: int, col2: int) -> bool:
    """Check if two squares are adjacent (Chebyshev distance = 1).

    Adjacent means sharing a side or corner (8-directional adjacency).

    Args:
        row1: First square row
        col1: First square column
        row2: Second square row
        col2: Second square column

    Returns:
        True if adjacent, False otherwise
    """
    distance = max(abs(row1 - row2), abs(col1 - col2))
    return distance == 1


def resolve_combat(attack_power: int, defense_power: int) -> CombatOutcome:
    """Resolve combat based on attack vs defense power.

    Combat outcomes:
    - Attack ≤ Defense: FAIL (nothing happens)
    - Attack = Defense + 1: RETREAT (defender must move next turn)
    - Attack ≥ Defense + 2: CAPTURE (defender destroyed)

    Args:
        attack_power: Total attack power
        defense_power: Total defense power

    Returns:
        CombatOutcome enum (FAIL, RETREAT, or CAPTURE)
    """
    if attack_power <= defense_power:
        return CombatOutcome.FAIL
    elif attack_power == defense_power + 1:
        return CombatOutcome.RETREAT
    else:  # attack_power >= defense_power + 2
        return CombatOutcome.CAPTURE


def calculate_combat(board: Board, target_row: int, target_col: int,
                 attacker: str, defender: str) -> Dict[str, object]:
    """Calculate complete combat scenario.

    This function performs full combat calculation:
    1. Calculate attack power
    2. Calculate defense power
    3. Resolve combat outcome

    Args:
        board: The game board
        target_row: Target row (0-19)
        target_col: Target column (0-24)
        attacker: 'NORTH' or 'SOUTH' - player making attack
        defender: 'NORTH' or 'SOUTH' - player being attacked

    Returns:
        Dictionary with combat results:
        {
            'attack_power': int,
            'defense_power': int,
            'outcome': CombatOutcome,
            'attack_units': List[Tuple[int, int, object]],
            'defense_units': List[Tuple[int, int, object]],
        }
    """
    # Calculate powers
    attack_power = calculate_attack_power(board, target_row, target_col, attacker)
    defense_power = calculate_defense_power(board, target_row, target_col, defender)

    # Resolve combat
    outcome = resolve_combat(attack_power, defense_power)

    # Collect unit information for debugging/analysis
    attack_units = []
    defense_units = []

    for direction in get_directions():
        attack_units.extend(get_line_units(board, target_row, target_col, direction, attacker))
        defense_units.extend(get_line_units(board, target_row, target_col, direction, defender))

    return {
        'attack_power': attack_power,
        'defense_power': defense_power,
        'outcome': outcome,
        'attack_units': attack_units,
        'defense_units': defense_units,
    }


def execute_capture(board: Board, target_row: int, target_col: int) -> object:
    """Execute a capture (remove target unit from board).

    This function removes the unit at target square.
    After capture, networks are recalculated for both players (0.2.0).

    Args:
        board: The game board
        target_row: Target row (0-19)
        target_col: Target column (0-24)

    Returns:
        The captured Unit object

    Raises:
        ValueError: If no unit at target position

    Note:
        Retreat execution is handled in turn management (0.1.4).
    """
    unit = board.get_unit(target_row, target_col)
    if unit is None:
        raise ValueError(f"No unit to capture at ({target_row}, {target_col})")

    board.clear_square(target_row, target_col)

    # Network recalculation is now lazy - marked dirty by clear_square()
    # Will be recalculated automatically when needed via _ensure_network_calculated()
    # This ensures backward compatibility for scenarios that don't use network system

    return unit


def can_attack(board: Board, target_row: int, target_col: int,
              attacker: str) -> bool:
    """Check if an attacker can attack the target square.

    In 0.1.3, this checks if there's at least one attacking unit.
    Range validation will be added in 0.2.0.

    Args:
        board: The game board
        target_row: Target row (0-19)
        target_col: Target column (0-24)
        attacker: 'NORTH' or 'SOUTH' - player making attack

    Returns:
        True if attacker has units in line with target, False otherwise

    Note:
        Range validation NOT checked in 0.1.3 (added in 0.2.0)
    """
    for direction in get_directions():
        units = get_line_units(board, target_row, target_col, direction, attacker)
        if units:
            return True
    return False
