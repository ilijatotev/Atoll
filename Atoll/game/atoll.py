from .board import Board
from .enums import GameMode
from .enums import Player
from .enums import CellType
from .enums import CellState
import pygame


class Atoll:
    def __init__(self, board_size, first_player, game_mode):
        self.board = Board(board_size)
        self.game_mode = game_mode
        self.current_player = first_player
        self.last_move = None
        self.board_logic = {}
        self.intialize_board_logic()

    def draw_board(self, screen):
        self.board.draw_board(screen)

    def intialize_board_logic(self):
        for i in range(0, 2*self.board.size):
            for j in range(0,2*self.board.size):
                alphabetic_coordinate = chr(ord("A") + i)
                numeric_coordinate = j + 1
                self.board_logic[(alphabetic_coordinate,numeric_coordinate)] = CellState.EMPTY

    def move(self, coordinates):
        i, j = coordinates
        self.board.board[i][j].cell_type = CellType.WHITE if self.current_player == Player.WHITE else CellType.BLACK
        self.board.update_buttons()
        self.last_move = self.convert_coordinates(i,j)
        self.board_logic[self.convert_coordinates(i,j)] = CellState.WHITE if self.current_player == Player.WHITE else CellState.BLACK
        #print(self.board_logic)
        self.change_player()

    def draw_last_move(self,screen):
        if self.last_move!=None:
            alphabetic_coordinate, numeric_coordinate = self.last_move
            last_move = "Last move: black" if self.current_player == Player.WHITE else "Last move: white"
            last_move = last_move + " (" + alphabetic_coordinate +", " + str(numeric_coordinate) + ")"

            font = pygame.font.Font(None, 28)
            text_surface = font.render(last_move, True, (0, 0, 0))
            screen.blit(text_surface, (700, 20))


    def undo(self):
        pass

    def change_player(self):
        self.current_player = Player.WHITE if self.current_player == Player.BLACK else Player.BLACK

    def check_hover(self, mouse_pos):
        self.board.check_hower(mouse_pos)

    def check_click(self, pos):
        return self.board.check_click(pos)

    def convert_coordinates(self, i, j):
        alphabetic_coordinate = chr(ord("A") + j//2 - 2)
        numeric_coordinate = 3 + 2*i - (self.board.size - (j//2 - 2+1))
        numeric_coordinate = (i - (self.board.size - (j//2-2+1)))//2
        return (alphabetic_coordinate,numeric_coordinate)
    
    def inverse_convert_coordinates(self, alphabetic_coordinate, numeric_coordinate):
        S = self.board.size
        j = 2 * (ord(alphabetic_coordinate) - ord("A") + 2)
        i = 2 * numeric_coordinate + S - (ord(alphabetic_coordinate) - ord("A"))
        return i, j

