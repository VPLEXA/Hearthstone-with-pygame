import pygame, os, math
from pygame import mixer
from game_config import *
from effects import *
from typing import Type

pygame.init()

class Base_Card(pygame.sprite.Sprite):
    def __init__(self, name: str, x=0, y=0, width=100, height=150, card_type=""):
        super().__init__()
        self.name = name
        self.type = card_type
        self.width = width
        self.height = height
        self.selected = False
        self.color = GOLD
        self.font = pygame.font.SysFont("Arial", 14, bold=True)

        # Основные атрибуты спрайта
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))

        # Загрузка изображения существа/заклинания
        self.card_art = None  # внутреннее изображение
        self.update()  # сразу отрисуем

        self.belongs_to_active_player = False


    def load_image(self, image_path: str):
        full_path = os.path.join(BASE_DIR, "assets", image_path)
        if not os.path.exists(full_path):
            # print(f"[Ошибка] Изображение не найдено: {full_path}")
            return

        try:
            self.card_art = pygame.image.load(full_path).convert_alpha()
            self.update()
        except pygame.error as e:
            print(f"[Ошибка загрузки изображения]: {e}")

    def _split_name(self, max_width):
        words = self.name.split(" ")
        if len(words) == 1:
            return self.name, None
        first_line = words[0]
        second_line = " ".join(words[1:])
        if self.font.size(first_line)[0] > max_width:
            return self.name[:10] + "...", None
        return first_line, second_line

    def update(self, in_hand=False):
        """Обновление изображения карты (при перерисовке, изменении состояния и т.д.)"""
        self.image.fill((0, 0, 0, 0))  # прозрачный фон

        # Рамка
        if self.selected:
            color = GREEN if self.belongs_to_active_player else RED
        else:
            color = self.color
        pygame.draw.rect(self.image, color, (0, 0, self.width, self.height), border_radius=10)
        pygame.draw.rect(self.image, BLACK, (0, 0, self.width, self.height), 2, border_radius=10)

        # Эллипс (фон под артом)
        oval_rect = pygame.Rect(
            self.width * 0.1,
            self.height * 0.2,
            self.width * 0.8,
            self.height * 0.6
        )
        pygame.draw.ellipse(self.image, (230, 230, 250), oval_rect)
        pygame.draw.ellipse(self.image, BLACK, oval_rect, 2)

        # Арт карты
        if self.card_art:
            scaled = pygame.transform.scale(self.card_art, (int(oval_rect.width * 0.9), int(oval_rect.height * 0.9)))
            self.image.blit(scaled, scaled.get_rect(center=oval_rect.center))

        # Имя
        max_text_width = self.width - 20
        line1, line2 = self._split_name(max_text_width)
        text1 = self.font.render(line1, True, BLACK)
        self.image.blit(text1, text1.get_rect(center=(self.width // 2, 20)))
        if line2:
            text2 = self.font.render(line2, True, BLACK)
            self.image.blit(text2, text2.get_rect(center=(self.width // 2, 45)))

    def set_owner(self, is_active: bool):
        self.belongs_to_active_player = is_active
        self.update()  # сразу перерисовать

    def draw_back(self, screen):
        pygame.draw.rect(screen, (40, 40, 180), self.rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3, border_radius=8)
        qfont = pygame.font.SysFont(None, 48)
        qtext = qfont.render("?", True, (255, 255, 255))
        screen.blit(qtext, qtext.get_rect(center=self.rect.center))


class Creature_card(Base_Card):
    def __init__(self, name, attack, health, defense=0, manacost=0,
                 special_effect="", effect_name="", effect_params=None, image="", x=0, y=0):
        super().__init__(name, x, y, card_type="Creature")
        self.attack = attack
        self.health = health
        self.defense = defense
        self.manacost = manacost
        self.special_effect = special_effect
        self.effect_name = effect_name
        self.effects = []
        self.effect_params = effect_params or {}
        self.is_alive = True

        # Для логики игры
        self.can_attack = False      # Может ли атаковать сейчас
        self.just_played = True      # Только что разыграно
        self.has_attacked = False    # Уже атаковало в этом ходу

        # Для анимации атаки
        self.is_animating = False
        self.animation_start_time = 0
        self.animation_duration = 400  # длительность в миллисекундах
        self.animation_offset = pygame.Vector2(0, 0)
        self.animation_draw_offset = pygame.Vector2(0, 0)
        self.attack_phase = 0  # 0 — нет, 1 — вперед, 2 — назад

        if image:
            self.load_image(image)

    def update(self, in_hand=False):
        super().update(in_hand=in_hand)
        # Временная проверка
        if not getattr(self, "is_alive", False):
            return
        if not self.is_alive:
            return

        radius = 15
        center = (15, 15)
        offset = 10

        # Отрисовка зелёной рамки, если может атаковать
        if self.can_attack and not self.has_attacked:
            pygame.draw.rect(self.image, (0, 255, 0), (0, 0, self.width, self.height), 4, border_radius=10)

        # Отрисовка здоровья (всегда)
        hp_pos = (self.width - offset, self.height - offset)
        pygame.draw.circle(self.image, (255, 100, 100), hp_pos, radius)
        pygame.draw.circle(self.image, BLACK, hp_pos, radius, 2)
        hp_text = self.font.render(str(self.health), True, WHITE)
        self.image.blit(hp_text, hp_text.get_rect(center=hp_pos))

        # Отрисовка атаки — только в руке
        atk_pos = (offset, self.height - offset)
        pygame.draw.circle(self.image, (240, 240, 240), atk_pos, radius)
        pygame.draw.circle(self.image, BLACK, atk_pos, radius, 2)
        atk_text = self.font.render(str(self.attack), True, BLACK)
        self.image.blit(atk_text, atk_text.get_rect(center=atk_pos))

        # Броня в виде щита над атакой
        if self.defense > 0:
            shield_width = 24
            shield_height = 28

            atk_pos = (10, self.height - 10)  # позиция круга атаки
            shield_pos = (atk_pos[0] - 13, atk_pos[1] - shield_height - 11)  # чуть выше атаки

            shield_rect = pygame.Rect(shield_pos, (shield_width, shield_height))

            # Форма щита
            pygame.draw.polygon(self.image, (150, 150, 200), [
                (shield_rect.centerx, shield_rect.top),               # верхняя точка
                (shield_rect.right, shield_rect.top + 8),             # верх-право
                (shield_rect.right - 4, shield_rect.bottom),          # низ-право
                (shield_rect.left + 4, shield_rect.bottom),           # низ-лево
                (shield_rect.left, shield_rect.top + 8)               # верх-лево
            ])
            pygame.draw.polygon(self.image, BLACK, [
                (shield_rect.centerx, shield_rect.top),
                (shield_rect.right, shield_rect.top + 8),
                (shield_rect.right - 4, shield_rect.bottom),
                (shield_rect.left + 4, shield_rect.bottom),
                (shield_rect.left, shield_rect.top + 8)
            ], 2)

            # Число брони
            def_text = self.font.render(str(self.defense), True, WHITE)
            self.image.blit(def_text, def_text.get_rect(center=shield_rect.center))

        if in_hand:
            # Отрисовка маны - только в руке
            hexagon_points = [
                (
                    center[0] + radius * math.cos(math.radians(angle)),
                    center[1] + radius * math.sin(math.radians(angle))
                )
                for angle in range(0, 360, 60)
            ]
            pygame.draw.polygon(self.image, (0, 50, 150), hexagon_points)
            pygame.draw.polygon(self.image, BLACK, hexagon_points, 2) 
            mana_text = self.font.render(str(self.manacost), True, WHITE)
            self.image.blit(mana_text, (10, 7))

        # Анимация атаки
        if self.is_animating:
            elapsed = pygame.time.get_ticks() - self.animation_start_time
            progress = elapsed / (self.animation_duration / 2)

            if self.attack_phase == 1:  # Движение вперёд
                if progress >= 1.0:
                    self.attack_phase = 2
                    self.animation_start_time = pygame.time.get_ticks()
                    self.animation_offset *= -1  # меняем направление
                else:
                    offset = self.animation_offset * progress
                    self.animation_draw_offset = offset

            elif self.attack_phase == 2:  # Возврат назад
                if progress >= 1.0:
                    self.is_animating = False
                    self.attack_phase = 0
                    self.animation_draw_offset = pygame.Vector2(0, 0)
                else:
                    offset = self.animation_offset * (1 - progress)
                    self.animation_draw_offset = offset
        else:
            self.animation_draw_offset = pygame.Vector2(0, 0)  

    def start_attack_animation(self, target):
        self.is_animating = True
        self.animation_start_time = pygame.time.get_ticks()
        self.attack_phase = 1

        # Направление от атакующего к цели
        direction = pygame.Vector2(target.rect.center) - pygame.Vector2(self.rect.center)
        if direction.length() > 0:
            self.animation_offset = direction.normalize() * 200  # сила выпада
        else:
            self.animation_offset = pygame.Vector2(0, 0)

    def block_damage(self, damage):
        if self.defense > 0:
            blocked = min(damage, self.defense)
            self.defense -= blocked
            damage -= blocked
        return damage

    def take_damage(self, damage, ignore_defense=False):
        effective_defense = 0 if ignore_defense else self.defense
        damage_after_defense = max(damage - effective_defense, 0)
        self.health -= damage_after_defense
        self.is_alive = self.health > 0
        if self.is_dead():
            self.kill()  # ✅ Удаляет спрайт из всех групп
        else:
            self.update()
    
    def hit(self, target, game=None):
        if not self.can_attack or self.has_attacked:
            print(f"[{self.name}] не может атаковать сейчас!")
            return

        if not isinstance(target, Creature_card):
            print("[Ошибка]: Можно атаковать только существа.")
            return
        
        if isinstance(target, Creature_card):
            self.start_attack_animation(target)

        # Применяем эффекты
        damage_dealt_by_effect = False
        if hasattr(self, "effects") and self.effects:
            for effect in self.effects:
                if effect.apply(source=self, target=target, game=game):
                    damage_dealt_by_effect = True

        # Если ни один эффект не нанёс урон — наносим обычный
        if not damage_dealt_by_effect:
            print(f"[Атака]: {self.name} -> {target.name} (-{self.attack})")
            target.take_damage(self.attack)

        #звук удара
        pygame.mixer.Channel(1).play(pygame.mixer.Sound('assets/music/zvuk-napadeniya.mp3'))
        # Ответный урон 
        self.take_damage(target.attack)

        self.has_attacked = True
        self.update()


    def is_dead(self):
        return self.health <= 0 or not self.is_alive

    def get_effect(self, effect_name) -> Type[Effect]: 
        effects = {
            PierceDamageEffect.effect_name: PierceDamageEffect,
            DamageAdjacentEffect.effect_name: DamageAdjacentEffect,
            HavePoison.effect_name: HavePoison,
            HealOverTimeEffect.effect_name: HealOverTimeEffect,
            StunEffect.effect_name: StunEffect,
            VampirismEffect.effect_name: VampirismEffect,
            StatBuffEffect.effect_name: StatBuffEffect,
            ArmorBreakEffect.effect_name: ArmorBreakEffect,
            BloodEffect.effect_name: BloodEffect
        }
        if effect_name not in effects:
            raise ValueError(f"Эффект с именем '{effect_name}' не найден.")
        return effects[effect_name]
    def clone(self):
        new_card = Creature_card(
            name=self.name,
            attack=self.attack,
            health=self.health,
            defense=self.defense,
            manacost=self.manacost,
            special_effect=self.special_effect,
            image=None,
            x=self.rect.x,
            y=self.rect.y
        )
        new_card.card_art = self.card_art  # ✅ переносим артовое изображение
        new_card.image = self.image.copy()  # ✅ копируем отрисованную карту
        return new_card


class Spell_card(Base_Card):
    def __init__(self, name, manacost, damage=0, special_effect="", image="", x=0, y=0):
        super().__init__(name, x, y, card_type="Spell")
        self.manacost = manacost
        self.damage = damage
        self.special_effect = special_effect
        self.color = (100, 100, 255)
        self.is_playable = True
        self.target_required = bool(damage or special_effect)  # если нужен выбор цели

        if image:
            self.load_image(image)

    def update(self, in_hand=False):
        super().update(in_hand=in_hand)
        pygame.draw.circle(self.image, (0, 50, 150), (15, 15), 12)
        mana_text = self.font.render(str(self.manacost), True, WHITE)
        self.image.blit(mana_text, (10, 7))

        if in_hand and self.damage:
            dmg_text = self.font.render(str(self.damage), True, RED)
            self.image.blit(dmg_text, dmg_text.get_rect(center=(self.width // 2, self.height - 20)))

    def play(self, target=None, game=None):
        """Применение заклинания к цели"""
        if not self.is_playable:
            return False

        # Если указано просто число урона
        if self.damage:
            if hasattr(target, 'take_damage'):
                target.take_damage(self.damage)
                print(f"{self.name} наносит {self.damage} урона {target.name}")
            else:
                print(f"Ошибка: цель не может получать урон")

        # Здесь можно применить спецэффекты
        # Например: 'heal', 'draw', 'destroy' и т.д.
        if self.special_effect == "draw":
            game.active_player.draw_card()

        self.is_playable = False
        return True

    def clone(self):
        new_card = Spell_card(
            name=self.name,
            manacost=self.manacost,
            damage=self.damage,
            special_effect=self.special_effect,
            image=None,
            x=self.rect.x,
            y=self.rect.y
        )
        new_card.card_art = self.card_art
        new_card.image = self.image.copy()
        return new_card

