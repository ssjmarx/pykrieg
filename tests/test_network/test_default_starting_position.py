"""Test relay propagation with default starting position."""

from pykrieg.constants import PLAYER_NORTH, UNIT_INFANTRY
from pykrieg.fen import Fen


def test_default_starting_position_relay_chain():
    """Test that relay chain works in default starting position.

    Load the actual default starting position FEN and test relay propagation.
    """
    # Load default starting position
    with open('src/pykrieg/console/default_starting_position.fen') as f:
        fen_string = f.read().strip()

    board = Fen.fen_to_board(fen_string)
    board.enable_networks()

    print("\n=== North Relay Chain ===")

    # Check arsenal
    print(f"Arsenal at A1 (1,0) online: {board.is_unit_online(1, 0, PLAYER_NORTH)}")

    # Check relays
    relay_positions = [
        (5, 1),   # B6
        (9, 1),   # B10
        (13, 1),  # B14
        (17, 1),  # B18
    ]

    for row, col in relay_positions:
        coord = board.tuple_to_spreadsheet(row, col)
        is_online = board.is_relay_online(row, col)
        covered = board.is_unit_online(row, col, PLAYER_NORTH)
        print(f"Relay at {coord} ({row},{col}): Online={is_online}, Covered={covered}")

    # Check some infantry along the path
    print("\n=== Sample Infantry Along Path ===")
    sample_positions = [
        (7, 3),   # Row 7
        (11, 5),  # Row 11
        (15, 7),  # Row 15
    ]

    for row, col in sample_positions:
        unit = board.get_unit(row, col)
        if unit and unit.unit_type == UNIT_INFANTRY and unit.owner == PLAYER_NORTH:
            coord = board.tuple_to_spreadsheet(row, col)
            online = board.is_unit_online(row, col, PLAYER_NORTH)
            print(f"Infantry at {coord} ({row},{col}): {'ONLINE' if online else 'OFFLINE'}")

    # Assertions
    assert board.is_unit_online(1, 0, PLAYER_NORTH), "Arsenal at A1 should be online"
    assert board.is_relay_online(5, 1), "Relay at B6 should be online"
    assert board.is_relay_online(9, 1), "Swift Relay at B10 should be online"
    assert board.is_relay_online(13, 1), "Swift Relay at B14 should be online"
    assert board.is_relay_online(17, 1), "Swift Relay at B18 should be online"


if __name__ == "__main__":
    test_default_starting_position_relay_chain()
    print("\n✓ All tests passed!")
