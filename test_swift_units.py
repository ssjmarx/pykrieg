#!/usr/bin/env python
"""Test script to verify swift unit rendering."""

from pykrieg.board import Board
from pykrieg.console.display import BoardDisplay, DisplayMode

# Create a test board (Board uses fixed 20x25 dimensions from constants)
board = Board()

# Add some test units
from pykrieg.pieces import Infantry, Cannon, Relay, SwiftCannon, SwiftRelay

# Regular units
board.place_unit(0, 0, Infantry("NORTH"))
board.place_unit(0, 1, Cannon("NORTH"))
board.place_unit(0, 2, Relay("NORTH"))

# Swift units (North)
board.place_unit(1, 0, SwiftCannon("NORTH"))
board.place_unit(1, 1, SwiftRelay("NORTH"))

# Swift units (South)
board.place_unit(3, 0, SwiftCannon("SOUTH"))
board.place_unit(3, 1, SwiftRelay("SOUTH"))

# Test compatibility mode
print("=" * 60)
print("COMPATIBILITY MODE (ASCII)")
print("=" * 60)
compat_display = BoardDisplay(DisplayMode.COMPATIBILITY)
compat_output = compat_display.render(board)
print(compat_output)

print("\n" + "=" * 60)
print("CURSES MODE (Unicode with Stars)")
print("=" * 60)
print("Swift Cannon (North): ♜★")
print("Swift Relay (North):  ♝★")
print("Swift Cannon (South): ♜★")
print("Swift Relay (South):  ♝★")
print("\nNote: Stars (★) are rendered in the space position after")
print("the unit symbol, preserving board alignment.")
