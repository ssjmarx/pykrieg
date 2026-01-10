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

**Version 0.1.0 Features:**

- 20×25 board representation
- Territory system (North/South)
- Coordinate system (tuple, spreadsheet-style, and index formats)
- FEN serialization format for board states
- Basic game state management

Quick Start
-----------

Installation::

   pip install pykrieg

Basic usage::

   from pykrieg import Board, Fen
   
   # Create a board
   board = Board()
   
   # Add pieces
   board.set_piece(0, 0, {'type': 'INFANTRY', 'owner': 'NORTH'})
   board.set_piece(19, 24, {'type': 'INFANTRY', 'owner': 'SOUTH'})
   
   # Serialize to FEN
   fen = Fen.board_to_fen(board)
   print(fen)
   
   # Deserialize from FEN
   board2 = Fen.fen_to_board(fen)

For more information, see the GitHub repository: https://github.com/ssjmarx/pykrieg
