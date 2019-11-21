from .playercolor import PlayerColor
from .piece import Piece
from typing import List
from pygame import Vector2
from typing import Tuple, Union

INITIAL_POSITION_BLACK = {
    'pawn': [
        (0, 1),
        (1, 1),
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1),
        (6, 1),
        (7, 1),
    ],
    'rook': [
        (0, 0),
        (7, 0)
    ],
    'knight': [
        (1, 0),
        (6, 0)
    ],
    'bishop': [
        (2, 0),
        (5, 0)
    ],
    'queen': (3, 0),
    'king': (4, 0)

}

INITIAL_POSITION_WHITE = {
    'pawn': [
        (0, 6),
        (1, 6),
        (2, 6),
        (3, 6),
        (4, 6),
        (5, 6),
        (6, 6),
        (7, 6),
    ],
    'rook': [
        (0, 7),
        (7, 7)
    ],
    'knight': [
        (1, 7),
        (6, 7)
    ],
    'bishop': [
        (2, 7),
        (5, 7)
    ],
    'queen': [(3, 7)],
    'king': [(4, 7)]

}

class Card(object):
    def __init__(self, name:str, owner:PlayerColor):
        self.name = name
        self.owner = owner
        self.tapped = False
        if self.owner == PlayerColor.WHITE:
            self.startPos = INITIAL_POSITION_WHITE[self.name]
        else:
            self.startPos = INITIAL_POSITION_BLACK[self.name]

    def played(self, board, target):
        pass

    def legal_start(self) -> List[Vector2]:
        sList = []
        for v in self.startPos:
            v = Vector2(v)
            print(v.x)
            sList.append(v)
        return sList

    def __str__(self):
        return f'Card(name={self.name}, owner={self.owner}, tapped={self.tapped})'

class PieceCard(Card):
    def __init__(self, name, owner):
        super().__init__(name, owner)

    def played(self, board, target):
        Piece(self.name, target, self.owner, board)

    def asset_name(self):
        return f'card_{self.name}_{"white" if self.owner == -1 else "black"}.png'