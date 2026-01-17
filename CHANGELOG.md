# Changelog

All notable changes to Pykrieg will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Cavalry charge restrictions for terrain (0.2.3 feature)
  - Cavalry charge bonus does NOT apply when attacking units in fortress or mountain pass

## [0.2.3] - 2025-01-17

### Added
- **KFEN Format**: Complete JSON-based game record format for saving and loading games
  - KFENMetadata: Game name, dates, players, events, result tracking
  - KFENBoardInfo: Board dimensions and FEN string representation
  - KFENGameState: Current turn, player, phase, pending retreats
  - KFENTurn: Complete turn structure with moves, attacks, and turn boundaries
  - KFENMove: Individual move records with position, unit type, retreat status
  - KFENAttack: Attack details including outcome, captures, retreat positions
  - KFENUndoRedo: Undo/redo history state

- **Game Serialization**: Full game state persistence
  - `write_kfen()`: Save board state and complete turn history to KFEN file
  - `read_kfen()`: Load KFEN file into KFENDocument structure
  - `reconstruct_board_from_history()`: Rebuild board from KFEN turn history

- **History Validation**: Turn sequence verification
  - `validate_history()`: Validates turn numbers, player alternation, move/attack counts
  - Checks board dimensions and game state consistency

- **Console Integration**: KFEN format support in console interface
  - Save games with `save filename.kfen` command
  - Load games with `load filename.kfen` command
  - Automatic format detection (.kfen vs .fen extension)
  - Metadata support (game name, players, event)

- **Format Conversion**: Convert between FEN and KFEN
  - `convert_fen_to_kfen()`: Convert legacy FEN files to KFEN format
  - `export_kfen_to_fen()`: Export board state from KFEN to FEN format

### Changed
- Updated version to 0.2.3 across all files
- Console interface displays version 0.2.3

### Fixed
- None

## [0.2.2] - 2025-01-09

### Added
- **Victory Condition Detection**: Complete win state detection system
  - Victory condition 1: Destruction of both enemy arsenals
  - Victory condition 2: Elimination of all enemy combat units
  - Victory condition 3: Destruction of both enemy relays with all enemy units offline
  - `check_victory_conditions()`: Check all victory conditions after each turn
  - `check_total_annihilation()`: Detect complete unit elimination
  - `check_network_collapse()`: Detect network collapse (all relays destroyed)

- **Game State Tracking**: Track game outcome
  - `is_game_over()`: Check if game has ended
  - `game_state` property: Current game state (ONGOING, NORTH_WINS, SOUTH_WINS, DRAW)
  - `victory_result` property: Detailed victory information
  - `handle_surrender()`: Support for player surrender

- **Enemy Arsenal Destruction**: Move onto enemy arsenal destroys it
  - Moving onto enemy arsenal destroys it immediately
  - Counts as the player's attack for the turn
  - Ends turn immediately after destruction
  - Victory condition checked after arsenal destruction

- **Console Commands**: Surrender support
  - `surrender` command: Player can surrender from console
  - Automatic victory detection after surrender

### Changed
- Updated version to 0.2.2 across all files
- Arsenals changed from units to terrain structures (0.2.1 change, completed in 0.2.2)

### Fixed
- Victory conditions properly checked after each turn
- Game over state correctly maintained across save/load

## [0.2.1] - 2025-01-09

### Added
- **Terrain System**: Complete terrain implementation with four terrain types
  - **Mountains**: Block movement and lines of communication
  - **Mountain Passes**: Allow movement, provide +2 defense bonus
  - **Fortresses**: Provide +2 defense bonus, neutral occupation
  - **Arsenals**: Network anchors with special destruction rules

- **Terrain Methods**: Board terrain management
  - `set_terrain()`: Place terrain on board
  - `get_terrain()`: Query terrain type at position
  - `get_terrain_list()`: Get all terrain positions
  - Terrain validation in movement and combat

- **Terrain in Combat**: Combat modifiers based on terrain
  - Mountain pass: +2 defense bonus to defender
  - Fortress: +2 defense bonus to defender
  - Mountains: Cannot be attacked or moved to
  - `calculate_defense_power()` includes terrain bonuses
  - Combat result includes terrain information

- **Terrain in Movement**: Movement restrictions based on terrain
  - Mountains block movement
  - All terrain types validated in movement
  - Movement range considers terrain obstacles

- **Arsenal as Terrain**: Arsenals changed from units to terrain structures
  - `set_arsenal()`: Place arsenal terrain
  - `get_arsenal_owner()`: Query arsenal ownership
  - `get_arsenal_list()`: Get all arsenal positions
  - Arsenals are no longer unit type in `create_piece()`

