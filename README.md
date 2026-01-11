# Pykrieg

[![PyPI Version](https://img.shields.io/pypi/v/pykrieg?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/pykrieg/)

A Pythonic wargame engine for Guy Debord's *Le Jeu de la Guerre* (A Game of War).

## About

Pykrieg is a Python library that implements the complex rules of Guy Debord's strategic tabletop game, providing a clean, extensible API for developers to build custom interfaces, AI opponents, and analysis tools. The project is inspired by the successful **python-chess** library and follows similar design principles.

## Planned Features

- **Complete Game Engine**: Full implementation of Debord's strategic game rules
- **Clean API**: Intuitive Pythonic interface modeled after python-chess
- **Extensible Design**: Easy to create custom variants, unit types, and victory conditions
- **Format Support**: Game record and position formats for saving/sharing games
- **Engine Protocol**: UCI-like protocol for communication between engines and frontends
- **Well-Tested**: Comprehensive test suite with 85%+ code coverage

## Installation

```bash
pip install pykrieg
```

## Quick Start

```python
from pykrieg import Board, create_piece

# Create a board
board = Board()

# Add units using the factory function
board.create_and_place_unit(0, 0, 'INFANTRY', 'NORTH')
board.create_and_place_unit(5, 10, 'CAVALRY', 'NORTH')
board.create_and_place_unit(19, 24, 'INFANTRY', 'SOUTH')

# Or create units directly and place them
from pykrieg import Infantry, Cannon
unit = Cannon('NORTH')
board.place_unit(10, 10, unit)

# Query units on the board
print(board.count_units())  # Total number of units
print(board.count_units(unit_type='INFANTRY'))  # Count of infantry
print(board.get_units_by_owner('NORTH'))  # List of coordinates with North's units

# Serialize to FEN
from pykrieg import Fen
fen = Fen.board_to_fen(board)
print(fen)

# Deserialize from FEN
board2 = Fen.fen_to_board(fen)

# Check territory
print(board.get_territory(0, 0))  # 'NORTH'
print(board.get_territory(19, 24))  # 'SOUTH'

# Convert coordinates
print(Board.tuple_to_spreadsheet(0, 0))  # 'A1'
print(Board.spreadsheet_to_tuple('A1'))  # (0, 0)

# Movement
from pykrieg import generate_moves, is_valid_move, execute_move

# Get legal moves for a unit
moves = generate_moves(board, 5, 10)
print(f"Available moves: {moves}")  # List of (row, col) tuples

# Check if a move is valid
if is_valid_move(board, 5, 10, 7, 12):
    print("Move is valid!")

# Execute a move
moved_unit = execute_move(board, 5, 10, 7, 12)
print(f"Moved {moved_unit.unit_type} to (7, 12)")

# Or use Board convenience methods
moves = board.get_legal_moves(5, 10)  # Same as generate_moves()
is_valid = board.is_legal_move(5, 10, 7, 12)  # Same as is_valid_move()
unit = board.make_move(5, 10, 7, 12)  # Same as execute_move()

# Check unit movement properties
from pykrieg import get_movement_range, can_move
unit = board.get_unit(7, 12)
print(f"Movement range: {get_movement_range(unit)}")  # 0, 1, or 2
print(f"Can move: {can_move(unit)}")  # True or False

# Combat
from pykrieg import calculate_combat, execute_capture, CombatOutcome

# Calculate combat for a target square
result = calculate_combat(board, 5, 12, attacker='NORTH', defender='SOUTH')
print(f"Attack Power: {result['attack_power']}")
print(f"Defense Power: {result['defense_power']}")
print(f"Outcome: {result['outcome'].value}")

# Capture a unit if attack was successful
if result['outcome'] == CombatOutcome.CAPTURE:
    captured_unit = execute_capture(board, 5, 12)
    print(f"Captured {captured_unit.unit_type}!")

# Or use Board convenience methods
result = board.calculate_combat(5, 12, 'NORTH', 'SOUTH')
captured = board.execute_capture(5, 12)

## Turn Management

Pykrieg enforces turn rules to ensure fair play, following the game's structure of movement phase (up to 5 units) and battle phase (1 attack or pass).

### Movement Phase

During the movement phase, you can move up to 5 units:

```python
from pykrieg import Board

board = Board()

# Place units
board.create_and_place_unit(5, 10, "INFANTRY", "NORTH")
board.create_and_place_unit(5, 11, "CAVALRY", "NORTH")
board.create_and_place_unit(5, 12, "CANNON", "NORTH")

# Make moves (enforces 5-unit limit)
board.make_turn_move(5, 10, 6, 10)
board.make_turn_move(5, 11, 6, 11)
board.make_turn_move(5, 12, 6, 12)

# Check move status
print(f"Moves made: {board.get_moves_this_turn()}")  # 3
print(f"Moves remaining: {5 - board.get_moves_this_turn()}")  # 2
print(f"Can move more: {board.can_move_more()}")  # True

# Check if a specific unit already moved
print(f"Did (5, 10) move? {board.has_moved_this_turn(5, 10)}")  # True
```

### Battle Phase

After movement, switch to the battle phase to attack or pass:

```python
# Switch to battle phase
board.switch_to_battle_phase()
print(f"Current phase: {board.current_phase}")  # 'B'

# Attack a target
result = board.make_turn_attack(1, 10)
print(f"Attack result: {result['outcome'].value}")  # CAPTURE, RETREAT, or NEUTRAL
print(f"Attacks made: {board.get_attacks_this_turn()}")  # 1
print(f"Can attack more: {board.can_attack_more()}")  # False

# Or pass (skip attack)
board.pass_attack()
```

### Turn Sequence

Complete a full turn by moving, attacking, and ending:

```python
from pykrieg import Board, get_turn_summary

board = Board()

# Setup: NORTH's turn
board.create_and_place_unit(5, 10, "INFANTRY", "NORTH")
board.create_and_place_unit(5, 11, "CAVALRY", "NORTH")
board.create_and_place_unit(5, 12, "CANNON", "SOUTH")

# Movement Phase
board.make_turn_move(5, 10, 6, 10)
board.make_turn_move(5, 11, 6, 11)

# Switch to battle
board.switch_to_battle_phase()

# Attack
result = board.make_turn_attack(5, 12)
print(f"Outcome: {result['outcome'].value}")

# End turn (switches to SOUTH, resets phase, resolves retreats)
board.end_turn()

# Check new turn state
print(f"Turn {board.turn_number}, {board.turn}'s turn")
print(f"Phase: {board.current_phase}")  # 'M' (movement)
```

### Turn Summary

Get a detailed summary of the current turn:

```python
from pykrieg import get_turn_summary

summary = get_turn_summary(board)
print(f"Turn: {summary['turn_number']}")
print(f"Player: {summary['current_player']}")
print(f"Phase: {summary['current_phase']}")
print(f"Moves: {summary['moves_made']}/{summary['moves_made'] + summary['moves_remaining']}")
print(f"Attacks: {summary['attacks_made']}/{summary['attacks_made'] + summary['attacks_remaining']}")
print(f"Pending retreats: {summary['pending_retreats']}")
```

### Retreat Management

When a combat results in RETREAT, the unit must retreat at the start of its next turn:

```python
# Simulate a retreat result (from combat)
board.create_and_place_unit(15, 10, "INFANTRY", "SOUTH")
board.add_pending_retreat(15, 10)

# End NORTH's turn, resolve SOUTH's retreats
board.end_turn()

# Check retreat status (unit marked as moved, cannot attack)
print(f"Pending retreats: {board.get_pending_retreats()}")
print(f"Unit at (15, 10) has moved: {board.has_moved_this_turn(15, 10)}")
```

### Turn State with FEN

Turn state is preserved in FEN format:

```python
from pykrieg import Fen

# Export board with turn state
fen = Fen.board_to_fen(board)
print(fen)  # Includes turn_number, phase, and retreats

# Import and restore turn state
board2 = Fen.fen_to_board(fen)
print(f"Restored turn: {board2.turn_number}")
print(f"Restored phase: {board2.current_phase}")
print(f"Restored player: {board2.turn}")
```

### Turn Validation

The board validates all turn actions:

```python
# Validate a move before making it
if board.validate_move(5, 10, 6, 10):
    board.make_turn_move(5, 10, 6, 10)

# Validate an attack before making it
if board.validate_attack(1, 12):
    result = board.make_turn_attack(1, 12)

# Check if turn can be ended
from pykrieg import can_end_turn
if can_end_turn(board):
    board.end_turn()
```

```

## Documentation

Comprehensive documentation is available at [docs/](docs/) covering:
- Basic usage
- API reference for Board, FEN, and utility functions
- Coordinate system details
- FEN format specification
- Type definitions

Build documentation locally::

   cd docs
   make html

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Donations

If you like the project and want to support future development, consider donating!

[![Donation Button](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=V444RPNWZTNXQ)

## License

This project is licensed under the GNU General Public License v3.0 - see [LICENSE](LICENSE) for details.

The GPL v3 license ensures that:
- The software remains free for all users
- Derivative works must be shared under the same license (copyleft)
- Commercial use is prohibited (requires separate commercial license)
- Users have the freedom to study, modify, and distribute the software
