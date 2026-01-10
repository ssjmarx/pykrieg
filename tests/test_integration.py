"""
Integration tests for Pykrieg - testing complete workflows and scenarios.
"""

import pytest
from pykrieg import Board, Fen


def test_full_board_serialization():
    """Test complete board serialization/deserialization with all squares filled."""
    board1 = Board()
    
    # Fill entire board with pieces
    unit_types = ['INFANTRY', 'CAVALRY', 'CANNON', 'ARSENAL', 'RELAY', 'SWIFT_CANNON', 'SWIFT_RELAY']
    
    for row in range(board1.rows):
        for col in range(board1.cols):
            owner = 'NORTH' if row < board1.territory_boundary else 'SOUTH'
            # Alternate unit types
            piece_type = unit_types[(row + col) % len(unit_types)]
            board1.set_piece(row, col, {'type': piece_type, 'owner': owner})
    
    # Serialize
    fen = Fen.board_to_fen(board1)
    
    # Deserialize
    board2 = Fen.fen_to_board(fen)
    
    # Verify all pieces match
    for row in range(board1.rows):
        for col in range(board1.cols):
            piece1 = board1.get_piece(row, col)
            piece2 = board2.get_piece(row, col)
            assert piece1 == piece2, f"Mismatch at ({row}, {col})"
    
    # Verify turn is preserved
    assert board1.turn == board2.turn


def test_complex_scenario_with_turns():
    """Test complex scenario with multiple pieces and turn changes."""
    # Create initial board state
    board1 = Board()
    
    # Add pieces in strategic positions
    pieces = [
        (0, 0, 'INFANTRY', 'NORTH'),
        (0, 5, 'CAVALRY', 'NORTH'),
        (0, 10, 'CANNON', 'NORTH'),
        (0, 15, 'ARSENAL', 'NORTH'),
        (0, 20, 'RELAY', 'NORTH'),
        (2, 2, 'SWIFT_CANNON', 'NORTH'),
        (2, 22, 'SWIFT_RELAY', 'NORTH'),
        (19, 0, 'INFANTRY', 'SOUTH'),
        (19, 5, 'CAVALRY', 'SOUTH'),
        (19, 10, 'CANNON', 'SOUTH'),
        (19, 15, 'ARSENAL', 'SOUTH'),
        (19, 20, 'RELAY', 'SOUTH'),
        (17, 2, 'SWIFT_CANNON', 'SOUTH'),
        (17, 22, 'SWIFT_RELAY', 'SOUTH'),
    ]
    
    for row, col, piece_type, owner in pieces:
        board1.set_piece(row, col, {'type': piece_type, 'owner': owner})
    
    # Set turn to SOUTH
    board1._turn = 'SOUTH'
    
    # Serialize and deserialize
    fen = Fen.board_to_fen(board1)
    board2 = Fen.fen_to_board(fen)
    
    # Verify all pieces
    for row, col, piece_type, owner in pieces:
        piece = board2.get_piece(row, col)
        assert piece is not None, f"No piece at ({row}, {col})"
        assert piece['type'] == piece_type, f"Wrong type at ({row}, {col})"
        assert piece['owner'] == owner, f"Wrong owner at ({row}, {col})"
    
    # Verify turn
    assert board2.turn == 'SOUTH'


def test_territory_distribution():
    """Test territory distribution across full board."""
    board = Board()
    
    north_squares = board.get_territory_squares('NORTH')
    south_squares = board.get_territory_squares('SOUTH')
    
    # Verify exact counts
    assert len(north_squares) == 250, "North should have exactly 250 squares"
    assert len(south_squares) == 250, "South should have exactly 250 squares"
    
    # Fill territories and verify
    for row, col in north_squares:
        board.set_piece(row, col, {'type': 'INFANTRY', 'owner': 'NORTH'})
    
    for row, col in south_squares:
        board.set_piece(row, col, {'type': 'INFANTRY', 'owner': 'SOUTH'})
    
    # Serialize and verify
    fen = Fen.board_to_fen(board)
    board2 = Fen.fen_to_board(fen)
    
    # Count pieces by owner
    north_count = 0
    south_count = 0
    
    for row in range(board2.rows):
        for col in range(board2.cols):
            piece = board2.get_piece(row, col)
            if piece:
                if piece['owner'] == 'NORTH':
                    north_count += 1
                else:
                    south_count += 1
    
    assert north_count == 250, f"Expected 250 NORTH pieces, got {north_count}"
    assert south_count == 250, f"Expected 250 SOUTH pieces, got {south_count}"


