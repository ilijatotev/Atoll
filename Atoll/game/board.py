from .celldata import CellData
from .enums import CellType
from common import *
from gui.circlebutton import CircleButton
import pygame


class Board:
    def __init__(self, size):
        self.size = size
        self.board_size = 4 * size + 5
        self.board = [[CellData(CellType.OUT) for _ in range(
            self.board_size)] for _ in range(self.board_size)]
        self.initialize_board()

    def update_buttons(self):
        cell_size = WINDOW_HEIGHT // self.board_size
        for i in range(self.board_size):
            for j in range(self.board_size):
                cell = self.board[i][j]
                center = (cell_size//2 + j*cell_size,
                          cell_size//2 + i*cell_size)
                radius = cell_size//2 * 1.5
                if cell.cell_type == CellType.EMPTY:
                    self.board[i][j].circle_button = CircleButton(
                        center, radius)
                elif cell.cell_type == CellType.BLACK:
                    self.board[i][j].circle_button = CircleButton(
                        center, radius, (0, 0, 0))
                elif cell.cell_type == CellType.WHITE:
                    self.board[i][j].circle_button = CircleButton(
                        center, radius, (255, 255, 255))

    def initialize_board(self):
        # left side
        j = 2
        k = -3
        step = 1
        for i in range(self.size-k, self.board_size-1-self.size+k, 2):
            if step <= self.size//2:
                self.board[i][j].cell_type = CellType.BLACK
            else:
                self.board[i][j].cell_type = CellType.WHITE
            step += 1

        # right side
        j = self.board_size-3
        k = -3
        step = 1
        for i in range(self.size-k, self.board_size-1-self.size+k, 2):
            if step <= self.size//2:
                self.board[i][j].cell_type = CellType.WHITE
            else:
                self.board[i][j].cell_type = CellType.BLACK
            step += 1

        # left mark
        j = 0
        k = -4
        step = 1
        for i in range(self.size-k, self.size-k + 2*self.size, 2):
            self.board[i][j].cell_type = CellType.MARK
            self.board[i][j].mark = str(step)
            step += 1

        # right mark
        j = self.board_size-1
        step = self.size
        for i in range(self.size, 3*self.size, 2):
            self.board[i][j].cell_type = CellType.MARK
            self.board[i][j].mark = str(step)
            step += 1

        k = 0
        step = 1
        for j in range(4, 4+2*(self.size-1), 2):
            self.board[0][j].cell_type = CellType.MARK
            self.board[0][j].mark = chr(ord('A') + j//2-2)
            self.board[self.board_size-3][j].cell_type = CellType.MARK
            self.board[self.board_size-3][j].mark = chr(ord('A') + j//2-2)

            i_last = (self.size - k) + 2 * ((self.board_size -
                                             2 - self.size + k - (self.size - k)) // 2)
            for i in range(self.size-k, self.board_size-1-self.size+k, 2):
                if i == self.size-k:
                    if step <= self.size//2:
                        self.board[i][j].cell_type = CellType.WHITE
                    else:
                        self.board[i][j].cell_type = CellType.BLACK
                elif i == i_last:
                    if step <= self.size//2:
                        self.board[i][j].cell_type = CellType.BLACK
                    else:
                        self.board[i][j].cell_type = CellType.WHITE
                else:
                    self.board[i][j].cell_type = CellType.EMPTY
            k += 1
            step += 1

        j = 4+2*(self.size-1)
        k = self.size-1
        self.board[0][j].cell_type = CellType.MARK
        self.board[0][j].mark = chr(ord('A') + j//2-2)
        self.board[self.board_size-3][j].cell_type = CellType.MARK
        self.board[self.board_size-3][j].mark = chr(ord('A') + j//2-2)
        for i in range(2+self.size-k, self.board_size-3-self.size+k, 2):
            self.board[i][j].cell_type = CellType.EMPTY

        k = self.size
        step = 1
        for j in range(4+2*(self.size), self.board_size-4, 2):
            self.board[0][j].cell_type = CellType.MARK
            self.board[0][j].mark = chr(ord('A') + j//2-2)
            self.board[self.board_size-3][j].cell_type = CellType.MARK
            self.board[self.board_size-3][j].mark = chr(ord('A') + j//2-2)

            i_last = (2 + self.size - k) + 2 * \
                ((self.board_size - 6 - 2*self.size + 2*k) // 2)
            for i in range(2+self.size-k, self.board_size-3-self.size+k, 2):
                if i == 2+self.size-k:
                    if step <= self.size//2:
                        self.board[i][j].cell_type = CellType.WHITE
                    else:
                        self.board[i][j].cell_type = CellType.BLACK
                elif i == i_last:
                    if step <= self.size//2:
                        self.board[i][j].cell_type = CellType.BLACK
                    else:
                        self.board[i][j].cell_type = CellType.WHITE
                else:
                    self.board[i][j].cell_type = CellType.EMPTY
            k -= 1
            step += 1

        self.update_buttons()

    def draw_board(self, screen):
        cell_size = WINDOW_HEIGHT // self.board_size

        for i in range(self.board_size):
            for j in range(self.board_size):
                cell = self.board[i][j]
                if cell.circle_button != None:
                    cell.circle_button.draw(screen)
                if cell.cell_type == CellType.MARK:
                    center = (cell_size//2 + j*cell_size,
                              cell_size//2 + i*cell_size)
                    self.draw_label(screen, center, cell.mark)

    def draw_label(self, screen, center, label):
        font = pygame.font.SysFont(None, 24)
        text = font.render(label, True, (0, 0, 0))
        rect = text.get_rect(center=center)
        screen.blit(text, rect)

    def check_hower(self, mouse_pos):
        for i in range(self.board_size):
            for j in range(self.board_size):
                cell = self.board[i][j]
                if cell.circle_button == None:
                    continue
                if cell.cell_type == CellType.EMPTY:
                    cell.circle_button.update(mouse_pos)

    def check_click(self, pos):
        for i in range(self.board_size):
            for j in range(self.board_size):
                cell = self.board[i][j]
                if cell.circle_button != None:
                    if cell.circle_button.is_clicked(pos) and cell.cell_type == CellType.EMPTY:
                        return {
                            "status": True,
                            "coordinates": (i, j)
                        }

        return {
            "status": False,
            "coordinates": (i, j)
        }