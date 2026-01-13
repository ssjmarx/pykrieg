# Pykrieg Usage Guide

Advanced usage and API documentation for developers.

## Table of Contents

- [Board API](#board-api)
- [Unit Creation and Placement](#unit-creation-and-placement)
- [Movement](#movement)
- [Combat](#combat)
- [Turn Management](#turn-management)
- [FEN Format](#fen-format)
- [Console Interface](#console-interface)

---

## Board API

### Creating a Board

```python
from pykrieg import Board

# Create an empty board
board = Board()

# Query board state
print(board.count_units())  # Total units on board
print(board.turn)  # Current player ('NORTH' or 'SOUTH')
print(board.turn_number)  # Current turn number (starts at 1)
print(board.current_phase)  # 'M' (movement) or 'B' (battle)
```

### Querying Units

```python
from pykrieg import Board

board = Board()

# Count all units
print(board.count_units())

# Count specific unit type
print(board.count_units(unit_type='INFANTRY'))
print(board.count_units(owner='NORTH'))
print(board.count_units(unit_type='CAVALRY', owner='SOUTH'))

# Get unit at position
unit = board.get_unit(5, 10)
if unit:
    print(unit.unit_type)
    print(unit.owner)

# Get all units by owner
north_units = board.get_units_by_owner('NORTH')
print(north_units)  # List of (row, col) tuples
```

### Coordinate System

Pykrieg uses a 0-indexed (row, col) coordinate system:

```python
from pykrieg import Board

# Convert to/from spreadsheet notation (e.g., "1A")
print(Board.tuple_to_spreadsheet(0, 0))  # '1A'
print(Board.tuple_to_spreadsheet(5, 10))  # '6K'

print(Board.spreadsheet_to_tuple('1A'))  # (0, 0)
print(Board.spreadsheet_to_tuple('6K'))  # (5, 10)

# Territory ownership
print(board.get_territory(0, 0))  # 'NORTH' (north side)
print(board.get_territory(19, 24))  # 'SOUTH' (south side)
```

---

## Unit Creation and Placement

### Creating Units

```python
from pykrieg import Infantry, Cavalry, Cannon, Relay, Depot, Train

# Create units directly
infantry = Infantry('NORTH')
cavalry = Cavalry('SOUTH')
cannon = Cannon('NORTH')
relay = Relay('NORTH')
depot = Depot('NORTH')
train = Train('SOUTH')
```

### Placing Units

```python
from pykrieg import Board

board = Board()

# Using factory function (recommended)
board.create_and_place_unit(5, 10, 'INFANTRY', 'NORTH')
board.create_and_place_unit(5, 11, 'CAVALRY', 'SOUTH')

# Creating and placing separately
from pykrieg import Infantry, Cannon
infantry = Infantry('NORTH')
cannon = Cannon('NORTH')

board.place_unit(10, 10, infantry)
board.place_unit(12, 12, cannon)

# Note: You can only place units in your territory
# Attempting to place in enemy territory will fail
```

### Unit Properties

```python
from pykrieg import Board, get_movement_range, can_move, get_unit_symbol

unit = board.get_unit(5, 10)

# Movement properties
print(get_movement_range(unit))  # 0, 1, or 2
print(can_move(unit))  # True or False

# Unit symbol for display
print(get_unit_symbol(unit, 'rich'))  # Unicode symbol
print(get_unit_symbol(unit, 'compat'))  # ASCII character
```

---

## Movement

### Getting Legal Moves

```python
from pykrieg import Board, generate_moves

board = Board()
board.create_and_place_unit(5, 10, 'CAVALRY', 'NORTH')

# Get legal moves for a unit
moves = generate_moves(board, 5, 10)
print(f"Available moves: {moves}")  # List of (row, col) tuples

# Using Board method
moves = board.get_legal_moves(5, 10)  # Same result
```

### Validating Moves

```python
from pykrieg import Board, is_valid_move

board = Board()
board.create_and_place_unit(5, 10, 'INFANTRY', 'NORTH')

# Check if move is valid
if is_valid_move(board, 5, 10, 6, 10):
    print("Move is valid!")

# Using Board method
if board.is_legal_move(5, 10, 6, 10):
    print("Move is legal!")
```

### Executing Moves

```python
from pykrieg import Board, execute_move

board = Board()
board.create_and_place_unit(5, 10, 'INFANTRY', 'NORTH')

# Execute move
moved_unit = execute_move(board, 5, 10, 6, 10)
print(f"Moved {moved_unit.unit_type} to (6, 10)")

# Using Board method
unit = board.make_move(5, 10, 6, 10)  # Same result
```

---

## Combat

### Calculating Combat

```python
from pykrieg import Board, calculate_combat, CombatOutcome

board = Board()
board.create_and_place_unit(5, 10, 'INFANTRY', 'NORTH')
board.create_and_place_unit(5, 12, 'CAVALRY', 'SOUTH')

# Calculate combat for a target square
result = calculate_combat(board, 5, 12, attacker='NORTH', defender='SOUTH')
print(f"Attack Power: {result['attack_power']}")
print(f"Defense Power: {result['defense_power']}")
print(f"Outcome: {result['outcome'].value}")  # CAPTURE, RETREAT, or NEUTRAL

# Using Board method
result = board.calculate_combat(5, 12, 'NORTH', 'SOUTH')
```

### Capturing Units

```python
from pykrieg import Board, calculate_combat, execute_capture, CombatOutcome

board = Board()
board.create_and_place_unit(5, 10, 'INFANTRY', 'NORTH')
board.create_and_place_unit(5, 12, 'CAVALRY', 'SOUTH')

# Calculate combat
result = calculate_combat(board, 5, 12, attacker='NORTH', defender='SOUTH')

# Capture if attack was successful
if result['outcome'] == CombatOutcome.CAPTURE:
    captured_unit = execute_capture(board, 5, 12)
    print(f"Captured {captured_unit.unit_type}!")

# Using Board method
captured = board.execute_capture(5, 12)
```

---

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

---

## FEN Format

Pykrieg uses KFEN (Krieg FEN) format for saving and loading game states.

### Exporting to FEN

```python
from pykrieg import Board, Fen

board = Board()

# Setup board
board.create_and_place_unit(5, 10, 'INFANTRY', 'NORTH')
board.create_and_place_unit(5, 11, 'CAVALRY', 'NORTH')
board.create_and_place_unit(5, 12, 'CANNON', 'SOUTH')

# Make some moves
board.make_turn_move(5, 10, 6, 10)

# Export to FEN string
fen = Fen.board_to_fen(board)
print(fen)
```

### Importing from FEN

```python
from pykrieg import Fen

# Load from FEN string
board = Fen.fen_to_board(fen)

# Or load from file
with open('save_game.fen', 'r') as f:
    fen = f.read()
    board = Fen.fen_to_board(fen)
```

### FEN Format Specification

See [KFEN-SPECIFICATION.md](KFEN-SPECIFICATION.md) for complete format details.

---

## Lines of Communication (LOC) Network

The Lines of Communication system (v0.2.0) implements network connectivity rules where units must be connected to Arsenals through lines of sight to function properly.

### Network States

The network system has two states:

1. **Disabled (Default)**: All units are considered "online" and can move, attack, and defend normally. This is the pre-0.2.0 behavior and provides backward compatibility.

2. **Enabled**: Units must be within network coverage to function. Arsenals emit signals along 8 directional rays; Relays and Swift Relays can extend these signals. Units not connected have zero attack/defense/range (except Relays which can still move and defend).

### Enabling Networks

Network rules are **not enabled by default**. To activate them, explicitly call `enable_networks()` after setting up your board:

```python
from pykrieg import Board

board = Board()

# Setup board with arsenals and units
board.create_and_place_unit(5, 10, 'ARSENAL', 'NORTH')
board.create_and_place_unit(5, 12, 'RELAY', 'NORTH')
board.create_and_place_unit(5, 14, 'INFANTRY', 'NORTH')

# ENABLE network rules for both players
board.enable_networks()

# Now network rules apply:
# - Check if a unit is online
if board.is_unit_online(5, 14, 'NORTH'):
    print("Infantry is online and can act")
else:
    print("Infantry is offline (zero attack/defense/range)")

# - Get all online units
online_units = board.get_online_units('NORTH')
print(f"Online units: {len(online_units)}")

# - Get all offline units
offline_units = board.get_offline_units('NORTH')
print(f"Offline units: {len(offline_units)}")
```

### Network Coverage Calculation

The network system uses a two-step propagation algorithm:

**Step 1**: Arsenals activate all units along 8 directional rays (horizontal, vertical, diagonal).

**Step 2**: Relays and Swift Relays propagate the signal. If a Relay or Swift Relay is activated, it also activates units along its own 8 rays. This process repeats until no new Relays are activated.

Example:
```python
from pykrieg import Board

board = Board()

# Arsenal at (5, 0) - emits signal in all directions
board.create_and_place_unit(5, 0, 'ARSENAL', 'NORTH')

# Relay at (5, 5) - receives signal from Arsenal
board.create_and_place_unit(5, 5, 'RELAY', 'NORTH')

# Infantry at (5, 10) - receives signal from Relay
board.create_and_place_unit(5, 10, 'INFANTRY', 'NORTH')

# Second Relay at (5, 8) - receives signal from first Relay
board.create_and_place_unit(5, 8, 'RELAY', 'NORTH')

# Enable networks
board.enable_networks()

# Check connectivity
print(board.is_unit_online(5, 0, 'NORTH'))  # True (Arsenal)
print(board.is_unit_online(5, 5, 'NORTH'))  # True (connected to Arsenal)
print(board.is_unit_online(5, 8, 'NORTH'))  # True (connected to Relay at 5,5)
print(board.is_unit_online(5, 10, 'NORTH'))  # True (connected to Relay at 5,8)
```

### Effective Stats

When networks are enabled, units have "effective" stats that depend on their online status:

- **Attack/Defense/Range**: Zero for offline units (except Relays which always have defense)
- **Movement**: Zero for offline units (except Relays and Swift Relays which can move even when offline)

```python
from pykrieg import Board

board = Board()

# Enable networks (no arsenals = all units offline)
board.enable_networks()
board.create_and_place_unit(5, 10, 'INFANTRY', 'NORTH')

unit = board.get_unit(5, 10)

# Effective stats (offline = zero)
print(unit.get_effective_attack(board))    # 0 (no network connection)
print(unit.get_effective_defense(board))   # 0 (no network connection)
print(unit.get_effective_movement(board))  # 0 (no network connection)

# Relays can still move and defend when offline
board.create_and_place_unit(5, 11, 'RELAY', 'NORTH')
relay = board.get_unit(5, 11)
print(relay.get_effective_defense(board))   # 1 (Relays always have defense)
print(relay.get_effective_movement(board))  # 1 (Relays can move offline)
```

### Backward Compatibility

If you don't call `calculate_network()`, the system uses the optimistic default (all units online):

```python
from pykrieg import Board

board = Board()

# No calculate_network() call = networks disabled
board.create_and_place_unit(5, 10, 'INFANTRY', 'NORTH')

# All units considered online
print(board.is_unit_online(5, 10, 'NORTH'))  # True

# All units have full stats
unit = board.get_unit(5, 10)
print(unit.get_effective_attack(board))    # 4 (full attack)
print(unit.get_effective_defense(board))   # 6 (full defense)
print(unit.get_effective_movement(board))  # 1 (full movement)
```

### Loading Games with Networks

When loading a saved game, you must re-enable networks:

```python
from pykrieg import Board, Fen

# Load from FEN
with open('save_game.fen', 'r') as f:
    fen = f.read()
board = Fen.fen_to_board(fen)

# Re-enable networks if game uses them
board.enable_networks()
```

### Network Queries

```python
from pykrieg import Board

board = Board()
# ... setup and enable networks ...

# Check if a square is covered by network
if board.is_unit_online(row, col, 'NORTH'):
    print(f"Unit at ({row}, {col}) is online")

# Check if a relay is online (can propagate)
if board.is_relay_online(row, col, 'NORTH'):
    print(f"Relay at ({row}, {col}) is online and active")

# Get all online units for a player
online_units = board.get_online_units('NORTH')
print(f"North has {len(online_units)} online units")

# Get all offline units for a player
offline_units = board.get_offline_units('NORTH')
print(f"North has {len(offline_units)} offline units")

# Get active relays (can propagate signal)
active_relays = board.get_network_active_relays('NORTH')
print(f"North has {len(active_relays)} active relays")
```

---

## Console Interface

Pykrieg includes a full-featured console interface for playing games interactively (v0.2.0).

### Launching the Console

```bash
# Auto-detect terminal capabilities
python -m pykrieg.console

# Force rich mode (Unicode + colors)
python -m pykrieg.console --mode=rich

# Force compatibility mode (ASCII only)
python -m pykrieg.console --mode=compat

# Show help
python -m pykrieg.console --help
```

### Console Commands

| Command | Aliases | Description |
|---------|----------|-------------|
| `move 5,10 6,10` | `m 5,10 6,10` | Move a unit from position A to B |
| `attack 5,12` | `a 5,12` | Attack a target position |
| `pass` | `p` | Skip attack phase |
| `end` | `e` | End turn |
| `save filename.fen` | `s filename.fen` | Save game to file |
| `load filename.fen` | `l filename.fen` | Load game from file |
| `help` | `h`, `?` | Show available commands |
| `mode rich/compat` | - | Switch display mode |
| `quit` | `q` | Exit the game |

### Console Features

- **Automatic Terminal Detection**: Auto-detects Unicode and color support
- **Two Display Modes**:
  - Rich mode: Unicode symbols with ANSI colors (modern terminals)
  - Compatibility mode: ASCII characters (older terminals)
- **Mouse Support**: Click-to-coordinate entry (requires `prompt_toolkit`)
- **Command Buffering**: Queue multiple commands before execution
- **Copy/Paste Support**: Multi-line and semicolon-separated commands

### Programmatic Console Use

You can also use the console interface components programmatically:

```python
from pykrieg.console import ConsoleGame, DisplayMode

# Create a game with specific display mode
game = ConsoleGame(display_mode='compatibility')

# Run the main loop
game.run()

# Or use components individually
from pykrieg.console import BoardDisplay, MouseHandler
from pykrieg import Board

board = Board()
display = BoardDisplay(DisplayMode.RICH)
handler = MouseHandler(board, display)

# Render board
print(display.render(board))

# Handle mouse clicks
result = handler.handle_mouse_click(5, 10)
```

### Console API

#### BoardDisplay

```python
from pykrieg.console import BoardDisplay, DisplayMode
from pykrieg import Board

# Create display
display = BoardDisplay(DisplayMode.RICH)
board = Board()

# Render board to string
output = display.render(board)
print(output)
```

#### MouseHandler

```python
from pykrieg.console import MouseHandler
from pykrieg import Board

board = Board()
display = BoardDisplay(DisplayMode.RICH)
handler = MouseHandler(board, display)

# Handle mouse click
# Returns None if incomplete selection
# Returns command string if complete (e.g., "5,10 6,10")
result = handler.handle_mouse_click(5, 10)
```

#### CommandBuffer

```python
from pykrieg.console import CommandBuffer

buffer = CommandBuffer()

# Add commands
buffer.add_command("move 5,10 6,10")
buffer.add_command("end")

# Get queued commands
commands = buffer.get_commands()  # Returns newline-separated string

# Remove last command
buffer.remove_last()

# Clear buffer
buffer.clear()
```

#### CommandParser

```python
from pykrieg.console import parse_command, validate_command

# Parse command string
command = parse_command("move 5,10 6,10")

# Validate command
from pykrieg import Board
board = Board()
is_valid, error = validate_command(board, command)
```

---

## Additional Resources

- **[Read the Docs](https://pykrieg.readthedocs.io/)** - Comprehensive API reference
- **[KFEN Specification](KFEN-SPECIFICATION.md)** - Game format specification
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute to the project
