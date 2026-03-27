import pygame
from spritesheet import *


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.spritesheets = {
            'idle': Spritesheet("Images/Spritesheets/player/idle/idle"),
            'run': Spritesheet("Images/Spritesheets/player/run/run"),
            'roll': Spritesheet("Images/Spritesheets/player/roll/roll"),
            'jump': Spritesheet("Images/Spritesheets/player/jump/jump"),
            'fall': Spritesheet("Images/Spritesheets/player/fall/fall"),
            'hit': Spritesheet("Images/Spritesheets/player/hit/hit"),
            'dying': Spritesheet("Images/Spritesheets/player/dying/dying"),
            'cast': Spritesheet("Images/Spritesheets/player/cast/cast"),
            'attack': Spritesheet("Images/Spritesheets/player/attack/attack")
        }
        self.state = 'idle'
        self.direction = 1
        self.moving = False
        self.jumping = False
        self.grounded = False
        self.gravity = 1
        self.x, self.y = 150, 50
        self.rect = pygame.Rect(self.x, self.y, 50, 64)
        self.velocity_x, self.velocity_y = 0, 0
        for sprite in self.spritesheets.values():
            sprite.x = self.x
            sprite.y = self.y
        self.speed = 8
        self.scale_frames('cast')
        self.scale_frames('attack')
        self.sfx = ''
        pygame.mixer.music.set_volume(0.75)

    def scale_frames(self, state):
        scaled_images = []
        for image in self.spritesheets[state].images:
            scaled_image = pygame.transform.scale(image, (128, 128))
            scaled_images.append(scaled_image)
        self.spritesheets[state].images = scaled_images
    
    def play_sfx(self):
        if self.state != self.sfx:
            pygame.mixer.music.pause()
            self.sfx = self.state
            pygame.mixer.music.load(f"SFX/{self.state}.mp3")
            pygame.mixer.music.play(-1)


    
    def update_position(self, level):
        self.x += self.velocity_x
        self.rect.x = self.x
        collision_tile_horizontal = level.check_player_collision(self.rect)
        self.handle_collision_horizontal(collision_tile_horizontal)
        if not self.grounded:
            self.velocity_y += self.gravity
        self.y += self.velocity_y
        self.rect.y = self.y
        collision_tile_vertical = level.check_player_collision(self.rect)
        on_ground = level.check_collision(self.rect)
        self.handle_collision_vertical(collision_tile_vertical, on_ground)
        for sprite in self.spritesheets.values():
            sprite.x = self.x
            sprite.y = self.y

    def set_state(self, state):
        self.state = state
        self.image = self.spritesheets[self.state]
    
    def run(self, direction):
        
        if direction != self.direction:
            self.direction = direction
            for sheet in self.spritesheets.values():
                for i in range(len(sheet.images)):
                    sheet.images[i] = pygame.transform.flip(sheet.images[i], True, False)
        
        self.velocity_x = direction * self.speed

        if self.grounded:
            self.set_state('run')

        else:
            self.set_state('roll')

    def jump(self):
        if self.grounded:
            self.jumping = True
            self.grounded = False
            self.velocity_y = -20
            self.set_state('jump')

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            self.jump()

        self.moving = False
        if keys[pygame.K_RIGHT]:
            self.run(1)
            self.moving = True
        elif keys[pygame.K_LEFT]:
            self.run(-1)
            self.moving = True
        else:
            self.velocity_x = 0
            if self.grounded:
                self.set_state('idle')
        
        self.play_sfx()

        
        
    def handle_collision_vertical(self, collision_tile, on_ground):
        if collision_tile:
            if self.velocity_y > 0:
                self.y = collision_tile.top - self.rect.height
                self.rect.y = self.y
                self.grounded = True
                self.velocity_y = 0
            elif self.velocity_y < 0:
                self.y = collision_tile.bottom
                self.rect.y = self.y
                self.velocity_y = 0
            
        else:
            self.grounded = on_ground

        if not self.grounded and self.velocity_y > 0:
            self.set_state('fall')
    
    def handle_collision_horizontal(self, collision_tile):
        if collision_tile:
            if self.velocity_x > 0:  # Moving right - hit left side of tile
                self.x = collision_tile.left - self.rect.width
                self.rect.x = self.x
                self.velocity_x = 0 
            elif self.velocity_x < 0:  # Moving left - hit right side of tile
                self.x = collision_tile.right
                self.rect.x = self.x 
                self.velocity_x = 0


                        

                