from pygame import Vector2
from typing import Tuple, Union
from .exceptions import *

class Board(object):
    def __init__(self):
        self.pieces = []
        # todo:initialize king?

    def get_piece(self, pos:Union[Vector2, Tuple[int, int]]):
        for p in self.pieces:
            if p.pos == pos:
                return p

    def add_piece(self, piece):
        if self.get_piece(piece.pos):
            raise IllegalPiecePosError
        self.pieces.append(piece)

    def remove_at(self, pos:Union[Vector2, Tuple]):
        piece = self.get_piece(pos)
        if not piece:
            raise IllegalPiecePosError
        self.pieces.remove(piece)

    def __str__(self):
        return ','.join([str(p) for p in self.pieces])