- **FEN Format Extension**: Terrain support in FEN strings
  - Bracket notation: `(I)` for unit on pass, `[I]` for unit in fortress
  - `m` for mountain, `p` for empty pass, `f` for empty fortress
  - Updated `board_to_fen()` and `fen_to_board()` to handle terrain
  - Backward compatible with terrain-free FEN (20 parts vs 25 parts)

- **Console Display**: Terrain visualization
  - Mountains displayed with special character
  - Passes and fortresses shown with terrain indicators
  - Terrain colors in rich mode
  - Terrain symbols in compatibility mode

### Changed
- Updated version to 0.2.1 across all files
- FEN format extended to 25 parts (from 23 in 0.1.4)

### Fixed
- Terrain correctly serialized and deserialized in FEN
- Movement validation respects terrain restrictions
- Combat calculation includes terrain defense bonuses

## [0.2.0] - 2025-01-09

### Added
- **Lines of Communication (LOC) Network System**: Complete network connectivity tracking
  - Network tracing from arsenals through relays
  - 8-directional ray propagation from arsenals
  - Recursive relay chaining (relays extend signals along their rays)
  - Two-step propagation: arsenals activate units, relays propagate signals

- **Online/Offline Status**: Unit connectivity tracking
  - `calculate_network()`: Compute network coverage for a player
  - `is_unit_online()`: Check if unit is connected to network
  - `is_relay_online()`: Check if relay can propagate signal
  - `get_online_units()`: Get all online units for a player
  - `get_offline_units()`: Get all offline units for a player
  - `get_network_active_relays()`: Get all active relays for propagation

- **Network Blockage Detection**: Terrain and unit obstacles
  - Mountains block network propagation
  - Enemy units block network propagation
  - Enemy relays are special: allow signal pass-through
  - Mountain passes allow network propagation

- **Effective Stats**: Network-dependent unit statistics
  - `get_effective_attack()`: Attack power (0 if offline)
  - `get_effective_defense()`: Defense power (0 if offline, relays always have defense)
  - `get_effective_movement()`: Movement range (0 if offline, relays can move offline)
  - `get_effective_range()`: Attack range (0 if offline)
  - Offline units have zero attack/defense/range (except relays have defense)

- **Network Update Triggers**: Automatic network recalculation
  - Network recalculated after each move
  - Network recalculated after captures/retreats
  - Network recalculated after undo/redo operations
  - `enable_networks()`: Activate network system (opt-in for backward compatibility)

- **Terrain Types (Pre-implementation)**: Constants for terrain system
  - `TERRAIN_NONE`: Default flat terrain
  - `TERRAIN_MOUNTAIN`: Mountain terrain
  - `TERRAIN_PASS`: Mountain pass terrain
  - `TERRAIN_FORTRESS`: Fortress terrain

- **Console Network Features**: Network status in console
  - Network calculation on board initialization
  - Network status messages for offline units
  - Relay placement guidance for network building
  - `enable_networks()` called on game start

- **Network Test Suite**: Comprehensive testing
  - `test_network/` directory with network tests
  - Ray propagation tests
  - Relay chaining tests
  - Effective stats tests
  - Proximity propagation tests
  - Console relay chaining tests

### Changed
- Updated version to 0.2.0 across all files
- Board structure extended with network tracking arrays

- **Backward Compatibility**: Networks disabled by default
  - All units considered "online" unless `enable_networks()` is called
  - Pre-0.2.0 behavior preserved for existing code
  - Users must explicitly activate network system

### Fixed
- Network propagation correctly handles relay chaining
- Enemy units properly block network rays
- Relays can still move and defend when offline
- Network updates triggered at appropriate game events

## [0.1.5] - Estimated 2024-12-XX

### Added
- **Retreat Enforcement**: System to ensure units retreat before other actions
  - `get_units_must_retreat()`: Get list of units that must retreat
  - `is_unit_in_retreat()`: Check if unit must retreat
  - Retreat enforcement in movement phase
  - Only retreating units can be selected/moved during retreat phase

- **Console Retreat UI**: Visual feedback for retreat requirements
  - Warning message for units that must retreat
  - Forced selection of retreating units first
  - Clear error messages when non-retreating units selected

### Changed
- Updated console interface for retreat enforcement
- Modified click handling to enforce retreat order

### Fixed
- Units must retreat before making other moves
- Retreat requirements clearly communicated to players

## [0.1.4] - Estimated 2024-12-XX

### Added
- **Turn Management**: Complete turn structure implementation
  - Movement phase (up to 5 units)
  - Battle phase (1 attack or pass)
  - Turn tracking and alternation
  - `end_turn()`: Complete turn and switch players

