import pygame
pygame.init()
import sys
from src import config
from src.gamestates import GameState, state_list

class Game:
    def __init__(self):
        self.this_state: GameState = state_list['main_menu']()
        self.screen = pygame.display.set_mode(config.screen_resolution)
        pygame.display.set_caption(config.window_title)
        pygame.display.set_icon(config.window_icon)
        self.clock = pygame.time.Clock()

    def run(self):
        while True:
            # advance state
            self.this_state = self.this_state.next_state

            # handle events
            event_list = pygame.event.get()
            for e in event_list:
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.this_state.handle_event(event_list)

            # draw
            self.this_state.render(self.screen)
            pygame.display.flip()

            # tick
            self.clock.tick(config.frame_rate)
