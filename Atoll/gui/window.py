import pygame
from game.board import Board
from game.atoll import Atoll
from common import *

def run_game(config):
    board_size = config["board_size"]
    game_mode = config["game_mode"] == "AI"
    first_player = config["first_player"]
    
    print(board_size, game_mode, first_player)
    game = Atoll(board_size, first_player, game_mode)

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
    pygame.display.set_caption("Atoll")
    icon = pygame.image.load("assets/atoll.png")
    pygame.display.set_icon(icon)

    clock = pygame.time.Clock()
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = game.check_click(event.pos)
                    if click["status"]:
                        game.move(click["coordinates"])


        screen.fill(BACKGROUND_COLOR)
        game.check_hover(mouse_pos)
        game.draw_board(screen)
        game.draw_last_move(screen)
        pygame.display.flip()
        # print("UNesite potez")
        # line = input()
        # alphabetic_coordinate = line[0]
        # numeric_coordinate = int(line[1:])
        # i,j = game.inverse_convert_coordinates(alphabetic_coordinate,numeric_coordinate)
        # game.move((i,j))
        clock.tick(60)

    pygame.quit()

