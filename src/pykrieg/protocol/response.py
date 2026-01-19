# Response generation for UCI protocol

from typing import Any, Optional

from pykrieg.protocol.uci import EngineOption, InfoParameters, ProtocolPhase


class ResponseGenerator:
    """Generate UCI protocol responses."""

    def __init__(
        self,
        engine_name: str = "Pykrieg Engine",
        engine_author: str = "Pykrieg Team",
        protocol_version: str = "1.0",
    ) -> None:
        self.engine_name = engine_name
        self.engine_author = engine_author
        self.protocol_version = protocol_version

    def uci_identification(self) -> str:
        """Generate UCI identification response.

        Returns:
            Multi-line string with id name, id author, and uciok.
        """
        return f"id name {self.engine_name}\nid author {self.engine_author}\nuciok"

    def ready_ok(self) -> str:
        """Generate ready response.

        Returns:
            String 'readyok'.
        """
        return "readyok"

    def best_move(self, move: Optional[str], ponder_move: Optional[str] = None) -> str:
        """Generate bestmove response.

        Args:
            move: The best move found, or None if no move available.
            ponder_move: The ponder move for bestmove ponder, or None.

        Returns:
            Formatted bestmove response string.
        """
        if move is None:
            return "bestmove (none)"
        if ponder_move:
            return f"bestmove {move} ponder {ponder_move}"
        return f"bestmove {move}"

    def info(self, info_params: InfoParameters) -> str:
        """Generate info response.

        Args:
            info_params: InfoParameters object containing search information.

        Returns:
            Formatted info response string.
        """
        parts = ["info"]

        if info_params.depth is not None:
            parts.append(f"depth {info_params.depth}")

        if info_params.seldepth is not None:
            parts.append(f"seldepth {info_params.seldepth}")

        if info_params.time is not None:
            parts.append(f"time {info_params.time}")

        if info_params.nodes is not None:
            parts.append(f"nodes {info_params.nodes}")

        if info_params.score is not None:
            score = info_params.score
            if score.cp is not None:
                bound = ""
                if score.lowerbound:
                    bound = " lowerbound"
                if score.upperbound:
                    bound = " upperbound"
                parts.append(f"score cp {score.cp}{bound}")
            elif score.mate is not None:
                parts.append(f"score mate {score.mate}")

        if info_params.currmove is not None:
            parts.append(f"currmove {info_params.currmove}")

        if info_params.currmovenumber is not None:
            parts.append(f"currmovenumber {info_params.currmovenumber}")

        if info_params.hashfull is not None:
            parts.append(f"hashfull {info_params.hashfull}")

        if info_params.nps is not None:
            parts.append(f"nps {info_params.nps}")

        return " ".join(parts)

    def option(self, option: EngineOption) -> str:
        """Generate option definition response.

        Args:
            option: EngineOption object to format.

        Returns:
            Formatted option response string.
        """
        parts = [
            f"option name {option.name} type {option.type}",
            f"default {self._format_option_value(option.default)}",
        ]

        if option.min is not None:
            parts.append(f"min {option.min}")

        if option.max is not None:
            parts.append(f"max {option.max}")

        if option.var:
            for var in option.var:
                parts.append(f"var {var}")

        return " ".join(parts)

    def _format_option_value(self, value: Any) -> str:
        """Format option value for response.

        Args:
            value: The option value to format.

        Returns:
            Formatted string representation.
        """
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "<empty>"
        return str(value)

    # Pykrieg-specific responses

    def status(self, turn: str, phase: str, turn_number: int) -> str:
        """Generate game status response.

        Args:
            turn: Current turn ("NORTH" or "SOUTH").
            phase: Current phase ("movement" or "battle").
            turn_number: Current turn number.

        Returns:
            Formatted status response string.
        """
        parts = ["status"]
        parts.append(f"turn={turn}")
        parts.append(f"phase={phase}")
        parts.append(f"turn_number={turn_number}")

        return " ".join(parts)

    def network(
        self,
        north_online: int,
        north_offline: int,
        south_online: int,
        south_offline: int,
    ) -> str:
        """Generate network status response.

        Args:
            north_online: Number of online units for NORTH.
            north_offline: Number of offline units for NORTH.
            south_online: Number of online units for SOUTH.
            south_offline: Number of offline units for SOUTH.

        Returns:
            Formatted network response string.
        """
        parts = ["network"]
        parts.append(f"north_online={north_online}")
        parts.append(f"north_offline={north_offline}")
        parts.append(f"south_online={south_online}")
        parts.append(f"south_offline={south_offline}")

        return " ".join(parts)

    def victory(self, winner: Optional[str], condition: Optional[str]) -> str:
        """Generate victory status response.

        Args:
            winner: Winning player ("NORTH" or "SOUTH"), or None if ongoing.
            condition: Victory condition met, or None if ongoing.

        Returns:
            Formatted victory response string.
        """
        if winner is None:
            return "victory false ongoing"

        parts = ["victory true"]
        parts.append(f"winner={winner}")
        if condition:
            parts.append(f"condition={condition}")

        return " ".join(parts)

    def phase(self, current_phase: ProtocolPhase) -> str:
        """Generate phase response.

        Args:
            current_phase: Current phase ("movement" or "battle").

        Returns:
            Formatted phase response string.
        """
        return f"phase {current_phase}"

    def retreats(self, retreat_positions: list[str]) -> str:
        """Generate retreats response.

        Args:
            retreat_positions: List of positions requiring retreat.

        Returns:
            Formatted retreats response string.
        """
        if not retreat_positions:
            return "retreats none"

        return f"retreats {','.join(retreat_positions)}"

    # Error responses

    def error(self, message: str) -> str:
        """Generate error response.

        Args:
            message: Error message to send.

        Returns:
            Formatted error response string.
        """
        return f"error {message}"
