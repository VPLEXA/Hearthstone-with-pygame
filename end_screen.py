import pygame

def show_game_over_screen(screen, player_name):
    if player_name == " ":
        return 
    screen_width, screen_height = screen.get_size()

    small_screen_width = screen_width // 2
    small_screen_height = screen_height // 2
    
    small_screen_x = (screen_width - small_screen_width) // 2
    small_screen_y = (screen_height - small_screen_height) // 2

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GRAY = (100, 100, 100)
    
    small_screen = pygame.Surface((small_screen_width, small_screen_height))
    small_screen.fill(GRAY)

    pygame.draw.rect(small_screen, WHITE, (0, 0, small_screen_width, small_screen_height), 3)

    try:
        title_font = pygame.font.Font(None, 48)
        name_font = pygame.font.Font(None, 36)
    except:
        title_font = pygame.font.SysFont('arial', 48)
        name_font = pygame.font.SysFont('arial', 36)
    
    game_over_text = title_font.render("ИГРА ОКОНЧЕНА", True, RED)
    name_text = name_font.render(f"Игрок: {player_name}", True, WHITE)
    
    game_over_rect = game_over_text.get_rect(center=(small_screen_width//2, small_screen_height//3))
    name_rect = name_text.get_rect(center=(small_screen_width//2, small_screen_height//2))

    small_screen.blit(game_over_text, game_over_rect)
    small_screen.blit(name_text, name_rect)
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  
        screen.blit(overlay, (0, 0))
        
        
        screen.blit(small_screen, (small_screen_x, small_screen_y))
        
        pygame.display.flip()