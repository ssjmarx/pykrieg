# Pykrieg Development Roadmap

This roadmap outlines the planned development path for Pykrieg, from initial prototype to a fully-featured, extensible library for Guy Debord's *Le Jeu de la Guerre*. Each major release focuses on specific functionality goals, with sub-releases providing incremental, testable milestones.

## Release Strategy

Pykrieg follows a phased development approach with five major releases (0.1.0 through 0.5.0), each broken down into sub-releases. This allows for:
- **Incremental delivery**: Each sub-release adds concrete, testable functionality
- **Early feedback**: Users can test features as soon as they're available
- **Risk mitigation**: Issues are identified and addressed early in development
- **Quality assurance**: Comprehensive testing at each stage ensures reliability

---

## 0.1.x Series: FUNCTIONAL PROTOTYPE

**Goal**: Create a working library that can be imported, manipulate board states, make moves, and calculate battles. Users should be able to import a board state, make moves for either player, export an updated board state, and calculate battles.

### 0.1.0 - Foundation Setup
**Milestone**: Project scaffolding and core data structures

**Features**:
- Project setup with Python 3.8+ support
- Testing framework (pytest) and packaging tools configured
- Initial repository structure following python-chess conventions
- Basic Board class with 20×25 grid (500 squares)
- Territory representation (North/South)
- Coordinate system implementation
- FEN-like string format for position serialization/deserialization
- Basic game state management

**Testing Requirements**:
- Unit tests for board coordinate transformations
- Territory boundary validation tests
- Board serialization accuracy tests (90%+ coverage)
- FEN roundtrip conversion tests
- Documentation framework with Sphinx

**Success Criteria**:
- Board can be created and saved/loaded accurately via FEN format
- All core data structures implemented and tested
- Documentation framework functional with API auto-generation

---

### 0.1.1 - Unit Type System
**Milestone**: Complete unit hierarchy and attributes

**Features**:
- Unit type system implementation:
  - Infantry (attack: 1, defense: 1, movement: 1, range: 3)
  - Cavalry (attack: 2, defense: 1, movement: 2, range: 2)
  - Cannon (attack: 3, defense: 2, movement: 1, range: 4)
  - Arsenals (attack: 0, defense: 4, movement: 0, range: N/A)
  - Relays (attack: 0, defense: 2, movement: 0, range: N/A)
- Class hierarchy following python-chess's piece model
- Unit placement on board
- Unit query methods

**Testing Requirements**:
- Unit type attribute tests (85%+ coverage)
- Unit placement accuracy tests
- Query method tests for all unit types
- Property-based testing for edge cases

**Success Criteria**:
- All unit types implemented with correct stats
- Units can be placed and queried on the board
- Class hierarchy allows easy extension

---

### 0.1.2 - Movement Rules
**Milestone**: Basic movement patterns (terrain-independent)

**Features**:
- Movement rules for all unit types:
  - Infantry: 1 square orthogonally
  - Cavalry: 2 squares orthogonally
  - Cannon: 1 square orthogonally
  - Arsenals: No movement
  - Relays: No movement
- Move generation system producing pseudo-legal moves
- Movement validation
- Move execution (updating board state)

**Testing Requirements**:
- Individual unit movement pattern tests (85%+ coverage)
- Move generation accuracy tests
- Basic move validation tests
- Integration tests for movement sequences

**Success Criteria**:
- All unit types can move according to basic rules
- Move generation produces all legal moves
- Board state updates correctly after movement

---

### 0.1.3 - Combat System
**Milestone**: Vector-based combat calculation

**Features**:
- Vector-based combat calculation system
- Attack/defense summation along straight lines
- Capture resolution (≥2 threshold)
- Retreat resolution (=1 threshold)
- Attack direction and adjacency handling
- Cavalry charge mechanics (adjacency bonus)
- Stacking bonuses for multiple cavalry

**Testing Requirements**:
- Combat calculation tests for all unit combinations (85%+ coverage)
- Capture/retreat scenario tests
- Cavalry charge bonus tests
- Property-based testing for combat invariants
- Regression tests from known game scenarios

**Success Criteria**:
- Combat accurately resolves attacks and retreats
- Capture/retreat thresholds enforced correctly
- Special mechanics (charges, stacking) work as specified

---

### 0.1.4 - Turn Management
**Milestone**: Complete turn structure

**Features**:
- Turn structure implementation:
  - Movement phase (up to 5 units)
  - Attack phase (1 attack per turn)
