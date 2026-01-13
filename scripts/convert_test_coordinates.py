#!/usr/bin/env python3
"""
Automated script to convert spreadsheet coordinates from old format (A1)
to new format (1A) throughout test files and documentation.

This script converts the coordinate system to match Debord's original convention:
- Old: LETTERS + NUMBERS (e.g., "A1" where A=column, 1=row)
- New: NUMBERS + LETTERS (e.g., "1A" where 1=column, A=row)

Usage:
    python scripts/convert_test_coordinates.py [--dry-run] <file_or_directory> [...]

Examples:
    # Preview changes without modifying files
    python scripts/convert_test_coordinates.py --dry-run tests/

    # Apply changes to test files
    python scripts/convert_test_coordinates.py tests/

    # Apply changes to specific file
    python scripts/convert_test_coordinates.py tests/test_coordinates.py

    # Apply changes to documentation
    python scripts/convert_test_coordinates.py docs/
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict

# Import Board class for conversion functions
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def convert_coordinate(coord: str) -> str:
    """Convert old spreadsheet coordinate to new format.

    Args:
        coord: Old format coordinate (e.g., "A1", "Y20")

    Returns:
        New format coordinate (e.g., "1A", "25T")

    Examples:
        "A1" → "1A"
        "Y20" → "25T"
        "AA10" → "27J"
        "G7" → "7G"
    """
    try:
        # Parse using old method (before board.py changes)
        # We need to manually parse since we're updating the board methods
        col_letters = ''
        row_number = ''
        i = 0
        while i < len(coord) and coord[i].isalpha():
            col_letters += coord[i]
            i += 1
        row_number = coord[i:]

        # Parse column (A=0, B=1, etc.)
        col_index = 0
        for char in col_letters:
            col_index = col_index * 26 + (ord(char.upper()) - ord('A') + 1)
        col_index -= 1

        # Parse row (number)
        row_index = int(row_number) - 1

        # Now convert using the NEW method
        # Column as number, row as letter
        col_number = col_index + 1
        row_letters_list = []
        temp_row = row_index + 1
        while temp_row > 0:
            temp_row -= 1
            row_letters_list.insert(0, chr(ord('A') + temp_row % 26))
            temp_row //= 26

        return f"{col_number}{''.join(row_letters_list)}"
    except (ValueError, IndexError):
        # If conversion fails, return original
        return coord


def convert_file(filepath: Path, dry_run: bool = False) -> Dict[str, int]:
    """Convert coordinates in a single file.

    Args:
        filepath: Path to file to convert
        dry_run: If True, preview changes without modifying file

    Returns:
        Dictionary with conversion statistics
    """
    content = filepath.read_text()
    original_content = content

    # Pattern 1: Standalone coordinates in quotes (e.g., "A1", 'Y20')
    # Match patterns like "A1", 'A1', or any quoted spreadsheet coordinate
    pattern1 = r'(["\'])([A-Z]+[0-9]+)\1'

    stats = {
        'coordinates_converted': 0,
        'total_matches': 0,
        'changes': []
    }

    def replace_coord(match):
        """Replace coordinate while preserving quotes."""
        quote_char = match.group(1)
        old_coord = match.group(2)
        new_coord = convert_coordinate(old_coord)

        stats['coordinates_converted'] += 1
        stats['total_matches'] += 1
        stats['changes'].append(f"{old_coord} → {new_coord}")

        return f'{quote_char}{new_coord}{quote_char}'

    # Apply pattern
    content = re.sub(pattern1, replace_coord, content)

    # Write changes
    if content != original_content:
        if dry_run:
            print(f"\n{filepath} (DRY RUN):")
            for change in stats['changes']:
                print(f"  {change}")
        else:
            # Create backup
            backup_path = filepath.with_suffix(filepath.suffix + '.bak')
            backup_path.write_text(original_content)
            # Write new content
            filepath.write_text(content)
            print(f"{filepath}: {stats['coordinates_converted']} coordinates converted")

    return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert spreadsheet coordinates from old format (A1) to new format (1A)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes without modifying files
  python scripts/convert_test_coordinates.py --dry-run tests/

  # Apply changes to test files
  python scripts/convert_test_coordinates.py tests/

  # Apply changes to documentation
  python scripts/convert_test_coordinates.py docs/
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        'paths',
        nargs='+',
        type=Path,
        help='File or directory paths to process'
    )

    args = parser.parse_args()

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No files will be modified")
        print("=" * 60)

    total_stats = {
        'coordinates_converted': 0,
        'total_matches': 0,
        'files_processed': 0,
        'files_with_changes': 0
    }

    for path in args.paths:
        if not path.exists():
            print(f"Warning: Path does not exist: {path}", file=sys.stderr)
            continue

        if path.is_file():
            files = [path]
        else:
            # Find all Python, RST, and Markdown files
            files = []
            for pattern in ['*.py', '*.rst', '*.md']:
                files.extend(path.rglob(pattern))

        for filepath in files:
            if any(
                exclude in str(filepath)
                for exclude in ['.git', '__pycache__', '_build', 'htmlcov']
            ):
                continue

            stats = convert_file(filepath, args.dry_run)

            if stats['coordinates_converted'] > 0:
                total_stats['files_with_changes'] += 1

            total_stats['coordinates_converted'] += stats['coordinates_converted']
            total_stats['total_matches'] += stats['total_matches']
            total_stats['files_processed'] += 1

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files scanned: {total_stats['files_processed']}")
    print(f"Files with changes: {total_stats['files_with_changes']}")
    print(f"Total coordinates converted: {total_stats['coordinates_converted']}")

    if args.dry_run:
        print("\n(DRY RUN - No files were modified)")
        print("To apply changes, run without --dry-run flag")


if __name__ == '__main__':
    main()
