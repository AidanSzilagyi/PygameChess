import pygame as pygame

class mouse:
    def __init__(self):
        self.selectedSquare = "empty"

    def selectSquare(self, square):
        self.selectedSquare = square
    def getSelectedSquare(self):
        return self.selectedSquare
