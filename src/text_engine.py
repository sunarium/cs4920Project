import logging
from enum import IntEnum
from typing import Tuple, List
from abc import ABC, abstractmethod

import src.config as config

class Player(IntEnum):
    WHITE = -1
    BLACK = 1

class Piece(ABC):
    def __init__(self, location:Tuple[int, int], owner:Player):
        self.location = location
        self.owner = owner

    @abstractmethod
    def get_legal_moves(self, board) -> List[Tuple[int, int]]:
        pass

    def move_to(self, location):
        self.location = location

class Pawn(Piece):
    def __init__(self, location:Tuple[int, int], owner:Player):
        super(Pawn, self).__init__(location, owner)
        self.has_moved = False

    def get_legal_moves(self, board) -> List[Tuple[int, int]]:
        if self.has_moved:
            return [(self.location[0], self.location[1] + self.owner)]
        else:
            return [(self.location[0], self.location[1] + self.owner),
                    (self.location[0], self.location[1] + 2 * self.owner)]

    def move_to(self, location):
        super(Pawn, self).move_to(location)
        self.has_moved = True

class Rook(Piece):


# class GameEngine(object):
#     def __init__(self):
#         self.this_turn = Player.WHITE