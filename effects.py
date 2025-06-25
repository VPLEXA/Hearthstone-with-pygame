# Базовый класс для особых эффектов карт
class Effect:
    def apply(self, source, target, game) -> bool:
        """Применяет эффект. Возвращает True, если урон уже был нанесён."""
        raise NotImplementedError('Метод apply должен быть переопределён!')

# Эффект провокации
class TauntEffect(Effect):
    def apply(self, source, target, game) -> None:
        source.has_tount = True
        return False
        
# Эффект игнорирования защиты
class PierceDamageEffect(Effect):
    effect_name = "PierceDamage"

    def __init__(self, damage: int):
        self.damage = damage
    
    def apply(self, source, target, game) -> bool:
        original_defense = target.defense
        target.defense = 0
        target.take_damage(self.damage, ignore_defense=True)
        target.defense = original_defense
        print(f"{source.name} наносит {self.damage} урона (игнорируя защиту) {target.name}")
        return True

# Урон существам слева и справа от основной цели
class DamageAdjacentEffect(Effect):
    effect_name = "DamageAdjacent"
    def __init__(self, damage: int):
        self.damage = damage

    def apply(self, source, target, game) -> None:
        if not game:
            return
        
        # Найти позицию цели на поле
        field = game.battlefield
        try:
            index = field.index(target)
        except ValueError:
            return
        
        # Найти соседей
        left_neighbor = field[index - 1] if index > 0 else None
        right_neighbor = field[index + 1] if index < len(field) - 1 else None

        # Нанести урон соседям
        for neighbor in [left_neighbor, right_neighbor]:
            if neighbor and neighbor != source:
                print(f"{source.name} наносит {self.damage} урона соседу {neighbor.name}")
                neighbor.take_damage(self.damage)
        return True

# Имеет яд
class HavePoison(Effect):
    effect_name = "HavePoison"
    def __init__(self, cnt_uses: int, damage_per_turn: int, duration: int):
        self.cnt_uses = cnt_uses
        self.damage_per_turn = damage_per_turn
        self.duration = duration
    
    def apply(self, target):
        Poison = PoisonEffect(self.damage_per_turn, self.duration)
        Poison.apply(target)

# Наложение яда на существо
class PoisonEffect(Effect):
    effect_name = "Poison"
    def __init__(self, damage_per_turn: int, duration: int):
        self.damage = damage_per_turn
        self.duration = duration
        self.current_duration = duration
    
    def apply(self, source, target, game) -> None:
        # При первом применении добавляем эффект к цели
        if not hasattr(target, 'active_effects'):
            target.active_effects = []
        
        # Проверяем, есть ли уже яд на цели
        existing_poison = next((e for e in target.active_effects 
                              if isinstance(e, PoisonEffect)), None)
        
        if existing_poison:
            # Увеличиваем длительность, если яд уже есть
            existing_poison.current_duration += self.duration
            print(f"{target.name}: длительность яда увеличена до {existing_poison.current_duration} ходов")
        else:
            target.active_effects.append(self)
            print(f"{target.name} отравлен на {self.duration} ходов ({self.damage} урона за ход)")
    
    def process_turn(self, target):
        """Вызывается каждый ход для обработки эффекта"""
        if self.current_duration > 0:
            target.take_damage(self.damage)
            self.current_duration -= 1
            print(f"{target.name} получает {self.damage} урона от яда (осталось {self.current_duration} ходов)")
            return True  # Эффект активен
        return False  # Эффект завершен

# Лечение существа
class HealOverTimeEffect(Effect):
    effect_name = "HealOverTime"
    def __init__(self, heal_per_turn: int, duration: int):
        self.heal = heal_per_turn
        self.duration = duration
    
    def apply(self, source, target, game) -> None:
        for _ in range(self.duration):
            target.current_health = min(target.max_health, target.current_health + self.heal)
        print(f"{target.name} восстановлено {self.heal * self.duration} здоровья")

