from src import config
from .button import Button
from src.engine import GameEngine, PlayerColor
from src.exceptions import *

import pygame
from pygame import Vector2 as V2
from abc import ABC, abstractmethod
from typing import List, Tuple


class GameState(ABC):
    def __init__(self):
        self.next_state:GameState = self

    @abstractmethod
    def render(self, screen:pygame.Surface):
        pass

    @abstractmethod
    def handle_event(self, events:List[pygame.event.Event]):
        pass

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
            Button(self, config.buttons['start_local'])
        ]

    def render(self, screen:pygame.Surface):
        screen.fill(config.ui_colors.goldenrod)
        for b in self.buttons:
            b.render(screen)

    def handle_event(self, events:List[pygame.event.Event]):
        for b in self.buttons:
            b.activated = b.rect.collidepoint(*pygame.mouse.get_pos())
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                # left click event
                for b in self.buttons:
                    if b.activated: b.on_click()

class LocalGame(GameState):
    def __init__(self):
        super().__init__()
        self.buttons = [
            Button(self, config.buttons['back_to_main_ingame']),
            Button(self, config.buttons['next_phase']),
            Button(self, config.buttons['next_turn']),
        ]
        self.engine = GameEngine(debug=True)
        # player interaction
        self.picked_piece = None
        self.hand_xoffset = 0
        self.board_rect = pygame.Rect(config.board_pos, config.board_size)
        # visual clues
        self.legal_positions = None

        # debug
        self.engine.phase = 1
        self.engine.board.on_turn_change()



    def handle_event(self, events:List[pygame.event.Event]):
        # todo: if game over, stop handle all mouse interaction except quit button
        # handle mouse over
        for b in self.buttons:
            b.activated = b.rect.collidepoint(*pygame.mouse.get_pos())
        # todo handle mouse click on card/piece/board/buttons
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                if self.board_rect.collidepoint(*e.pos):
                    self.on_click_board(e.pos)
                elif config.hand_draw_area.collidepoint(*e.pos):
                    self.on_click_hand()
                for b in self.buttons:
                    if b.activated: b.on_click()
            elif e.type == pygame.MOUSEMOTION and e.buttons[0]:
                pass
                # drag motion
        # handle hand drag?

    def on_click_board(self, mouse_pos):
        piece_pos = (V2(mouse_pos) - config.board_pos) // config.piece_size[0]
        if not self.picked_piece:
            self.picked_piece = self.engine.grab_piece(piece_pos)
        else:
            try:
                self.engine.move_piece(self.picked_piece, piece_pos)
                self.picked_piece = None
                if self.engine.game_ended:
                    self.set_next_state("main_menu")
            except IllegalPlayerActionError:
                # todo we could play a sound here
                pass


    def on_click_hand(self):
        pass

    def on_click_mana_pile(self):
        pass



    def render(self, screen:pygame.Surface):
        self.render_ui_sprite(screen)
        for b in self.buttons:
            b.render(screen)

        # draw pieces
        for p in self.engine.board.pieces:
            if p == self.picked_piece:
                location = pygame.Rect((0,0), config.piece_size)
                location.center = pygame.mouse.get_pos()
            else:
                location = (p.pos.elementwise() * V2(config.piece_size)) + config.board_pos
            assetfile = p.asset_name()
            surf = pygame.image.load(config.assetsroot+assetfile)
            screen.blit(surf, location)

        # draw picked piece


        # draw visual clues
        # todo: not tested
        if self.legal_positions is not None:
            for legal_pos in self.legal_positions:
                rect = pygame.Rect(
                    V2(config.board_pos) + (legal_pos.elementwise() * config.piece_size),
                    config.piece_size
                )
                pygame.draw.rect(screen, config.ui_colors.legal_pos, rect)

        # draw hand
        location = V2(config.hand_start_pos)
        screen.set_clip(config.hand_draw_area)
        for c in self.engine.get_curr_hand():
            # todo if user dragged it, the starting position will change.
            surf = pygame.image.load(config.assetsroot+c.asset_name())
            screen.blit(surf, location)
            location.x += (config.card_size[0] + config.hand_margin)
        screen.set_clip(None)

        # draw deck size
        text = "{}/50".format(self.engine.get_curr_deck_size())
        screen.blit(
            config.ui_fonts.s.render(text, True, config.ui_colors.black),
            config.deck_text_pos
        )

        # todo draw mana bar
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
        # todo draw phase indicator
        text = 'Player %d turn' % self.engine.current_player.color
        screen.blit(
            config.turn_indicator_font.render(text, True, config.ui_colors.black),
            config.turn_indicator_pos
        )


    # render sprites that doesnt need to move
    def render_ui_sprite(self, screen):
        screen.blit(config.game_background, (0,0))

    def click_to_board_pos(self, mouse_pos)-> pygame.Vector2:
        mouse_pos = pygame.Vector2(mouse_pos)
        mouse_pos -= config.board_pos
        mouse_pos /= config.piece_size
        return mouse_pos




state_list = {
    'main_menu': MainMenu,
    'quit': Quit,
    'credits': Credits,
    'local_game': LocalGame
}
