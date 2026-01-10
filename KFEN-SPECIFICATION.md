# KFEN (Kriegspiel FEN) Specification

## Overview
KFEN is a string format for representing Pykrieg board states, moves, and attacks. It supports arbitrarily sized boards using spreadsheet-style notation.

**Version**: 2.0  
**Last Updated**: 2025-01-09  
**Status**: Final Specification

---

## Format Structure
```
<board_data>/<turn>/<phase>/<actions>
```

- **board_data**: Row-by-row representation of pieces and terrain
- **turn**: Current player (`N` or `S`)
- **phase**: Turn phase (`M` for movement, `B` for battle)
- **actions**: Move pairs or attack target (inferred from turn/phase)

---

## Board State Timing

**Critical Rule**: The board state shown represents the position **BEFORE** the actions are executed.

This matches the standard chess FEN convention:
1. Load KFEN → see current position at START of turn
2. Parse actions → see what WILL happen this turn
3. Apply actions → get new position
4. Generate new KFEN → capture the result

---

## Coordinate System

Board squares use spreadsheet-style notation starting from **top-left corner**:

### Columns (letter notation):
- `A-Z`: First 26 columns
- `AA-ZZ`: Next 26×26 = 676 columns
- `AAA-ZZZ`: Next 26³ = 17,576 columns
- And so on...

### Rows (number notation):
- `1-9`: First 9 rows
- `10-99`: Next 90 rows
- `100-999`: Next 900 rows
- And so on...

**Examples**:
- `A1`: Top-left corner
- `Z9`: Rightmost column in first 9 rows
- `AA10`: 27th column, 10th row from top
- `AB1`: 28th column, 1st row (top row)
- `A100`: First column, 100th row from top

### Internal Representation
The library uses 0-based (row, col) coordinates internally where:
- Row 0 = top row
- Col 0 = leftmost column
- Direct mapping to `board[row][col]` array indexing

Helper functions translate between spreadsheet notation and internal coordinates as needed.

---

## Square Representations

### Flat Squares (Default)
| Representation | Meaning |
|----------------|---------|
| `_` | Empty flat square |
| `I`, `C`, `K`, `R`, `A`, `W`, `X` | North unit on flat |
| `i`, `c`, `k`, `r`, `a`, `w`, `x` | South unit on flat |

### Mountain Squares (Cannot contain pieces)
| Representation | Meaning |
|----------------|---------|
| `m` | Mountain (always empty) |

### Mountain Pass Squares
| Representation | Meaning |
|----------------|---------|
| `p` | Empty mountain pass |
| `(I)`, `(C)`, `(K)`, `(R)`, `(A)`, `(W)`, `(X)` | North unit on pass |
| `(i)`, `(c)`, `(k)`, `(r)`, `(a)`, `(w)`, `(x)` | South unit on pass |

### Fortress Squares
| Representation | Meaning |
|----------------|---------|
| `f` | Empty fortress |
| `[I]`, `[C]`, `[K]`, `[R]`, `[A]`, `[W]`, `[X]` | North unit in fortress |
| `[i]`, `[c]`, `[k]`, `[r]`, `[a]`, `[w]`, `[x]` | South unit in fortress |

---

## Unit Symbols

| Unit Type | North | South |
|-----------|-------|-------|
| Infantry | `I` | `i` |
| Cavalry | `C` | `c` |
| Cannon | `K` | `k` |
| Relay | `R` | `r` |
| Arsenal | `A` | `a` |
| Swift Cannon | `W` | `w` |
| Swift Relay | `X` | `x` |

**Note**: Uppercase = North, lowercase = South

---

## Terrain Types

| Terrain | Symbol | Can Contain Pieces? |
|---------|--------|---------------------|
| Flat | `_` (implicit) | Yes |
| Mountains | `m` | No (blocks movement) |
| Mountain Pass | `p` or `(unit)` | Yes |
| Fortress | `f` or `[unit]` | Yes |

---

## Actions Section

