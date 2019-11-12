
from typing import List
from pygame import Vector2
from typing import Tuple, Union

from src import config
from src.playercolor import PlayerColor



class Piece():
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

    INITIAL_POSITION = {
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

    def __init__(self, name: str, pos: Tuple[int, int], owner: PlayerColor, board = None) -> object:
        self.pos:Vector2 = Vector2(pos)
        self.owner = owner
        self.name = name
        if self.name != 'pawn':
            self._movement_vector = self.MOVEMENT_VECTOR[name]
        self.has_moved = False
        if board:
            self.board = board
            board.add_piece(self)
        self.newly_placed = True

    def get_legal_moves(self, board=None) -> List[Vector2]:
        if not board:
            board = self.board
        if self.name == 'pawn':
            if self.has_moved:
                return [Vector2(self.pos[0], self.pos[1] + self.owner)]
            else:
                return [Vector2(self.pos[0], self.pos[1] + self.owner),
                        Vector2(self.pos[0], self.pos[1] + 2 * self.owner)]
        else:
            mlist = []
            for v in self._movement_vector:
                v = Vector2(v)
                for i in range(1, config.BOARD_SIZE):
                    if self.name == 'king' and i > 1: break
                    if board.in_board_range(self.pos + i * v) and \
                        board.get_owner(self.pos + i * v) == PlayerColor.EMPTY:
                        mlist.append(self.pos + i * v)
                    else:
                        if board.in_board_range(self.pos + i * v) and \
                                board.get_owner(self.pos + i * v) != self.owner:
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

# if __name__ == '__main__':
#     b = Board()
#     p = Piece('pawn', (1,3), 1, b)
#     p1 = Piece('rook', (1,1), 1, b)
#     p2 = Piece('queen', (0,3), 1, b)
