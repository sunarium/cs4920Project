from src import config
from .button import Button
from src.engine import GameEngine, PlayerColor

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
        self.buttons = [Button(self, config.buttons['back_to_main_ingame'])]
        self.engine = GameEngine(debug=True)

        print()

    def handle_event(self, events:List[pygame.event.Event]):
        # todo: if game over, stop handle all mouse interaction except quit button

        # handle mouse over
        for b in self.buttons:
            b.activated = b.rect.collidepoint(*pygame.mouse.get_pos())
        # todo handle mouse click on card/piece/board/buttons

        # handle drag?
        pass

    def render(self, screen:pygame.Surface):
        self.render_ui_sprite(screen)
        for b in self.buttons:
            b.render(screen)

        # draw pieces
        for p in self.engine.board.pieces:
            assetfile = p.asset_name()
            surf = pygame.image.load(config.assetsroot+assetfile)
            location = (p.pos.elementwise()  * V2(config.piece_size)) + config.board_pos
            screen.blit(surf, location)

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

        # todo draw phase indicator


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