- Moved unit tracking per turn
- Turn validation (enforce limits)
- Turn state management (player alternation)
- Board export/import functionality

**Testing Requirements**:
- Turn enforcement tests (5-unit limit, 1-attack limit)
- Turn state transition tests
- Full turn sequence tests (70%+ coverage)
- Board export/import accuracy tests

**Success Criteria**:
- Turns can be played with proper rule enforcement
- Board state can be exported after any turn
- Users can import, move for both players, export, and calculate battles

---

## 0.2.x Series: PLAYABLE GAME

**Goal**: Complete game implementation with all mechanics and edge cases validated. Users can play full games by inputting moves sequentially, exporting board state to a UI of their own design turn by turn.

### 0.2.0 - Lines of Communication
**Milestone**: Network tracing and online/offline tracking

**Features**:
- Recursive network tracing from arsenals through relays
- Online/offline status tracking for all units
- Terrain blockage detection (mountains, enemy units)
- Special pass-through rules (passes, enemy relays)
- Network update after each movement
- Network severing detection

**Testing Requirements**:
- Line of communication tracing tests (all relay configurations)
- Online/offline status update tests
- Terrain interaction tests with networks
- Complex network scenario tests
- Performance profiling (<100ms per calculation)

**Success Criteria**:
- Lines of communication accurately tracked
- Online/offline status updates correctly after movements
- Complex networks with terrain obstacles handled properly

---

### 0.2.1 - Terrain System
**Milestone**: Complete terrain implementation

**Features**:
- Terrain types implementation:
  - Mountains (block movement and communication)
  - Passes (movement allowed, defensive bonus)
  - Fortresses (defensive bonus, occupation neutrality)
  - Arsenals (network anchors, special destruction rules)
- Terrain placement on board
- Movement restrictions per terrain type
- Combat modifiers per terrain type
- Terrain query methods

**Testing Requirements**:
- Terrain movement restriction tests (all unit × terrain combinations)
- Terrain combat modifier tests (85%+ coverage)
- Terrain placement accuracy tests
- Integration tests for terrain + line of communication

**Success Criteria**:
- All terrain types correctly implemented
- Movement and combat properly modified by terrain
- Terrain interacts correctly with lines of communication

---

### 0.2.2 - Victory Conditions
**Milestone**: Complete win state detection

**Features**:
- Victory condition 1: Destruction of both arsenals
- Victory condition 2: Elimination of all combat units
- Victory condition 3: Destruction of both relays with all units offline
- Victory condition checking after each turn
- Multiple condition detection
- Win/lose/draw state management

**Testing Requirements**:
- Individual victory condition tests (minimal scenarios)
- Multiple condition tests
- Edge case tests (simultaneous conditions)
- End-to-end game simulation tests

**Success Criteria**:
- All victory conditions detected correctly
- Game ends when victory condition met
- Edge cases handled properly

---

### 0.2.3 - Special Rules
**Milestone**: Edge cases and special mechanics

**Features**:
- Cavalry charge restrictions (cannot attack fortress/pass)
- Fortress occupation neutrality rules
- Arsenal destruction mechanics
- Special movement edge cases
- Unit placement restrictions
- Boundary condition handling

