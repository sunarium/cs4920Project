from .playercolor import PlayerColor
from . import config
from .exceptions import *
from .card import *
from typing import List
import random

class Player(object):
    def __init__(self, color:PlayerColor):
        self.color = color
        self.hand:List[Card] = []
        self.deck:List[Card] = []
        self.mana_pile:List[Card] = []
        self._init_deck()

        """tapped_card = Card("pawn", -1)
        tapped_card.tapped = True
        self.mana_pile.append(Card("pawn",-1))
        self.mana_pile.append(Card("pawn", -1))
        self.mana_pile.append(Card("pawn", -1))
        self.mana_pile.append(tapped_card)
        self.mana_pile.append(tapped_card)"""


    def debug_dump(self):
        print(f'''
        this is player {self.color}
        hand  { ','.join([str(c) for c in self.hand]) }
        mpile {','.join([str(c) for c in self.mana_pile])}
        mana  {self.turn_mana}
        ''')

    def _init_deck(self):
        for card_name, amount in config.DECK_AMOUNT.items():
            self.deck += [PieceCard(card_name, self.color)] * amount
        random.shuffle(self.deck)

    def on_turn_end(self):
        # hook
        # try not to use this one for consistency (use on_turn_start instead)
        pass

    def on_turn_start(self):
        # draw a card
        self.draw_card()
        # untap all cards
        for c in self.mana_pile:
            c.tapped = True

    def draw_card(self):
        if len(self.hand) > config.HAND_SIZE:
            raise IllegalPlayerActionError("Hand full")
        card = random.choice(self.deck)
        self.deck.remove(card)
        self.hand.append(card)
        return card

    @property
    def turn_mana(self):
        # https://stackoverflow.com/a/2900105
        # num of cards that are untapped
        return sum(1 for c in self.mana_pile if not c.tapped)

    @property
    def max_mana(self):
        return len(self.mana_pile)

    def place_to_mana_pile(self, index):
        try:
            card = self.hand[index]
        except IndexError:
            print(index)
            raise IllegalCardSelection
        self.hand.remove(card)
        self.mana_pile.append(card)

    def play_card(self, index, target, board):
        try:
            card = self.hand[index]
        except IndexError:
            raise IllegalCardSelection

        cost = config.MANA_COST[card.name]
        if self.turn_mana < cost:
            raise IllegalPlayerActionError('Insufficient mana')
        # take mana cost
        # tap cards from left to right
        tapped = 0
        for c in self.mana_pile:
            if not c.tapped:
                c.tapped = True
                tapped += 1
            if tapped == cost:
                break

        # play the card
        self.hand.remove(card)
        card.played(board, target)
