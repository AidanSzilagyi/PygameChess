import pygame as pygame
from square import square
from piece import piece
from mouse import mouse
from board import board

"""
Queen's Escape Solutions (gameMode == 1):
Level 1: 1. Qh1 Ne4 2. Qxe4 h6 3. Qa8
Level 2: 1. d6+ Qxd6 2. Qg2
Level 3: 1. Be5 Rxe5 2. Qg7
Level 4: 1. Qd4 a6 2. a5 Bc5 3. Qd7
"""

def main():

    # Setting up the Window
    print(pygame.init())
    screenWidth = 1280
    screenHeight = 920
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 36)

    # Board Parameters (column, row)
    BoardTopLeft = (300, 150)
    SquareSize = 75
    NumSquares = (8, 8)
    Board = board(BoardTopLeft, SquareSize, NumSquares)
    promotionLoc = [-1, -1]
    gameOver = False
    moveMade = False

    # Mouse
    Mouse = mouse()

    # Game Mode (0 -> Regular Chess, 1 -> Queen's Escape)
    gameMode = 1
    if gameMode == 0:
        Board.generateDefault()
    if gameMode == 1:
        Board.generateGameModeOne()
        moveMade = False

    running = True
    while running:
        # Poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and gameMode == 1:
                    Board.loadLevel()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if promotionLoc[0] != -1:
                    piecePromoted = Board.checkIfPromotion(promotionLoc)
                    if piecePromoted != "empty":
                        Board.promote(promotionLoc, piecePromoted)
                        promotionLoc = [-1, -1]
                else:
                    loc = Board.CheckIfOnBoard()
                    if loc[0] != -1 and loc[1] != -1:
                        CurrSquare = Mouse.getSelectedSquare()
                        TargetSquare = Board.getSquare(loc[0], loc[1])
                        if TargetSquare.getPiece() != "empty" and TargetSquare.getPiece().getColor() == Board.getColorToPlay():
                            Mouse.selectSquare(TargetSquare)
                        elif Mouse.getSelectedSquare() != "empty" and Board.isLegalMove(CurrSquare, TargetSquare):
                            Mouse.selectSquare("empty")
                            promotionLoc = Board.executeMove(CurrSquare, TargetSquare)
                            if gameMode == 1:
                                Board.turnsLeft -= 1
                                moveMade = True

        screen.fill((225, 225, 225))


        if gameMode == 1:
            textPos = (BoardTopLeft[0],
                       BoardTopLeft[1] - 40)
            font = pygame.font.SysFont("Arial", 20)
            txtsurf = font.render("Get the Queen to the highlighted square in the fewest moves", True, (0, 0, 0))
            screen.blit(txtsurf, textPos)

        # Checkmate:
        if gameMode == 0 and Board.getAllLegalMoves() == []:
            textPos = (BoardTopLeft[0],
                       BoardTopLeft[1] - 40)
            font = pygame.font.SysFont("Arial", 36)
            txtsurf = font.render("Checkmate!", True, (0, 0, 0))
            screen.blit(txtsurf, textPos)

        # Render the game
        # Render the board and the Pieces
        for i in range(NumSquares[0]):
            for j in range(NumSquares[1]):
                if Board.getSquare(i, j).getPiece() != "empty":
                    Board.getSquare(i, j).surf.blit(Board.getSquare(i, j).getPiece().surf, (0,0))
                screen.blit(Board.getSquare(i, j).surf, Board.getSquare(i, j).getTopLeft())

        # Render Promotion Options
        if promotionLoc[0] != -1:
            color = Board.squares[promotionLoc[0]][promotionLoc[1]].getPiece().getColor()
            TopLeft = [Board.BoardTopLeft[0] + Board.SquareSize * promotionLoc[0] - 1.5 * Board.SquareSize,
                       Board.BoardTopLeft[1] + 9 * color * Board.SquareSize - Board.SquareSize]
            if color == 0:
                surf = pygame.image.load("images/whitepromotion.png")
            if color == 1:
                surf = pygame.image.load("images/blackpromotion.png")
            surf = pygame.transform.scale(surf, (Board.SquareSize * 4, Board.SquareSize))
            screen.blit(surf, TopLeft)
        # Render target square and number of turns left
        if gameMode == 1:
            TargetSquareTopLeft = [BoardTopLeft[0] + SquareSize * Board.targetSquare.column,
                                   BoardTopLeft[1] + SquareSize * Board.targetSquare.row]
            targetSurf = pygame.image.load("images/targetsquare.png")
            targetSurf = pygame.transform.scale(targetSurf, (Board.SquareSize, Board.SquareSize))
            screen.blit(targetSurf, TargetSquareTopLeft)

            textPos = (BoardTopLeft[0] + SquareSize * NumSquares[0] + 100, BoardTopLeft[1] + (SquareSize * NumSquares[1] / 2) - 18)
            font = pygame.font.SysFont("Arial", 36)
            txtsurf = font.render("Turns Left: " + str(Board.turnsLeft), True, (0, 0, 0))
            screen.blit(txtsurf, textPos)

        # Display the game
        pygame.display.flip()
        clock.tick(120)  # limits FPS to 60



        # AI Move and Advance to the next Level:
        if gameMode == 1:
            Board.checkLevel()
            if Board.turnsLeft < 1:
                pygame.time.wait(1000)
                Board.loadLevel()
            if Board.getColorToPlay() == 1:
                Board.gameModeOneAlgo()

        if moveMade:
            pygame.time.wait(750)
            moveMade = False

    pygame.quit()

main()