**Testing Requirements**:
- Special rule implementation tests
- Edge case scenario tests
- Boundary condition tests
- Regression test suite (known scenarios from Debord's book)

**Success Criteria**:
- All special rules implemented correctly
- Edge cases handled without crashes
- Regression test suite passes (100%)

---

### 0.2.4 - Game Record Format
**Milestone**: Save/load complete games

**Features**:
- Game record format (similar to PGN for chess)
- Position format (similar to FEN for chess)
- Game serialization/deserialization
- Move notation system
- Game history tracking
- Replay functionality

**Testing Requirements**:
- Roundtrip conversion tests (game→format→game, board→format→board)
- Complex scenario tests (all unit types, all terrain)
- Game history accuracy tests
- Replay verification tests

**Success Criteria**:
- Complete games can be saved and loaded accurately
- Board states can be exported at any turn
- Users can build UIs that import/export states turn by turn

---

## 0.3.x Series: COMPUTER OPPOSITION

**Goal**: Develop efficient and effective computer opponents. This is the most experimental phase, requiring video game AI-inspired techniques since no equivalent to chess's Stockfish exists.

### 0.3.0 - Engine Communication Protocol
**Milestone**: UCI-like protocol for engine communication

**Features**:
- UCI-like protocol design for Debord's game
- Protocol commands:
  - Position setup
  - Move making
  - Analysis requests
  - Engine configuration
- Protocol parser implementation
- Response generation
- Protocol documentation

**Testing Requirements**:
- Protocol parser tests (all commands)
- Response generation tests
- Compliance tests with protocol specification
- Test harness simulating engine communication

**Success Criteria**:
- Protocol fully specified and documented
- Engines can communicate with frontends
- Protocol commands parsed and executed correctly

---

### 0.3.1 - Random Engine
**Milestone**: Baseline legal-move engine

**Features**:
- Random move generation from legal moves
- Engine communication protocol integration
- Position evaluation (basic heuristic)
- Move prioritization (simple scoring)
- Configuration options

**Testing Requirements**:
- Legal move generation tests
- Protocol compliance tests
- Engine functionality tests
- Performance benchmarks

**Success Criteria**:
- Random engine makes only legal moves
- Engine can play full games via protocol
- Serves as baseline for AI development

---

### 0.3.2 - Evaluation Function
**Milestone**: Static position evaluation

**Features**:
- Material evaluation (unit value calculation)
- Position evaluation (territory control, unit placement)
- Mobility evaluation (available moves)
- Network evaluation (online units, communication)
- Combined scoring function
- Position optimization hints

**Testing Requirements**:
- Evaluation component tests
- Position correlation tests (stronger positions score higher)
- Performance tests (<50ms per evaluation)
- Accuracy tests against known positions

**Success Criteria**:
- Evaluation function accurately assesses position strength
- Combined score correlates with winning chances
- Fast enough for real-time use

---

### 0.3.3 - Minimax Engine
**Milestone**: Basic adversarial search

**Features**:
- Minimax algorithm implementation
- Alpha-beta pruning
- Depth control
- Move ordering (simple heuristics)
- Evaluation function integration
- Quiescence search (optional)

**Testing Requirements**:
- Algorithm correctness tests
- Alpha-beta pruning efficiency tests
- Move ordering effectiveness tests
- Performance benchmarks (nodes/second)

**Success Criteria**:
- Minimax plays legal moves
- Alpha-beta pruning improves performance
- Engine plays stronger than random engine

---

### 0.3.4 - Advanced Search Techniques
**Milestone**: Video game AI-inspired optimizations

**Features**:
- Iterative deepening
- Transposition tables
- Principal variation search
- Aspiration windows
- Time management
- Adaptive depth based on position complexity

**Testing Requirements**:
- Search technique tests
- Performance improvement benchmarks
- Strength improvement tests
- Time control tests

**Success Criteria**:
- Advanced techniques improve performance significantly
- Engine respects time controls
- Stronger play than basic minimax

---

### 0.3.5 - Specialized Tactics
**Milestone**: Game-specific AI patterns

**Features**:
- Cavalry charge detection and evaluation
- Network attack prioritization
- Fortress/Pass special cases
- Endgame patterns
- Opening book support
- Pattern recognition

**Testing Requirements**:
- Tactic recognition tests
- Pattern evaluation accuracy tests
- Opening book integration tests
- Endgame pattern tests

**Success Criteria**:
- Engine recognizes and exploits tactical patterns
- Opening book provides solid early game
- Endgame play improves with pattern recognition

---

## 0.4.x Series: USABLE LIBRARY

**Goal**: Achieve great code hygiene, efficient performance, and complete API for clean, modern implementations. Library should have all necessary functions for developers to create implementations of Debord's game.

### 0.4.0 - API Refinement
**Milestone**: Polished, consistent public API

**Features**:
- API review and redesign
- Consistent naming conventions (python-chess style)
- Convenience methods for common operations
- Improved error handling
- Deprecation warnings for old API
- Backward compatibility within major version

**Testing Requirements**:
- API consistency tests
- Error handling tests
- Backward compatibility tests
- Documentation accuracy tests

**Success Criteria**:
- API intuitive and consistent
- All public methods documented
- Backward compatible with 0.3.x

---

### 0.4.1 - Performance Optimization
**Milestone**: Optimized critical paths

**Features**:
- Move generation optimization
- Combat calculation optimization
- Network tracing optimization
- Memory efficiency improvements
- Lazy evaluation where appropriate
- Performance regression tests

**Testing Requirements**:
- Critical path profiling
- Benchmark establishment
- Regression tests (fail if >10% degradation)
- Memory profiling
- Cross-platform performance tests

**Success Criteria**:
- Critical operations under 100ms
- No performance regressions
- Memory usage optimized for typical games

---

### 0.4.2 - Comprehensive Documentation
**Milestone**: Complete developer documentation

**Features**:
