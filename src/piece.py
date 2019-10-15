
from typing import Tuple, List
from abc import ABC, abstractmethod
from pygame import Vector2
from typing import Tuple, Union
from . import config
from .playercolor import PlayerColor
from .board import Board
from .exceptions import *



class Piece(ABC):

    def __init__(self, pos:Union[Vector2, Tuple], owner:PlayerColor):
        self.pos:Vector2 = Vector2(pos)
        self.owner = owner
        self.name = 'generic piece'

    def can_move_to(self, pos, board):
        if pos[0] < 0 or pos[0] >= config.BOARD_SIZE \
        or pos[1] < 0 or pos[1] >= config.BOARD_SIZE:
            return False
        return not board.get_piece(Vector2(pos))

    @abstractmethod
    def get_legal_moves(self, board:Board) -> List[Vector2]:
        pass

    def move_to(self, pos):
        self.pos = pos

    def __str__(self):
        return f'Piece(name={self.name}, pos={self.pos})'

class Pawn(Piece):
    def __init__(self, pos:Vector2, owner:PlayerColor):
        super().__init__(pos, owner)
        self.name = 'pawn'
        self.has_moved = False

    def get_legal_moves(self, board:Board) -> List[Vector2]:
        # fixme
        if self.has_moved:
            return [Vector2(self.pos[0], self.pos[1] + self.owner)]
        else:
            return [Vector2(self.pos[0], self.pos[1] + self.owner),
                    Vector2(self.pos[0], self.pos[1] + 2 * self.owner)]

    def move_to(self, location):
        super(Pawn, self).move_to(location)
        self.has_moved = True

class Rook(Piece):
    def __init__(self, pos:Vector2, owner:PlayerColor):
        super().__init__(pos, owner)
        self.name = 'rook'

    def get_legal_moves(self, board:Board) -> List[Vector2]:
        # fixme
        x, y = self.pos
        valid_pos = []
        check_x = True
        check_y = True
        for i in range(1, config.BOARD_SIZE):
            if check_y and self.can_move_to((x, y + i), board):
                valid_pos.append(Vector2(x, y + i))
            else:  # blocked by friendly piece, cannot move furthur
                check_y = False

            if check_x and self.can_move_to((x + i, y), board):
                valid_pos.append(Vector2(x + i, y))
            else:
                check_x = False

        check_x = True
        check_y = True
        for i in range(-1, -config.BOARD_SIZE):
            if check_y and self.can_move_to((x, y + i), board):
                valid_pos.append(Vector2(x, y + i))
            else:
                check_y = False

            if check_x and self.can_move_to((x + i, y), board):
                valid_pos.append(Vector2(x + i, y))
            else:
                check_x = False
        return valid_pos

class Queen(Piece):
    def __init__(self, pos:Vector2, owner:PlayerColor):
        super().__init__(pos, owner)
        self.name = 'queen'

    def get_legal_moves(self, board:Board) -> List[Vector2]:
        # Im so sorry
        # fixme
        x, y = self.pos
        valid_pos = []
        check_x = True
        check_y = True
        check_dia = True
        for i in range(1, config.BOARD_SIZE):
            if check_y and self.can_move_to((x, y + i), board):
                valid_pos.append(Vector2(x, y + i))
            else: # blocked by piece, cannot move furthur
                if board.get_piece(Vector2(x, y + i)) \
                    and board.get_piece(Vector2(x, y + i)).owner != self.owner:
                    valid_pos.append(Vector2(x, y + i))
                check_y = False

            if check_x and self.can_move_to((x + i, y), board):
                valid_pos.append(Vector2(x + i, y))
            else:
                check_x = False

            if check_dia and self.can_move_to((x + i, y + i), board):
                valid_pos.append(Vector2(x + i, y + i))
            else:
                check_dia = False
        check_x = True
        check_y = True
        check_dia = True
        for i in range(-1, -config.BOARD_SIZE, -1):
            if check_y and self.can_move_to((x, y + i), board):
                valid_pos.append(Vector2(x, y + i))
            else:
                check_y = False

            if check_x and self.can_move_to((x + i, y), board):
                valid_pos.append(Vector2(x + i, y))
            else:
                check_x = False

            if check_dia and self.can_move_to((x + i, y + i), board):
                valid_pos.append(Vector2(x + i, y + i))
            else:
                check_dia = False
        return valid_pos

class King(Piece):
    def __init__(self, pos:Vector2, owner:PlayerColor):
        super().__init__(pos, owner)
        self.name = 'king'

    def get_legal_moves(self, board:Board) -> List[Vector2]:
        x, y = self.pos
        valid_pos = []
        # check all 8 directions
        for i in range(-1, 2):
            if i == 0: continue
            if self.can_move_to((x, y + i), board):
                valid_pos.append(Vector2(x, y + i))
            if self.can_move_to((x + i, y), board):
                valid_pos.append(Vector2(x + i, y))
            if self.can_move_to((x + i, y + i), board):
                valid_pos.append(Vector2(x + i, y + i))
        return valid_pos

# this dict is for dynamically creating subclasses without the factory bullshit.
# use case:
# name:str = 'queen'
# q:Queen = PIECES[name](pos, owner)
# (at this point q is of Queen class and has been correctly constructed)
# fixme: need a better name
PIECES = {
    'pawn': Pawn,
    'rook': Rook,
    'queen': Queen,
    'king': King
}