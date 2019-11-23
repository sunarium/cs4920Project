from src import config
from .button import Button
from src.engine import GameEngine, NetworkStatus, NetworkGameEngine, PlayerColor
from src.exceptions import *

import pygame
from pygame import Vector2 as V2
from abc import ABC, abstractmethod
from typing import List

class GameState(ABC):
    def __init__(self):
        self.next_state:GameState = self

    @abstractmethod
    def render(self, screen:pygame.Surface):
        pass

    @abstractmethod
    def handle_event(self, events:List[pygame.event.Event]):
        pass

    def handle_button(self, events:List[pygame.event.Event]):
        if not self.buttons:
            return
        for b in self.buttons:
            b.activated = b.rect.collidepoint(*pygame.mouse.get_pos())
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                for b in self.buttons:
                    if b.activated: b.on_click()

    def set_next_state(self, next_state:str):
        self.next_state = state_list[next_state]()

class Quit(GameState):
    def __init__(self):
        super().__init__()

    def render(self, screen:pygame.Surface):
        pass

    def handle_event(self, events:List[pygame.event.Event]):
        pygame.event.post(pygame.event.Event(pygame.QUIT, {}))

class Credits(GameState):
    def __init__(self):
        super().__init__()
        self.texts = [
            'Credits:',
            ' ',
            'Developed by',
            'Foo',
            'Bar'
        ]
        self.yoffset = config.credits_initial_y

    def handle_event(self, events:List[pygame.event.Event]):
        pass

    def render(self, screen:pygame.Surface):
        screen.fill(config.ui_colors.white)
        offset = 0
        for text in self.texts:
            rentert = config.credits_font.render(text, True, config.credits_color)
            rect = rentert.get_rect()
            rect.centery = self.yoffset + offset
            rect.centerx = config.screen_resolution[0] / 2
            offset += config.credits_vertical_gap
            self.yoffset -= config.credits_speed
            screen.blit(rentert, rect)
        if offset + self.yoffset < 0:
            self.set_next_state('main_menu')


class MainMenu(GameState):
    def __init__(self):
        super().__init__()
        self.buttons = [
            Button(self, config.buttons['quit']),
            Button(self, config.buttons['show_credits']),
            Button(self, config.buttons['start_local']),
            Button(self, config.buttons['join_online']),
            Button(self, config.buttons['host_online'])
        ]

    def render(self, screen:pygame.Surface):
        screen.blit(config.menu_bg, (0,0))
        for b in self.buttons:
            b.render(screen)

    def handle_event(self, events:List[pygame.event.Event]):
        self.handle_button(events)

