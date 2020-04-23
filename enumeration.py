from enum import Enum, IntEnum, unique


@unique
class Method(Enum):
    INFECT = 1
    EXPLOIT = 2
    OVERHEAR = 3
    OVERLOAD = 4
    SCAN = 5
    PATCH = 6
    NOP = 7


@unique
class Result(Enum):
    WIN = 1
    LOSE = 2
    DRAW = 3
    FASTER_WINNER = 4


@unique
class Advantage(Enum):
    GAIN = 1
    LOST = 2
    NO_CHANGE = 3


@unique
class RoundWinner(IntEnum):
    DRAW = 0
    BOT_1 = 1
    BOT_2 = 2


@unique
class RoundAdvantage(IntEnum):
    TIME = 0
    BOT_1 = 1
    BOT_2 = 2
