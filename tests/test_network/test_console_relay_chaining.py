"""Test relay chaining in console game context."""

import os
import tempfile

from pykrieg.board import Board
from pykrieg.console.game import ConsoleGame
from pykrieg.constants import PLAYER_NORTH, UNIT_ARSENAL, UNIT_INFANTRY, UNIT_RELAY
from pykrieg.fen import Fen


def test_console_game_relay_chaining_via_fen():
    """Test relay-to-relay propagation by loading through ConsoleGame.

    This test creates a FEN file with relay chain, then loads it
    through ConsoleGame to replicate the actual game initialization.
    """
    # Create a board with relay chain
    board = Board()
    board.create_and_place_unit(1, 1, UNIT_ARSENAL, PLAYER_NORTH)
    board.create_and_place_unit(1, 5, UNIT_RELAY, PLAYER_NORTH)
    board.create_and_place_unit(5, 5, UNIT_RELAY, PLAYER_NORTH)
    board.create_and_place_unit(5, 20, UNIT_INFANTRY, PLAYER_NORTH)

    # Convert to FEN
    fen_string = Fen.board_to_fen(board)

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fen', delete=False) as f:
        f.write(fen_string)
        temp_fen_path = f.name

    try:
        # Load FEN using Fen.fen_to_board (what ConsoleGame does)
        loaded_board = Fen.fen_to_board(fen_string)

        # Enable networks (what ConsoleGame._load_default_position does)
        loaded_board.enable_networks()

        # Check that all relays and infantry are online
        print(f"\nRelay at (1,5) online: {loaded_board.is_relay_online(1, 5)}")
        print(f"Relay at (5,5) online: {loaded_board.is_relay_online(5, 5)}")
        print(f"Infantry at (5,20) online: {loaded_board.is_unit_online(5, 20, PLAYER_NORTH)}")

        assert loaded_board.is_relay_online(1, 5), "First relay should be online"
        assert loaded_board.is_relay_online(5, 5), "Second relay should be online"
        assert loaded_board.is_unit_online(5, 20, PLAYER_NORTH), "Infantry should be online"
    finally:
        # Clean up temp file
        os.unlink(temp_fen_path)


def test_console_game_board_direct():
    """Test by directly setting up ConsoleGame's board."""
    # Create a ConsoleGame (it loads default position)
    game = ConsoleGame(display_mode='compatibility')

    # Now manually set up relay chain on the game's board
    game.board.create_and_place_unit(1, 1, UNIT_ARSENAL, PLAYER_NORTH)
    game.board.create_and_place_unit(1, 5, UNIT_RELAY, PLAYER_NORTH)
    game.board.create_and_place_unit(5, 5, UNIT_RELAY, PLAYER_NORTH)
    game.board.create_and_place_unit(5, 20, UNIT_INFANTRY, PLAYER_NORTH)

    # Enable networks (like console game does after any board change)
    game.board.enable_networks()

    # Verify relay chain works on the actual game board
    print(f"\nGame board - Relay at (1,5) online: {game.board.is_relay_online(1, 5)}")
    print(f"Game board - Relay at (5,5) online: {game.board.is_relay_online(5, 5)}")
    print(f"Game board - Infantry at (5,20) online: {game.board.is_unit_online(5, 20, PLAYER_NORTH)}")

    assert game.board.is_relay_online(1, 5), "First relay should be online"
    assert game.board.is_relay_online(5, 5), "Second relay should be online"
    assert game.board.is_unit_online(5, 20, PLAYER_NORTH), "Infantry should be online"


if __name__ == "__main__":
    # Run tests with verbose output
    test_console_game_relay_chaining_via_fen()
    print("\n✓ test_console_game_relay_chaining_via_fen passed")

    test_console_game_board_direct()
    print("✓ test_console_game_board_direct passed")

    print("\n✓ All tests passed!")
