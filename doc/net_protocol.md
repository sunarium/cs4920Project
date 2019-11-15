## notes
default port is 11235

if, at anytime, the socket was unexpectedly closed 
a error message shall be displayed and game 
should drop to main menu

## handshake
client connects with timeout of 5 seconds

client send `b'ClientHello'`

server response with `b'ServerWavesBack'`

after handshake timeout is disabled

## protocol

#### **sender** is responsible for the legality of the message!

usage example:
```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
msg = sock.recv(128)
assert msg.startswith(b'<')
while not msg.endswith(b'>'):
    msg += sock.recv(128)
```

---

#### placed card into mana pile:

`b'<PlacedMana|{new mana pool size}>'`

---

#### played a piece `P` to board position `X`, `Y`

`b'<PlacedPiece|{name:str}|{X:int}|{Y:int}>'`

`name` should be one of the piece names

`X` and `Y` are integers

Example:`b'<PlacedPiece|knight|0|3>'`

---

#### moved piece from `<Xold, Yold>` to `<Xnew, Ynew>`

`b'<MovedPiece|{name}|{Xold}|{Yold}|{Xnew}|{Ynew}>'`

Example: moved rook from (1,2) to (5,2)

`b'<MovedPiece|rook|1|2|5|2>'`

---

#### end phase

`b'<NextPhase|{old_phase:int}|{new_phase:int}|{new_handsize:int}>'`

`old_phase` and `new_phase` are integer enum values defined in `GamePhase`

`new_handsize` for displaying

Example `b'<NextPhase|0|1|5>'`

---

#### end turn

`b'<NextTurn|{final_handsize:int}>'`

