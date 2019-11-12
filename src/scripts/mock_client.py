import socket
import threading
import sys

mode = 's'

if len(sys.argv) != 2 and not mode:
    print(f'Usage: {sys.argv[0]} [c|s|client|server]')
elif len(sys.argv) == 2:
    mode = sys.argv[1][0]
assert mode in ('c', 's')

def listener():
    global sock
    while True:
        msg = sock.recv(1024)
        if msg == b'':
            print('socket closed')
            sys.exit(0)
        print(msg.decode('ascii'))

def handshake():
    global sock, mode
    if mode == 's':
        assert sock.recv(1024) == b'ClientHello'
        sock.send(b'ServerWavesBack')
    else:
        sock.send(b'ClientHello')
        assert sock.recv(1024) == b'ServerWavesBack'
    print('handshake success')

_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_s.bind(('', 11235))
_s.listen(1)
sock, addr = _s.accept()
_s.close()
print('got connection from', addr)
handshake()
threading.Thread(target=listener).start()

while True:
    msg = input()
    sock.send(msg.encode('ascii'))