from pygame import Vector2
from typing import Tuple, Union
#from src.piece import Piece

from src.exceptions import *
from src.playercolor import PlayerColor
from src import config

class Board(object):
    def __init__(self):
        self.pieces = []

    def get_piece(self, pos:Union[Vector2, Tuple[int, int]]):
        for p in self.pieces:
            if p.pos == pos:
                return p

    def in_board_range(self, pos:Union[Vector2, Tuple]):
        return 0 <= pos[0] < config.BOARD_SIZE and 0 <= pos[1] < config.BOARD_SIZE

    def add_piece(self, piece):
        if self.get_piece(piece.pos):
            raise AttributeError(f"{piece.pos} is occupied")
        self.pieces.append(piece)

    def remove_at(self, pos:Union[Vector2, Tuple]):
        piece = self.get_piece(pos)
        if not piece:
            raise IllegalPiecePosError
        self.pieces.remove(piece)

    def get_owner(self, pos:Union[Vector2, Tuple]):
        p = self.get_piece(pos)
        if not p:
            return PlayerColor.EMPTY
        return p.owner

    def on_turn_change(self):
        for p in self.pieces:
            p.newly_placed = False

    def __str__(self):
        return ','.join([str(p) for p in self.pieces])