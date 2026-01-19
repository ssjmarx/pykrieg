# Protocol constants and type definitions

from dataclasses import dataclass
from typing import List, Literal, Optional, Union

# Command types
UCICommand = Literal[
    "uci",
    "debug",
    "isready",
    "setoption",
    "ucinewgame",
    "position",
    "go",
    "stop",
    "quit",
    "status",
    "network",
    "victory",
    "phase",
    "retreats",
]

# Position types
PositionType = Literal[
    "kfen",
    "startpos",
]

# Phase types for protocol
ProtocolPhase = Literal[
    "movement",
    "battle",
]

# Option types
OptionType = Literal[
    "check",
    "spin",
    "combo",
    "button",
    "string",
]


@dataclass
class GoParameters:
    """Parameters for the 'go' command."""

    depth: Optional[int] = None
    nodes: Optional[int] = None
    movetime: Optional[int] = None  # milliseconds
    infinite: bool = False
    ponder: bool = False


@dataclass
class Score:
    """Score information for info messages."""

    cp: Optional[int] = None  # centipawns
    mate: Optional[int] = None  # moves to mate
    lowerbound: bool = False
    upperbound: bool = False


@dataclass
class InfoParameters:
    """Parameters for the 'info' response."""

    depth: Optional[int] = None
    seldepth: Optional[int] = None
    time: Optional[int] = None  # milliseconds
    nodes: Optional[int] = None
    score: Optional[Score] = None
    currmove: Optional[str] = None
    currmovenumber: Optional[int] = None
    hashfull: Optional[int] = None
    nps: Optional[int] = None  # nodes per second


@dataclass
class EngineOption:
    """Engine option definition."""

    name: str
    type: OptionType
    default: Union[str, int, bool, None]
    min: Optional[int] = None  # for spin type
    max: Optional[int] = None  # for spin type
    var: Optional[List[str]] = None  # for combo type


# Constants
UCI_IDENTIFICATION = "uci"
UCI_READY = "readyok"
UCI_READY_QUERY = "isready"
UCI_NEW_GAME = "ucinewgame"
UCI_QUIT = "quit"

# Pykrieg-specific constants
PYKRIEG_PROTOCOL_VERSION = "1.0"
