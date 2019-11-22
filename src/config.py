from types import SimpleNamespace
import pygame
pygame.init()

######################
# GAMEPLAY CONSTANTS #
######################
debug = False

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
"""MANA_COST = {
    'pawn': 1,
    'bishop': 1,
    'knight': 1,
    'rook': 1,
    'queen': 1
}"""
# mana avaliable to player initially
INIT_MANA = 0

# mana gained each turn, set to 0 to turn off
MANA_PER_TURN = 0

# mana gained for placing this piece on mana pile
MANA_GAIN = {
    'pawn': 1,
    'bishop': 1,
    'knight': 1,
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
board_background = pygame.image.load(assetsroot + 'board_bg.png')
game_board = pygame.image.load(assetsroot + 'board.png')
hand_bg = pygame.image.load(assetsroot + 'hand_bg.png')
mana_bg = pygame.image.load(assetsroot + 'mana_bg.png')
deck_bg = pygame.image.load(assetsroot + 'deck_bg.png')
side_info_bg = pygame.image.load(assetsroot + 'side_info_bg.png')
phase_bg = pygame.image.load(assetsroot + 'phase_bg.png')
black_indicator_active = pygame.image.load(assetsroot + 'black_indicator_active.png')
black_indicator = pygame.image.load(assetsroot + 'black_indicator.png')
white_indicator_active = pygame.image.load(assetsroot + 'white_indicator_active.png')
white_indicator = pygame.image.load(assetsroot + 'white_indicator.png')
tm_logo = 'tm.png'
menu_bg = pygame.image.load(assetsroot + 'menu_bg.png')

# other UI elements
window_title = 'Chess: The Gathering'
credits_font = ui_fonts.l
credits_color = ui_colors.black
credits_vertical_gap = 100 # px
credits_initial_y = 400 # px
credits_speed = 1 # px/frame

connect = SimpleNamespace()
connect.prompt_text = 'Please enter server\'s ip address :'
connect.prompt_font = ui_fonts.m
connect.prompt_color = ui_colors.black
connect.prompt_center = (600, 200)
connect.input_font = ui_fonts.m
connect.input_color = ui_colors.black
connect.input_center = (600, 300)
connect.status_font = ui_fonts.xs
connect.status_color = ui_colors.red
connect.status_center = (600, 350)
connect.delete_frame_interval = 10 # if user held down backspace, pop one char every X frame

host = SimpleNamespace()
host.prompt_text = "Awaiting connection..."
host.prompt_center = (600, 200)
host.prompt_color = ui_colors.black
host.prompt_font = ui_fonts.m



# buttons
buttons = {
    'default': {
        'text':'TEXT',
        'left': 0,
        'top': 0,
        'width': 250,
        'height': 100,
        'font_size':'m',
        'color': ui_colors.light_blue,
        'active_color': ui_colors.blue,
        'text_color': ui_colors.black,
        'help_text': '',
        'help_text_size': 's',
        'help_text_color': ui_colors.white,
        'help_text_offset': 100,  # px
        'next_state': None,
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
    'join_online': {
        'text': 'join game',
        'left': 100,
        'top': 200,
        'color': ui_colors.green,
        'active_color': ui_colors.light_green,
        'help_text': 'Join online game',
        'next_state': 'join_game'
    },
    'host_online': {
        'text': 'host game',
        'left': 500,
        'top': 200,
        'color': ui_colors.red,
        'active_color': ui_colors.light_red,
        'help_text': 'Host online game',
        'next_state': 'host_game'
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
    'connect': {
        'text': 'connect',
        'left': 100,
        'top': 500,
        'color': ui_colors.red,
        'active_color': ui_colors.light_red,
        'help_text': None,
        'next_state': None
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
        'left': 1100,
        'top': 550,
        'width': 100,
        'height': 50,
        'color': ui_colors.red,
        'active_color': ui_colors.light_red,
        'help_text': '',
        'font_size': 'xs',
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
card_size = (137, 200)
# positions
board_pos = (149, 0)
hand_start_pos = (20, 680)
hand_bg_pos = (0,661)
deck_text_pos = (1010, 725)
deck_pos = (965,636)
mana_start_pos = (70, 605)
mana_text_pos = (20, 610)
mana_bg_pos = (0,601)
mana_zone = pygame.Rect((0,600), (900, 650))
side_info_bg_pos = (902,0)
phase_bg_pos = (902,550)
deck_bg_pos = (902,601)
black_indicator_pos = (965,122)
white_indicator_pos = (1091,122)
turn_indicator_pos = (955, 175)
turn_indicator_font = ui_fonts.s
opponent_mana_pos = (970, 205)
opponent_mana_font = ui_fonts.xs
opponent_hand_pos = (970, 225)
opponent_hand_font = ui_fonts.xs
phase_text_pos = (910, 555)
error_pos = (910, 430)
error_font = ui_fonts.xs
error_color = ui_colors.red

hand_draw_area = pygame.Rect((0, 661), (901, 240))


# margin size between cards
hand_margin = 20

############################
# NETWORKED GAME CONSTANTS #
############################

DEFAULT_PORT = 11235
HANDSHAKE_TIMEOUT = 5
CLIENT_REQUEST = b'ClientHello'
SERVER_RESPONSE = b'ServerWavesBack'