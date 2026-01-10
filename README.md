# Pykrieg

A Pythonic wargame engine for Guy Debord's *Le Jeu de la Guerre* (A Game of War).

## About

Pykrieg is a Python library that implements the complex rules of Guy Debord's strategic tabletop game, providing a clean, extensible API for developers to build custom interfaces, AI opponents, and analysis tools. The project is inspired by the successful **python-chess** library and follows similar design principles.

## Features

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
import pykrieg

# Create a new game
game = pykrieg.Game()

# Get legal moves
for move in game.legal_moves:
    print(move)

# Make a move
game.push(move)

# Check game state
print(game.is_game_over())
```

## Documentation

Comprehensive documentation is available at [docs/](docs/) covering:
- Basic usage
- API reference
- Creating custom variants
- Building AI engines
- Developing graphical interfaces

## Development Status

This project is currently in **Phase 1: Foundation and Core Infrastructure**. See [docs/prompt](docs/prompt) for the complete implementation plan.

### Current Phase Goals
- [x] Project setup and tooling
- [ ] Core data structures (board, territories, coordinate system)
- [ ] Game state management with FEN-like serialization
- [ ] Documentation framework setup

## Project Structure

```
pykrieg/
├── src/pykrieg/          # Main library code
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Example implementations
└── scripts/               # Utility scripts
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Inspired by Guy Debord's *Le Jeu de la Guerre*
- Modeled after the python-chess library
- Built following the implementation plan outlined in [docs/prompt](docs/prompt)
