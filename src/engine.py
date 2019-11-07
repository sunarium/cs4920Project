from typing import List, Tuple, Union
from pygame import Vector2
from enum import IntEnum, auto
import socket
import threading

from .board import Board
from .piece import Piece
from .exceptions import *
from .player import Player
from .playercolor import PlayerColor
from . import config

class GamePhase(IntEnum):
    MAIN = auto()
    MOVEMENT = auto()
    SECOND_MAIN = auto()


class NetworkStatus(IntEnum):
    INITIALIZED = auto()
    VALIDATING = auto()
    AWAITING_CONNECTION = auto()
    CONNECTING_TO_SERVER = auto()
    CONNECTED = auto()
    CONNECTION_CLOSED = auto()
    ERROR = auto()


class GameEngine(object):
    def __init__(self, debug=False):
        # game ends when a player loses his king
        self.game_ended = False
        self.winner = None

        # white goes first as per chess tradition
        self.current_player = Player(PlayerColor.WHITE)
        self.waiting_player = Player(PlayerColor.BLACK)
        self.board = Board()

        self.phase = GamePhase.MAIN

        # for display
        self.newly_drawn = None

        # turn flags
        self.has_placed_to_mana = False
        self.has_moved_piece = False

        # debug flag
        self.debug = debug

        # initialize the game
        self.current_player.on_turn_start()
        Piece("king", Vector2(4, 0), -1, self.board)
        Piece("king", Vector2(4, 7), 1, self.board)

    def debug_dump(self):
        if not self.debug:
            return
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
    # todo do we do the phase check in game engine or graphics engine?
    # for now we dont have phase checking.

    # recouperation phase
    # player tap a card in mana pile for mana
    # raise exception if index out of range
    # edit: this now happens automatically
    # def tap(self, tapped_index:int):
    #     self.current_player.tap(tapped_index)

    # Strategy Phase
    # for generating visual clue of where to deploy a new piece.
    def valid_positions(self, card_index: int) -> List[Vector2]:
        pass

    # player playes a card in his hand to target on board.
    # if card is piece card, this action places the piece onto the board.
    # raise exception if illegal index or invalid target or insufficient mana
    def play_card(self, card_index: int, target: Union[Vector2, Tuple[int, int]]):
        if not self.phase == GamePhase.MAIN:
            raise IllegalPlayerActionError("you can only play card in main phase")
        self.current_player.play_card(card_index, target, self.board)

    # player places a card into mana pile. this action can only be performed once per turn.
    def place_to_mana_pile(self, card_index: int):
        if not self.phase == GamePhase.MAIN:
            raise IllegalPlayerActionError("you can only place card to mana in main phase")
        if not self.debug and self.has_placed_to_mana:
            raise IllegalPlayerActionError("already placed a card to mana before")
        self.current_player.place_to_mana_pile(card_index)
        self.has_placed_to_mana = True

    # valid targets to which pieces ON THE BOARD move
    # raises error if no owned piece at old_pos
    def valid_movement_targets(self, old_pos) -> List[Vector2]:
        piece = self.board.get_piece(old_pos)
        if not piece:
            raise IllegalPiecePosError
        return piece.get_legal_moves(self.board)

    # player can move a piece once per turn(?)
    # raises error if
    #   - no owned piece at old_pos
    #   - new pos is invalid
    def move_piece(self, old_pos: Union[Vector2, Tuple[int, int]], new_pos: Union[Vector2, Tuple[int, int]]):
        if not self.debug and self.current_player.has_moved_piece:
            raise IllegalPlayerActionError("already moved a piece before")

        if not self.phase == GamePhase.MOVEMENT:
            raise IllegalPlayerActionError("you can only move pieces in movement phase")

        piece = self.board.get_piece(old_pos)
        # check movement legality
        if not piece or new_pos not in piece.get_legal_moves(self.board) or piece.newly_placed:
            raise IllegalPlayerActionError("cant move there")
        piece.move_to(new_pos)
        self.current_player.has_moved_piece = True

        # enemy piece capturing
        captured_piece = self.board.get_piece(new_pos)
        if captured_piece:  # captured
            self.board.remove_at(new_pos)

        # if king is captured, player made this move wins
        if captured_piece.name == 'king':
            self.winner = self.current_player
            self.game_ended = True

    def _turn_switch(self):
        self.board.on_turn_change()
        self.current_player.on_turn_end()
        self.has_placed_to_mana = False
        self.has_moved_piece = False
        self.current_player, self.waiting_player = self.waiting_player, self.current_player
        self.current_player.on_turn_start()
        self.newly_drawn = self.current_player.draw_card()

    # called when player end this phase
    def phase_change(self):
        if self.phase == GamePhase.SECOND_MAIN:
            self.phase = GamePhase.MAIN
            self._turn_switch()
        else:
            self.phase += 1


class LocalGameEngine(GameEngine):
    pass


class NetworkGameEngine:
    def __init__(self, debug=False):
        self.engine = GameEngine(debug)
        self.error_message = ''
        self.network_status = NetworkStatus.INITIALIZED
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_my_turn: bool = False

    def _handshake(self, addr):
        try:
            try:
                server_ip = socket.gethostbyname(addr)
            except socket.gaierror:
                raise NetworkError(msg='Invalid Hostname or ip')
            self.network_status = NetworkStatus.VALIDATING
            self.socket.settimeout(config.HANDSHAKE_TIMEOUT)
            try:
                self.socket.connect((server_ip, config.DEFAULT_PORT))
                self.socket.send(config.CLIENT_REQUEST)
                msg = self.socket.recv(1024)
            except socket.timeout:
                raise NetworkError(msg='handshake timeout')
            except ConnectionRefusedError:
                raise NetworkError(msg='connection refused')

            if msg.strip() != config.SERVER_RESPONSE:
                raise NetworkError(msg='server response do not match')
            self.network_status = NetworkStatus.CONNECTED
            self.socket.settimeout(0)  # disable timeout
            self.socket.setblocking(False)
            print('client: server connected')
        except NetworkError as e:
            self.network_status = NetworkStatus.ERROR
            self.error_message = e.msg

    def _await_handshake(self):
        self.socket.bind(('', config.DEFAULT_PORT))
        self.socket.listen(1)
        while True:
            _sock, addr = self.socket.accept()
            if _sock.recv(1024).strip() == config.CLIENT_REQUEST:
                print(f'got valid conn from {addr}')
                break
            else:
                _sock.close()
        self.socket.close()
        self.socket = _sock
        self.socket.send(config.SERVER_RESPONSE)
        self.network_status = NetworkStatus.CONNECTED
        self.socket.setblocking(False)
        print('server: client connected')

    # called if run as client
    def connect_to(self, server_addr: str):
        threading.Thread(target=self._handshake, args=(server_addr,)).start()

    # called if run as host
    def host_game(self):
        threading.Thread(target=self._await_handshake).start()
        self.is_my_turn = True

    def get_network_status(self):
        return self.network_status

    # for drawing
    def get_game_state(self):
        return self.engine.get_game_state()

    def check_opponent_move(self):
        try:
            opponent_move = self.socket.recv(1024)
            if opponent_move == b'':  # todo: discuss with gui team on how to handle this.
                self.network_status = NetworkStatus.ERROR
                self.error_message = 'socket closed'
                return
        except (socket.error, BlockingIOError):
            pass

        # todo: handle opponent move
        pass

    def on_game_start(self):
        pass
