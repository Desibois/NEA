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


fodder1 = Fodder(2012, -1240, 'air')
fodder2 = Fodder(2262, -1240, 'air')
fodder3 = Fodder(2532, -1240, 'air')
fodder4 = Fodder(2792, -1240, 'air') 

mage = Mage(3152, -1304, 'air')

tank1 = Tank(4006, -856 )
tank2 = Tank(4508, -1624)

assassin1 = Assassin(2622, -1752, 'air')
assassin2 = Assassin(3572, -1752, 'air')

boss = Boss(6890,522,'air')

entities = [player, fodder1, fodder2, fodder3, fodder4, mage, tank1, tank2, assassin1, assassin2, boss]

air_level = Level('air', screen, 'Images/Levels/air', entities)
camera = Camera(width, height, air_level.tile_map.map_width, air_level.tile_map.map_height)

while running:
    clock.tick(FPS)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    air_level.update_entities(player)
    player.handle_input(events) # Check input
    camera.update(player)
    air_level.draw(camera)

    pygame.display.flip()
    