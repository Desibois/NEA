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
tank = Tank(6400, -768)
boss = Boss(3840, -4480, 'water')
assassin1 = Assassin(5632, -1408, 'water')
assassin2 = Assassin(4288, -1408, 'water')
mage1 = Mage(3200, -1408, 'water')
mage2 = Mage(3968,3840, 'water')
entities = [player, tank ,boss, assassin1, assassin2, mage1, mage2]

for i in range(1, 23):
    entities.append(Fodder(400*i, 500, 'water'))

water_level = Level('water', screen, 'Images/Levels/Water', entities)
camera = Camera(width, height, water_level.tile_map.map_width, water_level.tile_map.map_height)

while running:
    clock.tick(FPS)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    water_level.update_entities(player)
    player.handle_input(events) # Check input
    camera.update(player)
    water_level.draw(camera)

    pygame.display.flip()
    