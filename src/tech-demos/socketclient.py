import socket
import sys, os
import pygame

pygame.init()
mode = sys.argv[1]
assert mode in ['client', 'server']
if len(sys.argv) < 3:
    port = 9999
else:
    port = int(sys.argv[2])

screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption(mode)
clk = pygame.time.Clock()

os.system('clear')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if mode == 'server':
    s.bind(('0.0.0.0', port))
    s.listen(0)
    _s, addr = s.accept()
    print(f'got connection from {addr}')
    s.close()
    s = _s
else:
    s.connect(('127.0.0.1', port))
    print(f'connected to server')
s.setblocking(False)

# server goes first
is_my_turn = mode == 'server'

def randomize_screen():
    global screen
    from random import randint
    r,g,b = randint(0,255), randint(0,255), randint(0,255)
    screen.fill((r,g,b))

while True:
    action = ''
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            s.close()
            sys.exit()
        if is_my_turn and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_1:
                randomize_screen()
                action = '1'
            elif e.key == pygame.K_0:
                action = '0'
    if is_my_turn:
        if action != '':
            print('user action', action)
            s.send(action.encode('ascii'))
        if action == '0':
            is_my_turn = not is_my_turn
    else:
        try:
            enemy_action = s.recv(1024).decode('ascii')
            if enemy_action == '':
                # connection closed, exiting
                sys.exit()
            print('got action', enemy_action)
            if enemy_action == '0':
                is_my_turn = not is_my_turn
        except socket.error:
            pass
    pygame.display.flip()
    clk.tick(30)
