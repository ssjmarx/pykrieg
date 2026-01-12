"""Command buffer management for console interface.

This module handles queuing multiple commands before execution,
providing enhanced copy/paste support and command editing.

Classes:
    CommandBuffer: Manage queued commands with editing capabilities

Functions:
    parse_multi_command_input(): Parse multi-line command input
"""

from typing import List, Optional, Tuple


class CommandBuffer:
    """Manage queued commands with editing capabilities.

    Features:
    - Queue multiple commands before execution
    - Edit/Remove individual commands
    - Clear entire buffer
    - Support copy/paste of multiple commands
    """

    def __init__(self) -> None:
        """Initialize command buffer."""
        self.commands: List[str] = []
        self.current_input: str = ""

    def add_command(self, command: str) -> None:
        """Add a command to the buffer.

        Args:
            command: Command string to add
        """
        self.commands.append(command)

    def remove_last(self) -> None:
        """Remove the last command from the buffer."""
        if self.commands:
            self.commands.pop()

    def clear(self) -> None:
        """Clear all commands from the buffer."""
        self.commands.clear()
        self.current_input = ""

    def get_commands(self) -> str:
        """Get all commands as a single string.

        Returns:
            Commands joined by semicolons for execution
        """
        return "; ".join(self.commands)

    def is_empty(self) -> bool:
        """Check if buffer is empty.

        Returns:
            True if no commands queued, False otherwise
        """
        return len(self.commands) == 0

    def get_count(self) -> int:
        """Get number of commands in buffer.

        Returns:
            Number of queued commands
        """
        return len(self.commands)

    def add_raw_input(self, input_str: str) -> Tuple[bool, Optional[str]]:
        """Add raw input and check if complete command is ready.

        Args:
            input_str: Raw input string from user

        Returns:
            Tuple of (is_complete, error_message)
        """
        # Parse multi-line input
        parsed_commands = self._parse_multi_command_input(input_str)

        if not parsed_commands:
            return True, None

        # Add commands to buffer
        for cmd in parsed_commands:
            self.commands.append(cmd)

        return False, None

    def _parse_multi_command_input(self, input_str: str) -> List[str]:
        """Parse multi-line or multi-command input.

        Args:
            input_str: Input string to parse

        Returns:
            List of parsed commands
        """
        # Split by semicolons (command separator)
        parts = input_str.split(';')

        commands = []
        for part in parts:
            cmd = part.strip()
            if cmd:
                # Validate basic command format
                if self._is_valid_command_format(cmd):
                    commands.append(cmd)

        return commands

    def _is_valid_command_format(self, cmd: str) -> bool:
        """Check if command has valid basic format.

        Args:
            cmd: Command string to validate

        Returns:
            True if valid format, False otherwise
        """
        # Basic validation: should start with a known command word
        if not cmd:
            return False

        words = cmd.lower().split()
        if not words:
            return False

        valid_starts = [
            'move', 'm', 'attack', 'a', 'pass', 'p', 'end', 'e',
            'save', 's', 'load', 'l', 'help', 'h', '?', 'mode',
            'quit', 'q',
        ]

        # Also allow coordinate-only shorthand (e.g., "5,10 6,10")
        if len(words) == 2 and self._looks_like_coordinates(cmd):
            return True

        return words[0] in valid_starts

    def _looks_like_coordinates(self, cmd: str) -> bool:
        """Check if command string looks like coordinates.

        Args:
            cmd: Command string to check

        Returns:
            True if looks like coordinates, False otherwise
        """
        # Split into parts
        parts = cmd.split()

        # Should have even number of parts (pairs of coordinates)
        if len(parts) % 2 != 0:
            return False

        # Each pair should look like "row,col"
        for part in parts[::2]:
            if not self._looks_like_single_coord(part):
                return False

        return True

    def _looks_like_single_coord(self, part: str) -> bool:
        """Check if part looks like a single coordinate.

        Args:
            part: String to check

        Returns:
            True if looks like coordinate, False otherwise
        """
        # Should contain comma or have two parts
        if ',' in part:
            coords = part.split(',')
            return len(coords) == 2
        else:
            parts = part.split()
            return len(parts) == 2

    def get_display(self) -> str:
        """Get display string for the buffer.

        Returns:
            Formatted display string
        """
        if self.is_empty():
            return "Buffer: Empty"

        lines = ["Buffer:"]
        for i, cmd in enumerate(self.commands):
            lines.append(f"  {i+1}. {cmd}")

        lines.append("")
        lines.append("Press ENTER to execute all commands")
        lines.append("BACKSPACE to remove last command")
        lines.append("ESC to clear buffer")

        return "\n".join(lines)


def parse_multi_command_input(input_str: str) -> List[str]:
    """Parse multi-line or multi-command input for pasting.

    Args:
        input_str: Input string to parse

    Returns:
        List of parsed commands
    """
    buffer = CommandBuffer()

    # Handle various line separators (from different OSes)
    normalized = input_str.replace('\r\n', ';').replace('\n', ';')

    is_complete, error = buffer.add_raw_input(normalized)

    if error:
        return []

    return buffer.commands
