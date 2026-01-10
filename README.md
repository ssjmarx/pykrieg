# Pykrieg

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
from pykrieg import Board, Fen

# Create a board
board = Board()

# Add pieces
board.set_piece(0, 0, {'type': 'INFANTRY', 'owner': 'NORTH'})
board.set_piece(5, 10, {'type': 'CAVALRY', 'owner': 'NORTH'})
board.set_piece(19, 24, {'type': 'INFANTRY', 'owner': 'SOUTH'})

# Serialize to FEN
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

## Version 0.1.0 Features

- **Board Representation**: 20×25 grid with territory divisions (North/South)
- **Coordinate System**: Support for tuple, spreadsheet-style, and index formats
- **FEN Serialization**: Save and load board states in FEN format
- **Territory Management**: Query and manage North and South territories
- **Well-Documented**: Comprehensive docstrings and Sphinx documentation

## Development Status

**Current Version: 0.1.0**

See [0.1.0-implementation-plan.ignore.md](0.1.0-implementation-plan.ignore.md) for the complete implementation plan.

### Completed Features
- [x] Project setup and tooling
- [x] Board class with 20×25 grid representation
- [x] Territory system (North/South)
- [x] Coordinate system (tuple, spreadsheet-style, index)
- [x] FEN serialization format
- [x] Core data structures
- [x] Game state management with FEN serialization
- [x] Documentation framework setup

### Next Steps
After 0.1.0, the next patch will implement:
- Unit type system (Infantry, Cavalry, Cannon, Arsenals, Relays)
- Unit class hierarchy
- Unit placement and querying
- Unit attribute testing

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
