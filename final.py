import pygame
from level import *
from player import *
from spritesheet import *
from tiles import *
from camera import *
from enemy import *
import random

pygame.init()
width, height = 1500, 1000
screen = pygame.display.set_mode((1500,1000))

running = True
clock = pygame.time.Clock()
FPS = 36
player =  Player(8308, -2904)

tank1 = Tank(5830, 40)

mage1 = Mage(5418, 40, 'water')
mage2 = Mage(10426, -1048, 'air')
mage3 = Mage(6460, 40, 'fire')
mage4 = Mage(7990, -2392, 'earth')
mage5 = Mage(15174, -1688, 'water')
mage6 = Mage(15174, -1688, 'fire')
mage7 = Mage(15174, -1688, 'earth')
mage8 = Mage(15174, -1688, 'air')

assassin1 = Assassin(8042, -536, 'water')
assassin2 = Assassin(8412, -536, 'air')
assassin3 = Assassin(10956, -1048, 'earth')
assassin4 = Assassin(8070, -2392, 'fire')
assassin5 = Assassin(15174, -1688, 'water')
assassin6 = Assassin(15174, -1688, 'fire')
assassin7 = Assassin(15174, -1688, 'air')
assassin8 = Assassin(15174, -1688, 'earth')

phase = 2
elements = ['water', 'earth', 'fire', 'air']
random.shuffle(elements)
boss = Boss(8308, -2904, elements.pop(0))
entities = [player, mage1, mage2, mage3, mage4, mage5, mage6, mage7, mage8, assassin1, assassin2, assassin3, assassin4, assassin5, assassin6, assassin7, assassin8, tank1, boss]
for i in range(400, 2000, 400):
    entities.append(Fodder(i, 488, 'water'))
    entities.append(Fodder(i+100, 488, 'earth'))
    entities.append(Fodder(i+200, 488, 'air'))
    entities.append(Fodder(i+300, 488, 'fire'))

final_level = Level('final', screen, 'Images/Levels/Final', entities)
camera = Camera(width, height, final_level.tile_map.map_width, final_level.tile_map.map_height)

while running:
    clock.tick(FPS)
    match phase:
        case 1:
            boss_x, boss_y = boss.x, boss.y
            if not boss in final_level.entities and elements:
                boss = Boss(boss_x, boss_y, elements.pop(0))
                entities.append(boss)
            elif not elements: phase += 1
        case 2: 
            boss = FinalBoss(8308, -2908)
            entities.append(boss)
    
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    final_level.update_entities(player)
    player.handle_input(events) # Check input
    camera.update(player)
    final_level.draw(camera)

    pygame.display.flip()
    