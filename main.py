from src.board import Board
from src.piece import *
from src.playercolor import PlayerColor
from src.engine import GameEngine

if __name__ == '__main__':
    e = GameEngine(debug=True)
    e.draw_card()
    e.draw_card()
    e.draw_card()
    e.draw_card()
    e.draw_card()
    e.place_to_mana_pile(0)
    e.tap(0)
    # e.play_card(0, (1, 1))
    # e.play_card(0, (1, 2))
    # e.play_card(0, (1, 3))
    # e.play_card(0, (1, 4))
    e.debug_dump()
    while not e.game_ended:
        userCommand = str(input())
        if userCommand == "end game":
            e.game_ended = True
        elif userCommand == "end turn":
            e.turn_switch()
            e.debug_dump()
        elif userCommand == "next":
            e.phase_change()
            e.debug_dump()
