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
  - Infantry: 1 square radius (8 maximum legal moves)
  - Cavalry: 2 squares radius (24 maximum legal moves)
  - Cannon: 1 square radius (8 maximum legal moves)
  - Arsenals: No movement (movement=0, immobile)
  - Relays: 1 square radius (8 maximum legal moves)
  - Swift Cannons: 2 squares radius (24 maximum legal moves)
  - Swift Relays: 2 squares radius (24 maximum legal moves)
- Move generation system producing pseudo-legal moves
- Movement validation
- Move execution (updating board state)
- Board convenience methods for movement operations
- Deprecated get_piece/set_piece methods (to be removed in 0.3.0)

**Testing Requirements**:
- Individual unit movement pattern tests (85%+ coverage)
- Move generation accuracy tests
- Basic move validation tests
- Integration tests for movement sequences

**Success Criteria**:
- All unit types can move according to basic rules
- Move generation produces all legal moves
- Board state updates correctly after movement

**Implementation Status**: Complete
- All movement functions implemented in src/pykrieg/movement.py
- Board convenience methods added (get_legal_moves, is_legal_move, make_move)
- Comprehensive test suite with 91 tests achieving 100% coverage
- All 291 tests passing (100% overall coverage)

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
- Stacking bonuses for multiple cavalry (up to 4, gaps break stacking)
- Turn number and phase tracking
- Retreat tracking infrastructure

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

**Implementation Status**: Complete
- Combat module implemented in src/pykrieg/combat.py (100% coverage)
- Turn/phase tracking added to Board class (100% coverage)
- Retreat tracking methods added to Board class (100% coverage)
- Comprehensive test suite with 91 tests (100% combat module coverage)
- All 384 tests passing (99% overall coverage)
- Ruff linting: All checks passed
- Mypy type checking: Success, no issues

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

### 0.1.5 - Console Interface (Basic)
**Milestone**: Text-based playable interface for development and testing

**Features**:
- ASCII board display (basic grid with unit symbols)
- Command-line input for moves (coordinate-based)
- Turn-by-turn game play against another human
- Game state display (current player, turn phase)
- Help system with commands and move format
- Save/load functionality (using FEN format)
- Basic error messages for invalid moves

**Testing Requirements**:
- Functional tests (complete game playable)
- Display accuracy tests (board representation)
- Input parsing tests (move commands)
- Save/load integration tests
- Cross-platform compatibility tests (basic verification)

**Success Criteria**:
- Complete game playable from terminal
- Clear board visualization with unit symbols
- Intuitive command interface
- Works on major platforms (Linux, macOS, Windows)
- Enables practical testing during development

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
- Tutorial: Basic usage for beginners
- Tutorial: Creating custom UIs
- Tutorial: Building AI engines
- API reference (complete)
- Example code snippets
- Common patterns and best practices
- Troubleshooting guide

**Testing Requirements**:
- Doctest execution (all examples)
- Tutorial code execution tests
- Documentation completeness checks
- Accuracy verification

**Success Criteria**:
- All public APIs documented with examples
- Tutorials walk through common use cases
- Examples execute without errors
- Documentation builds successfully

---

### 0.4.3 - Test Suite Completion
**Milestone**: Comprehensive test coverage

**Features**:
- Complete unit test suite (90%+ coverage overall, 95%+ for core)
- Integration test suite
- Regression test suite (all known scenarios)
- Property-based test suite (Hypothesis)
- Performance benchmark suite
- CI/CD pipeline optimization

**Testing Requirements**:
- Coverage measurement (coverage.py)
- All test categories passing
- CI/CD pipeline functional
- Test execution time <5 minutes for fast suite

**Success Criteria**:
- 90%+ code coverage achieved
- All tests pass in CI/CD
- Fast feedback during development
- Regression tests catch known bugs

---

### 0.4.4 - Stability and Robustness
**Milestone**: Production-ready stability

**Features**:
- Error handling improvements
- Input validation
- Graceful failure modes
- Logging infrastructure
- Debug mode options
- Comprehensive edge case handling

**Testing Requirements**:
- Error handling tests
- Input validation tests
- Edge case scenario tests
- Stress tests
- Fuzzing tests

**Success Criteria**:
- No crashes on invalid input
- Clear error messages
- Debug mode provides useful information
- Handles all edge cases gracefully

---

## 0.5.x Series: EXTENSIBILITY

**Goal**: Open code to alternative rulesets and community engagement. Provide example alternate game boards, pieces, and rules variations, with necessary functions for community to make more than 1:1 recreations of Debord's game.

### 0.5.0 - Extension Points
**Milestone**: Clean interfaces for customization

**Features**:
- Unit type extension interface
- Terrain type extension interface
- Victory condition extension interface
- Movement rule extension interface
- Combat rule extension interface
- Extension documentation and examples

**Testing Requirements**:
- Extension point tests (custom components integrate cleanly)
- Interface compliance tests
- Extension example tests
- Backward compatibility tests

