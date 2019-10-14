from player import *
from board import *
from piece import *

p1 = Player()
p2 = Player()

print("Player 1:")
print("\tdeck size: "+str(len(p1.deck)))
print("\thand size: "+str(len(p1.hand)))
print("\tmana size: "+str(len(p1.mana)))
print("Player 1's hand:")
for h in p1.hand:
    print(h.name)

print("Player 2:")
print("\tdeck size: "+str(len(p2.deck)))
print("\thand size: "+str(len(p2.hand)))
print("\tmana size: "+str(len(p2.mana)))
print("Player 2's hand:")
for h in p2.hand:
    print(h.name)

b = Board()

king1 = Piece("King","K",p1)
king2 = Piece("King","K",p2)
b.addPiece(king1,3,0)
b.addPiece(king2,4,7)

print("Board State:")
b.printBoard()