#Оглушение цели
class StunEffect(Effect):
    effect_name = "Stun"
    def apply(self, source, target, game) -> None:
        if not hasattr(target, 'is_stunned'):
            target.is_stunned = False
        
        target.is_stunned = True
        print(f"{target.name} оглушен и пропустит следующий ход!")
        
        # Автоматическое снятие после хода
        def remove_stun():
            target.is_stunned = False
            print(f"{target.name} больше не оглушен")
        
        # Регистрируем обработчик для снятия эффекта
        if hasattr(game, 'add_end_of_turn_effect'):
            game.add_end_of_turn_effect(remove_stun)
        return False


#Вамиризм для существ
class VampirismEffect(Effect):
    effect_name = "Vampirism"
    def apply(self, source, target, game) -> None:
        # Регистрируем обработчик для атаки
        original_attack = source.attack_target
        
        def vampirism_attack(target, game):
            damage_dealt = original_attack(target, game)
            heal_amount = damage_dealt // 2  # Восстанавливаем 50% от урона
            source.current_health = min(source.max_health, source.current_health + heal_amount)
            print(f"{source.name} поглощает {heal_amount} здоровья")
            return damage_dealt
        
        source.attack_target = vampirism_attack
        print(f"{source.name} получает вампиризм на 1 атаку")
        
        # Возвращаем оригинальную атаку после использования
        def reset_attack():
            source.attack_target = original_attack
        
        if hasattr(game, 'add_post_attack_effect'):
            game.add_post_attack_effect(reset_attack)

#Усиление атаки
class StatBuffEffect(Effect):
    effect_name = "StatBuff"
    def __init__(self, attack_bonus: int = 0, defense_bonus: int = 0, duration: int = 1):
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.duration = duration
        self.applied = False
    
    def apply(self, source, target, game) -> None:
        if not self.applied:
            target.attack += self.attack_bonus
            target.defense += self.defense_bonus
            print(f"{target.name} получает +{self.attack_bonus} к атаке и +{self.defense_bonus} к защите")
            self.applied = True

        # Уменьшаем длительность эффекта
        self.duration -= 1

        # Когда срок истёк — эффект можно удалить вручную извне
        if self.duration <= 0 and hasattr(target, "effects"):
            target.effects.remove(self)

# Еффект разрушения брони
class ArmorBreakEffect(Effect):
    effect_name = "ArmorBreak"
    def __init__(self, defense_reduction: int, duration: int):
        self.defense_reduction = defense_reduction
        self.duration = duration
    
    def apply(self, source, target, game) -> None:
        original_defense = target.base_defense
        target.base_defense = max(0, target.base_defense - self.defense_reduction)
        print(f"{target.name} теряет {self.defense_reduction} защиты (теперь {target.base_defense})")
        
        def restore_defense():
            target.base_defense = original_defense
            print(f"Защита {target.name} восстановлена")
        
        if hasattr(game, 'add_turn_effect'):
            for _ in range(self.duration):
                game.add_turn_effect(restore_defense)


# Кровотечение 
class BloodEffect(Effect):
    effect_name = "BloodEffect"
    def __init__(self, base_damage: int, duration: int, stacks: int = 1):
        self.base_damage = base_damage  # Урон за стак
        self.duration = duration
        self.stacks = stacks  # Количество стаков
        self.max_stacks = 5   # Лимит стаков
    
    def apply(self, source, target, game) -> None:
        # Проверяем существующее кровотечение
        existing = next((e for e in target.active_effects 
                        if isinstance(e, BloodEffect)), None)
        
        if existing:
            # Увеличиваем стаки (но не больше лимита)
            existing.stacks = min(existing.stacks + self.stacks, existing.max_stacks)
            existing.duration = max(existing.duration, self.duration)
            print(f"{target.name}: кровотечение усиливается (стаков: {existing.stacks})")
        else:
            if not hasattr(target, 'active_effects'):
                target.active_effects = []
            target.active_effects.append(self)
            print(f"{target.name} истекает кровью ({self.stacks} стак.)")
    
    def trigger_movement(self, target) -> None:
        """Вызывается при движении/атаке цели"""
        total_damage = self.base_damage * self.stacks
        target.take_damage(total_damage)
        print(f"{target.name} теряет {total_damage} HP от кровотечения при движении!")
        self.duration -= 1
    
    def process_turn(self, target) -> bool:
        """Пассивный урон в конце хода"""
        passive_damage = self.base_damage * self.stacks // 2  # Половина урона
        if passive_damage > 0:
            target.take_damage(passive_damage)
            print(f"{target.name} теряет {passive_damage} HP от кровотечения")
        self.duration -= 1
        return self.duration > 0
