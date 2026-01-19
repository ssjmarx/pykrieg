# Pykrieg Protocol Specification

## Overview
The Pykrieg Protocol is a UCI-like communication protocol for connecting game engines with frontends. It enables engines to process board states, calculate moves, and respond to analysis requests in a standardized way.

**Version**: 1.0  
**Last Updated**: 2026-01-18  
**Status**: Final Specification

---

## Protocol Design

### Design Rationale

The Pykrieg Protocol is based on the Universal Chess Interface (UCI) protocol used in chess engines, with adaptations for Guy Debord's *Le Jeu de la Guerre*:

1. **UCI Compatibility**: Follows UCI patterns for familiar implementation
2. **Text-based**: Simple line-oriented protocol, easy to debug
3. **Asynchronous**: Engines can respond immediately or after computation
4. **Extensible**: Custom commands for game-specific features
5. **Stateless**: Each command is independent (except position/go sequence)

### Communication Model

```
Frontend → Engine: Command
Engine → Frontend: Response (optional immediate)
Engine → Frontend: Best move (after search)
```

- Frontend sends commands one per line
- Engine responds immediately for simple commands
- Engine responds after computation for search commands
- Responses are guaranteed to arrive in order

---

## Protocol Commands

### 1. uci

Initialize UCI mode and identify the engine.

**Format:** `uci`

**Response:**
```
id name <engine_name>
id author <author_name>
option name <name> type <type> default <default> [min <min> max <max> var <var1> var <var2> ...]
[option name ...]
uciok
```

**Description:**
- Engine identifies itself with name and author
- Engine lists all configurable options
- Each option includes type (check, spin, combo, button, string)
- Spin options include min/max values
- Combo options include variable choices
- Final `uciok` signals readiness

**Example:**
```
Frontend: uci
Engine:    id name Pykrieg Random Engine
Engine:    id author Pykrieg Team
Engine:    option name Hash type spin default 128 min 1 max 1024
Engine:    option name Threads type spin default 1 min 1 max 4
Engine:    option name Ponder type check default false
Engine:    uciok
```

---

### 2. debug [on|off]

Toggle debug mode for verbose logging.

**Format:** `debug on` or `debug off`

**Response:** None

**Description:**
- When enabled, engine prints debug messages to stdout
- Messages prefixed with `debug:`
- Useful for development and troubleshooting
- Off by default

**Example:**
```
Frontend: debug on
Engine:    debug mode enabled
Frontend: uci
Engine:    debug: Parsing UCI command
Engine:    debug: Initializing options
Engine:    id name TestEngine
Engine:    id author TestAuthor
Engine:    uciok
```

---

### 3. isready

Check if engine is ready to receive commands.

**Format:** `isready`

**Response:** `readyok`

**Description:**
- Engine responds when ready to process new commands
- Used for synchronization during initialization
- Engine should respond quickly (<100ms)
- Always returns `readyok` (no failure mode)

**Example:**
```
Frontend: uci
Engine:    id name TestEngine
Engine:    id author TestAuthor
Engine:    uciok
Frontend: isready
Engine:    readyok
```

---

### 4. setoption name <name> value <value>

Configure engine options.

**Format:** `setoption name <name> value <value>`

**Response:** None

**Description:**
- Changes engine configuration dynamically
- Options must be declared in `uci` response
- Values validated against option type and constraints
- Changes take effect immediately or on next search

**Types:**
- `check`: "true" or "false"
- `spin`: integer within min/max range
- `combo`: one of declared var values
- `button`: no value, triggers action
- `string`: any text value

**Example:**
```
Frontend: setoption name Hash value 256
Frontend: setoption name Ponder value true
Frontend: setoption name Style value Aggressive
```

---

### 5. ucinewgame

Start a new game session.

**Format:** `ucinewgame`

**Response:** None

**Description:**
- Signals start of new game
- Engine should clear any cached data
- Reset transposition tables
- Clear history/undo stacks
- Prepare for fresh game state

**Example:**
```
Frontend: uci
Engine:    id name TestEngine
Engine:    uciok
Frontend: ucinewgame
Frontend: position startpos
```

---

### 6. position [startpos|kfen] [moves <move1> <move2> ...]

Set the current board position.

**Format:** `position startpos [moves <move1> <move2> ...]`  
**Format:** `position kfen <filename> [moves <move1> <move2> ...]`

**Response:** None

**Description:**
- Sets the board state for analysis/search
- `startpos`: Use default starting position
- `kfen`: Load position from KFEN file
- `moves`: Optional sequence of moves to apply
- Moves applied in order from given position

**Move Format:** `XXXX` where:
- First 2 chars: From position (e.g., "1A")
- Last 2 chars: To position (e.g., "1B")
- Spreadsheet notation: column letter, row number

**Example:**
```
Frontend: position startpos
Frontend: position kfen game.kfen
Frontend: position startpos moves 1A1B 2C2D 3E3F
Frontend: position kfen saved.kfen moves 1A1B
```