- **Moved Unit Tracking**: Track which units have moved this turn
  - `get_moves_this_turn()`: Count moves made this turn
  - `has_moved_this_turn()`: Check if specific unit moved
  - Move limit enforcement (5 units maximum)

- **Turn Validation**: Ensure rules are followed
  - `validate_move()`: Validate move against turn constraints
  - `validate_attack()`: Validate attack against turn constraints
  - `can_move_more()`: Check if more moves available
  - `can_attack_more()`: Check if attack available

- **Turn State Management**: Current phase and player tracking
  - `current_phase` property: 'M' (Movement) or 'B' (Battle)
  - `turn` property: 'NORTH' or 'SOUTH'
  - `turn_number` property: Current turn number

- **Phase Transitions**: Automatic and manual phase switching
  - `switch_to_battle_phase()`: Transition from movement to battle
  - Validation: Cannot switch if units must retreat
  - Auto-switch when all moves used

- **FEN Extension**: Turn state in FEN format
  - 25 parts format (from 23 parts in 0.1.0)
  - Turn character: 'N' or 'S'
  - Phase character: 'M' or 'B'
  - Actions string: Move list or attack target
  - Turn number: Integer turn counter

- **Console Phase Commands**: Phase management in console
  - `phase` command: Manual phase switching
  - Turn state display in game info
  - Phase-aware command validation

- **Turn Utilities**: Helper functions for turn state
  - `get_turn_state()`: Get complete turn state object
  - `get_turn_summary()`: Get turn summary dictionary
  - `can_end_turn()`: Check if turn can be ended
  - `validate_turn_action()`: Validate any turn action

### Changed
- Updated version to 0.1.4 across all files
- FEN format extended to 25 parts

### Fixed
- Turn rules properly enforced
- Turn state correctly persisted in FEN
- Phase transitions validated correctly

## [0.1.3] - Estimated 2024-12-XX

### Added
- **Combat System**: Complete vector-based combat calculation
  - Attack/defense summation along straight lines
  - 8 directional attack vectors (horizontal, vertical, diagonal)
  - Line-of-sight calculation for attack participation
  - `calculate_attack_power()`: Sum attack from all attacking units
  - `calculate_defense_power()`: Sum defense from all defending units

- **Combat Resolution**: Capture and retreat logic
  - Capture threshold: Attack ≥ Defense + 2
  - Retreat threshold: Attack = Defense + 1
  - Neutral: Attack ≤ Defense
  - `resolve_combat()`: Determine combat outcome
  - `execute_capture()`: Remove captured unit

- **Cavalry Charge Mechanics**: Adjacency bonus for cavalry
  - Cavalry adjacent to target get +1 attack bonus
  - Multiple cavalry stack bonuses (up to 4)
  - Gaps break stacking (consecutive cavalry required)
  - Directional stacking check (from same direction)

- **Combat Validation**: Pre-combat checks
  - `can_attack()`: Check if attack is possible
  - `is_adjacent()`: Check if squares are adjacent
  - Target validation (must have defending unit)

- **Line Units**: Get units along attack lines
  - `get_line_units()`: Get all units between attacker and target
  - Direction detection for attack vectors
  - Blocked attack detection (units in between)

- **Combat Preview**: Preview before attacking
  - `preview_combat()`: Calculate attack/defense without executing
  - Attack unit identification with contribution
  - Charging cavalry detection
  - Terrain bonus calculation

- **Turn Structure (Basic)**: Turn number tracking
  - `turn_number` property
  - Basic turn increment

### Changed
- Updated version to 0.1.3 across all files
- Combat is terrain-independent (terrain added in 0.2.1)
- Combat is range-independent (range added in 0.2.0)

### Fixed
- Combat correctly calculates attack/defense powers
- Capture/retreat thresholds enforced properly
- Cavalry charge stacking works correctly

## [0.1.2] - Estimated 2024-12-XX

### Added
- **Movement Rules**: Complete movement system for all unit types
  - Infantry: 1 square radius (8 maximum legal moves)
  - Cavalry: 2 squares radius (24 maximum legal moves)
  - Cannon: 1 square radius (8 maximum legal moves)
  - Swift Cannon: 2 squares radius (24 maximum legal moves)
  - Swift Relay: 2 squares radius (24 maximum legal moves)
  - Relays: 1 square radius (8 maximum legal moves)
  - Arsenals: No movement (immobile)

- **Move Generation**: Generate pseudo-legal moves
  - `generate_moves()`: Get all legal moves for a unit
  - `get_movement_range()`: Get movement range for unit type
  - `can_move()`: Check if unit can move

