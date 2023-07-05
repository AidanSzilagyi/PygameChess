

class utility:
    def contains(Point, TopLeft, BottomRight):
        if TopLeft[0] < Point[0] < BottomRight[0] and TopLeft[1] < Point[1] < BottomRight[1]:
                return True
        return False
