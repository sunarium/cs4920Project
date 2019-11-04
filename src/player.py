from .playercolor import PlayerColor
from . import config
from .exceptions import *
from .card import *
import random

class Player(object):
    def __init__(self, color:PlayerColor):
        self.color = color
        self.hand = []
        self.deck = []
        self.mana_pile = []
        self.turn_mana = config.INIT_MANA
        self._init_deck()

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
        # hook

        # clear mana
        self.turn_mana = config.INIT_MANA

    def draw_card(self):
        if len(self.hand) > config.HAND_SIZE:
            raise IllegalPlayerActionError("Hand full")
        card = random.choice(self.deck)
        self.deck.remove(card)
        self.hand.append(card)
        return card

    def tap(self, index):
        try:
            card = self.mana_pile[index]
        except IndexError:
            raise IllegalCardSelection
        if card.tapped: # already tapped
            raise IllegalCardSelection
        card.tapped = True
        self.turn_mana += config.MANA_GAIN[card.name]

    def untap(self, index):
        try:
            card = self.mana_pile[index]
        except IndexError:
            raise IllegalCardSelection
        if not card.tapped: # not tapped
            raise IllegalCardSelection
        card.tapped = False
        self.turn_mana -= config.MANA_GAIN[card.name]

    def place_to_mana_pile(self, index):
        try:
            card = self.hand[index]
        except IndexError:
            raise IllegalCardSelection
        self.hand.remove(card)
        self.mana_pile.append(card)

    def play_card(self, index, target, board):
        try:
            card = self.hand[index]
        except IndexError:
            raise IllegalCardSelection
        if self.turn_mana < config.MANA_COST[card.name]:
            raise IllegalPlayerActionError('Insufficient mana')
        self.hand.remove(card)
        self.turn_mana -= config.MANA_COST[card.name]
        card.played(board, target)
