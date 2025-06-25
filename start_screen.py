import pygame, sys
from pygame import mixer
from main import *
from game_config import *

# Инициализация Pygame
pygame.init()
mixer.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Стартовый экран")

# Шрифты
font = pygame.font.SysFont('Arial', 40)
small_font = pygame.font.SysFont('Arial', 30)

# Громкость (по умолчанию 50%)
volume = 0.5
mixer.music.set_volume(volume)

# Загрузка фоновой музыки (если есть)
pygame.mixer.Channel(0).play(pygame.mixer.Sound('Game_for_OPD/assets/music/2-08 Tabletop Battles.mp3'), loops=-1)  


def main_menu():
    play_button = Button(WIDTH//2 - 100, HEIGHT//2 - 80, 200, 50, "Играть", BLUE, (100, 100, 255))
    settings_button = Button(WIDTH//2 - 100, HEIGHT//2, 200, 50, "Настройки", BLUE, (100, 100, 255))
    quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50, "Выход", RED, (255, 100, 100))
    
    buttons = [play_button, settings_button, quit_button]
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if play_button.is_clicked(mouse_pos, event):
                hero_paths = select_heroes()
                main(hero_paths) # type: ignore
                pygame.quit()
                sys.exit()  # Здесь можно перейти к игровому экрану
                
            if settings_button.is_clicked(mouse_pos, event):
                settings_menu()
                
            if quit_button.is_clicked(mouse_pos, event):
                pygame.quit()
                sys.exit()
        
        # Отрисовка
        screen.fill(WHITE)
        
        # Заголовок
        title = font.render("Hearthstone", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Кнопки
        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)
        
        pygame.display.flip()


def settings_menu():
    back_button = Button(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50, "Назад", BLUE, (100, 100, 255))
    volume_down = Button(WIDTH//2 - 150, HEIGHT//2, 50, 50, "-", BLUE, (100, 100, 255))
    volume_up = Button(WIDTH//2 + 100, HEIGHT//2, 50, 50, "+", BLUE, (100, 100, 255))
    
    global volume
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if back_button.is_clicked(mouse_pos, event):
                return  # Возврат в главное меню
                
            if volume_down.is_clicked(mouse_pos, event):
                volume = max(0, volume - 0.1)
                mixer.music.set_volume(volume)
                
            if volume_up.is_clicked(mouse_pos, event):
                volume = min(1, volume + 0.1)
                mixer.music.set_volume(volume)
        
        # Отрисовка
        screen.fill(WHITE)
        
        # Заголовок
        title = font.render("Настройки", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Громкость
        volume_text = small_font.render(f"Громкость: {int(volume * 100)}%", True, BLACK)
        screen.blit(volume_text, (WIDTH//2 - volume_text.get_width()//2, HEIGHT//2 - 50))
        
        # Кнопки
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        
        volume_down.check_hover(mouse_pos)
        volume_down.draw(screen)
        
        volume_up.check_hover(mouse_pos)
        volume_up.draw(screen)
        
        # Ползунок громкости (просто визуализация)
        pygame.draw.rect(screen, GRAY, (WIDTH//2 - 100, HEIGHT//2, 200, 10))
        pygame.draw.rect(screen, BLUE, (WIDTH//2 - 100, HEIGHT//2, int(200 * volume), 10))
        pygame.draw.circle(screen, BLUE, (WIDTH//2 - 100 + int(200 * volume), HEIGHT//2 + 5), 10)
        
        pygame.display.flip()

def select_heroes():
    hero_data = [
        ("Иллидан", "Game_for_OPD/assets/heroes/illidan.png"),
        ("Король Лич", "Game_for_OPD/assets/heroes/king_lich.png"),
        ("Воин", "Game_for_OPD/assets/heroes/warrior.png")
    ]

    hero_images = [pygame.image.load(path) for _, path in hero_data]
    hero_positions = [(150, 250), (325, 250), (500, 250)]

    selected_heroes = [None, None]
    current_player = 0
    start_button = Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, "Начать игру", BLUE, (100, 100, 255))

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, pos in enumerate(hero_positions):
                    rect = pygame.Rect(pos[0], pos[1], 125, 125)
                    if rect.collidepoint(mouse_pos) and i not in selected_heroes:
                        selected_heroes[current_player] = i
                        current_player += 1

            if start_button.is_clicked(mouse_pos, event):
                if None not in selected_heroes:
                    return [hero_data[i][1] for i in selected_heroes]  # возвращаем пути

        # Отрисовка
        screen.fill(WHITE)
        title = font.render("Выбери своего героя", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        player_text = small_font.render(f"Игрок {current_player + 1} выбирает...", True, BLACK)
        screen.blit(player_text, (WIDTH//2 - player_text.get_width()//2, 160))

        for i, (img, pos) in enumerate(zip(hero_images, hero_positions)):
            scaled = pygame.transform.scale(img, (125, 125))
            screen.blit(scaled, pos)
            if i in selected_heroes:
                pygame.draw.rect(screen, GREEN, (*pos, 125, 125), 4)

        start_button.check_hover(mouse_pos)
        start_button.draw(screen)
        pygame.display.flip()

