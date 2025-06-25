from cards_classes import Creature_card, Spell_card

# Существа
# Огненные существа
dragon = Creature_card(
        name="Дракон",
        attack=2,
        health=2,
        defense=0,
        manacost=2,
        special_effect="Огненное дыхание"
    )
dragon.load_image('dragon.png')

phoenix = Creature_card(
    name="Феникс",
    attack=4,
    health=3,
    defense=0,
    manacost=5,
    special_effect="Перерождается с 1 хп"
)
phoenix.load_image('phoenix.png')

volcanic_golem = Creature_card(
    name="Вулканический голем",
    attack=1,
    health=5,
    defense=2,
    manacost=3,
    special_effect="Каждый ход +1 урон"
)
volcanic_golem.load_image('volcanic_golem.png')

salamander = Creature_card(
    name="Саламандра",
    attack=3,
    health=1,
    defense=0,
    manacost=3,
    special_effect="Игнорирует броню"
)
salamander.load_image('salamander.png')

lord_of_fire = Creature_card(
    name="Повелитель огня",
    attack=2,
    health=4,
    defense=0,
    manacost=4,
    special_effect="Даёт +1 атаку другим огненным существам"
)
lord_of_fire.load_image('lord_of_fire.png')

fiery_wolf = Creature_card(
    name="Огненный волк",
    attack=3,
    health=3,
    defense=0,
    manacost=3,
    special_effect="Рывок(может атаковать сразу после разыгрования)"
)
fiery_wolf.load_image('fiery_wolf.png')

ashtrainer = Creature_card(
    name="Пеплоход",
    attack=0,
    health=6,
    defense=0,
    manacost=4,
    special_effect="Призыв: Наносит урон, равный своему хп, себе и врагу"
)



# Заклинания
# Огненные заклинания
fireball = Spell_card(
    name="Огненный шар",
    manacost=2,
    damage=3,
    special_effect="Игнорирует броню",
    x=500,
    y=300
)
fireball.load_image('fireball.png')

ignition = Spell_card(
    name="Воспламенение",
    manacost=1, 
    damage=0,
    special_effect="+2 урона существу до конца хода"
)
ignition.load_image('ignition.png')

fire_shield = Spell_card(
    name="Огненный щит",
    manacost=2,
    damage=0,
    special_effect="+3 брони и возгорание 1 выбранному существу"
)
fire_shield.load_image('fire_shield.png')

volcanic_outburst = Spell_card(
    name="Вулканический выброс",
    manacost=4,
    damage=0,
    special_effect="Наносит 5 урона всем. -2 хп герою"
)
volcanic_outburst.load_image('volcanic_outburst.png')