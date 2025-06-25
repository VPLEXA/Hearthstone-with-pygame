import pygame, os

# путь для фотографий
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Настройки экрана
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1200
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GREEN = (0, 100, 0)
GOLD = (212, 175, 55)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Шрифты
pygame.font.init()
FONT = pygame.font.SysFont("Arial", 24, bold=True)

# Класс Slider
class Slider(pygame.sprite.Sprite):
    def __init__(self, groups, pos: tuple[int], size=(200, 10), 
                 min_value=0.0, max_value=1.0, initial_value=0.5,
                 color_bg='#cccccc', color_fg='#CA7842', handle_color='#4B352A',
                 label_text: str = '', label_font = None, label_color='black'):
        super().__init__(groups)

        self.pos = pos
        self.width = size[0]
        self.height = size[1]
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.handle_color = handle_color

        self.label_text = label_text
        self.label_font = label_font
        self.label_color = label_color

        self.label_surf = None
        self.label_rect = None
        label_width = 0
        label_height = 0
        if self.label_text and self.label_font:
            self.label_surf = self.label_font.render(self.label_text, True, self.label_color)
            self.label_rect = self.label_surf.get_rect()
            label_width = self.label_rect.width + 10
            label_height = self.label_rect.height

        total_width = self.width + label_width + 20
        total_height = max(self.height, label_height) + 10

        self.image = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

        self.label_width = label_width
        self.label_height = label_height
        self.total_height = total_height

        self.dragging = False

        self.update_slider()

    def update_slider(self):
        self.image.fill((0, 0, 0, 0))

        slider_y = (self.total_height - self.height) // 2

        # draw label
        if self.label_surf:
            label_y = (self.total_height - self.label_height) // 2
            self.image.blit(self.label_surf, (0, label_y))

        progress_width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.width)

        # background
        pygame.draw.rect(
            self.image, self.color_bg,
            (self.label_width, slider_y, self.width, self.height), border_radius=5
        )
        # foreground
        pygame.draw.rect(
            self.image, self.color_fg,
            (self.label_width, slider_y, progress_width, self.height), border_radius=5
        )
        # handle
        pygame.draw.circle(
            self.image, self.handle_color,
            (self.label_width + progress_width, slider_y + self.height // 2), 10
        )

    def get_value(self):
        return self.value

    def input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        if self.dragging and not mouse_pressed[0]:
            self.dragging = False

        if self.rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            self.dragging = True

        if self.dragging:
            rel_x = mouse_pos[0] - self.rect.left - self.label_width
            rel_x = max(0, min(self.width, rel_x))
            self.value = self.min_value + (rel_x / self.width) * (self.max_value - self.min_value)
            self.update_slider()

    def update(self, dt):
        self.input()
        
        
    def draw_text_window(surface, pos, text, font=None, padding=20, bg_color='#cccccc', text_color='black', border_radius=10):
        if not font:
            font = pygame.font.Font(os.join('fonts', 'PixCyrillic.ttf'), 25)
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect()
        width = text_rect.width + padding * 2
        height = text_rect.height + padding * 2
        window_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(window_surf, bg_color, window_surf.get_rect(), border_radius=border_radius)
        window_surf.blit(text_surf, (padding, padding))
        window_rect = window_surf.get_rect(center=(pos[0]-width//2, pos[1]))
        surface.blit(window_surf, window_rect)

# Класс кнопок
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surf = FONT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False
    
    def set_text(self, new_text):
        self.text = new_text
