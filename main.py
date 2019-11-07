from src.engine import GameEngine
import pygame
pygame.init()
from src.game import Game

if __name__ == '__main__':
    Game().run()
    # e = GameEngine(debug=True)
    # e.debug_dump()
    # while not e.game_ended:
    #     userCommand = str(input())
    #     if userCommand == "end game":
    #         print("Game Ended")
    #         e.game_ended = True
    #     elif userCommand == "end turn":
    #         e.turn_switch()
    #         e.debug_dump()
    #     elif userCommand == "next":
    #         e.phase_change()
    #         e.debug_dump()
    #     elif userCommand == "draw":
    #         e.draw_card()
    #         e.debug_dump()
    #     elif userCommand == "add mana":
    #         index = int(input("select index "))
    #         e.place_to_mana_pile(index)
    #         print("mana added")
    #         e.debug_dump()
    #     elif userCommand == "play card":
    #         index = int(input("select index "))
    #         x = int(input("select x "))
    #         y = int(input("select y "))
    #         e.play_card(index, (x,y))
    #         print("card played")
    #         e.debug_dump()
    #     elif userCommand == "move piece":
    #         fromX = int(input("select x from "))
    #         fromY = int(input("select y from "))
    #         toX = int(input("select x to "))
    #         toY = int(input("select y to "))
    #         e.move_piece((fromX,fromY), (toX,toY))
    #         print("piece moved")
    #         e.debug_dump()
