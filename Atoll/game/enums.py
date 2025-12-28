from enum import IntEnum

class CellType(IntEnum):
    OUT = 0
    EMPTY = 1
    BLACK = 2
    WHITE = 3
    MARK = 4

class CellState(IntEnum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2

class GameMode(IntEnum):
    PVP = 0
    AI = 1

class Player(IntEnum):
    WHITE = 0
    BLACK = 1