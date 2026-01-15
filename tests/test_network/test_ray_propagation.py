"""Tests for ray-based propagation (Step 1 & 2)."""


from pykrieg.board import Board
from pykrieg.constants import (
    PLAYER_NORTH,
    PLAYER_SOUTH,
    TERRAIN_MOUNTAIN,
    TERRAIN_MOUNTAIN_PASS,
    UNIT_ARSENAL,
    UNIT_INFANTRY,
    UNIT_RELAY,
    UNIT_SWIFT_RELAY,
)


class TestRayPropagation:
    """Test ray-based propagation from arsenals and relays."""

    def test_arsenal_radiates_in_all_8_directions(self):
        """Test that an arsenal radiates lines in all 8 directions."""
        board = Board()

        # Place arsenal at center
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.enable_networks()

        # Check that squares in all directions are online
        assert board.is_unit_online(10, 11, PLAYER_NORTH)  # North
        assert board.is_unit_online(11, 11, PLAYER_NORTH)  # Northeast
        assert board.is_unit_online(11, 12, PLAYER_NORTH)  # East
        assert board.is_unit_online(11, 13, PLAYER_NORTH)  # Southeast
        assert board.is_unit_online(10, 13, PLAYER_NORTH)  # South
        assert board.is_unit_online(9, 13, PLAYER_NORTH)  # Southwest
        assert board.is_unit_online(9, 12, PLAYER_NORTH)  # West
        assert board.is_unit_online(9, 11, PLAYER_NORTH)  # Northwest

    def test_arsenal_ray_extends_to_board_edge(self):
        """Test that rays extend to board edge."""
        board = Board()

        # Place arsenal at (10, 12)
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.enable_networks()

        # Check that edge squares are online
        assert board.is_unit_online(0, 12, PLAYER_NORTH)  # North edge
        assert board.is_unit_online(19, 12, PLAYER_NORTH)  # South edge
        assert board.is_unit_online(10, 0, PLAYER_NORTH)  # West edge
        assert board.is_unit_online(10, 24, PLAYER_NORTH)  # East edge

    def test_ray_stops_on_enemy_unit(self):
        """Test that ray stops immediately on enemy unit."""
        board = Board()

        # Place arsenal and enemy infantry
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.create_and_place_unit(10, 10, UNIT_INFANTRY, PLAYER_SOUTH)
        board.create_and_place_unit(10, 9, UNIT_INFANTRY, PLAYER_SOUTH)

        board.enable_networks()

        # Square before enemy should be online, enemy and beyond should not
        assert board.is_unit_online(10, 11, PLAYER_NORTH)
        assert not board.is_unit_online(10, 10, PLAYER_NORTH)
        assert not board.is_unit_online(10, 9, PLAYER_NORTH)

    def test_ray_stops_on_enemy_relay(self):
        """Test that ray stops on enemy relay."""
        board = Board()

        # Place arsenal and enemy relay with infantry beyond
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.create_and_place_unit(10, 11, UNIT_RELAY, PLAYER_SOUTH)
        board.create_and_place_unit(10, 10, UNIT_INFANTRY, PLAYER_SOUTH)

        board.enable_networks()

        # Ray should stop at enemy relay (it blocks like any other enemy unit)
        assert not board.is_unit_online(10, 11, PLAYER_NORTH)  # Enemy relay blocks
        # Infantry beyond is also offline
        assert not board.is_unit_online(10, 10, PLAYER_NORTH)

    def test_ray_stops_on_mountain(self):
        """Test that ray stops on mountain terrain."""
        board = Board()

        # Place arsenal and set mountain
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.set_terrain(10, 11, TERRAIN_MOUNTAIN)
        board.create_and_place_unit(10, 10, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # Square before mountain should be online, mountain and beyond should not
        assert not board.is_unit_online(10, 11, PLAYER_NORTH)
        assert not board.is_unit_online(10, 10, PLAYER_NORTH)

    def test_ray_continues_through_mountain_pass(self):
        """Test that ray continues through mountain pass."""
        board = Board()

        # Place arsenal and set mountain pass
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.set_terrain(10, 11, TERRAIN_MOUNTAIN_PASS)
        board.create_and_place_unit(10, 10, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # Both squares should be online
        assert board.is_unit_online(10, 11, PLAYER_NORTH)
        assert board.is_unit_online(10, 10, PLAYER_NORTH)

    def test_friendly_unit_does_not_block_ray(self):
        """Test that friendly units don't block ray."""
        board = Board()

        # Place arsenal and friendly infantry
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.create_and_place_unit(10, 11, UNIT_INFANTRY, PLAYER_NORTH)
        board.create_and_place_unit(10, 10, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # Both friendly units should be online
        assert board.is_unit_online(10, 11, PLAYER_NORTH)
        assert board.is_unit_online(10, 10, PLAYER_NORTH)

    def test_friendly_relay_activates_and_continues_ray(self):
        """Test that friendly relay activates and continues ray."""
        board = Board()

        # Place arsenal and friendly relay with infantry beyond
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.create_and_place_unit(10, 11, UNIT_RELAY, PLAYER_NORTH)
        board.create_and_place_unit(10, 10, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # All should be online
        assert board.is_unit_online(10, 11, PLAYER_NORTH)
        assert board.is_relay_online(10, 11)
        assert board.is_unit_online(10, 10, PLAYER_NORTH)

    def test_relay_propagates_in_all_directions(self):
        """Test that activated relays propagate in all 8 directions."""
        board = Board()

        # Place arsenal and relay
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.create_and_place_unit(10, 11, UNIT_RELAY, PLAYER_NORTH)

        # Place infantry in all 7 free directions from relay (skip (0, 1) which would overwrite arsenal)
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (-1, 1), (-1, 0), (-1, -1)]
        for dx, dy in directions:
            board.create_and_place_unit(10 + dx, 11 + dy, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # All infantry should be online via relay
        for dx, dy in directions:
            assert board.is_unit_online(10 + dx, 11 + dy, PLAYER_NORTH)

    def test_multiple_relays_chain_propagation(self):
        """Test that multiple relays chain propagation."""
        board = Board()

        # Place arsenal and chain of relays
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.create_and_place_unit(10, 11, UNIT_RELAY, PLAYER_NORTH)
        board.create_and_place_unit(10, 10, UNIT_RELAY, PLAYER_NORTH)
        board.create_and_place_unit(10, 9, UNIT_RELAY, PLAYER_NORTH)
        board.create_and_place_unit(10, 8, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # All should be online
        assert board.is_unit_online(10, 11, PLAYER_NORTH)
        assert board.is_relay_online(10, 11)
        assert board.is_unit_online(10, 10, PLAYER_NORTH)
        assert board.is_relay_online(10, 10)
        assert board.is_unit_online(10, 9, PLAYER_NORTH)
        assert board.is_relay_online(10, 9)
        assert board.is_unit_online(10, 8, PLAYER_NORTH)

    def test_swift_relay_propagates_correctly(self):
        """Test that swift relays propagate like normal relays."""
        board = Board()

        # Place arsenal and swift relay
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.create_and_place_unit(10, 11, UNIT_SWIFT_RELAY, PLAYER_NORTH)
        board.create_and_place_unit(10, 10, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # All should be online
        assert board.is_unit_online(10, 11, PLAYER_NORTH)
        assert board.is_relay_online(10, 11)
        assert board.is_unit_online(10, 10, PLAYER_NORTH)
