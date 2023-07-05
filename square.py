import pygame as pygame


class square(pygame.sprite.Sprite):
    def __init__(self, boardTopLeft, size, column, row):
        super(square, self).__init__()
        self.topLeft = (boardTopLeft[0] + column * size, boardTopLeft[1] + row * size)
        self.size = size
        self.column = column
        self.row = row
        self.piece = "empty"

        self.setSurface()

    def setSurface(self):
        self.surf = pygame.Surface((self.size, self.size))
        if (self.column + self.row + 1) % 2 == 1:
            self.surf.fill((238, 238, 210, 255))
        else:
            self.surf.fill((119, 150, 86, 255))
        # self.rect = self.surf.get_rect()

    def getPiece(self):
        return self.piece
    def getPos(self):
        return self.column, self.row

    def replacePiece(self, piece):
        self.piece = piece
        self.setSurface()

    def getTopLeft(self):
        return self.topLeft
