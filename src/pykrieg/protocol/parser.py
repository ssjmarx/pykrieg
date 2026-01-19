# UCI command parser

from dataclasses import dataclass
from typing import Any, Callable

from pykrieg.protocol.exceptions import (
    ParseError,
    UnknownCommandError,
)
from pykrieg.protocol.uci import (
    GoParameters,
    UCICommand,
)


@dataclass
class ParsedCommand:
    """Parsed command with its parameters."""

    command: UCICommand
    parameters: dict[str, Any]


class ProtocolParser:
    """Parse UCI-like protocol commands."""

    def __init__(self) -> None:
        self._command_map: dict[str, Callable[[list[str]], ParsedCommand]] = {
            "uci": self._parse_uci,
            "debug": self._parse_debug,
            "isready": self._parse_isready,
            "setoption": self._parse_setoption,
            "ucinewgame": self._parse_ucinewgame,
            "position": self._parse_position,
            "go": self._parse_go,
            "stop": self._parse_stop,
            "quit": self._parse_quit,
            "status": self._parse_status,
            "network": self._parse_network,
            "victory": self._parse_victory,
            "phase": self._parse_phase,
            "retreats": self._parse_retreats,
        }

    def parse(self, command_string: str) -> ParsedCommand:
        """Parse a command string into a structured command.

        Args:
            command_string: The raw command string to parse.

        Returns:
            ParsedCommand: The parsed command with its parameters.

        Raises:
            ParseError: If the command string is empty or invalid.
            UnknownCommandError: If the command is not recognized.
        """
        # Strip whitespace, skip empty lines
        command_string = command_string.strip()
        if not command_string:
            raise ParseError(command_string, "Empty command")

        # Split into parts
        parts = command_string.split()
        if not parts:
            raise ParseError(command_string, "No command found")

        command_name = parts[0].lower()

        # Lookup parser for command
        if command_name not in self._command_map:
            raise UnknownCommandError(command_name)

        # Parse command with its specific parser
        parser_func = self._command_map[command_name]
        return parser_func(parts[1:])

    def _parse_uci(self, args: list[str]) -> ParsedCommand:
        """Parse 'uci' command (no arguments)."""
        if args:
            raise ParseError("uci", f"Unexpected arguments: {' '.join(args)}")
        return ParsedCommand(command="uci", parameters={})

    def _parse_debug(self, args: list[str]) -> ParsedCommand:
        """Parse 'debug [on|off]' command."""
        if len(args) != 1:
            raise ParseError("debug", "Expected 'on' or 'off'")
        mode = args[0].lower()
        if mode not in ("on", "off"):
            raise ParseError("debug", f"Invalid mode '{mode}', expected 'on' or 'off'")
        return ParsedCommand(command="debug", parameters={"mode": mode})

    def _parse_isready(self, args: list[str]) -> ParsedCommand:
        """Parse 'isready' command (no arguments)."""
        if args:
            raise ParseError("isready", f"Unexpected arguments: {' '.join(args)}")
        return ParsedCommand(command="isready", parameters={})

    def _parse_setoption(self, args: list[str]) -> ParsedCommand:
        """Parse 'setoption name <name> value <value>' command."""
        # Expected format: setoption name <name> value <value>
        if len(args) < 4:
            raise ParseError("setoption", "Expected format: setoption name <name> value <value>")

        # Find 'name' and 'value' keywords
        try:
            name_idx = args.index("name")
            value_idx = args.index("value")
        except ValueError as e:
            raise ParseError("setoption", f"Missing keyword: {e}") from None

        if name_idx >= value_idx:
            raise ParseError("setoption", "'name' must come before 'value'")

        # Extract name (between 'name' and 'value')
        name_parts = args[name_idx + 1 : value_idx]
        if not name_parts:
            raise ParseError("setoption", "Missing option name")
        name = " ".join(name_parts)

        # Extract value (after 'value')
        value_parts = args[value_idx + 1 :]
        if not value_parts:
            raise ParseError("setoption", "Missing option value")
        value = " ".join(value_parts)

        return ParsedCommand(command="setoption", parameters={"name": name, "value": value})

    def _parse_ucinewgame(self, args: list[str]) -> ParsedCommand:
        """Parse 'ucinewgame' command (no arguments)."""
        if args:
            raise ParseError("ucinewgame", f"Unexpected arguments: {' '.join(args)}")
        return ParsedCommand(command="ucinewgame", parameters={})

    def _parse_position(self, args: list[str]) -> ParsedCommand:
        """Parse position command.

        Formats:
        - position startpos [moves <move1> <move2> ...]
        - position kfen <filename> [moves <move1> <move2> ...]

        Raises:
            ParseError: If position type is invalid or arguments are missing.
        """
        if not args:
            raise ParseError("position", "Expected position type (startpos or kfen)")

        # Determine position type
        position_type = args[0].lower()
        if position_type not in ("startpos", "kfen"):
            raise ParseError(
                "position",
                f"Invalid position type '{position_type}', expected 'startpos' or 'kfen'",
            )

        params: dict[str, Any] = {"type": position_type}

        # Parse position value (if not startpos)
        if position_type != "startpos":
            if len(args) < 2:
                raise ParseError(
                    "position", f"Expected {position_type} string after '{position_type}'"
                )
            params["value"] = args[1]
            remaining_args = args[2:]
        else:
            remaining_args = args[1:]

        # Parse move sequence if present
        if remaining_args and remaining_args[0].lower() == "moves":
            if len(remaining_args) < 2:
                raise ParseError("position", "Expected moves after 'moves'")
            params["moves"] = remaining_args[1:]
        else:
            params["moves"] = []

        return ParsedCommand(command="position", parameters=params)

    def _parse_go(self, args: list[str]) -> ParsedCommand:
        """Parse 'go' command with various parameters."""
        go_params = GoParameters(
            depth=None, nodes=None, movetime=None, infinite=False, ponder=False
        )

        i = 0
        while i < len(args):
            arg = args[i].lower()

            if arg == "depth":
                i += 1
                if i >= len(args):
                    raise ParseError("go", "Expected value after 'depth'")
                try:
                    go_params.depth = int(args[i])
                except ValueError:
                    raise ParseError(
                        "go", f"Invalid depth value '{args[i]}', expected integer"
                    ) from None

            elif arg == "nodes":
                i += 1
                if i >= len(args):
                    raise ParseError("go", "Expected value after 'nodes'")
                try:
                    go_params.nodes = int(args[i])
                except ValueError:
                    raise ParseError(
                        "go", f"Invalid nodes value '{args[i]}', expected integer"
                    ) from None

            elif arg == "movetime":
                i += 1
                if i >= len(args):
                    raise ParseError("go", "Expected value after 'movetime'")
                try:
                    go_params.movetime = int(args[i])
                except ValueError:
                    raise ParseError(
                        "go", f"Invalid movetime value '{args[i]}', expected integer"
                    ) from None

            elif arg == "infinite":
                go_params.infinite = True

            elif arg == "ponder":
                go_params.ponder = True

            else:
                raise ParseError("go", f"Unknown parameter '{arg}'")

            i += 1

        return ParsedCommand(command="go", parameters=go_params.__dict__)

    def _parse_stop(self, args: list[str]) -> ParsedCommand:
        """Parse 'stop' command (no arguments)."""
        if args:
            raise ParseError("stop", f"Unexpected arguments: {' '.join(args)}")
        return ParsedCommand(command="stop", parameters={})

    def _parse_quit(self, args: list[str]) -> ParsedCommand:
        """Parse 'quit' command (no arguments)."""
        if args:
            raise ParseError("quit", f"Unexpected arguments: {' '.join(args)}")
        return ParsedCommand(command="quit", parameters={})

    def _parse_status(self, args: list[str]) -> ParsedCommand:
        """Parse 'status' command (no arguments)."""
        if args:
            raise ParseError("status", f"Unexpected arguments: {' '.join(args)}")
        return ParsedCommand(command="status", parameters={})

    def _parse_network(self, args: list[str]) -> ParsedCommand:
        """Parse 'network' command (no arguments)."""
        if args:
            raise ParseError("network", f"Unexpected arguments: {' '.join(args)}")
        return ParsedCommand(command="network", parameters={})

    def _parse_victory(self, args: list[str]) -> ParsedCommand:
        """Parse 'victory' command (no arguments)."""
        if args:
            raise ParseError("victory", f"Unexpected arguments: {' '.join(args)}")
        return ParsedCommand(command="victory", parameters={})

    def _parse_phase(self, args: list[str]) -> ParsedCommand:
        """Parse 'phase [movement|battle]' command."""
        if args:
            phase = args[0].lower()
            if phase not in ("movement", "battle"):
                raise ParseError(
                    "phase", f"Invalid phase '{phase}', expected 'movement' or 'battle'"
                )
            return ParsedCommand(command="phase", parameters={"phase": phase})
        return ParsedCommand(command="phase", parameters={})

    def _parse_retreats(self, args: list[str]) -> ParsedCommand:
        """Parse 'retreats' command (no arguments)."""
        if args:
            raise ParseError("retreats", f"Unexpected arguments: {' '.join(args)}")
        return ParsedCommand(command="retreats", parameters={})