def test_multiple_serialization_roundtrips():
    """Test multiple serialization/deserialization roundtrips preserve state."""
    board1 = Board()
    
    # Add pieces
    test_pieces = [
        (0, 0, 'INFANTRY', 'NORTH'),
        (5, 5, 'CAVALRY', 'NORTH'),
        (10, 10, 'CANNON', 'SOUTH'),
        (15, 15, 'ARSENAL', 'SOUTH'),
    ]
    
    for row, col, piece_type, owner in test_pieces:
        board1.set_piece(row, col, {'type': piece_type, 'owner': owner})
    
    # Perform multiple roundtrips
    board2 = Fen.fen_to_board(Fen.board_to_fen(board1))
    board3 = Fen.fen_to_board(Fen.board_to_fen(board2))
    board4 = Fen.fen_to_board(Fen.board_to_fen(board3))
    board5 = Fen.fen_to_board(Fen.board_to_fen(board4))
    
    # Verify all boards are identical
    for row, col, piece_type, owner in test_pieces:
        piece1 = board1.get_piece(row, col)
        piece2 = board2.get_piece(row, col)
        piece3 = board3.get_piece(row, col)
        piece4 = board4.get_piece(row, col)
        piece5 = board5.get_piece(row, col)
        
        assert piece1 == piece2 == piece3 == piece4 == piece5
        assert piece5['type'] == piece_type
        assert piece5['owner'] == owner


def test_empty_board_operations():
    """Test operations on empty board."""
    board = Board()
    
    # Verify empty
    for row in range(board.rows):
        for col in range(board.cols):
            assert board.get_piece(row, col) is None
    
    # Serialize empty board
    fen = Fen.board_to_fen(board)
    
    # Should be all underscores
    assert 'I' not in fen  # No infantry
    assert 'i' not in fen  # No south infantry
    
    # Deserialize and verify
    board2 = Fen.fen_to_board(fen)
    for row in range(board2.rows):
        for col in range(board2.cols):
            assert board2.get_piece(row, col) is None


def test_board_with_single_piece():
    """Test board with single piece."""
    board1 = Board()
    board1.set_piece(10, 12, {'type': 'CAVALRY', 'owner': 'SOUTH'})
    
    fen = Fen.board_to_fen(board1)
    board2 = Fen.fen_to_board(fen)
    
    # Verify single piece
    piece = board2.get_piece(10, 12)
    assert piece is not None
    assert piece['type'] == 'CAVALRY'
    assert piece['owner'] == 'SOUTH'
    
    # Verify all other squares are empty
    count = 0
    for row in range(board2.rows):
        for col in range(board2.cols):
            if board2.get_piece(row, col) is not None:
                count += 1
    
    assert count == 1


def test_coordinate_integration():
    """Test coordinate conversions with board operations."""
    board = Board()
    
    # Add piece using tuple coordinates
    board.set_piece(5, 10, {'type': 'INFANTRY', 'owner': 'NORTH'})
    
    # Get piece
    piece = board.get_piece(5, 10)
    assert piece['type'] == 'INFANTRY'
    
    # Test spreadsheet coordinate conversion
    spreadsheet = Board.tuple_to_spreadsheet(5, 10)
    back_tuple = Board.spreadsheet_to_tuple(spreadsheet)
    assert back_tuple == (5, 10)
    
    # Test index conversion
    index = Board.tuple_to_index(5, 10)
    back_tuple = Board.index_to_tuple(index)
    assert back_tuple == (5, 10)
    
    # Verify piece still accessible through different coordinate systems
    assert board.get_piece(*back_tuple) == piece


def test_turn_integration():
    """Test turn integration with serialization."""
    board1 = Board()
    board1._turn = 'SOUTH'
    
    fen = Fen.board_to_fen(board1)
    assert '/S/' in fen
    
    board2 = Fen.fen_to_board(fen)
    assert board2.turn == 'SOUTH'
    
    # Change turn and re-serialize
    board2._turn = 'NORTH'
    fen2 = Fen.board_to_fen(board2)
    assert '/N/' in fen2
    
    board3 = Fen.fen_to_board(fen2)
    assert board3.turn == 'NORTH'


def test_all_unit_types_integration():
    """Test all unit types work correctly in integration."""
    board1 = Board()
    
    # Add one of each unit type for both players
    unit_types = ['INFANTRY', 'CAVALRY', 'CANNON', 'ARSENAL', 'RELAY', 'SWIFT_CANNON', 'SWIFT_RELAY']
    
    col = 0
    for unit_type in unit_types:
        board1.set_piece(0, col, {'type': unit_type, 'owner': 'NORTH'})
        board1.set_piece(19, col, {'type': unit_type, 'owner': 'SOUTH'})
        col += 1
    
    # Serialize
    fen = Fen.board_to_fen(board1)
    
    # Deserialize
    board2 = Fen.fen_to_board(fen)
    
    # Verify all unit types
    col = 0
    for unit_type in unit_types:
        north_piece = board2.get_piece(0, col)
        south_piece = board2.get_piece(19, col)
        
        assert north_piece['type'] == unit_type
        assert north_piece['owner'] == 'NORTH'
        
        assert south_piece['type'] == unit_type
        assert south_piece['owner'] == 'SOUTH'
        
        col += 1
