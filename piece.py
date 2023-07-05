import pygame as pygame
from pygame.locals import (
    RLEACCEL,
)

class piece(pygame.sprite.Sprite):
    def __init__(self, squareSize, color, type):
        super(piece, self).__init__()
        self.color = color
        self.type = type
        if self.type == "queen":
            self.subtypes = ["rook", "bishop"]
        else:
            self.subtypes = [self.type]

        self.squareSize = squareSize
        self.setIcon()

        #self.currSquare = currSquare
        # self.topLeft = (boardTopLeft[0] + currSquare[0] * squareSize, boardTopLeft[1] + currSquare[1] * squareSize)

    def getSubtypes(self):
        return self.subtypes
    def getColor(self):
        return self.color

    def getType(self):
        return self.type

    def setIcon(self):
        imageFile = "images/"
        if self.color == 0:
            imageFile += "white"
        elif self.color == 1:
            imageFile += "black"
        imageFile += self.type
        imageFile += ".png"
        self.surf = pygame.image.load(imageFile)
        self.surf = pygame.transform.scale(self.surf, (self.squareSize, self.squareSize))
        # self.surf.set_colorkey((255, 255, 255), RLEACCEL)
