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
boss = Boss(4096, -6400, 'earth')
boss.offset_x = -60
boss.offset_y = -100

fodder1 = Fodder(7738, -2456, 'earth')
fodder2 = Fodder(7228, -2520, 'earth')
fodder3 = Fodder(6638, -2584, 'earth')

assassin1 = Assassin(5872, -358, 'earth')
assassin2 = Assassin(70*64, -358, 'earth')
assassin3 = Assassin(3064, -358, 'earth')

mage1 = Mage(1600, -2560, 'earth')
mage2 = Mage(5120 ,-42*64, 'earth')

tank1 = Tank(128, -13*64)

entities = [player, fodder1, fodder2, fodder3, assassin1, assassin2, assassin3, mage1, mage2, tank1, boss]

for i in range(1, 23):
    entities.append(Fodder(400*i, 500, 'earth'))

for i in range(2, 6):
    entities.append(Tank(1280*i, -640))



earth_level = Level('earth', screen, 'Images/Levels/Earth', entities)
camera = Camera(width, height, earth_level.tile_map.map_width, earth_level.tile_map.map_height)

while running:
    clock.tick(FPS)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    earth_level.update_entities(player)
    player.handle_input(events) # Check input
    camera.update(player)
    earth_level.draw(camera)

    pygame.display.flip()
    