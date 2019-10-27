from typing import Tuple, List, Union
import random
from pygame import Vector2
from .board import Board
from .piece import Piece
from .playercolor import PlayerColor
from . import config
from .exceptions import *

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
        # untaps
        for c in self.hand:
            c.tapped = False

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



class GameEngine(object):
    def __init__(self, debug=False):
        # game ends when a player loses his king
        self.game_ended = False
        self.winner = None

        # white goes first as per chess tradition
        # self.turn = Player.WHITE
        self.current_player = Player(PlayerColor.WHITE) # might pass in a
        self.waiting_player = Player(PlayerColor.BLACK)
        self.board = Board()

        """
        0 = main phase
        1 = movement phase
        2 = 2nd main phase
        """
        self.phase = 0

        # turn flags
        self.has_placed_to_mana = False
        self.has_moved_piece = False

        #debug flag
        self.debug = debug

    def debug_dump(self):
        if not self.debug: return
        print('current player:')
        self.current_player.debug_dump()
        print('waiting player:')
        self.waiting_player.debug_dump()
        print('board:')
        # print(str(self.board))
        print(self.board)
        print(self.phase)

    def get_game_state(self):
        """
        used by graphics engine to render the game.
        things need to dump:
        - board state
        - player's hands
        - status of mana pile
        - both player's mana count(?)

        return a json(?) representation of game state.
        """
        pass

    # functions that alters game state; called by graphics engine
    # do we do the phase check in game engine or graphics engine?
    # for now we dont have phase checking.

    # recouperation phase
    # player tap a card in mana pile for mana
    # raise exception(?) if index out of range
    def tap(self, tapped_index:int):
        self.current_player.tap(tapped_index)

    def untap(self, tapped_index:int):
        self.current_player.untap(tapped_index)

    # draw a card from deck into hand
    # return the card drawn
    # error if hand full
    def draw_card(self) -> Card:
        return self.current_player.draw_card()

    # Strategy Phase

    # for generating visual clue of where to deploy a new piece.
    def valid_positions(self, card_index:int) -> List[Vector2]:
        # todo: it is needed for text engine?
        pass

    # player playes a card in his hand to target on board.
    # if card is piece card, this action places the piece onto the board.
    # raise exception if illegal index or invalid target or insufficient mana
    def play_card(self, card_index:int, target:Union[Vector2, Tuple[int, int]]):
        self.current_player.play_card(card_index, target, self.board)

    # player places a card into mana pile. this action can only be performed once per turn.
    def place_to_mana_pile(self, card_index:int):
        if not self.debug and self.has_placed_to_mana:
            raise IllegalPlayerActionError("already placed a card to mana before")
        self.current_player.place_to_mana_pile(card_index)
        self.has_placed_to_mana = True

    # valid targets to which pieces ON THE BOARD move
    # raises error if no owned piece at old_pos
    def valid_movement_targets(self, old_pos) -> List[Vector2]:
        piece = self.board.get_piece(old_pos)
        if not piece :
            raise IllegalPiecePosError
        return piece.get_legal_moves(self.board)

    # player can move a piece once per turn(?)
    # raises error if
    #   - no owned piece at old_pos
    #   - new pos is invalid
    def move_piece(self, old_pos:Union[Vector2, Tuple[int, int]], new_pos:Union[Vector2, Tuple[int, int]]):
        if not self.debug and self.current_player.has_moved_piece:
            raise IllegalPlayerActionError("already moved a piece before")

        piece = self.board.get_piece(old_pos)
        if not piece or new_pos not in piece.get_legal_moves(self.board):
            raise IllegalMoveError
        piece.move_to(new_pos)

        if self.board.get_piece(new_pos): # captured
            self.board.remove_at(new_pos)

        self.current_player.has_moved_piece = True

    # called when player indicates to end his turn
    def turn_switch(self):
        self.phase = 0
        self.current_player.on_turn_end()
        self.has_placed_to_mana = False
        self.has_moved_piece = False
        self.current_player, self.waiting_player = self.waiting_player, self.current_player
        self.current_player.on_turn_start()

    def phase_change(self):
        self.phase += 1
        if self.phase > 2:
            self.turn_switch()