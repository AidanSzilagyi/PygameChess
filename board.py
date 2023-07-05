from square import square
from piece import piece
from utility import utility
import pygame as pygame
import random
import copy


class board:
    def __init__(self, BoardTopLeft, SquareSize, NumSquares):
        self.SquareSize = SquareSize
        self.BoardTopLeft = BoardTopLeft
        self.NumSquares = NumSquares
        self.colorToPlay = 0
        self.castling = [0, 0, 0, 0]
        self.passant = [-1, -1]
        self.prevMove = [[-1, -1, "empty"]]

        self.squares = [[] for _ in range(NumSquares[0])]
        for i in range(NumSquares[0]):
            for j in range(NumSquares[1]):
                self.squares[i].append(square(BoardTopLeft, SquareSize, i, j))

    def generateDefault(self):
        self.colorToPlay = 0
        self.castling = [1, 1, 1, 1]
        for i in range(2):
            for j in range(8):
                self.squares[j][6 - 5 * i].replacePiece(piece(self.SquareSize, i, "pawn"))
            self.squares[0][7 - 7 * i].replacePiece(piece(self.SquareSize, i, "rook"))
            self.squares[1][7 - 7 * i].replacePiece(piece(self.SquareSize, i, "knight"))
            self.squares[2][7 - 7 * i].replacePiece(piece(self.SquareSize, i, "bishop"))
            self.squares[3][7 - 7 * i].replacePiece(piece(self.SquareSize, i, "queen"))
            self.squares[4][7 - 7 * i].replacePiece(piece(self.SquareSize, i, "king"))
            self.squares[5][7 - 7 * i].replacePiece(piece(self.SquareSize, i, "bishop"))
            self.squares[6][7 - 7 * i].replacePiece(piece(self.SquareSize, i, "knight"))
            self.squares[7][7 - 7 * i].replacePiece(piece(self.SquareSize, i, "rook"))

    def generateGameModeOne(self):
        self.level = 1
        self.targetSquare = self.squares[0][0]
        self.loadLevel()

    def getSquare(self, column, row):
        return self.squares[column][row]

    def swapColorToPlay(self):
        if self.colorToPlay == 0:
            self.colorToPlay = 1
        elif self.colorToPlay == 1:
            self.colorToPlay = 0

    def getColorToPlay(self):
        return self.colorToPlay

    def clearBoard(self):
        for i in range(self.NumSquares[0]):
            for j in range(self.NumSquares[1]):
                self.squares[i][j].replacePiece("empty")

    def executeMove(self, start, dest):

        # Disable Castling
        if "king" in start.getPiece().getSubtypes():
            self.castling[start.getPiece().getColor() * 2] = 0
            self.castling[start.getPiece().getColor() * 2 + 1] = 0
        elif (start.column == 0 or start.column == 7) and (start.row == 0 or start.row == 7):
            self.castling[(start.column // 7) + (start.row // 7) + start.getPiece().getColor()] = 0

        # Castling
        if "king" in start.getPiece().getSubtypes() and \
                (start.column - dest.column == 2 or start.column - dest.column == -2):
            # Move King
            self.squares[dest.column][dest.row].replacePiece(self.squares[start.column][start.row].getPiece())
            self.squares[start.column][start.row].replacePiece("empty")

            # Move Rook
            if start.column - dest.column == -2:  # Short Castling
                self.squares[dest.column - 1][dest.row].replacePiece(self.squares[start.column + 3][start.row].getPiece())
                self.squares[start.column + 3][start.row].replacePiece("empty")
            if start.column - dest.column == 2:  # Long Castling
                self.squares[dest.column + 1][dest.row].replacePiece(self.squares[start.column - 4][start.row].getPiece())
                self.squares[start.column - 4][start.row].replacePiece("empty")
            self.swapColorToPlay()


        else:
            # En Passant
            if "pawn" in self.squares[start.column][start.row].getPiece().getSubtypes() and \
                    start.column != dest.column and self.squares[dest.column][dest.row].getPiece() == "empty":
                self.squares[dest.column][start.row].replacePiece("empty")
            # Regular Moves
            self.squares[dest.column][dest.row].replacePiece(self.squares[start.column][start.row].getPiece())
            self.squares[start.column][start.row].replacePiece("empty")
            self.swapColorToPlay()
            self.prevMove.append([dest.column, dest.row, self.squares[dest.column][dest.row].getPiece().getType()])

        # Update en passant
        if "pawn" in self.squares[dest.column][dest.row].getPiece().getSubtypes() and \
            (start.row - dest.row == -2 or start.row - dest.row == 2):
            self.passant = [start.column, (start.row + dest.row) // 2]
        else:
            self.passant = [-1, -1]

        # Promotion
        if "pawn" in self.squares[dest.column][dest.row].getPiece().getSubtypes() \
                and dest.row == dest.getPiece().getColor() * 7:
            self.colorToPlay = 2
            return [dest.column, dest.row]
        return [-1, -1]

    def promote(self, pos, pieceType):
        color = self.squares[pos[0]][pos[1]].getPiece().getColor()
        self.squares[pos[0]][pos[1]].replacePiece(piece(self.SquareSize, color, pieceType))
        self.colorToPlay = 1 - color

    def isLegalMove(self, start, dest):
        PsuedoLegalMoves = self.findPseudoLegalMoves(start.getPos())
        ActualLegalMoves = []
        for i in range(len(PsuedoLegalMoves)):
            if self.determineLegality(start, [PsuedoLegalMoves[i].column, PsuedoLegalMoves[i].row]):
                ActualLegalMoves.append(PsuedoLegalMoves[i])

        for i in range(len(ActualLegalMoves)):
            if dest == ActualLegalMoves[i]:
                return True
        return False

    def getAllLegalMoves(self):
        # get All Psuedolegal Moves
        PsuedoLegalMoves = []
        for i in range(self.NumSquares[0]):
            for j in range(self.NumSquares[1]):
                p = []
                if self.squares[i][j].getPiece() != "empty" and \
                   self.squares[i][j].getPiece().getColor() == self.colorToPlay:
                    p.extend(self.findPseudoLegalMoves([i, j]))
                for k in range(len(p)):
                    PsuedoLegalMoves.append([self.squares[i][j], [p[k].column, p[k].row]])

        # Check if they are Legal
        ActualLegalMoves = []
        for i in range(len(PsuedoLegalMoves)):
            if self.determineLegality(PsuedoLegalMoves[i][0], PsuedoLegalMoves[i][1]):
                ActualLegalMoves.append(PsuedoLegalMoves[i])
        return ActualLegalMoves
    """
    def getPieceLegalMoves(self, pieceLoc):
        PsuedoLegalMoves = []
        p = []
        if self.squares[pieceLoc[0]][pieceLoc[1]].getPiece() != "empty" and \
                self.squares[pieceLoc[0]][pieceLoc[1]].getPiece().getColor() == self.colorToPlay:
            p = self.findPseudoLegalMoves([pieceLoc[0]][pieceLoc[1]])
        for k in range(len(p)):
            PsuedoLegalMoves.append([self.squares[pieceLoc[0]][pieceLoc[1]], [p[k].column, p[k].row]])

        # Check if they are Legal
        ActualLegalMoves = []
        for i in range(len(PsuedoLegalMoves)):
            if self.determineLegality(PsuedoLegalMoves[i][0], PsuedoLegalMoves[i][1]):
                ActualLegalMoves.append(PsuedoLegalMoves[i])
        return ActualLegalMoves
    """
    def findPseudoLegalMoves(self, start):
        PieceColor = self.squares[start[0]][start[1]].getPiece().getColor()
        AllPossibleDests = []

        RealPieceType = self.squares[start[0]][start[1]].getPiece().getType()
        Subpiece = [RealPieceType]
        if RealPieceType == "queen":
            Subpiece = ["rook", "bishop"]
        for a in range(len(Subpiece)):
            PieceType = Subpiece[a]
            if PieceType == "rook" or PieceType == "bishop":
                Direction = []
                if PieceType == "rook":
                    Direction = [[1, 0], [0, 1], [-1, 0], [0, -1]]  # right, down, left, up
                if PieceType == "bishop":
                    Direction = [[1, 1], [1, -1], [-1, -1], [-1, 1]]

                for i in range(4):
                    anotherSquare = True
                    j = 1
                    while anotherSquare:
                        posCheck = [start[0] + j * Direction[i][0], start[1] + j * Direction[i][1]]
                        if self.isOnBoard(posCheck):
                            squareCheck = self.squares[posCheck[0]][posCheck[1]]
                            # checks if the square is empty
                            if squareCheck.getPiece() != "empty":
                                # checks if friendly or enemy piece
                                if squareCheck.getPiece().getColor() == PieceColor:
                                    anotherSquare = False
                                else:
                                    AllPossibleDests.append(squareCheck)
                                    anotherSquare = False
                            else:
                                AllPossibleDests.append(squareCheck)
                        else:
                            anotherSquare = False
                        j += 1
            elif PieceType == "knight":
                PotentialPos = [[start[0] + 2, start[1] - 1], [start[0] + 2, start[1] + 1],
                                [start[0] + 1, start[1] + 2],
                                [start[0] - 1, start[1] + 2], [start[0] - 2, start[1] + 1],
                                [start[0] - 2, start[1] - 1],
                                [start[0] - 1, start[1] - 2], [start[0] + 1, start[1] - 2]]
                for i in range(len(PotentialPos)):
                    if self.isOnBoard(PotentialPos[i]):
                        AllPossibleDests.append(self.squares[PotentialPos[i][0]][PotentialPos[i][1]])

            elif PieceType == "pawn":
                # One and two squares in front of the pawn
                if self.squares[start[0]][start[1] + (PieceColor * 2 - 1)].getPiece() == "empty":
                    AllPossibleDests.append(self.squares[start[0]][start[1] + (PieceColor * 2 - 1)])
                    if start[1] == -5 * PieceColor + 6 and self.squares[start[0]][
                        start[1] + (PieceColor * 4 - 2)].getPiece() == "empty":
                        AllPossibleDests.append(self.squares[start[0]][start[1] + (PieceColor * 4 - 2)])
                # Left Capture
                if start[0] - 1 >= 0 and self.squares[start[0] - 1][start[1] + (PieceColor * 2 - 1)].getPiece() != "empty" \
                        and self.squares[start[0] - 1][start[1] + (PieceColor * 2 - 1)].getPiece().getColor() != PieceColor:
                    AllPossibleDests.append(self.squares[start[0] - 1][start[1] + (PieceColor * 2 - 1)])
                # Right Capture
                if start[0] + 1 < self.NumSquares[0] and self.squares[start[0] + 1][start[1] + (PieceColor * 2 - 1)].getPiece() != "empty" \
                        and self.squares[start[0] + 1][start[1] + (PieceColor * 2 - 1)].getPiece().getColor() != PieceColor:
                    AllPossibleDests.append(self.squares[start[0] + 1][start[1] + (PieceColor * 2 - 1)])
                # En Passant
                if self.passant[0] != -1 and start[1] + PieceColor * 2 - 1 == self.passant[1] and \
                        (start[1] == self.passant[1] - 1 or start[1] == self.passant[1] + 1):
                    AllPossibleDests.append(self.squares[self.passant[0]][self.passant[1]])


            elif PieceType == "king":
                v = [-1, 0, 1]
                for i in range(3):
                    for j in range(3):
                        if (i != 1 or j != 1) and self.isOnBoard([start[0] + v[i], start[1] + v[j]]) and \
                                (self.squares[start[0] + v[i]][start[1] + v[j]].getPiece() == "empty" or
                                 self.squares[start[0] + v[i]][start[1] + v[j]].getPiece().getColor() != PieceColor):
                            AllPossibleDests.append(self.squares[start[0] + v[i]][start[1] + v[j]])

                # Castling
                # self.castling / 2 = color, self.castling % 2 = 0 ---> short
                kingLoc = self.findKing(PieceColor)
                if self.castling[PieceColor * 2] == 1:  # short
                    anotherSquare = True
                    j = 1
                    while anotherSquare:
                        if self.isOnBoard([kingLoc[0] + j, kingLoc[1]]):
                            if self.squares[kingLoc[0] + j][kingLoc[1]].getPiece() == "empty":
                                j += 1
                            elif self.squares[kingLoc[0] + j][kingLoc[1]].getPiece().getType() == "rook":
                                anotherSquare = False
                                AllPossibleDests.append(self.squares[kingLoc[0] + 2][kingLoc[1]])
                            else:
                                anotherSquare = False
                if self.castling[PieceColor * 2 + 1] == 1:  # long
                    anotherSquare = True
                    j = -1
                    while anotherSquare:
                        if self.isOnBoard([kingLoc[0] + j, kingLoc[1]]):
                            if self.squares[kingLoc[0] + j][kingLoc[1]].getPiece() == "empty":
                                j -= 1
                            elif self.squares[kingLoc[0] + j][kingLoc[1]].getPiece().getType() == "rook":
                                anotherSquare = False
                                AllPossibleDests.append(self.squares[kingLoc[0] - 2][kingLoc[1]])
                            else:
                                anotherSquare = False

        return AllPossibleDests

    def determineLegality(self, start, dest):
        # Create a deep copy of the current board
        newBoard = board([800, 100], 50, [self.NumSquares[0], self.NumSquares[1]])
        color = self.squares[start.column][start.row].getPiece().getColor()
        for i in range(self.NumSquares[0]):
            for j in range(self.NumSquares[1]):
                newBoard.squares[i][j].replacePiece(self.squares[i][j].getPiece())

        # Update the copy with the move made
        # Castling
        if "king" in self.squares[start.column][start.row].getPiece().getSubtypes() and \
                (start.column - dest[0] == 2 or start.column - dest[0] == -2):
            kingPiece = self.squares[start.column][start.row].getPiece()
            j = 0
            if start.column - dest[0] == -2:
                j = -1
            if start.column - dest[0] == 2:
                j = 1
            works = newBoard.isInCheck(color)
            newBoard.squares[start.column + j][start.row].replacePiece(kingPiece)
            newBoard.squares[start.column][start.row].replacePiece("empty")
            works = works and newBoard.isInCheck(color)
            newBoard.squares[start.column + 2 * j][start.row].replacePiece(kingPiece)
            newBoard.squares[start.column + j][start.row].replacePiece("empty")
            works and newBoard.isInCheck(color)
            return works

        # En passant
        elif "pawn" in self.squares[start.column][start.row].getPiece().getSubtypes() and dest == self.passant:
            newBoard.squares[dest[0]][dest[1]].replacePiece(newBoard.squares[start.column][start.row].getPiece())
            newBoard.squares[start.column][start.row].replacePiece("empty")
            newBoard.squares[dest[1]][start.row].replacePiece("empty")
        else:
            newBoard.squares[dest[0]][dest[1]].replacePiece(newBoard.squares[start.column][start.row].getPiece())
            newBoard.squares[start.column][start.row].replacePiece("empty")

        return newBoard.isInCheck(color)

    def isInCheck(self, color):

        kingLoc = self.findKing(color)

        # Find if a move can capture the king
        for i in range(self.NumSquares[0]):
            for j in range(self.NumSquares[1]):
                if self.squares[i][j].getPiece() != "empty" and \
                        self.squares[i][j].getPiece().getColor() == 1 - color:
                    legalMoves = self.findPseudoLegalMoves([i, j])
                    for k in range(len(legalMoves)):
                        if [legalMoves[k].column, legalMoves[k].row] == kingLoc:
                            return False
        return True

    def findKing(self, color):
        for i in range(self.NumSquares[0]):
            for j in range(self.NumSquares[1]):
                kingPiece = self.squares[i][j].getPiece()
                if kingPiece != "empty" and kingPiece.getType() == "king" \
                        and kingPiece.getColor() == color:
                    return [i, j]

    def isOnBoard(self, pos):
        if 0 <= pos[0] < self.NumSquares[0] and 0 <= pos[1] < self.NumSquares[1]:
            return True
        return False

    def CheckIfOnBoard(self):
        pos = pygame.mouse.get_pos()
        if utility.contains(pos, self.BoardTopLeft, (self.BoardTopLeft[0] + self.SquareSize * self.NumSquares[0],
                                                     self.BoardTopLeft[1] + self.SquareSize * self.NumSquares[1])):
            for i in range(self.NumSquares[0]):
                for j in range(self.NumSquares[1]):
                    TopLeft = (self.BoardTopLeft[0] + self.SquareSize * i, self.BoardTopLeft[1] + self.SquareSize * j)
                    BottomRight = (TopLeft[0] + self.SquareSize, TopLeft[1] + self.SquareSize)
                    if utility.contains(pos, TopLeft, BottomRight):
                        return tuple((i, j))
        return tuple((-1, -1))

    def checkIfPromotion(self, piecePos):
        mousePos = pygame.mouse.get_pos()
        color = self.squares[piecePos[0]][piecePos[1]].getPiece().getColor()
        TopLeft = [self.BoardTopLeft[0] + self.SquareSize * piecePos[0] - 1.5 * self.SquareSize,
                   self.BoardTopLeft[1] + 9 * color * self.SquareSize - self.SquareSize]
        BottomRight = [self.BoardTopLeft[0] + self.SquareSize * piecePos[0] + 2.5 * self.SquareSize,
                       self.BoardTopLeft[1] + 9 * color * self.SquareSize]

        if utility.contains(mousePos, TopLeft, BottomRight):
            if TopLeft[0] < mousePos[0] < TopLeft[0] + self.SquareSize:
                return "queen"
            if TopLeft[0] + self.SquareSize < mousePos[0] < TopLeft[0] + self.SquareSize * 2:
                return "knight"
            if TopLeft[0] + self.SquareSize * 2 < mousePos[0] < TopLeft[0] + self.SquareSize * 3:
                return "rook"
            if TopLeft[0] + self.SquareSize * 3 < mousePos[0] < TopLeft[0] + self.SquareSize * 4:
                return "bishop"
        else:
            return "empty"

    def checkLevel(self):
        if self.targetSquare.getPiece() != "empty" and self.targetSquare.getPiece().getType() == "queen" \
           and self.targetSquare.getPiece().getColor() == 0:
            self.level += 1
            pygame.time.wait(2000)
            self.loadLevel()

    def loadLevel(self):
        self.clearBoard()
        self.moveNum = 1
        self.colorToPlay = 0
        if self.level == 1:
            self.targetSquare = self.squares[0][0]
            self.turnsLeft = 3

            self.squares[3][7].replacePiece(piece(self.SquareSize, 0, "king"))
            self.squares[7][0].replacePiece(piece(self.SquareSize, 1, "king"))
            self.squares[7][1].replacePiece(piece(self.SquareSize, 1, "pawn"))
            self.squares[6][1].replacePiece(piece(self.SquareSize, 1, "pawn"))
            self.squares[0][5].replacePiece(piece(self.SquareSize, 0, "pawn"))
            self.squares[1][6].replacePiece(piece(self.SquareSize, 0, "pawn"))
            self.squares[2][6].replacePiece(piece(self.SquareSize, 0, "pawn"))
            self.squares[3][6].replacePiece(piece(self.SquareSize, 0, "pawn"))
            self.squares[6][0].replacePiece(piece(self.SquareSize, 1, "rook"))
            self.squares[0][7].replacePiece(piece(self.SquareSize, 0, "rook"))
            self.squares[4][7].replacePiece(piece(self.SquareSize, 0, "queen"))
            self.squares[6][3].replacePiece(piece(self.SquareSize, 1, "knight"))
            self.squares[1][3].replacePiece(piece(self.SquareSize, 1, "pawn"))
            self.squares[5][2].replacePiece(piece(self.SquareSize, 1, "bishop"))
            self.squares[1][2].replacePiece(piece(self.SquareSize, 1, "pawn"))

        elif self.level == 2:
            self.targetSquare = self.squares[6][6]
            self.turnsLeft = 2
            self.squares[7][0].replacePiece(piece(self.SquareSize, 0, "king"))
            self.squares[4][1].replacePiece(piece(self.SquareSize, 1, "king"))
            self.squares[0][0].replacePiece(piece(self.SquareSize, 0, "queen"))
            self.squares[3][3].replacePiece(piece(self.SquareSize, 0, "pawn"))
            self.squares[4][3].replacePiece(piece(self.SquareSize, 0, "pawn"))
            self.squares[7][1].replacePiece(piece(self.SquareSize, 0, "pawn"))
            self.squares[3][7].replacePiece(piece(self.SquareSize, 1, "queen"))

        elif self.level == 3:
            self.targetSquare = self.squares[6][1]
            self.turnsLeft = 2
            self.squares[0][0].replacePiece(piece(self.SquareSize, 1, "king"))
            self.squares[0][5].replacePiece(piece(self.SquareSize, 0, "king"))
            self.squares[0][4].replacePiece(piece(self.SquareSize, 0, "pawn"))
            self.squares[1][5].replacePiece(piece(self.SquareSize, 0, "pawn"))
            self.squares[0][1].replacePiece(piece(self.SquareSize, 1, "pawn"))
            self.squares[1][1].replacePiece(piece(self.SquareSize, 1, "pawn"))

            self.squares[6][5].replacePiece(piece(self.SquareSize, 0, "bishop"))
            self.squares[6][6].replacePiece(piece(self.SquareSize, 0, "queen"))
            self.squares[3][3].replacePiece(piece(self.SquareSize, 1, "rook"))
        elif self.level == 4:
            self.targetSquare = self.squares[3][1]
            self.turnsLeft = 3
            self.squares[0][1].replacePiece(piece(self.SquareSize, 1, "pawn"))
            self.squares[0][4].replacePiece(piece(self.SquareSize, 0, "pawn"))
            self.squares[2][2].replacePiece(piece(self.SquareSize, 0, "pawn"))
            self.squares[2][1].replacePiece(piece(self.SquareSize, 1, "pawn"))
            self.squares[4][1].replacePiece(piece(self.SquareSize, 1, "pawn"))
            self.squares[4][2].replacePiece(piece(self.SquareSize, 0, "bishop"))
            self.squares[4][0].replacePiece(piece(self.SquareSize, 0, "rook"))
            self.squares[5][7].replacePiece(piece(self.SquareSize, 0, "king"))
            self.squares[0][5].replacePiece(piece(self.SquareSize, 1, "king"))
            self.squares[3][2].replacePiece(piece(self.SquareSize, 1, "bishop"))
            self.squares[6][1].replacePiece(piece(self.SquareSize, 0, "queen"))

    def gameModeOneAlgo(self):
        #prevMove is column, row, piece

        # Level One
        if self.level == 1:
            if not self.isInCheck(1):
                self.makeRandomMove()
            elif self.prevMove[-1][1] == 0 and self.prevMove[-1][2] == "queen" and self.prevMove[-1][0] != 0:
                self.executeMove(self.squares[6][0], self.squares[self.prevMove[0]][0])
            elif self.prevMove[-1] == [4, 1, "queen"]:
                self.executeMove(self.squares[5][2], self.squares[4][1])
            elif self.prevMove[-1] == [4, 2, "queen"]:
                self.executeMove(self.squares[6][3], self.squares[4][2])
            elif self.prevMove[-1] == [4, 3, "queen"]:
                self.executeMove(self.squares[5][2], self.squares[4][3])
            elif self.prevMove[-1] == [4, 4, "queen"] and self.squares[6][3].getPiece() != "empty":
                self.executeMove(self.squares[6][3], self.squares[4][4])

            elif self.prevMove[-1] == [0, 3, "queen"] and self.squares[1][2].getPiece() != "empty":
                self.executeMove(self.squares[1][2], self.squares[0][3])
            elif self.prevMove[-1] == [5, 5, "queen"] and self.squares[6][3].getPiece() != "empty":
                self.executeMove(self.squares[6][3], self.squares[5][5])
            elif self.prevMove[-1] == [7, 7, "queen"] or self.prevMove[-1] == [6, 6, "queen"]:
                self.executeMove(self.squares[6][3], self.squares[4][4])
            else:
                if self.squares[7][1].getPiece() != "empty":
                    self.executeMove(self.squares[7][1], self.squares[7][2])
                elif self.squares[7][2].getPiece() != "empty":
                    self.executeMove(self.squares[7][2], self.squares[7][3])
                else:
                    self.makeRandomMove()

        # Level Two
        elif self.level == 2:
            if not self.isInCheck(1):
                self.makeRandomMove()
            elif self.prevMove[-1] == [0, 6, "queen"]:
                self.executeMove(self.squares[3][7], self.squares[3][6])
            elif self.prevMove[-1] == [6, 0, "queen"]:
                self.executeMove(self.squares[3][7], self.squares[6][4])
            else:
                self.makeRandomMove()

        elif self.level == 3:
            if not self.isInCheck(1):
                self.makeRandomMove()
            elif self.prevMove[-1] == [1, 6, "queen"]:
                self.executeMove(self.squares[3][3], self.squares[3][4])
            elif self.prevMove[-1] == [4, 3, "bishop"]:
                self.executeMove(self.squares[3][3], self.squares[4][3])
            elif self.prevMove[-1][2] == "bishop":
                self.executeMove(self.squares[3][3], self.squares[6][3])
            else:
                self.executeMove(self.squares[0][1], self.squares[0][2])

        elif self.level == 4:
            if self.prevMove[-1] == [4,1, "queen"]:
                self.executeMove(self.squares[3][2], self.squares[4][1])
            elif self.moveNum == 1:
                # Checks (good)
                if self.prevMove[-1] == [6, 5, "queen"]:
                    self.executeMove(self.squares[3][2], self.squares[6][5])
                elif not self.isInCheck(1):
                    self.makeRandomMove()
                    # Non-checks
                elif self.prevMove[-1] == [0, 3, "pawn"]:
                    self.executeMove(self.squares[0][5], self.squares[0][4])
                elif self.prevMove[-1] == [6,4, "queen"]:
                    self.executeMove(self.squares[0][5], self.squares[1][6])
                elif self.prevMove[-1] == [3, 4, "queen"]:
                    self.executeMove(self.squares[0][1], self.squares[0][2])
                else:
                    self.executeMove(self.squares[0][1], self.squares[0][2])
                #else:
                    #self.makeRandomMove()
            elif self.moveNum == 2:
                # Checks
                if self.prevMove[-3] == [2, 5, "queen"] and self.prevMove[-1] == [3,4, "queen"]:
                    self.executeMove(self.squares[0][4], self.squares[0][3])
                elif not self.isInCheck(1):
                    self.makeRandomMove()
                # Non-checks
                elif self.prevMove[-3] == [0, 3, "pawn"] and self.prevMove[-1] == [3, 4, "queen"]:
                    self.executeMove(self.squares[0][4], self.squares[0][3])
                elif (self.prevMove[-1] == [6, 4, "queen"] or self.prevMove[-3] == [6, 4, "queen"]) and \
                        (self.prevMove[-1][2] == "bishop" or self.prevMove[-3][2] == "bishop"):
                    self.executeMove(self.squares[4][1], self.squares[4][2])
                elif self.prevMove[-3] == [4, 1, "rook"] and self.prevMove[-1][2] == "rook":
                    self.executeMove(self.squares[3][2], self.squares[4][1])

                elif self.squares[0][3].getPiece() == "empty" and self.squares[0][2].getPiece() != "empty" and \
                        self.squares[0][2].getPiece().getType() == "pawn":
                    self.executeMove(self.squares[0][2], self.squares[0][3])
                elif self.squares[0][2].getPiece() == "empty" and self.squares[0][1].getPiece() != "empty" and \
                        self.squares[0][1].getPiece().getType() == "pawn":
                    self.executeMove(self.squares[0][1], self.squares[0][2])
                elif self.prevMove[-3][2] != "queen" and self.prevMove[-3][2] != "queen":
                    self.executeMove(self.squares[3][2], self.squares[2][3])
                else:
                    self.makeRandomMove()
        self.moveNum += 1
# elif self.moveNum == 1:

    def makeRandomMove(self):
        moves = self.getAllLegalMoves()
        num = random.randint(0, len(moves) - 1)
        self.executeMove(moves[num][0], self.squares[moves[num][1][0]][moves[num][1][1]])

    #def makeRandomMoveWithPiece(self):

    #    moves = self.getPieceLegalMoves(self.findKing(1))
    #    if len(moves) == 0:
    #        return False
    #    num = random.randint(0, len(moves) - 1)
    #    self.executeMove(moves[num][0], self.squares[moves[num][1][0]][moves[num][1][1]])
    #    return True