**Move Sequence:**
- Each move executed sequentially
- Board state updates after each move
- Network recalculated after all moves
- Turn/phase updated accordingly

---

### 7. go [depth|nodes|movetime|infinite|ponder]

Start searching for best move.

**Format:** `go depth <d>`  
**Format:** `go nodes <n>`  
**Format:** `go movetime <ms>`  
**Format:** `go infinite`  
**Format:** `go ponder`

**Parameters:**
- `depth <d>`: Search to depth d
- `nodes <n>`: Search until n nodes evaluated
- `movetime <ms>`: Search for exactly ms milliseconds
- `infinite`: Search until stopped
- `ponder`: Search in pondering mode (background)

**Response:** `bestmove <move> [ponder <move>]`

**Description:**
- Engine searches current position
- Returns best move found
- Can include ponder move for opponent
- Stops when criteria met or `stop` command received

**Move Response:**
- `bestmove (none)`: No legal moves available
- `bestmove <move>`: Best move found
- `bestmove <move> ponder <move2>`: Best move + expected reply

**Example:**
```
Frontend: position startpos
Frontend: go depth 10
Engine:    info depth 10 score cp 150 nodes 100000
Engine:    bestmove 1A1B ponder 2C2D
```

**Info Responses (Optional):**
```
info depth <d>
info depth <d> score cp <cp> nodes <n>
info depth <d> score mate <moves> nodes <n>
info depth <d> currmove <move> currmovenumber <n> nodes <n>
info nodes <n> nps <speed>
```

---

### 8. stop

Stop current search.

**Format:** `stop`

**Response:** None (followed by `bestmove`)

**Description:**
- Interrupts ongoing search
- Engine returns best move found so far
- Should respond quickly (<50ms)
- No response if no search in progress

**Example:**
```
Frontend: position startpos
Frontend: go infinite
Frontend: info depth 5 score cp 50
Frontend: info depth 10 score cp 100
Frontend: stop
Engine:    bestmove 1A1B
```

---

### 9. quit

Exit the engine.

**Format:** `quit`

**Response:** None (engine terminates)

**Description:**
- Engine should cleanup resources
- Close any open files/connections
- Exit gracefully
- No further commands accepted

**Example:**
```
Frontend: quit
Engine:    [exits]
```

---

## Pykrieg-Specific Commands

### 10. status

Query current game status.

**Format:** `status`

**Response:** `status turn=<NORTH|SOUTH> phase=<movement|battle> turn_number=<n>`

**Description:**
- Returns current turn (NORTH or SOUTH)
- Returns current phase (movement or battle)
- Returns turn number (1-indexed)
- Useful for frontend state synchronization

**Example:**
```
Frontend: status
Engine:    status turn=NORTH phase=movement turn_number=5
```

---

### 11. network

Query network connectivity status.

**Format:** `network`

**Response:** `network north_online=<n> north_offline=<o> south_online=<n> south_offline=<o>`

**Description:**
- Returns counts of online/offline units per player
- Online units: Connected to arsenal via relays
- Offline units: Disconnected from network
- Useful for UI display and debugging

**Example:**
```
Frontend: network
Engine:    network north_online=20 north_offline=5 south_online=18 south_offline=7
```

---

### 12. victory

Query victory status.

**Format:** `victory`

**Response:** `victory <true|false> [winner=<NORTH|SOUTH>] [condition=<condition>]`

**Description:**
- Returns whether game is over
- If true, includes winner and victory condition
- If false, indicates game is ongoing
- Conditions: "arsenal_destruction", "unit_elimination", "network_collapse"

**Example:**
```
Frontend: victory
Engine:    victory false ongoing

Frontend: victory
Engine:    victory true winner=NORTH condition=unit_elimination
```

---

### 13. phase

Query or set current phase.

**Format:** `phase [movement|battle]`

**Response:** `phase <movement|battle>`

**Description:**
- Query: Returns current phase
- Set: Changes current phase (if valid transition)
- Phases: movement (M), battle (B)
- Useful for forcing phase transitions

**Example:**
```
Frontend: phase
Engine:    phase movement

Frontend: phase battle
Engine:    phase battle
```

---

### 14. retreats

Query units that must retreat.

**Format:** `retreats`

**Response:** `retreats <none|pos1,pos2,...>`

**Description:**
- Returns positions of units requiring retreat
- Empty string or "none" if no retreats needed
- Comma-separated list of positions
- Units must retreat before other moves

**Example:**
```
Frontend: retreats
Engine:    retreats none

Frontend: retreats
Engine:    retreats 1A,5B,10C
```

---

## Response Types

### Engine Identification
```
id name <name>
id author <author>
```

### Ready Response
```
readyok
```

### Best Move Response
```
bestmove <move> [ponder <move>]
bestmove (none)
```

### Info Response
```
info [depth <d>] [seldepth <d>] [time <ms>] [nodes <n>]
      [score cp <cp>|mate <m>] [currmove <move>] [currmovenumber <n>]
      [hashfull <permill>] [nps <speed>]
```

