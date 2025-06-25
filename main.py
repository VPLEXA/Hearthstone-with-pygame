import pygame
import sys
from game_config import *
from game_objects import GameBoard
from cards_classes import *
from start_screen import *


def main(hero_paths):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(8)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption('Hearthstone by pygame')
    pygame.mixer.Channel(0).play(pygame.mixer.Sound('Game_for_OPD/assets/music/2-01 Pull up a Chair.mp3'), loops=-1)
    clock = pygame.time.Clock()
    game_board = GameBoard(hero_paths)
    End_turn_btn = Button(1750, 550, 150, 70, "EndTurn", RED, (255, 100, 100))

    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if End_turn_btn.is_clicked(pygame.mouse.get_pos(), event):
                if not game_board.turn_transition:
                    game_board.turn_transition = True
                    End_turn_btn.set_text("StartTurn")
                else:
                    game_board._end_turn()
                    game_board.turn_transition = False
                    End_turn_btn.set_text("EndTurn")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game_board.handle_mouse_event(screen, event.pos)

        game_board.update()           # Обновление логики спрайтов
        game_board.draw(screen)       # Отрисовка всех спрайтов

        End_turn_btn.check_hover(pygame.mouse.get_pos())
        End_turn_btn.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()