# Класс аура классс Effect берется из спецаилбных эффектов карт
class AuraEffect(Effect):
    def __init__(self, radius: int, duration: int = -1):
        """
        :param radius: Радиус действия ауры (0 - только владелец, 1 - соседи и т.д.)
        :param duration: Длительность (-1 - бесконечно)
        """
        self.radius = radius
        self.duration = duration
        self.affected_creatures = set()  # Множество существ под эффектом ауры
    
    def get_affected_targets(self, source, game) -> list:
        """Возвращает список существ в радиусе действия ауры"""
        if not hasattr(game, 'battlefield'):
            return []
        
        try:
            index = game.battlefield.index(source)
            start = max(0, index - self.radius)
            end = min(len(game.battlefield), index + self.radius + 1)
            return [creature for creature in game.battlefield[start:end] 
                    if creature != source and creature.is_alive]
        except ValueError:
            return []
    
    def apply(self, source, target, game) -> None:
        """Активирует ауру на источнике"""
        self.source = source
        self.game = game
        print(f"{source.name} активирует ауру {self.__class__.__name__} (радиус: {self.radius})")
        
        # Для обработки на каждом ходу
        if hasattr(game, 'add_turn_effect'):
            game.add_turn_effect(self.update_aura)
    
    def update_aura(self) -> None:
        """Обновляет состояние ауры каждый ход"""
        if self.duration == 0:
            self.remove_aura()
            return
            
        current_targets = self.get_affected_targets(self.source, self.game)
        
        # Удаляем эффект у существ, выбывших из радиуса
        for creature in self.affected_creatures - set(current_targets):
            self.remove_from_creature(creature)
        
        # Добавляем эффект новым существам в радиусе
        for creature in current_targets:
            if creature not in self.affected_creatures:
                self.apply_to_creature(creature)
        
        if self.duration > 0:
            self.duration -= 1
    
    def apply_to_creature(self, creature) -> None:
        """Применяет эффект ауры к конкретному существу"""
        raise NotImplementedError
    
    def remove_from_creature(self, creature) -> None:
        """Удаляет эффект ауры у существа"""
        raise NotImplementedError
    
    def remove_aura(self) -> None:
        """Полностью снимает ауру"""
        for creature in list(self.affected_creatures):
            self.remove_from_creature(creature)
        print(f"Аура {self.__class__.__name__} рассеивается")


# усиление атаки союзников
class AttackAura(AuraEffect):
    def __init__(self, attack_bonus: int, radius: int = 1):
        super().__init__(radius)
        self.attack_bonus = attack_bonus
    
    def apply_to_creature(self, creature):
        creature.temp_attack_bonus += self.attack_bonus
        self.affected_creatures.add(creature)
        print(f"{creature.name} получает +{self.attack_bonus} к атаке от ауры")
    
    def remove_from_creature(self, creature):
        creature.temp_attack_bonus -= self.attack_bonus
        self.affected_creatures.remove(creature)
        print(f"{creature.name} теряет бонус атаки от ауры")

