"""Terminal capability detection for console interface.

This module provides utilities to detect terminal capabilities
and automatically select the appropriate display mode.

Functions:
    has_unicode_support(): Check if terminal supports Unicode
    has_color_support(): Check if terminal supports ANSI colors
    get_terminal_width(): Get terminal width
    detect_best_mode(): Detect and return best display mode
"""

import os
import sys


def has_unicode_support() -> bool:
    """Check if terminal supports Unicode characters.

    Returns:
        True if Unicode likely supported, False otherwise
    """
    # Check platform
    if sys.platform == 'win32':
        # Windows 10+ generally supports UTF-8
        try:
            import locale
            encoding = locale.getpreferredencoding()
            return encoding.lower() in ('utf-8', 'utf8')
        except Exception:
            return False
    else:
        # Unix-like systems generally support Unicode
        return True


def has_color_support() -> bool:
    """Check if terminal supports ANSI color codes.

    Returns:
        True if colors likely supported, False otherwise
    """
    # Check NO_COLOR environment variable
    if os.environ.get('NO_COLOR'):
        return False

    # Check for common terminal variables
    term = os.environ.get('TERM', '').lower()

    # These terminals generally don't support colors
    no_color_terms = ['dumb', 'emacs', 'linux']
    if any(t in term for t in no_color_terms):
        return False

    # Check if running in a CI environment
    if os.environ.get('CI'):
        return False

    # Assume colors are supported for most modern terminals
    return True


def get_terminal_width() -> int:
    """Get terminal width in characters.

    Returns:
        Terminal width, or 80 if unable to determine
    """
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def detect_best_mode() -> str:
    """Auto-detect best display mode at startup.

    Detection logic (ALL OR NOTHING):
    1. Check if curses module is available
    2. Check if terminal supports colors
    3. If both true: return 'curses'
    4. Otherwise: return 'compatibility'

    This runs ONCE at startup - no mid-game switching unless explicit.
    """
    # Check curses availability
    try:
        import curses
        # Check if terminal supports colors
        curses.setupterm()
        if curses.tigetnum('colors') >= 8:
            return 'curses'
    except Exception:
        pass

    # Fallback to compatibility mode
    return 'compatibility'
