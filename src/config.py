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