**Success Criteria**:
- Custom unit types work without modifying core code
- Custom terrain types work without modifying core code
- Extensions documented with clear examples

---

### 0.5.1 - Console Interface (Enhanced)
**Milestone**: Feature-rich terminal experience

**Features**:
- Enhanced ASCII board display with terrain
- Advanced command-line interface (move history, undo/redo)
- Support for playing against AI engines
- Game state display (online/offline units, networks)
- Comprehensive help system
- Save/load functionality with game records
- Detailed error messages and move validation

**Testing Requirements**:
- Functional tests (full game play with AI)
- Display accuracy tests (terrain and unit symbols)
- Input parsing tests (all command types)
- Save/load integration tests (full game records)
- Cross-platform compatibility tests

**Success Criteria**:
- Complete game playable from terminal with AI
- Clear visual representation of all game elements
- Intuitive command interface with full feature set
- Works on Windows, macOS, Linux

---

### 0.5.2 - GUI Reference Implementation
**Milestone**: Graphical playable interface

**Features**:
- Pygame-based GUI
- Visual board with pieces and terrain
- Click-based move input
- Animation support (optional)
- Game state visualization
- Save/load functionality
- Engine integration support

**Testing Requirements**:
- Functional tests (full game play)
- Visual accuracy tests
- Event handling tests
- Performance tests (60 FPS target)
- Cross-platform tests

**Success Criteria**:
- Complete game playable with mouse
- Clear visual representation
- Smooth animations
- Multiple screen sizes supported

---

### 0.5.3 - Enhanced Engines
**Milestone**: Advanced AI opponents

**Features**:
- Opening system (book + generation)
- Endgame tables
- Machine learning integration (optional)
- Personality profiles (aggressive, defensive, etc.)
- Difficulty levels
- Analysis mode
- Multi-threading support

**Testing Requirements**:
- Engine strength tests (ELO-like rating system)
- Opening system tests
- Endgame table tests
- Performance tests
- Multi-threading correctness tests

**Success Criteria**:
- Multiple difficulty levels available
- Opening system provides solid early play
- Endgame tables improve final phase
- Multi-threading improves search depth

---

### 0.5.4 - Game Variants
**Milestone**: Example alternate rulesets

**Features**:
- Smaller board variant (10×12)
- Fog of war variant
- Asymmetric unit variants
- Alternative victory conditions
- Custom terrain layouts
- Variant selection interface
- Variant documentation

**Testing Requirements**:
- Each variant playable (full game tests)
- Variant rule enforcement tests
- Extension point demonstration tests
- Documentation accuracy tests

**Success Criteria**:
- Multiple variants included and playable
- Variants demonstrate extension capabilities
- Clear documentation for creating variants
- Community can create new variants easily

---

### 0.5.5 - Community Ecosystem
**Milestone**: Ready for community contributions

**Features**:
- Contribution guidelines
- Code of conduct
- Issue reporting templates
- Pull request template
- Release process documentation
- Community showcase (links to projects)
- Extension gallery

**Testing Requirements**:
- Contribution process tests (simulated PRs)
- Documentation completeness tests
- Template usability tests

**Success Criteria**:
- Clear contribution process
- Community guidelines established
- Multiple example implementations available
- Documentation for all extension points

---

## Post-0.5.0: Maintenance and Evolution

After 0.5.0 release, the project will transition to maintenance mode with:

### Maintenance Updates (0.5.x, 0.6.x)
- Bug fixes and stability improvements
- Performance optimizations
- Documentation updates
- Minor feature additions
- Python version support updates

### Major Feature Updates (1.0.0+)
- Breaking API changes (with migration guides)
- Significant new features
- Major performance improvements
- Community-driven enhancements

### Long-term Goals
- Integration with existing chess UIs (via protocol adapters)
- Online multiplayer support
- Tournament management tools
- Analysis and training features
- Mobile applications

---

## Development Principles

This roadmap is guided by these principles:

1. **Incremental Delivery**: Each sub-release adds concrete value
2. **Testing First**: Comprehensive tests ensure reliability
3. **Documentation Continuous**: Updated alongside code
4. **Community Focus**: Extension points from the beginning
5. **Performance Aware**: Optimization built into design
6. **Backward Compatible**: Stable API within major versions
7. **Open Development**: Community input throughout

## Timeline Estimates

- **0.1.x (Functional Prototype)**: 8-10 weeks
- **0.2.x (Playable Game)**: 10-12 weeks
- **0.3.x (Computer Opposition)**: 12-16 weeks (most experimental)
- **0.4.x (Usable Library)**: 8-10 weeks
- **0.5.x (Extensibility)**: 8-10 weeks

**Total estimated time**: 46-58 weeks (11-14 months)

*Note: These estimates assume part-time development. Actual timeline may vary based on complexity, unexpected challenges, and available development time.*

---

## Status Legend

- In Progress
- Complete
- Planned
- Blocked
- Deprecated

*Current version: Development phase*

For the latest status of each item, please check the [Issues](https://github.com/ssjmarx/pykrieg/issues).