# аура защиты
class DefenseAura(AuraEffect):
    def __init__(self, defense_bonus: int, radius: int = 1):
        super().__init__(radius)
        self.defense_bonus = defense_bonus
    
    def apply_to_creature(self, creature):
        creature.temp_defense_bonus += self.defense_bonus
        self.affected_creatures.add(creature)
        print(f"{creature.name} получает +{self.defense_bonus} к защите от ауры")
    
    def remove_from_creature(self, creature):
        creature.temp_defense_bonus -= self.defense_bonus
        self.affected_creatures.remove(creature)
        print(f"{creature.name} теряет бонус защиты от ауры")


# аура вампиризма
class VampirismAura(AuraEffect):
    def __init__(self, lifesteal_percent: int, radius: int = 1):
        super().__init__(radius)
        self.lifesteal_percent = lifesteal_percent / 100
    
    def apply_to_creature(self, creature):
        original_attack = creature.attack_target
        
        def vampirism_attack(target, game):
            damage = original_attack(target, game)
            heal_amount = int(damage * self.lifesteal_percent)
            creature.current_health = min(creature.max_health, creature.current_health + heal_amount)
            print(f"{creature.name} поглощает {heal_amount} здоровья")
            return damage
        
        creature.attack_target = vampirism_attack
        self.affected_creatures.add(creature)
        print(f"{creature.name} получает вампиризм {self.lifesteal_percent*100}% от ауры")
    
    def remove_from_creature(self, creature):
        # В реализации нужно сохранять оригинальный attack_target
        creature.attack_target = lambda target, game: target.take_damage(creature.attack)
        self.affected_creatures.remove(creature)
        print(f"{creature.name} теряет вампиризм")


# аура лечения союзников
class HealingAura(AuraEffect):
    def __init__(self, heal_amount: int, radius: int = 1):
        super().__init__(radius)
        self.heal_amount = heal_amount
    
    def apply_to_creature(self, creature):
        creature.current_health = min(creature.max_health, 
                                    creature.current_health + self.heal_amount)
        self.affected_creatures.add(creature)
        print(f"{creature.name} восстанавливает {self.heal_amount} здоровья")
    
    def remove_from_creature(self, creature):
        self.affected_creatures.remove(creature)

# аура гниения/яда
class PoisonAura(AuraEffect):
    def __init__(self, damage: int, radius: int = 1, affects_allies: bool = False):
        super().__init__(radius)
        self.damage = damage
        self.affects_allies = affects_allies
    
    def get_affected_targets(self, source, game):
        targets = super().get_affected_targets(source, game)
        if not self.affects_allies:
            targets = [t for t in targets if t not in game.get_allies(source)]
        return targets
    
    def apply_to_creature(self, creature):
        creature.take_damage(self.damage)
        self.affected_creatures.add(creature)  # Для отслеживания, но урон наносим сразу
    
    def remove_from_creature(self, creature):
        self.affected_creatures.remove(creature)

#аура кровотечения
class BleedAura(AuraEffect):
    def __init__(self, damage_per_attack: int, radius: int = 1):
        super().__init__(radius)
        self.damage_per_attack = damage_per_attack
    
    def apply_to_creature(self, creature):
        # Запоминаем оригинальную атаку
        original_attack = creature.attack_target
        
        def bleeding_attack(target, game):
            # Наносим обычный урон
            damage = original_attack(target, game)
            # Добавляем кровотечение
            bleed = BloodEffect(base_damage=self.damage_per_attack, duration=3)
            bleed.apply(creature, target, game)
            return damage
        
        creature.attack_target = bleeding_attack
        self.affected_creatures.add(creature)
        print(f"Аура кровотечения: {creature.name} теперь накладывает кровотечение")
    
    def remove_from_creature(self, creature):
        # В реальной реализации нужно восстановить оригинальный attack_target
        creature.attack_target = lambda target, game: target.take_damage(creature.attack)
        self.affected_creatures.remove(creature)
