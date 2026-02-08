import pygame
from game.board import Board
from game.atoll import Atoll
from common import *
from game.enums import GameMode

def run_game(config):
    board_size = config["board_size"]
    game_mode = config["game_mode"]
    first_player = config["first_player"]
    computer_color = config["computer_color"]
    
    game = Atoll(board_size, first_player, game_mode, computer_color)

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
    pygame.display.set_caption("Atoll")
    icon = pygame.image.load("assets/atoll.png")
    pygame.display.set_icon(icon)

    clock = pygame.time.Clock()
    running = True
    game_over = False
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = game.check_click(event.pos)
                    if click["status"]:
                        game_over = game.move(click["coordinates"])
                        
        if game_mode == GameMode.AI:
            if game.computer_move():
                game_over = True
            

        screen.fill(BACKGROUND_COLOR)
        game.check_hover(mouse_pos)
        game.draw_board(screen)
        game.draw_last_move(screen)
        if game_over:
            game.draw_game_over(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

