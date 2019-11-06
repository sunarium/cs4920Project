from typing import List, Tuple, Union
from pygame import Vector2
from enum import IntEnum
import socket
import threading

from .board import Board
from .card import *
from .exceptions import *
from .piece import Piece
from .player import Player
from .playercolor import PlayerColor
from . import config

class GamePhase(IntEnum):
    MAIN = 0
    MOVEMENT = 1
    SECOND_MAIN = 2

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

        self.phase = GamePhase.MAIN

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

    def get_curr_deck_size(self):
        return len(self.current_player.deck)

    def get_curr_hand(self):
        return self.current_player.hand
    # functions that alters game state; called by graphics engine
    # do we do the phase check in game engine or graphics engine?
    # for now we dont have phase checking.

    # recouperation phase
    # player tap a card in mana pile for mana
    # raise exception if index out of range
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
        if not piece or new_pos not in piece.get_legal_moves(self.board): # check movement legality
            raise IllegalMoveError
        piece.move_to(new_pos)
        self.current_player.has_moved_piece = True

        # enemy piece capturing
        captured_piece:Piece = self.board.get_piece(new_pos)
        if captured_piece: # captured
            self.board.remove_at(new_pos)

        # if king is captured, player made this move wins
        if captured_piece.name == 'king':
            self.winner = self.current_player
            self.game_ended = True

    # called when player indicates to end his turn
    def turn_switch(self):
        self.current_player.on_turn_end()
        self.has_placed_to_mana = False
        self.has_moved_piece = False
        self.current_player, self.waiting_player = self.waiting_player, self.current_player
        self.current_player.on_turn_start()

    def phase_change(self):
        self.phase += 1
        if self.phase > 2:
            self.phase = 0
            self.turn_switch()

class LocalGameEngine(GameEngine):
    pass

class NetworkStatus(IntEnum):
    INITIALIZED = -1
    VALIDATING = 0
    AWAITING_CONNECTION = 1
    CONNECTING_TO_SERVER = 2
    CONNECTED = 3
    CONNECTION_CLOSED = 4
    ERROR = 5

class NetworkgameEngine(GameEngine):
    def __init__(self, debug=False, port=config.DEFAULT_PORT):
        super().__init__(debug)
        self.error_message = ''
        self.network_status = NetworkStatus.INITIALIZED
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.is_my_turn:bool = False

    def _handshake(self, addr):
        self.socket.settimeout(config.HANDSHAKE_TIMEOUT)
        self.socket.sendto(config.CLIENT_REQUEST, (addr, config.DEFAULT_PORT))
        try:
            msg, server_addr = self.socket.recvfrom(1024)
        except socket.timeout:
            self.network_status = NetworkStatus.ERROR
            self.error_message = 'handshake timeout'
            return
        else:
            print(msg, server_addr)
        if msg != config.SERVER_RESPONSE:
            self.network_status = NetworkStatus.ERROR
            self.error_message = 'server response do mot match'
            print(msg)
            return
        self.network_status = NetworkStatus.CONNECTED
        self.socket.settimeout(0) # disable timeout

    def _await_handshake(self):
        self.socket.bind(('', config.DEFAULT_PORT))
        msg = b''
        while msg != config.CLIENT_REQUEST:
            msg, client_addr = self.socket.recvfrom(1024)
        self.socket.sendto(config.SERVER_RESPONSE, client_addr)
        self.network_status = NetworkStatus.CONNECTED

    # called if run as client
    def connect_to(self, server_addr:str):
        # validate
        try:
            server_ip = socket.gethostbyname(server_addr)
        except socket.gaierror:
            self.network_status = NetworkStatus.ERROR
            self.error_message = 'Invalid Hostname or ip'
            return
        self.network_status = NetworkStatus.VALIDATING
        threading.Thread(target=self._handshake, args=(server_ip,)).start()

    # called if run as host
    def host_game(self):
        threading.Thread(target=self._await_handshake).start()

    def get_network_status(self):
        return self.network_status

