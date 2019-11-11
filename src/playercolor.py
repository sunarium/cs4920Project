from enum import IntEnum

class PlayerColor(IntEnum):
    WHITE = -1
    EMPTY = 0
    BLACK = 1
    def __str__(self):
        return self.name