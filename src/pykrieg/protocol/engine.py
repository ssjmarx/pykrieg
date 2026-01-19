# Base engine interface for UCI protocol

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Union

from pykrieg.protocol.uci import EngineOption, GoParameters, InfoParameters


class UCIEngine(ABC):
    """Base class for UCI-compatible engines."""

    def __init__(self) -> None:
        self._options: Dict[str, EngineOption] = {}
        self._option_values: Dict[str, Union[str, int, bool]] = {}
        self.debug_mode: bool = False
        self.info_callback: Optional[Callable[[str], None]] = None

    @abstractmethod
    def get_name(self) -> str:
        """Return engine name.

        Returns:
            Engine name string.
        """
        pass

    @abstractmethod
    def get_author(self) -> str:
        """Return engine author.

        Returns:
            Engine author string.
        """
        pass

    def uci(self) -> None:
        """Initialize UCI mode."""
        self._initialize_options()
        self._debug("UCI mode initialized")

    def _debug(self, message: str) -> None:
        """Log debug message.

        Args:
            message: Debug message to log.
        """
        if self.debug_mode:
            print(f"debug: {message}")

    def isready(self) -> bool:
        """Check if engine is ready.

        Returns:
            True if engine is ready.
        """
        return True

    def setoption(self, name: str, value: str) -> None:
        """Set engine option.

        Args:
            name: Option name.
            value: Option value string.

        Raises:
            ValueError: If option is unknown.
        """
        if name not in self._options:
            raise ValueError(f"Unknown option: {name}")

        option = self._options[name]

        # Convert value based on option type
        parsed_value: Union[str, int, bool]
        if option.type == "check":
            parsed_value = value.lower() in ("true", "yes", "1")
        elif option.type == "spin":
            parsed_value = int(value)
        else:
            parsed_value = value

        self._option_values[name] = parsed_value
        self._debug(f"Option '{name}' set to '{parsed_value}'")

    def ucinewgame(self) -> None:
        """Start a new game."""
        self._debug("New game started")
        # Subclasses can override for game-specific initialization

    def position(self, position_type: str, value: Optional[str], moves: List[str]) -> None:
        """Set board position.

        Args:
            position_type: Position type ("startpos" or "kfen").
            value: Position string (for KFEN), or None for startpos.
            moves: List of move strings to apply.

        Raises:
            ValueError: If position setup fails.
        """
        self._debug(f"Position set: {position_type}")
        if moves:
            self._debug(f"Applied {len(moves)} moves")

    def _apply_move(self, move: str) -> None:
        """Apply a move to the board.

        Args:
            move: Move string in format "1A1B" (from 1A to 1B).

        Raises:
            ValueError: If move format is invalid.
        """
        # Validate move format
        if len(move) != 4:
            raise ValueError(f"Invalid move format: {move}")

        # Extract coordinates
        from_row = int(move[0])
        from_col = ord(move[1].upper()) - ord("A")
        to_row = int(move[2])
        to_col = ord(move[3].upper()) - ord("A")

        # Validate coordinates are within bounds
        if not (1 <= from_row <= 19):
            raise ValueError(f"Invalid from row: {from_row}")
        if not (0 <= from_col <= 18):
            raise ValueError(f"Invalid from column: {move[1]}")
        if not (1 <= to_row <= 19):
            raise ValueError(f"Invalid to row: {to_row}")
        if not (0 <= to_col <= 18):
            raise ValueError(f"Invalid to column: {move[3]}")

        self._debug(f"Move applied: {move}")

    @abstractmethod
    def go(self, params: GoParameters) -> str:
        """Start search and return best move.

        Args:
            params: GoParameters object containing search parameters.

        Returns:
            Best move string, or empty string if no move available.
        """
        pass

    def stop(self) -> None:
        """Stop current search."""
        self._debug("Search stopped")

    def send_info(self, info: InfoParameters) -> None:
        """Send info via callback if set.

        Args:
            info: InfoParameters object containing search information.
        """
        if self.info_callback:
            from pykrieg.protocol.response import ResponseGenerator

            gen = ResponseGenerator()
            self.info_callback(gen.info(info))

    def _initialize_options(self) -> None:  # noqa: B027
        """Initialize default engine options.

        Subclasses can override to add engine-specific options.
        """
        pass

    def cleanup(self) -> None:
        """Cleanup resources."""
        self._debug("Engine cleanup complete")
