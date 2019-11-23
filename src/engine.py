from typing import List, Tuple, Union
from pygame import Vector2
from enum import IntEnum, auto
import socket
import threading
import queue
import pygame

from .board import Board
from .piece import Piece
from .exceptions import *
from .player import Player
from .playercolor import PlayerColor
from . import config

class GamePhase(IntEnum):
    STRATEGY = 0
    ACTION = 1
    FALL_BACK = 2


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
    def __init__(self, debug=False, first_player=PlayerColor.WHITE):
        # game ends when a player loses his king
        self.game_ended = False
        self.winner = None

        # white goes first as per chess tradition
        self.current_player = Player(first_player)
        self.waiting_player = Player(0 - first_player.value)
        self.board = Board()

        self.phase = GamePhase.STRATEGY

        #setup game state
        for i in range(0,6):
            self.current_player.draw_card()
            self.waiting_player.draw_card()

        # for display
        self.newly_drawn = None

        # turn flags
        self.has_placed_to_mana = False
        self.has_moved_piece = False
        #self.has_played_card = False

        # debug flag
        self.debug = debug
        if debug:
            print('WARNING DEBUG MODE')
            self.phase = 0
            Piece('rook',  (0, 0), PlayerColor.WHITE, self.board)
            Piece('knight', (1, 0), PlayerColor.WHITE, self.board)
            Piece('bishop', (2, 0), PlayerColor.WHITE, self.board)

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
        card = self.current_player.hand[card_index]
        newList = []
        for v in card.legal_start():
            owner = self.board.get_owner(v)
            if owner == PlayerColor.EMPTY:
                newList.append(v)
        return newList

    # player playes a card in his hand to target on board.
    # if card is piece card, this action places the piece onto the board.
    # raise exception if illegal index or invalid target or insufficient mana
    def play_card(self, card_index: int, target: Union[Vector2, Tuple[int, int]]):
        if not self.debug:
            if not self.phase in (GamePhase.STRATEGY, GamePhase.FALL_BACK):
                raise IllegalPlayerActionError('you can only play card in Strategy or Fall Back phase')
            #elif self.has_played_card:
                #raise IllegalPlayerActionError('already placed a card on board before')
            elif target not in self.valid_positions(card_index):
                raise IllegalPlayerActionError('you cannot place the piece here')
        #self.has_played_card = True
        self.current_player.play_card(card_index, target, self.board)

    def text_objects(self, text, font):
        textSurface = font.render(text, True, config.ui_colors.black)
        return textSurface, textSurface.get_rect()

    # player places a card into mana pile. this action can only be performed once per turn.
    def place_to_mana_pile(self, card_index: int):
        if not self.debug:
            if not self.phase in (GamePhase.STRATEGY, GamePhase.FALL_BACK):
                raise IllegalPlayerActionError('you can only place card to mana in main phase')
            elif self.has_placed_to_mana:
                raise IllegalPlayerActionError('already placed a card to mana before')
        self.current_player.place_to_mana_pile(card_index)
        self.has_placed_to_mana = True

    # valid targets to which pieces ON THE BOARD move
    # raises error if no owned piece at old_pos
    def valid_movement_targets(self, old_pos) -> List[Vector2]:
        piece = self.board.get_piece(old_pos)
        if not piece:
            raise AttributeError(f'no piece at {old_pos}')
        return piece.get_legal_moves(self.board)

    # player can move a piece once per turn(?)
    # raises error if
    #   - no owned piece at old_pos
    #   - new pos is invalid
    def move_piece(self, piece: Piece, new_pos: Union[Vector2, Tuple[int, int]]):
        # check movement legality
        if (new_pos not in piece.get_legal_moves(self.board) or piece.newly_placed) and not self.debug:
            raise IllegalPlayerActionError('You cannot move there')

        # enemy piece capturing
        captured_piece = self.board.get_piece(new_pos)
        if captured_piece:  # captured
            self.board.remove_at(new_pos)

        piece.move_to(new_pos)
        self.has_moved_piece = True

        # if king is captured, player made this move wins
        if captured_piece and captured_piece.name == 'king':
            self.winner = self.determine_winner()
            self.game_ended = True

    def determine_winner(self):
        return self.current_player

    # if current player can move piece at pos, return piece
    # otherwise raise exception
    def grab_piece(self, pos):
        if not self.debug:
            if self.phase != GamePhase.ACTION:
                raise IllegalPlayerActionError('Can only move piece in Action Phase')
            if self.has_moved_piece:
                raise IllegalPlayerActionError('You can only move piece once per turn')
        piece = self.board.get_piece(pos)
        if piece:
            if piece.owner == self.current_player.color and not piece.newly_placed:
                return piece
            else:
                raise IllegalPlayerActionError('You cannot move that piece')

    def turn_switch(self):
        self.phase = GamePhase.STRATEGY
        self.board.on_turn_change()
        self.current_player.on_turn_end()
        self.has_placed_to_mana = False
        self.has_moved_piece = False
        #self.has_played_card = False
        self.current_player, self.waiting_player = self.waiting_player, self.current_player
        self.current_player.on_turn_start()
        # self.newly_drawn = self.current_player.draw_card()

    # called when player end this phase
    def phase_change(self):
        if self.phase == GamePhase.FALL_BACK:
            self.phase = GamePhase.STRATEGY
            self.turn_switch()
        else:
            self.phase += 1

    def get_is_my_turn(self):
        return True

    def on_quit(self):
        pass


