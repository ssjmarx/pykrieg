"""Tests for effective stats (online/offline units)."""


from pykrieg.board import Board
from pykrieg.constants import (
    PLAYER_NORTH,
    UNIT_CAVALRY,
    UNIT_INFANTRY,
    UNIT_RELAY,
    UNIT_SWIFT_RELAY,
)


class TestEffectiveStats:
    """Test that offline units have zero stats (except relays)."""

    def test_offline_infantry_has_zero_attack(self):
        """Test that offline infantry has zero attack."""
        board = Board()

        # Place infantry without any network
        board.create_and_place_unit(5, 5, UNIT_INFANTRY, PLAYER_NORTH)
        board.enable_networks()

        infantry = board.get_unit(5, 5)
        assert infantry is not None
        assert infantry.get_effective_attack(board) == 0

    def test_offline_infantry_has_zero_defense(self):
        """Test that offline infantry has zero defense."""
        board = Board()

        board.create_and_place_unit(5, 5, UNIT_INFANTRY, PLAYER_NORTH)
        board.enable_networks()

        infantry = board.get_unit(5, 5)
        assert infantry is not None
        assert infantry.get_effective_defense(board) == 0

    def test_offline_infantry_has_zero_range(self):
        """Test that offline infantry has zero range."""
        board = Board()

        board.create_and_place_unit(5, 5, UNIT_INFANTRY, PLAYER_NORTH)
        board.enable_networks()

        infantry = board.get_unit(5, 5)
        assert infantry is not None
        assert infantry.get_effective_range(board) == 0

    def test_offline_infantry_has_zero_movement(self):
        """Test that offline infantry has zero movement."""
        board = Board()

        board.create_and_place_unit(5, 5, UNIT_INFANTRY, PLAYER_NORTH)
        board.enable_networks()

        infantry = board.get_unit(5, 5)
        assert infantry is not None
        assert infantry.get_effective_movement(board) == 0

    def test_online_infantry_has_full_stats(self):
        """Test that online infantry has full stats."""
        board = Board()

        board.set_arsenal(5, 5, PLAYER_NORTH)
        board.create_and_place_unit(6, 5, UNIT_INFANTRY, PLAYER_NORTH)
        board.enable_networks()

        infantry = board.get_unit(6, 5)
        assert infantry is not None
        assert infantry.get_effective_attack(board) == 4
        assert infantry.get_effective_defense(board) == 6
        assert infantry.get_effective_range(board) == 2
        assert infantry.get_effective_movement(board) == 1

    def test_offline_relay_has_full_defense(self):
        """Test that offline relay has full defense."""
        board = Board()

        board.create_and_place_unit(5, 5, UNIT_RELAY, PLAYER_NORTH)
        board.enable_networks()

        relay = board.get_unit(5, 5)
        assert relay is not None
        assert relay.get_effective_defense(board) == 1

    def test_offline_relay_can_move(self):
        """Test that offline relay can move."""
        board = Board()

        board.create_and_place_unit(5, 5, UNIT_RELAY, PLAYER_NORTH)
        board.enable_networks()

        relay = board.get_unit(5, 5)
        assert relay is not None
        assert relay.get_effective_movement(board) == 1

    def test_offline_swift_relay_can_move(self):
        """Test that offline swift relay can move."""
        board = Board()

        board.create_and_place_unit(5, 5, UNIT_SWIFT_RELAY, PLAYER_NORTH)
        board.enable_networks()

        relay = board.get_unit(5, 5)
        assert relay is not None
        assert relay.get_effective_movement(board) == 2

    def test_offline_cavalry_has_zero_charge_bonus(self):
        """Test that offline cavalry can't charge."""
        board = Board()

        board.create_and_place_unit(5, 5, UNIT_CAVALRY, PLAYER_NORTH)
        board.enable_networks()

        cavalry = board.get_unit(5, 5)
        assert cavalry is not None
        # Even if adjacent, offline cavalry has 0 attack
        assert cavalry.get_effective_attack(board) == 0
