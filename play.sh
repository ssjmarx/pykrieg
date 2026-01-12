#!/bin/bash
# Play Pykrieg - Launch console game
#
# This script launches the Pykrieg console interface for interactive gameplay.
#
# Usage:
#   ./play.sh [options]
#
# Options:
#   --rich, -r     Force rich mode (Unicode + colors)
#   --compat, -c    Force compatibility mode (ASCII only)
#   --help, -h      Show this help message

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default: auto-detect mode
MODE_FLAG=""

# Parse command line arguments
for arg in "$@"; do
    case "$arg" in
        --rich|-r)
            MODE_FLAG="--mode=rich"
            ;;
        --compat|-c)
            MODE_FLAG="--mode=compat"
            ;;
        --help|-h)
            echo "Play Pykrieg - Launch console game"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --rich, -r     Force rich mode (Unicode + colors)"
            echo "  --compat, -c    Force compatibility mode (ASCII only)"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0              Auto-detect terminal capabilities"
            echo "  $0 --rich       Force rich mode"
            echo "  $0 --compat      Force compatibility mode"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
elif [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Check if pykrieg is installed
if ! python -c "import pykrieg" 2>/dev/null; then
    echo "✗ Pykrieg not found. Installing..."
    pip install -e . || pip install pykrieg
fi

# Launch the game
echo ""
echo "═════════════════════════════════════════════════════════"
echo "  Pykrieg - Guy Debord's Le Jeu de la Guerre"
echo "═════════════════════════════════════════════════════════"
echo ""
python -m pykrieg.console $MODE_FLAG