The actions section is inferred from turn and phase:

### Movement Phase (`M`)
- **Format**: `[(from,to),(from,to),...]`
- **Count**: Up to 5 move pairs for the current player
- **Unit type**: Inferred from board state before move
- **Order**: Moves are executed sequentially

**Example**: `[(A1,A2),(B3,B4),(C5,C6)]`
- Move unit from A1 to A2
- Move unit from B3 to B4
- Move unit from C5 to C6

**Example with empty moves**: `[(A1,A2),,,(D5,D6),]`
- Move unit from A1 to A2
- Skip second move
- Skip third move
- Move unit from D5 to D6
- Skip fifth move

### Battle Phase (`B`)
- **Format**: `<target>` or `pass`
- **Count**: Exactly 1 attack target or `pass`
- **Target**: Square being attacked

**Examples**:
- `A5`: Attack square A5
- `pass`: No attack this turn

---

## Complete Examples

### Example 1: Empty Board, North's Turn, Movement Phase
```
_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/N/M/[]
```
- 20 rows of 25 underscores (for 20×25 board)
- North to move, movement phase
- No moves made yet (empty list)

### Example 2: Board with Units, South's Turn, Movement Phase
```
IC_____________/ic_____________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/S/M/[(A1,A2),(B1,B2)]
```
- Row 1: North Infantry at A1, Cavalry at A2
- Row 20: South Infantry at A1, Cavalry at A2
- South to move, movement phase
- Two moves: A1→A2, B1→B2

### Example 3: Board with Terrain, North's Turn, Battle Phase
```
(I)(C)_m_p_f_____/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/N/B/A5
```
- Row 1: Infantry on pass at A1 `(I)`, Cavalry on pass at A3 `(C)`
- Mountain at A5 `m`, empty pass at A7 `p`, empty fortress at A9 `f`
- North to attack, battle phase
- Targeting square A5 (the mountain - would be invalid but just an example)

### Example 4: Board with Attack Passed
```
IC_____________/ic_____________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/S/B/pass
```
- South to attack, battle phase
- Attack passed (no attack this turn)

### Example 5: Larger Board Example (30×30)
```
__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/__________________________/N/M/[(A1,A2),(AD5,AD6),(Z25,Z26)]
```
- 30 rows of 30 underscores
- Move uses column notation: A, B, ..., Z, AA, AB, AC, AD
- Three moves: A1→A2, AD5→AD6, Z25→Z26

### Example 6: Complete Game Sequence
```
# Initial state
_____________________/_____________________/.../_____________________/N/M/[]

# After North moves 3 units
_____________________/_____________________/.../_____________________/S/M/[(A1,A2),(B3,B4),(C5,C6)]

# After South moves 2 units
_____________________/_____________________/.../_____________________/N/M/[(D1,D2),(E3,E4),,,]

# After North attacks
_____________________/_____________________/.../_____________________/S/B/A5

# After South passes attack
_____________________/_____________________/.../_____________________/N/M/[]
```

---

## Format Summary

| Section | Content |
|---------|---------|
| **board_data** | Board rows separated by `/`, each row contains piece/terrain symbols |
| **turn** | `N` (North) or `S` (South) |
| **phase** | `M` (Movement) or `B` (Battle) |
| **actions** | `[(from,to),...]` for movement, `<target>` or `pass` for battle |

---

## Parsing Rules

1. **Board data**: Split by `/` to get rows. Each row contains 25+ characters for piece/terrain representation.
2. **Turn**: Single character `N` or `S`.
3. **Phase**: Single character `M` or `B`.
4. **Actions**: 
   - If phase=`M`: Parse as list of move pairs `[(from,to),...]`
   - If phase=`B`: Parse as single target `<target>` or `pass`
5. **Coordinates**: Parse column letters (A-Z, AA-ZZ, etc.) and row numbers (1-9, 10-99, etc.)
6. **Unit inference**: Look up piece at "from" location in current board state

---

