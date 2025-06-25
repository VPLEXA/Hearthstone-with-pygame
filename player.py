import random, json, os, pygame
from cards_classes import Creature_card, Spell_card

class Player:
    def __init__(self, name, hero_image_path=None, hero_pos=(0, 50)):
        self.name = name
        self.hp = 30
        self.max_mana = 3
        self.current_mana = self.max_mana
        
        self.hand = pygame.sprite.Group()  # Группа спрайтов карт в руке
        self.deck = []                     # Колода — список карт (спрайтов)
        
        if hero_image_path:
            self.hero_image = pygame.image.load(hero_image_path).convert_alpha()
            self.avatar_rect = self.hero_image.get_rect(center=hero_pos)
        else:
            self.hero_image = None
            
        self._load_deck()

    def _load_deck(self):
        """Загружаем начальные карты в колоду из cards_data.json"""
        base_path = os.path.dirname(__file__)
        json_path = os.path.join(base_path, "cards_data.json")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        creatures = [card for card in data if card.get("type") == "creature"]
        spells = [card for card in data if card.get("type") == "spell"]

        self.deck = []
        for card in creatures:
            # Извлечение названия эффекта и его параметров
            effect_name = card.get("effect_name", "")
            effect_params = card.get("effect_params", {})

            # Парсинг существа
            creature = Creature_card(
                name=card["name"],
                attack=card["attack"],
                health=card["health"],
                defense=card.get("defense"),
                manacost=card.get("mana_cost", card.get("manacost")),
                special_effect=card.get("description", ""),
                effect_name=effect_name,
                image=card["image"]
            )

            # Присваиваем параметры эффекта (напрямую в Creature_card)
            creature.effect_params = effect_params

            # Если указан эффект — создаём его экземпляр и добавляем
            if effect_name:
                try:
                    effect = creature.get_effect(effect_name)(**effect_params)
                    creature.effects.append(effect)
                    print(f"Добавлен эффект {effect_name} к карте {creature.name}")  # Отладочный вывод
                except Exception as e:
                    print(f"[Ошибка эффекта] {effect_name} с параметрами {effect_params}: {e}")
 

            # Добавляем по 3 копии карты
            self.deck.extend([creature.clone() for _ in range(3)])

        random.shuffle(self.deck)

    def draw_card(self):
        """Добираем карту из колоды в руку, если есть карты"""
        if self.deck:
            card = self.deck.pop(0)
            self.hand.add(card)  # Добавляем карту в группу спрайтов руки

    def end_turn(self, cnt_moves):
        """Завершение хода игрока"""
        if cnt_moves.is_integer():
            self.max_mana = min(10, self.max_mana + 1)

    def start_turn(self):
        """Начало хода игрока"""
        self.current_mana = self.max_mana
        self.draw_card()


    def draw_hand(self, screen, y, face_up=True):
        """Отрисовка карт в руке"""
        card_width = 100
        spacing = 30
        hand_list = list(self.hand)
        total_width = len(hand_list) * (card_width + spacing) - spacing
        start_x = (1920 - total_width) // 2

        for idx, card in enumerate(hand_list):
            x = start_x + idx * (card_width + spacing)
            card.rect.topleft = (x, y)
            if face_up:
                card.update(in_hand=True)
                screen.blit(card.image, card.rect)
            else:
                card.draw_back(screen)

