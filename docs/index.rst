Pykrieg Documentation
======================

Welcome to Pykrieg's documentation!

Pykrieg is a Pythonic wargame engine for Guy Debord's *Le Jeu de la Guerre* (A Game of War).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Introduction
============

Pykrieg is a Python implementation of Guy Debord's strategic tabletop game *Le Jeu de la Guerre*. This library provides a clean, extensible API for representing game states, managing territories, and serializing board positions.

**Version 0.3.0 Features:**

- Complete game rules implementation (movement, combat, turns)
- Lines of Communication (LOC) network system
- Terrain system (mountains, passes, fortresses, arsenals)
- Victory condition detection
- KFEN game record format with history tracking
- UCI-like protocol for engine communication
- Console interface with mouse support
- FEN and KFEN serialization formats
- Undo/redo functionality
- 71%+ test coverage

Quick Start
-----------

Installation::

   pip install pykrieg

Basic usage::

   from pykrieg import Board, Fen
   
   # Create a board
   board = Board()
   
   # Add pieces
   board.create_and_place_unit(0, 0, 'INFANTRY', 'NORTH')
   board.create_and_place_unit(19, 24, 'INFANTRY', 'SOUTH')
   
   # Serialize to FEN
   fen = Fen.board_to_fen(board)
   print(fen)
   
   # Deserialize from FEN
   board2 = Fen.fen_to_board(fen)

For more information, see:

- GitHub repository: https://github.com/ssjmarx/pykrieg
- Protocol Specification: https://github.com/ssjmarx/pykrieg/blob/main/PROTOCOL-SPECIFICATION.md
- KFEN Specification: https://github.com/ssjmarx/pykrieg/blob/main/KFEN-SPECIFICATION.md
- Usage Guide: https://github.com/ssjmarx/pykrieg/blob/main/USAGE.md

For full API documentation, visit https://pykrieg.readthedocs.io/en/latest/
