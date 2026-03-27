import pygame
from level import *
from player import *
from spritesheet import *
from tiles import *
from camera import *
from enemy import *

pygame.init()
width, height = 1500, 1000
screen = pygame.display.set_mode((1500,1000))

running = True
clock = pygame.time.Clock()
FPS = 36
player =  Player(0, 0)

boss = Boss(5738, -4248, 'fire')
boss.offset_x = -60
boss.offset_y = -93

fodder1 = Fodder(3444, -1560, 'fire')
fodder2 = Fodder(3184, -1560, 'fire')
fodder3 = Fodder(2856, -1560, 'fire')
fodder4 = Fodder(2438, -1560, 'fire')

assassin1 = Assassin(3822, -3224, 'fire')
assassin2 = Assassin(5952, -3224, 'fire')
assassin3 = Assassin(7832, -3224, 'fire')

mage1 = Mage(1156, -3160, 'fire')

tank1 = Tank(7286, -856)
tank2 = Tank(6084, -1496)
entities = [player, fodder1, fodder2, fodder3, fodder4, assassin1, assassin2, assassin3, mage1, tank1, tank2, boss]
for i in range(1, 6):
    entities.append(Fodder(900*i, 424, 'fire'))



fire_level = Level('fire', screen, 'Images/Levels/Fire', entities)
camera = Camera(width, height, fire_level.tile_map.map_width, fire_level.tile_map.map_height)

while running:
    clock.tick(FPS)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    fire_level.update_entities(player)
    player.handle_input(events) # Check input
    camera.update(player)
    fire_level.draw(camera)

    pygame.display.flip()
    