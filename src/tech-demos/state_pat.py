from abc import ABC, abstractmethod

class State(ABC):
    def __init__(self, name):
        self.next_state = self
        self.name = name

    @abstractmethod
    def render(self, screen):
        pass

    @abstractmethod
    def handle_event(self):
        pass

class RunningState(State):
    def __init__(self, name):
        super().__init__()
        self.backend_engine = GameEngine()

    def render(self, screen):
        # grab information from engine
        # and draw to screen

    def handle_event(self):
        # ...handle other events...
        if user_clicked_exit:
            self.next_state = MenuState()

class MainmenuState(State):
    def render(self, screen):
        # render menu buttons and shit
        pass

    def handle_event(self):
        if user_clicked_networkgame:
            self.next_state = NetworkMenuState()
        elif user_clicked_localgame:
            self.next_state = RunningState()

# render cycle
state = MainmenuState()
while True:
    state.handle_event()
    state.render()
    state = state.next_state
    
    main_clock.tick(30)
    pygame.display.flip()