### Option Response
```
option name <name> type <type> default <default>
       [min <min>] [max <max>] [var <var1> var <var2> ...]
```

### Error Response
```
error <message>
```

### Pykrieg-Specific Responses
```
status turn=<N|S> phase=<M|B> turn_number=<n>
network north_online=<n> north_offline=<o> south_online=<n> south_offline=<o>
victory <true|false> [winner=<N|S>] [condition=<c>]
phase <movement|battle>
retreats <none|pos1,pos2,...>
```

---

## Complete Session Example

### Simple Game
```
Frontend: uci
Engine:    id name Pykrieg Random Engine
Engine:    id author Pykrieg Team
Engine:    option name Hash type spin default 128 min 1 max 1024
Engine:    uciok

Frontend: isready
Engine:    readyok

Frontend: ucinewgame

Frontend: position startpos
Frontend: go depth 5
Engine:    info depth 1 score cp 10
Engine:    info depth 3 score cp 20
Engine:    info depth 5 score cp 50 nodes 50000
Engine:    bestmove 1A1B

Frontend: status
Engine:    status turn=SOUTH phase=movement turn_number=1

Frontend: position startpos moves 1A1B
Frontend: go depth 5
Engine:    bestmove 2C2D

Frontend: quit
```

### Analysis Session
```
Frontend: uci
Engine:    id name Pykrieg Analysis Engine
Engine:    id author Pykrieg Team
Engine:    uciok

Frontend: position kfen mygame.kfen
Frontend: go infinite
Engine:    info depth 1 score cp -100
Engine:    info depth 3 score cp -80
Engine:    info depth 5 score cp -50 nodes 100000
Engine:    info depth 7 score cp -30 nodes 250000
Engine:    info depth 9 score cp -20 nodes 500000

Frontend: stop
Engine:    bestmove 5E6F ponder 7G8H

Frontend: victory
Engine:    victory false ongoing

Frontend: network
Engine:    network north_online=15 north_offline=3 south_online=12 south_offline=5

Frontend: quit
```

---

## Error Handling

### Parse Errors
- Engine sends: `error <message>`
- Frontend should correct command
- Common causes: invalid syntax, out-of-range values

### Unknown Commands
- Engine sends: `error Unknown command: <command>`
- Frontend should check protocol version

### Invalid Options
- Engine sends: `error Invalid option: <name>` or `error Invalid value: <value>`
- Frontend should check option definition

### Invalid Moves
- Engine sends: `error Invalid move: <move>`
- Frontend should verify move format and legality

---

## Protocol Extensions

### Custom Commands
Engines may implement custom commands:
- Prefix with engine name: `pykrieg_analyze <mode>`
- Document in `uci` response
- Frontend should handle gracefully if not supported

### Custom Info
Engines may send custom info:
- `info pv <move1> <move2> ...` (principal variation)
- `info string <text>` (arbitrary info)
- `info refutation <move> <refutation>` (refutation analysis)

---

## Performance Requirements

### Response Times
- `isready`: < 100ms
- `stop`: < 50ms
- `quit`: Immediate
- `position`: < 200ms
- Search: Dependent on parameters

### Memory
- Options (Hash size): 1MB - 1GB
- Position storage: Minimal overhead
- Transposition table: Configurable

---

## Implementation Guidelines

### Engine Developers
1. Implement all standard commands
2. Respond immediately to non-search commands
3. Send periodic `info` updates during long searches
4. Handle `stop` promptly (interrupt search thread)
5. Validate all inputs before processing
6. Document custom commands and options

### Frontend Developers
1. Send `uci` first and wait for `uciok`
2. Use `isready` to synchronize
3. Always call `ucinewgame` between games
4. Send `stop` before new `go` commands
5. Handle errors gracefully
6. Support all standard commands

---

## Compatibility

### Version 1.0
- This is the initial protocol version
- Backward compatibility maintained within 1.x series
- Breaking changes reserved for 2.0+

### UCI Compatibility
- Subset of UCI commands supported
- Extended with game-specific commands
- Move format differs (spreadsheet vs algebraic)
- Position format differs (KFEN vs FEN)

---

## Testing

### Test Harness
```python
import subprocess

def test_engine():
    proc = subprocess.Popen(['python', '-m', 'engine'], 
                           stdin=subprocess.PIPE, 
                           stdout=subprocess.PIPE, 
                           text=True)
    
    # Send uci
    proc.stdin.write('uci\n')
    proc.stdin.flush()
    
    # Read response
    line = proc.stdout.readline()
    assert 'id name' in line
    
    # Continue with more commands...
    proc.stdin.write('quit\n')
    proc.stdin.flush()
    proc.wait()
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-18 | Initial protocol specification |

---

## References

- UCI Protocol: http://wbec-ridderkerk.nl/html/UCIProtocol.html
- KFEN Specification: KFEN-SPECIFICATION.md
- Le Jeu de la Guerre: Guy Debord's original game rules
- Pykrieg Documentation: docs/

---

**End of Protocol Specification**
