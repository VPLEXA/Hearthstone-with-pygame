import pygame, random
from game_config import *
from player import *
from end_screen import show_game_over_screen

class GameBoard:
    def __init__(self, hero_paths):
        # Основные параметры
        self.player_hand_rect = pygame.Rect(150, 1000, 1600, 150)
        self.battlefield_rect = pygame.Rect(190, 300, 1500, 600)
        self.opponent_hand_rect = pygame.Rect(150, 50, 1600, 150)

        # Спрайты
        self.active_player_sprites = pygame.sprite.Group()
        self.non_active_player_sprites = pygame.sprite.Group()

        # Инициализация игроков
        player1_hero, player2_hero = hero_paths
        self.player = Player("Лёша", hero_image_path=player1_hero)
        self.opponent = Player("Максим", hero_image_path=player2_hero)
        self.active_player = self.player  # Начинаем с игрока 1
        self.none_active_player = self.opponent

        # Счетчик ходов
        self.cnt_moves = 1

        self.selected_card = None

        self.turn_transition = False
        # Старт игры
        self._start_game()

    def _start_game(self):
        """Начальный этап игры, например, раздача карт"""
        self.player.draw_card()
        self.opponent.draw_card()
        self.active_player.start_turn()  # Первый игрок начинает ход
        # Создаём поля для карт на поле боя
        self.active_player_battlefield = []
        self.non_active_player_battlefield = []
        # Спрайты опять же
        self.active_player_sprites.empty()
        self.non_active_player_sprites.empty()
        
    def _end_game(self, screen):
        name = " "
        if self.active_player.hp <= 0:
            name = self.active_player.name
        if self.none_active_player.hp <= 0:
            name = self.none_active_player.name
        show_game_over_screen(screen, name)

    def _end_turn(self):
        # Увеличиваем счетчик ходов
        self.cnt_moves += 0.5

        # Завершаем ход текущего игрока
        self.active_player.end_turn(self.cnt_moves)  # Завершаем ход текущего игрока
        self.none_active_player.end_turn(self.cnt_moves)

        # Переключаем игроков и их поля
        self.active_player, self.none_active_player = self.none_active_player, self.active_player
        self.active_player_sprites, self.non_active_player_sprites = (
            self.non_active_player_sprites,
            self.active_player_sprites
        )

        # Короче надо
        self.arrange_battlefield_cards()

        # Снимаем выделение с карты
        self.selected_card = None
        
        # Начало нового хода
        self.start_turn()

    def start_turn(self):
        # Разрешение атаки существам, кроме только что разыгранных
        for card in self.active_player_sprites:
            if isinstance(card, Creature_card):
                if card.just_played:
                    card.can_attack = True  # Только что призванное — не может
                    card.just_played = False  # Сбрасываем флаг сразу
                else:
                    card.can_attack = True  # Все остальные — могут
                card.has_attacked = False  # Сбросили флаг атаки
            if isinstance(card, Creature_card) and hasattr(card, "effects"):
                for effect in card.effects[:]:
                    effect.apply(source=card, target=self.none_active_player, game=self)

        # Начинаем ход нового игрока
        self.active_player.start_turn()  

    def _draw_hand(self, screen):
        """Отрисовка карт игрока в руке с использованием метода карты"""
        if not self.active_player.hand:
            return

        card_width = 100  
        spacing = 30  # небольшое расстояние между картами
        total_width = len(self.active_player.hand) * (card_width + spacing) - spacing

        start_x = (1920 - total_width) // 2
        y = 1000  # Рука игрока (чуть выше полоски)

        for idx, card in enumerate(self.active_player.hand):
            x = start_x + idx * (card_width + spacing)

            # Обновляем положение карты перед отрисовкой
            card.rect.topleft = (x, y)

            # Рисуем карту через её метод draw
            card.draw(screen)

    def arrange_battlefield_cards(self):
        def arrange(group, y):
            cards = group.sprites()
            total_width = len(cards) * 120 + (len(cards) - 1) * 20
            start_x = self.battlefield_rect.centerx - total_width // 2
            for i, card in enumerate(cards):
                card.rect.topleft = (start_x + i * 140, y)

        arrange(self.active_player_sprites, self.battlefield_rect.centery + 110)
        arrange(self.non_active_player_sprites, self.battlefield_rect.centery - 220)


    def handle_mouse_event(self, screen, pos):
        # Обработка карт игрока
        for card in self.active_player.hand:
            if card.rect.collidepoint(pos) and card.manacost <= self.active_player.current_mana:
                for other_card in self.active_player.hand:
                    other_card.selected = False
                
                self.selected_card = card
                card.selected = True
                return
            
        if self.selected_card:
            for target in self.active_player_sprites:
                if target is not self.selected_card and target.rect.collidepoint(pos):
                    self.selected_card.buff(target)
                    self.selected_card.selected = False
                    self.selected_card = None
                    return

            for enemy in self.non_active_player_sprites:
                if enemy.rect.collidepoint(pos):
                    self.selected_card.hit(enemy, game=self)
                    self.selected_card.selected = False
                    self.selected_card = None
                    self._cleanup_dead_cards()
                    return
            
            
            if self.enemy_hero_rect.collidepoint(pos):
                self.hit_hero(self.selected_card.attack)
                self.selected_card.has_attacked = True
                self.selected_card.selected = False
                self.selected_card = None
                self._end_game(screen)
                return
            
        
        else:
            # 3. Нет выбранной карты — ищем, кликнули ли по своей карте, чтобы выбрать её
            for card in self.active_player_sprites:
                if card.rect.collidepoint(pos):
                    # Снимаем выделение со всех
                    for other_card in self.active_player_battlefield:
                        other_card.selected = False
                        other_card.update(in_hand=False)

                    card.selected = True  # Выбираем карту для действия
                    card.update(in_hand=False)
                    self.selected_card = card
                    return
            
        # Если клик по полю битвы и карта выбрана, разыгрываем её
        if self.battlefield_rect.collidepoint(pos) and self.selected_card:
            self.active_player.hand.remove(self.selected_card)
            self.active_player_sprites.add(self.selected_card)
            self.arrange_battlefield_cards()
            self.active_player.current_mana -= self.selected_card.manacost
            self.selected_card.selected = False
            self.selected_card = None


    def _cleanup_dead_cards(self):
        for group in [self.active_player_sprites, self.non_active_player_sprites]:
            for card in group.copy():
                if card.is_dead():
                    group.remove(card)
    
    def update(self):
        # Обновляем спрайты активного игрока
        self.active_player_sprites.update()
        # Обновляем спрайты неактивного игрока
        self.non_active_player_sprites.update()

    def hit_hero(self, damage):
        self.none_active_player.hp -= damage

    def end_game(self):
          """Здесь должна быть функция конца игры"""
          pass
             
    def draw(self, screen):
        # Фон
        screen.fill((18, 18, 25))  # Тёмно-синий фон
        
        # Поле битвы
        pygame.draw.rect(screen, (50, 100, 50), self.battlefield_rect, border_radius=20)
        pygame.draw.rect(screen, (200, 200, 200), self.battlefield_rect, 4, border_radius=20)
        
        # Руки игроков
        pygame.draw.rect(screen, (40, 40, 60), self.player_hand_rect, border_radius=10)
        pygame.draw.rect(screen, (40, 40, 60), self.opponent_hand_rect, border_radius=10)
        
        # Линия разделения поля
        pygame.draw.line(screen, (255, 255, 255), (0, 230), (1920, 230), 3)  # Линия разделения сверху
        pygame.draw.line(screen, (255, 255, 255), (0, 950), (1920, 950), 3)  # Линия разделения снизу
        pygame.draw.line(screen, (200, 200, 200), (190, 600), (1685, 600), 3)  # Линия разделения по середине

        # Понимание кто сверху, а кто снизу
        bottom_player = self.active_player
        top_player = self.opponent if self.active_player == self.player else self.player

        # Отрисовка портретов героев
        if self.active_player.hero_image:
            screen.blit(pygame.transform.scale(self.active_player.hero_image, (150, 150)), (0, 1000))

        if self.none_active_player.hero_image:
            self.enemy_hero_rect = pygame.Rect(0, 50, 150, 150)
            hero_surf = pygame.transform.scale(self.none_active_player.hero_image, (150, 150))
            screen.blit(hero_surf, self.enemy_hero_rect.topleft)


        # ХП и Мана
        self._draw_health(screen)
        self._draw_mana(screen)
        
        # Обновляем флаг принадлежности карт к активному игроку
        for card in self.active_player_sprites:
            card.set_owner(True)

        for card in self.non_active_player_sprites:
            card.set_owner(False)

        # Отрисовка карт в руке
        bottom_player.draw_hand(screen, y=1000, face_up=True)
        top_player.draw_hand(screen, y=50, face_up=False)

        # Отрисовка карт на поле при разыгрывании
        for card in self.active_player_sprites:
            card.update(in_hand=False)
            screen.blit(card.image, card.rect.move(card.animation_draw_offset))

        for card in self.non_active_player_sprites:
            card.update(in_hand=False)
            screen.blit(card.image, card.rect.move(card.animation_draw_offset))
        
        # Блюр между ходами
        if self.turn_transition:
            dark_overlay = pygame.Surface((1920, 1200), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 250))
            screen.blit(dark_overlay, (0, 0))


    def _draw_health(self, screen):
        # ХП игрока
        pygame.draw.circle(screen, (200, 30, 30), (135, 1150), 20)  # Увеличиваем радиус
        hp_text = FONT.render(f"{self.active_player.hp}", True, WHITE)
        screen.blit(hp_text, (122, 1135))
        
        # ХП противника
        pygame.draw.circle(screen, (200, 30, 30), (135, 200), 20)  # Увеличиваем радиус
        hp_text = FONT.render(f"{self.none_active_player.hp}", True, WHITE)
        screen.blit(hp_text, (122, 186))

    
    def _draw_mana(self, screen):
        # Мана игрока
        pygame.draw.rect(screen, (30, 144, 255), (1770, 1040, 120, 60), border_radius=10)  # Увеличиваем размеры
        mana_text = FONT.render(f"{self.active_player.current_mana}/{self.active_player.max_mana}", True, WHITE)
        screen.blit(mana_text, (1795, 1055))

        # Мана противника
        pygame.draw.rect(screen, (30, 144, 255), (1770, 20, 120, 60), border_radius=10)  # Местоположение для противника
        mana_text = FONT.render(f"{self.none_active_player.current_mana}/{self.none_active_player.max_mana}", True, WHITE)
        screen.blit(mana_text, (1795, 35))
    


        