## Validation Rules

- **Movement phase**: 0-5 move pairs
- **Battle phase**: Exactly 1 target or `pass`
- **Coordinates**: Must be within board dimensions
- **Move validity**: "from" and "to" must be different squares
- **Mountains**: Cannot be move destinations or attack targets
- **Unit existence**: "from" square must contain a unit owned by current player

---

## Coordinate Parsing Algorithm

### Parse Coordinate String
```python
def parse_coordinate(coord_str):
    """
    Parse spreadsheet-style coordinate (e.g., 'A1', 'AA10', 'AB1').
    
    Returns (row_index, col_index) where:
    - row_index: 0-based integer (0 = row 1, 9 = row 10, etc.)
    - col_index: 0-based integer (0 = A, 25 = Z, 26 = AA, etc.)
    
    Note: Coordinate origin is top-left (A1 = top-left corner)
    """
    # Separate letters (column) and numbers (row)
    i = 0
    while i < len(coord_str) and coord_str[i].isalpha():
        i += 1
    
    col_letters = coord_str[:i]
    row_number = coord_str[i:]
    
    # Parse column
    col_index = 0
    for char in col_letters:
        col_index = col_index * 26 + (ord(char.upper()) - ord('A') + 1)
    col_index -= 1  # Convert to 0-based
    
    # Parse row
    row_index = int(row_number) - 1  # Convert to 0-based
    
    return (row_index, col_index)
```

### Format Coordinate String
```python
def format_coordinate(row_index, col_index):
    """
    Format row and col indices into spreadsheet-style coordinate.
    
    Args:
        row_index: 0-based integer (0 = top row)
        col_index: 0-based integer (0 = leftmost column)
    
    Returns string like 'A1', 'AA10', etc.
    
    Note: Coordinate origin is top-left (A1 = top-left corner)
    """
    # Format column
    col_index += 1  # Convert to 1-based
    col_letters = []
    while col_index > 0:
        col_index -= 1
        col_letters.insert(0, chr(ord('A') + col_index % 26))
        col_index //= 26
    
    # Format row
    row_number = row_index + 1  # Convert to 1-based
    
    return f"{''.join(col_letters)}{row_number}"
```

---

## KFEN vs Chess FEN Comparison

| Feature | Chess FEN | KFEN |
|---------|-----------|------|
| Board state | Before moves | Before moves ✓ |
| Turn indication | `w` (white) / `b` (black) | `N` (North) / `S` (South) ✓ |
| Piece representation | Single character per piece | Single character (brackets for terrain) ✓ |
| Empty squares | Numbers for consecutive empty | `_` for each empty ✓ |
| Castle/en passant rights | Separate metadata | Actions inferred from turn/phase ✓ |
| Move counter | Halfmove/fullmove counts | Not needed (inferred) ✓ |
| Special notation | `+` for promoted pieces | `()` for pass, `[]` for fortress ✓ |

---

## Design Rationale

### Why Board State Before Actions?
- Matches standard chess FEN convention
- Intuitive for loading/saving positions
- Clear: "Here's where we are, here's what happens next"
- Easy to implement replay/undo

### Why Bracket Notation for Terrain?
- Clear visual distinction between flat and special terrain
- Easy to parse (find `(` and `[`)
- Backward compatible with flat-only boards
- ASCII-compatible

### Why Spreadsheet-Style Coordinates?
- Familiar to users (Excel, chess notation)
- Supports arbitrarily large boards
- Human-readable
- Easy to parse and validate

### Why Inferred Actions?
- Reduces metadata clutter
- More flexible (can add move/attack counts later if needed)
- Cleaner format
- Matches game flow naturally

---

## Future Extensions

The KFEN format is designed to be extensible. Potential future additions:

1. **Board dimensions**: Add metadata for non-standard board sizes
2. **Move counters**: Add halfmove/fullmove counts like chess FEN
3. **Version field**: Add version number for format evolution
4. **Checksums**: Add integrity verification
5. **Comments**: Allow inline comments in KFEN strings

