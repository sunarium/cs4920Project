from piece import *

class Board:
    def __init__(self):
        self.boardState = [[0 for i in range(8)] for j in range(8)]

    def addPiece(self,p,x,y):
        self.boardState[x][y] = p

    def printBoard(self):
        for j in range(8):
            for i in range(8):
                if(self.boardState[i][j] == 0):
                    print("0 ",end=" ")
                else:
                    print(self.boardState[i][j].nick + " ",end=" ")
            print("\n")
