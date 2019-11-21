
from typing import List
from pygame import Vector2
from typing import Tuple, Union

from src import config
from src.playercolor import PlayerColor

MOVEMENT_VECTOR = {
    'rook': [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1)
    ],
    'bishop': [
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1)
    ],
    'knight': [
        (1, 2),
        (1, -2),
        (-1, 2),
        (-1, -2),
        (2, 1),
        (2, -1),
        (-2, 1),
        (-2, -1),
    ],
    'queen': [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1)
    ],
    'king': [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1)
    ]
}



class Piece():
    def __init__(self, name: str, pos: Tuple[int, int], owner: PlayerColor, board = None) -> object:
        self.pos:Vector2 = Vector2(pos)
        self.owner = owner
        self.name = name
        if self.name != 'pawn':
            self._movement_vector = MOVEMENT_VECTOR[name]
        self.has_moved = False
        if board:
            self.board = board
            board.add_piece(self)
        self.newly_placed = True


    def get_legal_moves(self, board=None) -> List[Vector2]:
        if not board:
            board = self.board
        mlist = []
        if self.name == 'pawn':
            # movement
            if self.board.get_owner(self.pos + (0, self.owner)) == PlayerColor.EMPTY:
                mlist.append(self.pos + (0, self.owner))
            if not self.has_moved and board.get_owner(self.pos+(0, 2*self.owner)) == PlayerColor.EMPTY:
                mlist.append(self.pos+(0, 2*self.owner))
            # capture
            if board.get_owner(self.pos + (1, self.owner)) + self.owner == 0:
                mlist.append(self.pos + (1, self.owner))
            if board.get_owner(self.pos + (-1, self.owner)) + self.owner == 0:
                mlist.append(self.pos + (-1, self.owner))
            return list(filter(self.board.in_board_range, mlist))
        else:
            for v in self._movement_vector:
                v = Vector2(v)
                for i in range(1, config.BOARD_SIZE):
                    if self.name in ('king', 'knight') and i > 1: break
                    if not board.in_board_range(self.pos + i * v): break
                    owner = board.get_owner(self.pos + i * v)
                    if owner == PlayerColor.EMPTY:
                        mlist.append(self.pos + i * v)
                    elif owner != self.owner:
                        mlist.append(self.pos + i * v)
                        break
            return mlist

    def move_to(self, pos):
        self.has_moved = True
        self.pos = Vector2(pos)

    def __str__(self):
        return f'Piece(name={self.name}, pos={self.pos})'

    def asset_name(self) -> str:
        return f'piece_{self.name}_{"white" if self.owner == -1 else "black"}.png'
