# Protocol-specific exceptions


class ProtocolError(Exception):
    """Base exception for protocol errors."""

    pass


class UnknownCommandError(ProtocolError):
    """Raised when an unknown command is received."""

    def __init__(self, command: str) -> None:
        self.command = command
        super().__init__(f"Unknown command: {command}")


class ParseError(ProtocolError):
    """Raised when command parsing fails."""

    def __init__(self, command: str, reason: str) -> None:
        self.command = command
        self.reason = reason
        super().__init__(f"Parse error in command '{command}': {reason}")


class InvalidPositionError(ProtocolError):
    """Raised when position setup fails."""

    def __init__(self, position_type: str, value: str, reason: str) -> None:
        self.position_type = position_type
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid {position_type} '{value}': {reason}")


class InvalidMoveError(ProtocolError):
    """Raised when a move is invalid."""

    def __init__(self, move: str, reason: str) -> None:
        self.move = move
        self.reason = reason
        super().__init__(f"Invalid move '{move}': {reason}")


class EngineNotReadyError(ProtocolError):
    """Raised when engine receives command before ready."""

    pass


class SearchError(ProtocolError):
    """Raised during search execution."""

    pass
