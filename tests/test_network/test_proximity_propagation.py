"""Tests for proximity-based propagation (Step 3)."""


from pykrieg.board import Board
from pykrieg.constants import PLAYER_NORTH, PLAYER_SOUTH, UNIT_ARSENAL, UNIT_INFANTRY


class TestProximityPropagation:
    """Test proximity-based propagation from active units."""

    def test_active_unit_activates_adjacent_friendly_units(self):
        """Test that active units activate adjacent friendly units."""
        board = Board()

        # Place arsenal and infantry nearby
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.create_and_place_unit(11, 12, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # Adjacent infantry should be online via proximity
        assert board.is_unit_online(11, 12, PLAYER_NORTH)

    def test_proximity_checks_all_8_adjacent_squares(self):
        """Test that proximity checks all 8 adjacent squares."""
        board = Board()

        # Place arsenal and infantry in all 8 directions
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        for dx, dy in [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]:
            board.create_and_place_unit(10 + dx, 12 + dy, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # All adjacent infantry should be online
        for dx, dy in [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]:
            assert board.is_unit_online(10 + dx, 12 + dy, PLAYER_NORTH)

    def test_proximity_does_not_activate_enemy_units(self):
        """Test that proximity doesn't activate enemy units."""
        board = Board()

        # Place arsenal and enemy infantry adjacent
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.create_and_place_unit(11, 12, UNIT_INFANTRY, PLAYER_SOUTH)

        board.enable_networks()

        # Enemy infantry should not be online for North
        assert not board.is_unit_online(11, 12, PLAYER_NORTH)
        # But it might be online for South if they have their own network
        assert not board.is_unit_online(11, 12, PLAYER_SOUTH)  # South has no arsenal

    def test_proximity_propagation_cascades(self):
        """Test that proximity propagation cascades through chain of units."""
        board = Board()

        # Place arsenal and chain of infantry
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.create_and_place_unit(11, 12, UNIT_INFANTRY, PLAYER_NORTH)
        board.create_and_place_unit(12, 12, UNIT_INFANTRY, PLAYER_NORTH)
        board.create_and_place_unit(13, 12, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # All should be online via cascading proximity
        assert board.is_unit_online(11, 12, PLAYER_NORTH)
        assert board.is_unit_online(12, 12, PLAYER_NORTH)
        assert board.is_unit_online(13, 12, PLAYER_NORTH)

    def test_already_online_units_dont_reactivate(self):
        """Test that already online units don't cause issues."""
        board = Board()

        # Place arsenal and infantry
        board.create_and_place_unit(10, 12, UNIT_ARSENAL, PLAYER_NORTH)
        board.create_and_place_unit(11, 12, UNIT_INFANTRY, PLAYER_NORTH)
        board.create_and_place_unit(12, 12, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # Calculate again - should be stable
        board.calculate_network(PLAYER_NORTH)

        # All should still be online
        assert board.is_unit_online(11, 12, PLAYER_NORTH)
        assert board.is_unit_online(12, 12, PLAYER_NORTH)
