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
HAND_SIZE = 6
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
    'rook': 2,
    'queen': 5
}

# size of board
BOARD_SIZE = 8

# king placement policy
# if true, player can choose where to place the king
FREE_KING = False

######################
# GRAPHICS CONSTANTS #
######################
ASSET_PATH = '../assets'
FRAME_RATE = 60
SCREEN_RESOLUTION = 1200, 900
MENU_FONT = 'comicsansms'
TEXT_SIZE_XS = 15
TEXT_SIZE_S = 25
TEXT_SIZE_M = 50
TEXT_SIZE_L = 75
COLORS = {
    "MAIN_MENU_BG": (218,165,32),       # goldenrod
    "BUTTON_COL1": (0, 155, 0),         # green
    "BUTTON_COL1_LIGHT": (0, 255, 0),   # light green
    "BUTTON_COL2": (200, 200, 0),       # yellow
    "BUTTON_COL2_LIGHT": (255,255,0),   # yellow light
    "BUTTON_COL3": (200, 0, 0),         # red
    "BUTTON_COL3_LIGHT": (255, 0, 0),   #light red
    "BLACK": (0, 0, 0)
}
WINDOW_TITLE = 'Chess: The Gathering'
ICON_PATH = '../assets/icon.png'

############################
# NETWORKED GAME CONSTANTS #
############################

DEFAULT_PORT = 11235
CONNECTION_TIMEOUT = 60 # needed?