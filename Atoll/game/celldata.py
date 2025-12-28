from game.enums import CellType
from gui.circlebutton import CircleButton

class CellData:
    def __init__(self, cell_type=CellType.EMPTY):
        self.cell_type = cell_type
        self.mark = None
        self.circle_button = None