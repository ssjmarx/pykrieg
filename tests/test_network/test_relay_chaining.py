"""Tests for relay-to-relay chaining."""


from pykrieg.board import Board
from pykrieg.constants import PLAYER_NORTH, UNIT_ARSENAL, UNIT_INFANTRY, UNIT_RELAY


class TestRelayChaining:
    """Test that relays can chain through multiple hops."""

    def test_arsenal_relay_relay_infantry_chain(self):
        """Test relay-to-relay propagation with proper geometry.

        Layout:
            Arsenal at (1, 1)
            Relay 1 at (1, 5) - activated by arsenal's east ray
            Relay 2 at (5, 5) - activated by relay 1's south ray
            Infantry at (5, 20) - activated by relay 2's east ray
        """
        board = Board()

        # Place arsenal at (1, 1)
        board.create_and_place_unit(1, 1, UNIT_ARSENAL, PLAYER_NORTH)

        # Place first relay at (1, 5) - should be activated by arsenal's east ray
        board.create_and_place_unit(1, 5, UNIT_RELAY, PLAYER_NORTH)

        # Place second relay at (5, 5) - should be activated by first relay's south ray
        board.create_and_place_unit(5, 5, UNIT_RELAY, PLAYER_NORTH)

        # Place infantry at (5, 20) - should be activated by second relay's east ray
        board.create_and_place_unit(5, 20, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # First relay should be online via arsenal
        assert board.is_unit_online(1, 5, PLAYER_NORTH), "First relay should be online via arsenal"
        assert board.is_relay_online(1, 5), "First relay should be marked as online"

        # Second relay should be online via first relay
        assert board.is_unit_online(5, 5, PLAYER_NORTH), "Second relay should be online via first relay"
        assert board.is_relay_online(5, 5), "Second relay should be marked as online"

        # Infantry should be online via second relay
        assert board.is_unit_online(5, 20, PLAYER_NORTH), "Infantry should be online via second relay"

    def test_multiple_relay_hops(self):
        """Test that relay propagation works through multiple hops.

        Layout:
            Arsenal at (2, 2)
            Relay 1 at (2, 6) - activated by arsenal's east ray
            Relay 2 at (6, 6) - activated by relay 1's south ray
            Relay 3 at (6, 12) - activated by relay 2's east ray
            Infantry at (6, 18) - activated by relay 3's east ray
        """
        board = Board()

        # Place arsenal
        board.create_and_place_unit(2, 2, UNIT_ARSENAL, PLAYER_NORTH)

        # Chain of relays
        board.create_and_place_unit(2, 6, UNIT_RELAY, PLAYER_NORTH)
        board.create_and_place_unit(6, 6, UNIT_RELAY, PLAYER_NORTH)
        board.create_and_place_unit(6, 12, UNIT_RELAY, PLAYER_NORTH)

        # Final target unit
        board.create_and_place_unit(6, 18, UNIT_INFANTRY, PLAYER_NORTH)

        board.enable_networks()

        # All relays should be online
        assert board.is_relay_online(2, 6), "Relay 1 should be online"
        assert board.is_relay_online(6, 6), "Relay 2 should be online"
        assert board.is_relay_online(6, 12), "Relay 3 should be online"

        # Infantry should be online through relay chain
        assert board.is_unit_online(6, 18, PLAYER_NORTH), "Infantry should be online through relay chain"
