from card import *
from collections import deque
from random import shuffle

class Player:

    def __init__(self):
        self.deck = deque()
        self.hand = []
        self.mana = []

        for i in range(23):
            new = Card("pawn")
            self.deck.append(new)

        for i in range(6):
            new = Card("rook")
            self.deck.append(new)

        for i in range(9):
            new = Card("knight")
            self.deck.append(new)

        for i in range(9):
            new = Card("bishop")
            self.deck.append(new)

        for i in range(3):
            new = Card("queen")
            self.deck.append(new)

        shuffle(self.deck)
        
        for i in range(6):
            self.draw()

    def draw(self):
        self.hand.append(self.deck.popleft())
