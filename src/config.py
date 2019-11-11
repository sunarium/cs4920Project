from types import SimpleNamespace
import pygame
pygame.init()

######################
# GAMEPLAY CONSTANTS #
######################
PIECES = ['pawn', 'rook', 'bishop', 'knight', 'queen']
DECK_AMOUNT = {
    'pawn': 23,
    'rook': 6,
    'bishop': 9,
    'knight': 9,
    'queen': 3
}
HAND_SIZE = 99999
# costs of deploying each pieces
MANA_COST = {
    'pawn': 1,
    'bishop': 3,
    'knight': 3,
    'rook': 5,
    'queen': 10
}
# mana avaliable to player initially
INIT_MANA = 0

# mana gained each turn, set to 0 to turn off
MANA_PER_TURN = 0

# mana gained for placing this piece on mana pile
MANA_GAIN = {
    'pawn': 1,
    'rook': 1,
    'queen': 1
}

# size of board
BOARD_SIZE = 8

# king placement policy
# if true, player can choose where to place the king
FREE_KING = False

######################
# GRAPHICS CONSTANTS #
######################
frame_rate = 60
screen_resolution = (1200, 900)
screen_w, screen_h = screen_resolution

ui_colors = SimpleNamespace()
# (R,G,B)
ui_colors.white = (255, 255, 255)
ui_colors.black = (0, 0, 0)
ui_colors.red = (200, 0, 0)
ui_colors.light_red = (255, 0, 0)
ui_colors.green = (0, 155, 0)
ui_colors.light_green = (0, 255, 0)
ui_colors.blue = (0, 0, 255)
ui_colors.light_blue = (0, 0, 200)
ui_colors.yellow = (200, 200, 0)
ui_colors.light_yellow = (255, 255, 0)
ui_colors.goldenrod = (218, 165, 32)

ui_colors.legal_pos = (0, 128, 0, 128) # transparent green

# text renderers
# usage: config.fonts.xsmall.render(text, antialias, color) -> Surface
ui_fonts = SimpleNamespace()
ui_fonts.xs = pygame.font.SysFont("comicsansms", 15)
ui_fonts.s  = pygame.font.SysFont("comicsansms", 25)
ui_fonts.m  = pygame.font.SysFont("comicsansms", 50)
ui_fonts.l  = pygame.font.SysFont("comicsansms", 75)

# asset path
assetsroot = 'assets/'
window_icon = pygame.image.load(assetsroot + 'icon.png')
game_background = pygame.image.load(assetsroot + 'UI_v0.5.png')
tm_logo = 'tm.png'

# other UI elements
window_title = 'Chess: The Gathering'
credits_font = ui_fonts.l
credits_color = ui_colors.black
credits_vertical_gap = 100 # px
credits_initial_y = 400 # px
credits_speed = 1 # px/frame

# buttons
buttons = {
    'default': {
        'text':'TEXT',
        'left': 0,
        'top': 0,
        'width': 200,
        'height': 100,
        'font_size':'m',
        'color': ui_colors.light_blue,
        'active_color': ui_colors.blue,
        'text_color': ui_colors.black,
        'help_text': '',
        'help_text_size': 's',
        'help_text_color': ui_colors.black,
        'help_text_offset': 100,  # px
        'next_state': None,
        'next_turn': None,
        'next_phase': None
    },
    'start_local':{
        'text': 'local',
        'left': 100,
        'top': 500,
        'color': ui_colors.green,
        'active_color': ui_colors.light_green,
        'help_text': 'Start local game',
        'next_state': 'local_game'
    },
    'show_controls':{
        'text': 'controls',
        'left': 70,
        'top': 400,
        'color': ui_colors.green,
        'active_color': ui_colors.light_green,
        'help_text': 'Display controls',
        'next_state': 'controls'
    },
    'show_credits':{
        'text': 'credits',
        'left': 500,
        'top': 500,
        'color': ui_colors.red,
        'active_color': ui_colors.light_red,
        'help_text':'Display Credits',
        'next_state': 'credits'
    },
    'back_to_main':{
        'text': 'back',
        'left': 900,
        'top': 500,
        'color': ui_colors.red,
        'active_color': ui_colors.light_red,
        'help_text': 'back to main',
        'next_state': 'main_menu'
    },
    'back_to_main_ingame': {
        'text': 'back',
        'left': 1120,
        'top': 0,
        'width': 80,
        'height': 30,
        'color': ui_colors.red,
        'active_color': ui_colors.light_red,
        'help_text': '',
        'font_size': 'xs',
        'next_state': 'main_menu'
    },
    'next_phase': {
        'text': 'next_phase',
        'left': 1020,
        'top': 400,
        'width': 80,
        'height': 30,
        'color': ui_colors.red,
        'active_color': ui_colors.light_red,
        'help_text': '',
        'font_size': 'xs',
        'next_phase': 'next'
    },
    'next_turn': {
        'text': 'next_turn',
        'left': 1020,
        'top': 500,
        'width': 80,
        'height': 30,
        'color': ui_colors.red,
        'active_color': ui_colors.light_red,
        'help_text': '',
        'font_size': 'xs',
        'next_turn': 'next'
    },
    'quit': {
        'text': 'quit',
        'left': 900,
        'top': 500,
        'next_state': 'quit'
    }
}

# game interface
# sizes
board_size = (600, 600)
piece_size = (75, 75)
card_size = (150, 200)
# positions
board_pos = (150, 0)
hand_start_pos = (20, 680)
deck_text_pos = (1010, 725)
mana_start_pos = (70, 605)
mana_text_pos = (20, 610)
turn_indicator_pos = (955, 175)
turn_indicator_font = ui_fonts.s
# hand drawing shenanigans
hand_draw_area = pygame.Rect((0, 661), (900, 239))


# margin size
hand_margin = 20



############################
# NETWORKED GAME CONSTANTS #
############################

DEFAULT_PORT = 11235
HANDSHAKE_TIMEOUT = 5
CLIENT_REQUEST = b'ClientHello'
SERVER_RESPONSE = b'ServerWavesback'