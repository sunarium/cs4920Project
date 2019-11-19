from typing import List, Tuple, Union
from pygame import Vector2
from enum import IntEnum, auto
import socket
import threading
import queue

from .board import Board
from .piece import Piece
from .exceptions import *
from .player import Player
from .playercolor import PlayerColor
from . import config

class GamePhase(IntEnum):
    MAIN = 0
    MOVEMENT = 1
    SECOND_MAIN = 2


class NetworkStatus(IntEnum):
    INITIALIZED = auto()
    AWAITING_CONNECTION = auto()
    CONNECTING_TO_SERVER = auto()
    CONNECTED = auto()
    CONNECTION_CLOSED = auto()
    ERROR = auto()

    def __str__(self):
        if self.value == self.AWAITING_CONNECTION:
            return 'Awaiting connection...'
        elif self.value == self.CONNECTING_TO_SERVER:
            return 'Connecting...'
        elif self.value == self.CONNECTED:
            return 'Connected.'
        elif self.value == self.ERROR:
            return 'Error: '
        else:
            return ''


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

        #setup game state
        for i in range(0,6):
            self.current_player.draw_card()
            self.waiting_player.draw_card()

        # for display
        self.newly_drawn = None

        # turn flags
        self.has_placed_to_mana = False
        self.has_moved_piece = False

        # debug flag
        self.debug = debug
        if debug:
            self.phase = 0
            self.board.on_turn_change()
            self.board.pieces.append(Piece('rook',  (0, 0), PlayerColor.WHITE, self.board))
            self.board.pieces.append(Piece('knight', (1, 0), PlayerColor.WHITE, self.board))
            self.board.pieces.append(Piece('bishop', (2, 0), PlayerColor.WHITE, self.board))
            print(self.board.pieces)

        # initialize the game
        self.current_player.on_turn_start()
        Piece("king", Vector2(4, 7), -1, self.board)
        Piece("king", Vector2(4, 0), 1, self.board)
        self.board.on_turn_change()

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
    def move_piece(self, piece: Piece, new_pos: Union[Vector2, Tuple[int, int]]):
        # check movement legality
        if new_pos not in piece.get_legal_moves(self.board) or piece.newly_placed:
            raise IllegalPlayerActionError("cant move there")

        # enemy piece capturing
        captured_piece = self.board.get_piece(new_pos)
        if captured_piece:  # captured
            self.board.remove_at(new_pos)

        piece.move_to(new_pos)
        self.has_moved_piece = True

        # if king is captured, player made this move wins
        if captured_piece and captured_piece.name == 'king':
            self.winner = self.current_player
            self.game_ended = True

    # if current player can move piece at pos, return piece
    # otherwise return None
    def grab_piece(self, pos):
        if not self.debug and (self.has_moved_piece or self.phase != GamePhase.MOVEMENT):
            return None
        piece = self.board.get_piece(pos)
        if piece and piece.owner == self.current_player.color and not piece.newly_placed:
            return piece

    def turn_switch(self):
        self.board.on_turn_change()
        self.current_player.on_turn_end()
        self.has_placed_to_mana = False
        self.has_moved_piece = False
        self.current_player, self.waiting_player = self.waiting_player, self.current_player
        self.current_player.on_turn_start()
        # self.newly_drawn = self.current_player.draw_card()

    # called when player end this phase
    def phase_change(self):
        if self.phase == GamePhase.SECOND_MAIN:
            self.phase = GamePhase.MAIN
            self.turn_switch()
        else:
            self.phase += 1


class NetworkGameEngine:
    def __init__(self, debug=False):
        self.engine = GameEngine(debug)
        self.error_message = ''
        self.network_status = NetworkStatus.INITIALIZED
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.queue = queue.Queue()
        self.is_my_turn: bool = False

    def reset(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.network_status = NetworkStatus.INITIALIZED
        self.error_message = ''

    def _handshake(self, addr):
        try:
            try:
                server_ip = socket.gethostbyname(addr)
            except socket.gaierror:
                raise NetworkError('Invalid Hostname or ip')
            self.socket.settimeout(config.HANDSHAKE_TIMEOUT)
            try:
                self.socket.connect((server_ip, config.DEFAULT_PORT))
                self.socket.send(config.CLIENT_REQUEST)
                msg = self.socket.recv(1024)
            except socket.timeout:
                raise NetworkError('handshake timeout')
            except ConnectionRefusedError:
                raise NetworkError('connection refused')
            except OSError as e:
                raise NetworkError(str(e))

            if msg.strip() != config.SERVER_RESPONSE:
                raise NetworkError('server response do not match')
            self.network_status = NetworkStatus.CONNECTED
            self.socket.settimeout(0)  # disable timeout
            print('client: server connected')
        except NetworkError as e:
            self.network_status = NetworkStatus.ERROR
            self.error_message = e.args[0]


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

    # ↑ handshake code
    ##############################################################################
    # ↓ game running code

    def listener(self):
        assert self.network_status == NetworkStatus.CONNECTED
        while not self.engine.game_ended:
            # todo: add check for closed socket
            msg = self.socket.recv(1024)
            assert msg.startswith(b'<')
            while not msg.endswith(b'>'):
                msg += self.socket.recv(1024)
            self.queue.put_nowait(msg.decode('ascii'))

    def on_game_start(self):
        # todo: init game?
        threading.Thread(target=self.listener).start()
        pass

    def on_game_tick(self):
        if not self.queue.empty():
            raw_msg = self.queue.get_nowait()
            # todo: translate message to function calls to `self.engine`
            msg = raw_msg.strip('<>').split('|')
            if msg[0] == 'PlacedMana':
                pass
            elif msg[0] == 'PlacedPiece':
                pass
            elif msg[0] == 'MovedPiece':
                pass
            elif msg[0] == 'NextPhase':
                pass
            elif msg[0] == 'NextTurn':
                pass
            print(raw_msg)
            print(msg)
        pass
