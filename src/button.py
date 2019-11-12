from src import config
import pygame

class Button:
    def __init__(self, owner, spec:dict, on_click_callback=None):
        for k, v in config.buttons['default'].items():
            self.__setattr__(k, v)
        for k, v in spec.items():
            self.__setattr__(k, v)
        self.owner = owner
        self.activated = False
        self.rect = pygame.Rect(self.left, self.top, self.width, self.height)
        self.text_renderer = config.ui_fonts.__getattribute__(self.font_size)
        self.on_click_callback = on_click_callback

    def render(self, screen:pygame.Surface):
        color = self.active_color if self.activated else self.color
        pygame.draw.rect(screen, color, self.rect)
        btn_text = self.text_renderer.render(self.text, True, self.text_color)
        text_rect = btn_text.get_rect()
        text_rect.center = self.rect.center
        screen.blit(btn_text, text_rect)
        if self.activated and self.help_text != '':
            help_text = self.text_renderer.render(self.help_text, True, self.help_text_color)
            help_rect = help_text.get_rect()
            help_rect.centerx = self.rect.centerx
            help_rect.centery = self.rect.centery - self.help_text_offset
            screen.blit(help_text, help_rect)


    def on_click(self):
        if self.next_state:
            self.owner.set_next_state(self.next_state)
        if self.on_click_callback:
            self.on_click_callback()