class LocalGame(GameState):
    def __init__(self, engine=None):
        super().__init__()
        pygame.mixer.init()
        pygame.mixer.music.load("assets/bg_music.mp3")
        pygame.mixer.music.play(-1)

        self.buttons = [
            Button(self, config.buttons['back_to_main_ingame'], on_click_callback=self.on_quit),
            Button(self, config.buttons['next_phase'], on_click_callback=self.phase_change),
            Button(self, config.buttons['next_turn'], on_click_callback=self.turn_change),
        ]
        # game engine
        if engine:
            self.engine = engine
        else:
            self.engine = GameEngine(debug=config.debug)

        # player interaction
        self.picked_piece = None
        self.hand_xoffset = 0
        self.board_rect = pygame.Rect(config.board_pos, config.board_size)
        self.drag = False
        self.error_message = ''
        # visual clues
        self.legal_positions = None
        self.legal_starts = None
        self.start_offset = 0
        self.picked_card = None

    def on_quit(self):
        self.engine.on_quit()

    def phase_change(self):
        if self.engine.get_is_my_turn():
            self.picked_card = None
            self.picked_piece = None
            self.engine.phase_change()

    def turn_change(self):
        if self.engine.get_is_my_turn():
            self.picked_card = None
            self.picked_piece = None
            self.engine.turn_switch()

    def handle_event(self, events:List[pygame.event.Event]):
        # todo if game over, stop handling all mouse interaction except quit button
        self.handle_button(events)

        # if not my turn, do not handle events
        if not self.engine.get_is_my_turn():
            self.engine.on_game_tick()
            return

        if self.engine.game_ended:
            self.set_next_state("main_menu")

        # handle player events
        # for clearing error message
        dismiss_error = False
        try:
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == pygame.BUTTON_LEFT:
                    if self.board_rect.collidepoint(*e.pos):
                        self.on_click_board(e.pos)
                    elif config.hand_draw_area.collidepoint(*e.pos):
                        self.on_click_hand(e.pos)
                        self.drag = True
                        posX, posY = e.pos
                        self.start_offset = self.hand_xoffset - posX
                    elif config.mana_zone.collidepoint(*e.pos):
                        self.on_click_mana_pile()
                # drag motion for dragging hand
                elif e.type == pygame.MOUSEMOTION and e.buttons[0] and self.drag:
                    posX, posY = e.pos
                    self.hand_xoffset = self.start_offset + posX
                    self.picked_card = None
                elif e.type == pygame.MOUSEBUTTONUP:
                    self.drag = False
                # cancellation
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == pygame.BUTTON_RIGHT:
                    self.picked_piece = None
                    self.picked_card = None
                    self.error_message = ''
                elif e.type == pygame.KEYDOWN and e.unicode == 'k':
                    # for debugging, dont delete!
                    print("a")
        except IllegalPlayerActionError as e:
            self.error_message = str(e)


    def on_click_board(self, mouse_pos):
        piece_pos = (V2(mouse_pos) - config.board_pos) // config.piece_size[0]
        if self.picked_piece:
            self.engine.move_piece(self.picked_piece, piece_pos)
            self.picked_piece = None
        elif self.picked_card is not None:
            self.engine.play_card(self.picked_card, piece_pos)
            self.picked_card = None
        elif not self.picked_piece:
            self.picked_piece = self.engine.grab_piece(piece_pos)

    def on_click_hand(self, mouse_pos):
        hand_pos = (mouse_pos[0] - config.hand_start_pos[0] - self.hand_xoffset) // (config.card_size[0] + config.hand_margin)
        if self.picked_card is None and hand_pos >= 0 and not self.engine.phase == 1:
            self.picked_card = hand_pos
        pass

    def on_click_mana_pile(self):
        if self.picked_card is not None:
            self.engine.place_to_mana_pile(self.picked_card)
            self.picked_card = None

    def render(self, screen:pygame.Surface):
        # draw game backgrounds
        self.render_ui_sprite(screen)

        # draw button
        for b in self.buttons:
            b.render(screen)

        # draw hand
        location = V2(config.hand_start_pos)
        location.x += self.hand_xoffset
        screen.set_clip(config.hand_draw_area)
        for c in self.engine.get_curr_hand():
            surf = pygame.image.load(config.assetsroot + c.asset_name())
            screen.blit(surf, location)
            location.x += (config.card_size[0] + config.hand_margin)
        screen.set_clip(None)

        # draw visual clues
        if self.picked_piece and self.legal_positions:
            for legal_pos in self.legal_positions:
                # see https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangle-in-pygame
                surf = pygame.Surface(config.piece_size, pygame.SRCALPHA)
                surf.fill(config.ui_colors.legal_pos)
                screen.blit(surf, V2(config.board_pos) + (legal_pos.elementwise() * config.piece_size))

        if self.picked_card is not None:
            self.legal_starts = self.engine.valid_positions(self.picked_card)
            for legal_pos in self.legal_starts:
                surf = pygame.Surface(config.piece_size, pygame.SRCALPHA)
                surf.fill(config.ui_colors.legal_pos)
                screen.blit(surf, V2(config.board_pos) + (legal_pos.elementwise() * config.piece_size))
            surf = pygame.Surface(config.card_size, pygame.SRCALPHA)
            surf.fill(config.ui_colors.legal_pos)
            pickedLoc = V2(config.hand_start_pos)
            pickedLoc.x += self.hand_xoffset
            for x in range (0,self.picked_card):
                pickedLoc.x += (config.card_size[0] + config.hand_margin)
            screen.blit(surf, pickedLoc)

        # draw pieces
        for p in self.engine.board.pieces:
            if p == self.picked_piece:
                location = pygame.Rect((0,0), config.piece_size)
                location.center = pygame.mouse.get_pos()
                self.legal_positions = p.get_legal_moves()
            else:
                location = (p.pos.elementwise() * V2(config.piece_size)) + config.board_pos
            assetfile = p.asset_name()
            surf = pygame.image.load(config.assetsroot+assetfile)
            screen.blit(surf, location)

        # draw deck size
        text = "{}/50".format(self.engine.get_curr_deck_size())
        screen.blit(
            config.ui_fonts.s.render(text, True, config.ui_colors.black),
            config.deck_text_pos
        )

        #draw mana bar
        position = V2(config.mana_start_pos)
        currMana = self.engine.current_player.turn_mana
        maxMana = self.engine.current_player.max_mana
        text = "{}/{}".format(currMana, maxMana)
        drawCounter = 0
        while drawCounter < currMana:
            drawCounter += 1
            image = pygame.image.load("assets/mana_untapped.png")
            screen.blit(image, position)
            position.x += 60

        while drawCounter < maxMana:
            drawCounter += 1
            image = pygame.image.load("assets/mana_tapped.png")
            screen.blit(image, position)
            position.x += 60

        screen.blit(
            config.ui_fonts.s.render(text, True, config.ui_colors.black),
            config.mana_text_pos
        )

        #draw error message
        if self.error_message != '':
            error_words = self.error_message.split(' ')
            space_width = config.error_font.size(' ')[0]
            x, y = config.error_pos
            for w in error_words:
                word_surface = config.error_font.render(w, True, config.error_color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= config.screen_w:
                    x = config.error_pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                screen.blit(word_surface, (x, y))
                x += word_width + space_width
            x = config.error_pos[0]
            y += word_height
            word_surface = config.error_font.render('(Right click to dismiss)', True, config.error_color)
            screen.blit(word_surface, (x, y))

        #  draw phase indicator
        if self.engine.phase == 0:
            text = "Strategy Phase"
        elif self.engine.phase == 1:
            text = "Action Phase"
        elif self.engine.phase == 2:
            text = "Fall Back Phase"
        
        screen.blit(
            config.ui_fonts.s.render(text, True, config.ui_colors.black),
            config.phase_text_pos
        )

        # draw player indicator
        if (self.engine.current_player.color == PlayerColor.WHITE) ^ (not self.engine.get_is_my_turn()):
            p_colour = "white"
            black_ind = config.black_indicator
            white_ind = config.white_indicator_active
        else:
            p_colour = "black"
            black_ind = config.black_indicator_active
            white_ind = config.white_indicator
        text = 'Player ' + p_colour +  ' turn'
        screen.blit(
            config.turn_indicator_font.render(text, True, config.ui_colors.black),
            config.turn_indicator_pos
        )
        screen.blit(black_ind, config.black_indicator_pos)
        screen.blit(white_ind, config.white_indicator_pos)

        # draw opponent information
        currMana = self.engine.waiting_player.turn_mana
        maxMana = self.engine.waiting_player.max_mana
        text = "opponent's mana: " + "{}/{}".format(currMana, maxMana)
        screen.blit(
            config.opponent_mana_font.render(text, True, config.ui_colors.black),
            config.opponent_mana_pos
        )

        text = "opponent's hand: " + str(len(self.engine.waiting_player.hand))
        screen.blit(
            config.opponent_hand_font.render(text, True, config.ui_colors.black),
            config.opponent_hand_pos
        )


    # render sprites that doesnt need to move
    def render_ui_sprite(self, screen):
        screen.blit(config.game_background, (0,0))
        screen.blit(config.board_background, (0,0))
        screen.blit(config.game_board, config.board_pos)
        screen.blit(config.hand_bg, config.hand_bg_pos)
        screen.blit(config.mana_bg, config.mana_bg_pos)
        screen.blit(config.side_info_bg, config.side_info_bg_pos)
        screen.blit(config.phase_bg, config.phase_bg_pos)
        screen.blit(config.side_info_bg, config.deck_bg_pos)
        screen.blit(config.deck_bg, config.deck_pos)

    def click_to_board_pos(self, mouse_pos)-> pygame.Vector2:
        mouse_pos = pygame.Vector2(mouse_pos)
        mouse_pos -= config.board_pos
        mouse_pos /= config.piece_size
        return mouse_pos

class HostGame(GameState):
    def __init__(self):
        super().__init__()
        self.buttons = [Button(self, config.buttons['back_to_main'], on_click_callback=self.on_exit)]
        self.network_engine = NetworkGameEngine(debug=config.debug, is_host=True)
        self.local_ip = self.get_local_ip()
        self.network_engine.host_game()

    def on_exit(self):
        self.network_engine.exiting = True

    def get_local_ip(self) -> str:
        # from https://stackoverflow.com/a/28950776
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def render(self, screen:pygame.Surface):
        screen.fill(config.ui_colors.goldenrod)
        # buttons
        for b in self.buttons:
            b.render(screen)
        # render status text
        prompt = config.host.prompt_font.render(config.host.prompt_text, True, config.host.prompt_color)
        prompt_rect = prompt.get_rect()
        prompt_rect.center = config.host.prompt_center
        screen.blit(prompt, prompt_rect)

    def handle_event(self, events:List[pygame.event.Event]):
        self.handle_button(events)
        if self.network_engine.network_status == NetworkStatus.CONNECTED:
            self.network_engine.on_game_start()
            self.next_state = LocalGame(engine=self.network_engine)

class JoinGame(GameState):
    def __init__(self):
        super().__init__()
        self.network_engine = NetworkGameEngine(debug=config.debug, is_host=False)
        self.buttons = [
            Button(self, config.buttons['back_to_main'], on_click_callback=self.on_leave),
            Button(self, config.buttons['connect'], on_click_callback=self.connect_to)
        ]
        self.delete_frame_counter = config.connect.delete_frame_interval
        self.ip_string = "127.0.0.1"
        self.status_text = ""

    def on_leave(self):
        self.network_engine.socket.close()

    def connect_to(self):
        if self.ip_string != '' and self.network_engine.network_status != NetworkStatus.CONNECTED:
            self.status_text = ''
            self.network_engine.reset()
            self.network_engine.connect_to(self.ip_string)

    def render(self, screen:pygame.Surface):
        screen.fill(config.ui_colors.goldenrod)
        for b in self.buttons:
            b.render(screen)

        # render prompt text
        prompt = config.connect.prompt_font.render(config.connect.prompt_text, True, config.connect.prompt_color)
        prompt_rect = prompt.get_rect()
        prompt_rect.center = config.connect.prompt_center
        screen.blit(prompt, prompt_rect)

        # render input field
        input_ip = config.connect.input_font.render(self.ip_string, True, config.connect.input_color)
        input_rect = input_ip.get_rect()
        input_rect.center = config.connect.input_center
        screen.blit(input_ip, input_rect)

        # render error message if any
        status = config.connect.status_font.render(self.status_text, True, config.connect.status_color)
        status_rect = status.get_rect()
        status_rect.center = config.connect.status_center
        screen.blit(status, status_rect)

    def handle_event(self, events:List[pygame.event.Event]):
        self.handle_button(events)
        # user events
        if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
            self.delete_frame_counter -= 1
            if self.delete_frame_counter == 0:
                self.ip_string = self.ip_string[:-1]
                self.delete_frame_counter = config.connect.delete_frame_interval
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    self.ip_string = self.ip_string[:-1]
                elif e.unicode != '' and e.unicode.isprintable():
                    self.ip_string += e.unicode

        # network events
        self.status_text = str(self.network_engine.network_status)
        if self.network_engine.network_status == NetworkStatus.ERROR:
            self.status_text += self.network_engine.error_message

        if self.network_engine.network_status == NetworkStatus.CONNECTED:
            self.network_engine.on_game_start()
            self.next_state = LocalGame(engine=self.network_engine)

state_list = {
    'main_menu': MainMenu,
    'quit': Quit,
    'credits': Credits,
    'local_game': LocalGame,
    'join_game': JoinGame,
    'host_game': HostGame
}
