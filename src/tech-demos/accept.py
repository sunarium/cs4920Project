import socket
import threading


d = {
    'socket':None,
    'addr': None
}


def sock_accept(res):
    _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _s.bind(('127.0.0.1', 9999))
    _s.listen(0)
    _sock, addr = _s.accept()
    _sock.setblocking(False)
    res['socket'] = _sock
    res['addr'] = addr


threading.Thread(target=sock_accept, args=(d,)).start()
while True:
    if not d['socket']:
        print('nada')
    else:
        try:
            message = d['socket'].recv(1024)
            if message == b'':
                print('socket closed')
                break
            else:
                print(message.decode('ascii'), end='')
        except socket.error:
            pass