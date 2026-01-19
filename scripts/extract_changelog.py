#!/usr/bin/env python3
"""
Extract release notes from CHANGELOG.md for a specific version.

Usage:
    python scripts/extract_changelog.py <version>

Example:
    python scripts/extract_changelog.py 0.3.0
"""

import re
import sys
from pathlib import Path


def extract_changelog_entry(version: str, changelog_path: str = "CHANGELOG.md") -> str:
    """
    Extract the changelog entry for a specific version.

    Args:
        version: Version string (e.g., "0.3.0")
        changelog_path: Path to CHANGELOG.md file

    Returns:
        String containing the changelog entry
    """
    changelog_file = Path(changelog_path)

    if not changelog_file.exists():
        print(f"Error: {changelog_path} not found", file=sys.stderr)
        sys.exit(1)

    content = changelog_file.read_text()

    # Pattern to match version sections
    # Format: ## [0.3.0] - 2026-01-17
    pattern = rf'## \[{re.escape(version)}\] .*?(?=\n## \[|\Z)'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print(f"Error: Version {version} not found in CHANGELOG.md", file=sys.stderr)
        sys.exit(1)

    entry = match.group(0).strip()

    # Remove the version header line to keep just the content
    lines = entry.split('\n')
    if lines and lines[0].startswith('## ['):
        content_lines = lines[1:]
    else:
        content_lines = lines

    # Remove leading blank lines
    while content_lines and not content_lines[0].strip():
        content_lines.pop(0)

    # Clean up: remove trailing blank lines
    while content_lines and not content_lines[-1].strip():
        content_lines.pop()

    return '\n'.join(content_lines)


def format_for_github_release(version: str, changelog_content: str) -> str:
    """
    Format the changelog content for GitHub release.

    Args:
        version: Version string
        changelog_content: Extracted changelog content

    Returns:
        Formatted release body
    """
    header = f"""## Pykrieg {version}

### Installation
```bash
pip install pykrieg=={version}
```

### What's New

"""

    footer = f"""

---

### Documentation
- [API Documentation](https://pykrieg.readthedocs.io/)
- [GitHub Repository](https://github.com/ssjmarx/pykrieg)
- [Protocol Specification](https://github.com/ssjmarx/pykrieg/blob/main/PROTOCOL-SPECIFICATION.md)
- [KFEN Specification](https://github.com/ssjmarx/pykrieg/blob/main/KFEN-SPECIFICATION.md)

### Installation
```bash
# Install from PyPI
pip install pykrieg

# Install with console support (includes mouse support)
pip install pykrieg[console]

# Install specific version
pip install pykrieg=={version}
```

### Quick Start
```python
from pykrieg import Board, Fen

# Create a board
board = Board()

# Add units
board.create_and_place_unit(5, 10, 'INFANTRY', 'NORTH')

# Move a unit
board.make_turn_move(5, 10, 6, 10)

# End turn
board.end_turn()
```

For more usage examples, see [USAGE.md](https://github.com/ssjmarx/pykrieg/blob/main/USAGE.md)
"""

    return header + changelog_content + footer.format(version=version)


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <version>", file=sys.stderr)
        print(f"Example: {sys.argv[0]} 0.3.0", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]

    # Validate version format (semantic versioning)
    if not re.match(r'^\d+\.\d+\.\d+', version):
        msg = f"Error: Invalid version format '{version}'. Expected semantic version (e.g., 0.3.0)"
        print(msg, file=sys.stderr)
        sys.exit(1)

    try:
        changelog_content = extract_changelog_entry(version)
        release_body = format_for_github_release(version, changelog_content)
        print(release_body)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