---

## Examples in Code

### Python Pseudocode for Parsing
```python
def parse_kfen(kfen_string):
    """Parse KFEN string into components."""
    parts = kfen_string.split('/')
    
    board_data = parts[:-3]
    turn = parts[-3]
    phase = parts[-2]
    actions = parts[-1]
    
    return {
        'board_data': board_data,
        'turn': turn,
        'phase': phase,
        'actions': actions
    }

def parse_actions(actions_str, phase):
    """Parse actions based on phase."""
    if phase == 'M':
        # Parse move list: [(from,to),...]
        if actions_str == '[]':
            return []
        # Remove outer brackets and split by '),('
        moves_str = actions_str[1:-1]
        if not moves_str:
            return []
        pairs = moves_str.split('),(')
        pairs[0] = pairs[0].replace('(', '')
        pairs[-1] = pairs[-1].replace(')', '')
        
        moves = []
        for pair in pairs:
            if not pair:
                continue
            from_coord, to_coord = pair.split(',')
            moves.append((from_coord, to_coord))
        return moves
    elif phase == 'B':
        # Return target or 'pass'
        return actions_str if actions_str else 'pass'
    else:
        raise ValueError(f"Invalid phase: {phase}")
```

### Python Pseudocode for Formatting
```python
def format_kfen(board_data, turn, phase, actions):
    """Format KFEN string from components."""
    board_str = '/'.join(board_data)
    
    if phase == 'M':
        actions_str = '[' + ','.join([f"({frm},{to})" for frm, to in actions]) + ']'
    elif phase == 'B':
        actions_str = actions if actions else 'pass'
    else:
        raise ValueError(f"Invalid phase: {phase}")
    
    return f"{board_str}/{turn}/{phase}/{actions_str}"
```

---

## Test Cases

### Test Case 1: Empty Board Roundtrip
**Input KFEN**:
```
_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/_____________________/N/M/[]
```

**Expected Parsing**:
- Board: 20×25 empty squares
- Turn: North
- Phase: Movement
- Actions: Empty list

### Test Case 2: Move Parsing
**Input KFEN**:
```
IC_____________/ic_____________/_____________________/.../_____________________/S/M/[(A1,A2),(B3,B4)]
```

**Expected Parsing**:
- Turn: South
- Phase: Movement
- Actions: `[('A1', 'A2'), ('B3', 'B4')]`

### Test Case 3: Attack Target
**Input KFEN**:
```
_____________________/.../_____________________/N/B/A5
```

**Expected Parsing**:
- Turn: North
- Phase: Battle
- Actions: `'A5'`

### Test Case 4: Attack Pass
**Input KFEN**:
```
_____________________/.../_____________________/S/B/pass
```

**Expected Parsing**:
- Turn: South
- Phase: Battle
- Actions: `'pass'`

### Test Case 5: Terrain Units
**Input KFEN**:
```
(I)(C)_m_p_f_____/_____________________/.../_____________________/N/M/[(A1,A2)]
```

**Expected Parsing**:
- Row 1: Infantry on pass, Cavalry on pass, mountain, empty pass, empty fortress
- Turn: North
- Phase: Movement
- Actions: `[('A1', 'A2')]`

---

## Implementation Notes

1. **Always validate coordinates** before using them
2. **Handle empty move slots** in movement phase gracefully
3. **Convert between coordinate systems** as needed (spreadsheet ↔ (row, col) ↔ index)
4. **Preserve board state** before applying actions for undo functionality
5. **Log warnings** for deprecated or edge-case formats

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2025-01-09 | Final specification with terrain brackets, spreadsheet coordinates, inferred actions |
| 1.0 | 2025-01-09 | Initial draft with basic FEN format |

---

## References

- Chess FEN: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
- Le Jeu de la Guerre: Guy Debord's original game rules
- Spreadsheet notation: Excel, Google Sheets convention

---

**End of KFEN Specification**
