API Reference
=============

Pieces Module
--------------

Unit Type System
~~~~~~~~~~~~~~~~

.. autoclass:: pykrieg.pieces.Unit
    :members:

.. autoclass:: pykrieg.pieces.Infantry
    :members:

.. autoclass:: pykrieg.pieces.Cavalry
    :members:

.. autoclass:: pykrieg.pieces.Cannon
    :members:

.. autoclass:: pykrieg.pieces.Arsenal
    :members:

.. autoclass:: pykrieg.pieces.Relay
    :members:

.. autoclass:: pykrieg.pieces.SwiftCannon
    :members:

.. autoclass:: pykrieg.pieces.SwiftRelay
    :members:

Factory Function
~~~~~~~~~~~~~~~~

.. autofunction:: pykrieg.pieces.create_piece

Board Module
------------

.. automodule:: pykrieg.board
   :members:
   :undoc-members:
   :show-inheritance:

FEN Module
-----------

.. automodule:: pykrieg.fen
   :members:
   :undoc-members:
   :show-inheritance:

Constants Module
----------------

.. automodule:: pykrieg.constants
   :members:
   :undoc-members:

Types Module
------------

.. automodule:: pykrieg.types
   :members:
   :undoc-members:
   :no-index:

Turn Management

.. automodule:: pykrieg.turn
   :members:
   :undoc-members:

Turn Methods on Board
--------------------

The Board class provides turn management methods:

Movement Phase
~~~~~~~~~~~~~

.. automethod:: pykrieg.Board.has_moved_this_turn

.. automethod:: pykrieg.Board.get_moves_this_turn

.. automethod:: pykrieg.Board.can_move_more

.. automethod:: pykrieg.Board.validate_move

.. automethod:: pykrieg.Board.make_turn_move

Battle Phase
~~~~~~~~~~~~

.. automethod:: pykrieg.Board.get_attacks_this_turn

.. automethod:: pykrieg.Board.can_attack_more

.. automethod:: pykrieg.Board.validate_attack

.. automethod:: pykrieg.Board.make_turn_attack

.. automethod:: pykrieg.Board.pass_attack

Phase Management
~~~~~~~~~~~~~~~

.. automethod:: pykrieg.Board.switch_to_battle_phase

Retreat Management
~~~~~~~~~~~~~~~~~~

.. automethod:: pykrieg.Board.add_pending_retreat

.. automethod:: pykrieg.Board.get_pending_retreats

.. automethod:: pykrieg.Board.has_pending_retreat

.. automethod:: pykrieg.Board.clear_pending_retreats

.. automethod:: pykrieg.Board.resolve_retreats

Turn Control
~~~~~~~~~~~~

.. automethod:: pykrieg.Board.end_turn

.. automethod:: pykrieg.Board.reset_turn_state

.. automethod:: pykrieg.Board.increment_turn

Turn State
~~~~~~~~~~

.. automethod:: pykrieg.Board.turn_number

.. automethod:: pykrieg.Board.current_phase

Protocol Module
---------------

The protocol module implements a UCI-like communication protocol for engine-frontend communication.

Protocol Engine
~~~~~~~~~~~~~~~~

.. automodule:: pykrieg.protocol.engine
   :members:
   :undoc-members:

Protocol Parser
~~~~~~~~~~~~~~~~

.. automodule:: pykrieg.protocol.parser
   :members:
   :undoc-members:

Protocol Response
~~~~~~~~~~~~~~~~~

.. automodule:: pykrieg.protocol.response
   :members:
   :undoc-members:

Protocol Types
~~~~~~~~~~~~~~

.. automodule:: pykrieg.protocol.uci
   :members:
   :undoc-members:
