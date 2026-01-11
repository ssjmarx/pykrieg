"""
Success criteria tests for Pykrieg 0.1.0.

These tests verify the acceptance criteria defined in the implementation plan.
"""

from pykrieg import Board, Fen


def test_board_can_be_created_and_loaded():
    """Success criterion: Board can be created and saved/loaded accurately via FEN format."""

    # Create board with pieces
    board1 = Board()
    test_positions = [
        (0, 5, 'INFANTRY', 'NORTH'),
        (2, 10, 'CAVALRY', 'NORTH'),
        (4, 15, 'CANNON', 'NORTH'),
        (6, 20, 'ARSENAL', 'NORTH'),
        (19, 5, 'INFANTRY', 'SOUTH'),
        (17, 10, 'CAVALRY', 'SOUTH'),
        (15, 15, 'CANNON', 'SOUTH'),
        (13, 20, 'ARSENAL', 'SOUTH'),
    ]

    for row, col, piece_type, owner in test_positions:
        board1.set_piece(row, col, {'type': piece_type, 'owner': owner})

    # Save to FEN
    fen = Fen.board_to_fen(board1)

    # Verify FEN structure
    parts = fen.split('/')
    assert len(parts) == 25  # 20 rows + 5 metadata (turn, phase, actions, turn_number, retreats)
    assert '/N/' in fen or '/S/' in fen  # Has turn info

    # Load from FEN
    board2 = Fen.fen_to_board(fen)

    # Verify all positions match
    for row, col, piece_type, owner in test_positions:
        piece = board2.get_piece(row, col)
        assert piece is not None, f"No piece at ({row}, {col})"
        assert piece['type'] == piece_type, f"Wrong type at ({row}, {col})"
        assert piece['owner'] == owner, f"Wrong owner at ({row}, {col})"

    # Verify turn matches
    assert board1.turn == board2.turn


def test_all_core_data_structures_implemented():
    """Success criterion: All core data structures implemented and tested."""

    # Test Board class
    board = Board()
    assert board.rows == 20
    assert board.cols == 25
    assert board.territory_boundary == 10

    # Test coordinate system - spreadsheet
    assert Board.spreadsheet_to_tuple("A1") == (0, 0)
    assert Board.spreadsheet_to_tuple("Y25") == (24, 24)
    assert Board.tuple_to_spreadsheet(0, 0) == "A1"
    assert Board.tuple_to_spreadsheet(24, 24) == "Y25"

    # Test coordinate system - index
    assert Board.tuple_to_index(0, 0) == 0
    assert Board.tuple_to_index(19, 24) == 499
    assert Board.index_to_tuple(0) == (0, 0)
    assert Board.index_to_tuple(499) == (19, 24)

    # Test territory system
    assert board.get_territory(0, 0) == 'NORTH'
    assert board.get_territory(19, 24) == 'SOUTH'
    assert len(board.get_territory_squares('NORTH')) == 250
    assert len(board.get_territory_squares('SOUTH')) == 250

    # Test piece management
    board.set_piece(5, 10, {'type': 'INFANTRY', 'owner': 'NORTH'})
    piece = board.get_piece(5, 10)
    assert piece['type'] == 'INFANTRY'
    assert piece['owner'] == 'NORTH'

    board.clear_square(5, 10)
    assert board.get_piece(5, 10) is None

    # Test coordinate validation
    assert board.is_valid_square(0, 0) is True
    assert board.is_valid_square(19, 24) is True
    assert board.is_valid_square(-1, 0) is False
    assert board.is_valid_square(20, 0) is False
    assert board.is_valid_square(0, -1) is False
    assert board.is_valid_square(0, 25) is False

    # Test FEN serialization
    fen = Fen.board_to_fen(board)
    board2 = Fen.fen_to_board(fen)
    assert board2.turn == board.turn

    # Test FEN with pieces
    board.set_piece(0, 0, {'type': 'CAVALRY', 'owner': 'NORTH'})
    board.set_piece(19, 24, {'type': 'CANNON', 'owner': 'SOUTH'})
    fen = Fen.board_to_fen(board)
    board3 = Fen.fen_to_board(fen)

    assert board3.get_piece(0, 0)['type'] == 'CAVALRY'
    assert board3.get_piece(19, 24)['type'] == 'CANNON'

    # Test turn tracking
    assert board.turn_side() == 'NORTH'
    board._turn = 'SOUTH'
    assert board.turn_side() == 'SOUTH'


def test_documentation_framework_functional():
    """Success criterion: Documentation framework functional with API auto-generation.

    This test verifies the documentation setup is correct.
    Full verification requires running Sphinx: `cd docs && make html`
    """
    # Verify documentation files exist
    from pathlib import Path

    project_root = Path(__file__).parent.parent

    # Check Sphinx configuration exists
    assert (project_root / 'docs' / 'conf.py').exists(), "Sphinx config not found"
    assert (project_root / 'docs' / 'Makefile').exists(), "Makefile not found"

    # Check API documentation exists
    assert (project_root / 'docs' / 'api.rst').exists(), "API docs not found"

    # Check index documentation exists
    assert (project_root / 'docs' / 'index.rst').exists(), "Index docs not found"

    # Verify docstrings exist on public APIs
    assert Board.__doc__ is not None, "Board class missing docstring"
    assert Board.__init__.__doc__ is not None, "Board.__init__ missing docstring"
    assert Board.spreadsheet_to_tuple.__doc__ is not None, "spreadsheet_to_tuple missing docstring"
    assert Board.tuple_to_spreadsheet.__doc__ is not None, "tuple_to_spreadsheet missing docstring"
    assert Board.tuple_to_index.__doc__ is not None, "tuple_to_index missing docstring"
    assert Board.index_to_tuple.__doc__ is not None, "index_to_tuple missing docstring"

    assert Fen.__doc__ is not None, "Fen class missing docstring"
    assert Fen.board_to_fen.__doc__ is not None, "board_to_fen missing docstring"
    assert Fen.fen_to_board.__doc__ is not None, "fen_to_board missing docstring"

    # Verify module-level docstrings
    import pykrieg
    import pykrieg.board
    import pykrieg.constants
    import pykrieg.fen

    assert pykrieg.board.__doc__ is not None, "board module missing docstring"
    assert pykrieg.fen.__doc__ is not None, "fen module missing docstring"
    assert pykrieg.constants.__doc__ is not None, "constants module missing docstring"

    # Note: To fully verify documentation builds, run:
    # cd docs && make html
    # This should be done manually or in CI/CD


def test_acceptance_criteria_board_representation():
    """Verify acceptance criterion: Board representation with 20×25 grid implemented."""
    board = Board()

    assert board.rows == 20, "Board must have 20 rows"
    assert board.cols == 25, "Board must have 25 columns"
    assert board.rows * board.cols == 500, "Board must have 500 squares"


def test_acceptance_criteria_territory_system():
    """Verify acceptance criterion: Territory representation (North/South) working."""
    board = Board()

    # Verify territory boundary
    assert board.territory_boundary == 10, "Territory boundary must be at row 10"

    # Verify North territory (rows 0-9)
    for row in range(10):
        for col in range(board.cols):
            assert board.get_territory(row, col) == 'NORTH', f"Square ({row}, {col}) should be NORTH"

    # Verify South territory (rows 10-19)
    for row in range(10, 20):
        for col in range(board.cols):
            assert board.get_territory(row, col) == 'SOUTH', f"Square ({row}, {col}) should be SOUTH"

    # Verify territory square counts
    north_squares = board.get_territory_squares('NORTH')
    south_squares = board.get_territory_squares('SOUTH')
    assert len(north_squares) == 250, "North must have 250 squares"
    assert len(south_squares) == 250, "South must have 250 squares"


def test_acceptance_criteria_coordinate_system():
    """Verify acceptance criterion: Coordinate system supports tuple, string, and index formats."""
    Board()

    # Test tuple format (internal)
    assert Board.spreadsheet_to_tuple("A1") == (0, 0)
    assert Board.tuple_to_spreadsheet(0, 0) == "A1"

    # Test string format (spreadsheet)
    assert Board.spreadsheet_to_tuple("G7") == (6, 6)
    assert Board.tuple_to_spreadsheet(6, 6) == "G7"

    # Test index format (row-major)
    assert Board.tuple_to_index(0, 0) == 0
    assert Board.index_to_tuple(0) == (0, 0)
    assert Board.tuple_to_index(19, 24) == 499
    assert Board.index_to_tuple(499) == (19, 24)

    # Test roundtrip conversions
    spreadsheet = "H10"
    tuple_coord = Board.spreadsheet_to_tuple(spreadsheet)
    index = Board.tuple_to_index(*tuple_coord)
    back_tuple = Board.index_to_tuple(index)
    back_spreadsheet = Board.tuple_to_spreadsheet(*back_tuple)

    assert spreadsheet == back_spreadsheet


def test_acceptance_criteria_fen_format():
    """Verify acceptance criterion: FEN format can serialize/deserialize board states accurately."""
    board1 = Board()

    # Add test pieces
    board1.set_piece(0, 0, {'type': 'INFANTRY', 'owner': 'NORTH'})
    board1.set_piece(19, 24, {'type': 'CAVALRY', 'owner': 'SOUTH'})
    board1.set_piece(10, 12, {'type': 'CANNON', 'owner': 'NORTH'})

    # Serialize
    fen = Fen.board_to_fen(board1)

    # Verify FEN contains expected symbols
    assert 'I' in fen, "Should contain North Infantry"
    assert 'c' in fen, "Should contain South Cavalry"
    assert 'K' in fen, "Should contain North Cannon"

    # Deserialize
    board2 = Fen.fen_to_board(fen)

    # Verify all pieces match
    assert board2.get_piece(0, 0) == {'type': 'INFANTRY', 'owner': 'NORTH'}
    assert board2.get_piece(19, 24) == {'type': 'CAVALRY', 'owner': 'SOUTH'}
    assert board2.get_piece(10, 12) == {'type': 'CANNON', 'owner': 'NORTH'}

    # Verify turn is preserved
    assert board1.turn == board2.turn


def test_acceptance_criteria_all_unit_types():
    """Verify all 7 unit types are supported."""
    board = Board()

    unit_types = [
        'INFANTRY',
        'CAVALRY',
        'CANNON',
        'ARSENAL',
        'RELAY',
        'SWIFT_CANNON',
        'SWIFT_RELAY',
    ]

    # Add all unit types
    for i, unit_type in enumerate(unit_types):
        board.set_piece(0, i, {'type': unit_type, 'owner': 'NORTH'})
        board.set_piece(19, i, {'type': unit_type, 'owner': 'SOUTH'})

    # Serialize and deserialize
    fen = Fen.board_to_fen(board)
    board2 = Fen.fen_to_board(fen)

    # Verify all unit types preserved
    for i, unit_type in enumerate(unit_types):
        north_piece = board2.get_piece(0, i)
        south_piece = board2.get_piece(19, i)

        assert north_piece['type'] == unit_type
        assert north_piece['owner'] == 'NORTH'

        assert south_piece['type'] == unit_type
        assert south_piece['owner'] == 'SOUTH'