class NetworkGameEngine(GameEngine):
    def __init__(self, debug=True, is_host=True):
        firstplayer_color = PlayerColor.WHITE if is_host else PlayerColor.BLACK
        super().__init__(debug=debug, first_player=firstplayer_color)
        self.error_message = ''
        self.network_status = NetworkStatus.INITIALIZED
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.queue = queue.Queue()
        self.is_my_turn: bool = False
        self.exiting = False

    def reset(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.network_status = NetworkStatus.INITIALIZED
        self.error_message = ''

    def on_quit(self):
        self.game_ended = True

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
            self.socket.settimeout(0)
            print('client: server connected')
        except NetworkError as e:
            self.network_status = NetworkStatus.ERROR
            self.error_message = e.args[0]

    def _await_handshake(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', config.DEFAULT_PORT))
        s.setblocking(False)
        s.listen(1)
        while True:
            try:
                _sock, addr = s.accept()
            except BlockingIOError:
                if self.exiting:
                    s.close()
                    quit()
            else:
                if _sock.recv(1024).strip() == config.CLIENT_REQUEST:
                    print(f'got valid conn from {addr}')
                    break
                else:
                    _sock.close()
        s.close()
        self.socket = _sock
        self.socket.setblocking(True)
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
        self.socket.settimeout(0.5)
        while not self.game_ended:
            # todo: add check for closed socket
            try:
                msg = self.socket.recv(1024)
            except socket.timeout:
                if self.game_ended:
                    break
                else:
                    continue
            if self.is_my_turn:
                continue
            if msg == b'': # socket closed
                self.game_ended = True
                break
            elif not msg.startswith(b'<'):
                print('!!!!' + msg.decode('ascii'))
                break
            while not msg.endswith(b'>\n'):
                msg += self.socket.recv(1024)
            self.queue.put_nowait(msg.decode('ascii'))
        self.socket.close()
        print('listener thread quited')

    def on_game_start(self):
        self.socket.setblocking(True)
        threading.Thread(target=self.listener).start()

    def on_game_tick(self):
        if not self.queue.empty():
            raw_msg = self.queue.get_nowait()
            msg = raw_msg.strip().strip('<>').split('|')
            for i, arg in enumerate(msg[1:]):
                try:
                    msg[i+1] = int(float(arg))
                except ValueError:
                    pass
            if msg[0] == 'PlacedMana':
                self.waiting_player.place_to_mana_pile(msg[1])
            elif msg[0] == 'PlacedPiece':
                # fixme:should pass in card name and construct and play the card.
                #print(self.waiting_player.hand)
                self.waiting_player.pseudo_play_card((msg[1]), (int(msg[2]), int(msg[3])), self.board)
            elif msg[0] == 'MovedPiece':
                old_pos = Vector2(msg[1], msg[2])
                piece = self.board.get_piece(old_pos)
                assert piece # fixme:replace this with error checking after testing
                self.move_piece(piece, tuple(msg[3:5]))
            elif msg[0] == 'NextPhase':
                self.phase_change()
            elif msg[0] == 'NextTurn':
                self.turn_switch()
            elif msg == 'endgame':
                self.game_ended = True

            else:
                print('!!!!'+ raw_msg)
        pass

    # overidden methods
    def turn_switch(self):
        self.phase = GamePhase.MAIN
        self.board.on_turn_change()
        self.has_placed_to_mana = False
        self.has_moved_piece = False
        if self.get_is_my_turn():
            self.socket.send(b'<NextTurn>\n')
            self.current_player.on_turn_end()
            self.waiting_player.on_turn_start()
            self.is_my_turn = False
        else:
            self.waiting_player.on_turn_end()
            self.current_player.on_turn_start()
            self.is_my_turn = True

    def determine_winner(self):
        if self.is_my_turn:
            return self.current_player
        return self.waiting_player

    def phase_change(self):
        super().phase_change()
        if self.is_my_turn:
            self.socket.send(b'<NextPhase>\n')

    def move_piece(self, piece: Piece, new_pos: Union[Vector2, Tuple[int, int]]):
        old_pos = piece.pos
        super().move_piece(piece, new_pos)
        if self.is_my_turn:
            message = f'<MovedPiece|{old_pos.x}|{old_pos.y}|{new_pos[0]}|{new_pos[1]}>\n'
            self.socket.send(message.encode('ascii'))

    def play_card(self, card_index: int, target: Union[Vector2, Tuple[int, int]]):
        try:
            super().play_card(card_index, target)
        except IllegalPlayerActionError:
            if self.is_my_turn:
                raise
        cardName = self.current_player.hand[card_index].name
        if self.is_my_turn:
            message = f'<PlacedPiece|{cardName}|{target[0]}|{target[1]}>\n'
            self.socket.send(message.encode('ascii'))

    def place_to_mana_pile(self, card_index: int):
        try:
            super().place_to_mana_pile(card_index)
        except IllegalPlayerActionError:
            if self.is_my_turn:
                raise
        if self.is_my_turn:
            self.socket.send(f'<PlacedMana|{card_index}>\n'.encode('ascii'))

    def get_is_my_turn(self):
        return self.is_my_turn