- **Move Validation**: Ensure moves are legal
  - `is_valid_move()`: Validate move constraints
  - Range checking (within unit's movement range)
  - Boundary checking (stay on board)
  - Destination validation (empty square)

- **Move Execution**: Apply moves to board
  - `execute_move()`: Execute validated move
  - Update unit position
  - Return moved unit

- **Board Convenience Methods**: Movement helper methods
  - `get_legal_moves()`: Alias for generate_moves()
  - `is_legal_move()`: Alias for is_valid_move()
  - `make_move()`: Alias for execute_move()

- **Swift Unit Types**: Fast variants of existing units
  - Swift Cannon: Extended movement (range 2)
  - Swift Relay: Extended movement (range 2)

### Changed
- Updated version to 0.1.2 across all files
- Movement is terrain-independent (terrain added in 0.2.1)

### Deprecated
- `get_piece()`: Use `get_unit()` instead
- `set_piece()`: Use `place_unit()` instead

### Fixed
- All unit types can move according to their rules
- Move generation produces all legal moves
- Board state updates correctly after movement

## [0.1.1] - Estimated 2024-12-XX

### Added
- **Unit Type System**: Complete unit hierarchy
  - Infantry: Attack 1, Defense 1, Movement 1, Range 3
  - Cavalry: Attack 2, Defense 1, Movement 2, Range 2
  - Cannon: Attack 3, Defense 2, Movement 1, Range 4
  - Relay: Attack 0, Defense 2, Movement 1, Range N/A
  - Swift Cannon: Attack 3, Defense 2, Movement 2, Range 4
  - Swift Relay: Attack 0, Defense 2, Movement 2, Range N/A

- **Unit Placement**: Place units on board
  - `place_unit()`: Place unit at position
  - `create_and_place_unit()`: Create and place unit in one call
  - Territory validation (can only place in own territory)

- **Unit Query Methods**: Query board for units
  - `get_unit()`: Get unit at position
  - `get_units_by_owner()`: Get all units for a player
  - `count_units()`: Count units by type and/or owner
  - `get_all_units()`: Get all units on board

- **Unit Factory**: Create units by type string
  - `create_piece()`: Factory function for unit creation
  - Supports all unit types: INFANTRY, CAVALRY, CANNON, RELAY, SWIFT_CANNON, SWIFT_RELAY

- **Unit Properties**: Query unit attributes
  - `get_movement_range()`: Get unit's movement range
  - `can_move()`: Check if unit can move
  - `get_unit_symbol()`: Get display symbol (rich/compat modes)

### Changed
- Updated version to 0.1.1 across all files
- Arsenals are units (changed to terrain in 0.2.1)

### Fixed
- All unit types implemented with correct stats
- Units can be placed and queried on the board
- Class hierarchy allows easy extension

## [0.1.0] - Estimated 2024-12-XX

### Added
- **Project Scaffolding**: Initial project setup
  - Python 3.8+ support
  - Testing framework (pytest) configuration
  - Packaging tools (setuptools) configured
  - Repository structure following python-chess conventions

- **Board Class**: Core board data structure
  - 20×25 grid (500 squares)
  - Territory representation (North/South)
  - Coordinate system implementation
  - Boundary validation

- **Coordinate System**: Spreadsheet-style coordinates
  - `tuple_to_spreadsheet()`: Convert (row, col) to "1A" notation
  - `spreadsheet_to_tuple()`: Convert "1A" notation to (row, col)
  - 0-indexed internal representation

- **FEN Format**: Position serialization/deserialization
  - `board_to_fen()`: Serialize board to FEN string
  - `fen_to_board()`: Deserialize FEN string to board
  - Basic FEN format (23 parts: board + turn + phase + actions)

- **Territory System**: Board territory tracking
  - `get_territory()`: Get territory at position
  - Territory boundaries: North (rows 0-9), South (rows 10-19)
  - Territory validation for placement

- **Basic Game State Management**: Turn and phase tracking
  - `turn`: Current player ('NORTH' or 'SOUTH')
  - `turn_number`: Current turn number
  - `current_phase`: Current phase ('M' or 'B')

- **Documentation Framework**: Sphinx documentation setup
  - docs/ directory structure
  - API documentation templates
  - ReadTheDocs configuration

### Changed
- Initial version 0.1.0

### Fixed
- Board can be created and saved/loaded accurately via FEN format
- All core data structures implemented

## [0.0.1] - Initial Release

### Added
- Initial project structure
- Basic board representation
- Unit type definitions
- Core constants

---

## Version Format

- **Major version**: Incompatible API changes
- **Minor version**: Backward-compatible functionality additions
- **Patch version**: Backward-compatible bug fixes

For more information, see the [ROADMAP.md](ROADMAP.md) for planned features and the [README.md](README.md) for usage instructions.
