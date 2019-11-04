import pygame
from abc import ABC, abstractmethod

from . import config

class GUIState(ABC):
    def __init__(self, name):
        self.next_state:GUIState = self
        self.name = name

    @abstractmethod
    def handle_events(self, event:pygame.event.Event):
        pass

    @abstractmethod
    def render(self, screen:pygame.Surface):
        pass


class MainMenu(GUIState):
    pass