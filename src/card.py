from .playercolor import PlayerColor
from .piece import Piece

class Card(object):
    def __init__(self, name:str, owner:PlayerColor):
        self.name = name
        self.owner = owner
        self.tapped = False

    def played(self, board, target):
        pass

    def __str__(self):
        return f'Card(name={self.name}, owner={self.owner}, tapped={self.tapped})'

class PieceCard(Card):
    def __init__(self, name, owner):
        super().__init__(name, owner)

    def played(self, board, target):
        Piece(self.name, target, self.owner, board)