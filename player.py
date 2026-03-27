import pygame
from spritesheet import *
from spells import *



class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.is_player = True
        self.x, self.y = x, y
        self.rect = pygame.Rect(self.x, self.y, 50, 64)
        self.velocity_x, self.velocity_y = 0, 0
        self.speed = 10
        self.max_health = 100
        self.hp = 100
        self.jumping = False
        self.moving = False
        self.grounded = False
        self.casting = False
        self.display_spells = False
        self.end_boss = False
        self.input_phrase = ""
        self.attack_timer = 0
        self.hit_timer = 0
        self.hit_duration = 20
        self.spells = {'IGNATIOUS':{'name': 'ignatious', 'element': 'fire', 'speed': 20, 'damage': 10, 'lifetime': 25, 'size': (64,64), 'caster': self}, 
                       'HYDROBLAST': {'name': 'hydroblast', 'element': 'water', 'speed': 15, 'damage': 10, 'lifetime': 20, 'size': (64,64), 'caster': self},
                       'AEROSLASH': {'name': 'aeroslash', 'element': 'air', 'speed': 25, 'damage': 10, 'lifetime': 30, 'size': (64,64), 'caster': self},
                       'TERRATHROW': {'name': 'terrathrow', 'element': 'earth', 'speed': 15, 'damage': 10, 'lifetime': 33, 'size': (64,64), 'caster': self}}
        self.spell = {}
        self.input_spell = ''
        self.spell = {}
        self.gravity = 1
        self.direction = 1
        self.spritesheets = {
            'idle': Spritesheet("Images/Spritesheets/player/idle/idle"),
            'run': Spritesheet("Images/Spritesheets/player/run/run"),
            'roll': Spritesheet("Images/Spritesheets/player/roll/roll"),
            'jump': Spritesheet("Images/Spritesheets/player/jump/jump"),
            'fall': Spritesheet("Images/Spritesheets/player/fall/fall"),
            'hit': Spritesheet("Images/Spritesheets/player/hit/hit"),
            'dying': Spritesheet("Images/Spritesheets/player/dying/dying"),
            'cast': Spritesheet("Images/Spritesheets/player/cast/cast"),
            'attack': Spritesheet("Images/Spritesheets/player/attack/attack"),
            'dead':  Spritesheet("Images/Spritesheets/player/dead/dead")
        }
        self.set_state('idle')
        self.scale_frames('cast')
        self.scale_frames('attack')

    
    def scale_frames(self, state):
        scaled_images = []
        for image in self.spritesheets[state].images:
            scaled = pygame.transform.scale(image, (128, 128))
            frame = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
            frame.blit(scaled, (0, 0))
            scaled_images.append(frame)
        self.spritesheets[state].images = scaled_images


    def set_state(self, state): # Change animation
        self.state = state
        self.image = self.spritesheets[self.state]
    

    def run(self, direction):
        self.moving = True
        if direction != self.direction: #Check for a change in direction
            self.direction = direction
            for sheet in self.spritesheets.values(): 
                for i in range(len(sheet.images)): # Flip every frame in the sprite sheet
                    sheet.images[i] = pygame.transform.flip(sheet.images[i], True, False)
        self.velocity_x = self.speed * self.direction # Apply direction to motion
        if self.grounded:
            self.set_state('run')
        else:
            self.set_state('roll')      

    
    def jump(self):
        if self.grounded: # Only allow jumping when on the ground
            self.jumping = True
            self.grounded = False
            self.velocity_y = -20
            self.set_state('jump')


    def cast(self, events):

        if not self.casting: return
        if self.state != 'attack':
            self.set_state('cast')

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.casting = False
                    return
                if event.key == pygame.K_RETURN and self.state != 'attack':
                    self.set_state('attack')
                    self.velocity_x = 0
                    self.attack_timer = 0
                    return
                character = event.unicode
                if character.isalpha() and len(self.input_spell) <= 20:
                    character = character.upper() 
                    self.input_spell += character
                
        if self.state == 'attack':
            if self.input_spell in self.spells:
                self.attack()
            else: 
                self.take_damage(0)
                self.casting = False
                self.input_spell = ''


    def attack(self):
        self.attack_timer += 1
        if self.attack_timer >= 6:
            self.attack_timer = 0
            self.casting = False
            self.spell = self.spells[self.input_spell]
            self.input_spell = ''


    
    def handle_input(self, events): 
        keys = pygame.key.get_pressed() # Get key presses
        self.moving = False

        if self.end_boss:
            self.velocity_x = 0
            self.velocity_y = 0
            for event in events:
                if event.type == pygame.KEYDOWN:
                    char = event.unicode.upper()
                    self.input_phrase += char
            return

        if keys[pygame.K_1]: 
            self.hp = 100
        
        if self.hp <= 0: 
            self.dead()
            return
        
        if self.hit_timer > 0:
            self.hit_timer -= 1
            self.velocity_x = 0  
            return
        
        if self.casting:
            self.velocity_x = 0
            self.cast(events)
            return

        if keys[pygame.K_e]: 
            self.display_spells = True
        else: self.display_spells = False
        
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]: #JUMP
            self.jump()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: #RIGHT
            self.run(1)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]: #LEFT
            self.run(-1)
        elif keys[pygame.K_0]: self.take_damage(1)
        elif any(event.type == pygame.KEYDOWN and event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) for event in events) and self.grounded:
            self.casting = True

        else:
            if self.grounded: 
                self.set_state('idle')
            self.velocity_x = 0
        if not self.grounded and self.velocity_y > 0:
            self.set_state('fall')
    

    def update(self,level):
        if self.state == 'dead': return 
        self.x += self.velocity_x  # Update x
        self.rect.x = self.x 

        collision_tile = level.check_collision(self.rect)
        if collision_tile:
            if self.velocity_x > 0:  # Moving right - hit left side of tile
                self.x = collision_tile.left - self.rect.width
                self.rect.x = self.x
                self.velocity_x = 0 
            elif self.velocity_x < 0:  # Moving left - hit right side of tile
                self.x = collision_tile.right
                self.rect.x = self.x 
                self.velocity_x = 0

        if not self.grounded: self.velocity_y += self.gravity # XLR8 ;)
        self.y += self.velocity_y # Update y
        self.rect.y = self.y
        
        collision_tile = level.check_collision(self.rect)

        if collision_tile:
            if self.velocity_y > 0:  # falling
                self.y = collision_tile.top - self.rect.height
                self.rect.y = self.y
                self.velocity_y = 0
                self.grounded = True

            elif self.velocity_y < 0:  # rising
                self.y = collision_tile.bottom
                self.rect.y = self.y
                self.velocity_y = 0

        else: self.grounded = level.is_grounded(self.rect)

        # Falling animation
        if not self.grounded and self.velocity_y > 0:
            self.set_state('fall')
        
        if self.y > 600: # Half life
            self.x = 0
            self.y = 0
            self.take_damage(self.hp/2)
        
        for sprite in self.spritesheets.values(): # Update coordinates for all frames in spritesheet
            sprite.x = self.x
            sprite.y = self.y
        
        return False
    

    def take_damage(self, damage, element=None):
        self.casting = False
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.dead()
        else:
            self.set_state('hit')
            self.hit_timer = self.hit_duration
    

    def dead(self):
        if self.state == 'dead':
            return
        if self.state != 'dying':
            self.set_state('dying')
            self.death_timer = 0
            return
        self.death_timer += 1
        if self.death_timer >= 10:
            self.velocity_x = 0  
            self.set_state('dead')

            
    def draw_health_bar(self, screen, x=20, y=20, width=200, height=20):
        pygame.draw.rect(screen, (40, 40, 40), (x, y, width, height), border_radius=4)
        ratio = self.hp / self.max_health
        ratio = max(0, min(ratio, 1)) # Clamp between 0 and 1
        fill_width = int(width * ratio)
        pygame.draw.rect(screen, (200, 50, 50), (x, y, fill_width, height), border_radius=4)
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2, border_radius=4)


    def draw_text_box(self, screen, x=20, y=60, height=60, padding=20):
        font = pygame.font.Font('Images/PixelPurl.ttf', 48)
        text_surface = font.render(self.input_spell, True, '#783CA0')
        char_width = 21
        if len(self.input_spell) == 0:
            width = height 
        else:
            width = len(self.input_spell) * char_width + padding * 2
        fill_color = '#E8D4C4'
        border_color = '#C58F3D'
        pygame.draw.rect(screen, fill_color, (x, y, width, height), border_radius=6)
        pygame.draw.rect(screen, border_color, (x, y, width, height), 3, border_radius=6)

        text_x = x + padding
        text_y = y + (height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))


    def draw_spells(self, screen, x=20, y=60, width=260):
        font = pygame.font.Font('Images/PixelPurl.ttf', 36)

        fill_color = '#E8D4C4'
        border_color = '#C58F3D'
        text_color = '#783CA0'

        line_height = 40
        padding = 15

        spells = list(self.spells.keys())
        height = padding * 2 + len(spells) * line_height

        pygame.draw.rect(screen, fill_color, (x, y, width, height), border_radius=6)
        pygame.draw.rect(screen, border_color, (x, y, width, height), 3, border_radius=6)

        for i in range(0, len(spells)):
            text_surface = font.render(spells[i], True, text_color)
            text_x = x + padding
            text_y = y + padding + i * line_height
            screen.blit(text_surface, (text_x, text_y))

    
    def draw(self, screen, camera):
        if self.casting and self.grounded:
            orig_x, orig_y = self.image.x, self.image.y
            self.image.x = self.x - 32
            self.image.y = self.y - 64
            self.image.draw(screen, camera)
            self.image.x, self.image.y = orig_x, orig_y
            if self.attack_timer == 0: self.draw_text_box(screen)
        else:
            self.image.draw(screen, camera)
        self.draw_health_bar(screen)
        if self.display_spells: self.draw_spells(screen)


