import pygame
import json

class Spritesheet:

    def __init__(self, file_path):
        self.file_path = file_path # Path to JSON and Sprite sheet image
        self.sprite_sheet = pygame.image.load(f"{self.file_path}.png").convert_alpha() # Load the spritesheet image
        self.data_path = f"{self.file_path}.json"  # Path to JSON
        self.x, self.y = 0,0 # Position of sprite
        self.images = [] # List of images for animation
        self.index = 0 # Index of image in animation
        with open(self.data_path, 'r') as f: # Read JSON file and extract data
             self.data = json.load(f)
        self.parse_sprites()
    
    def parse_sprites(self): # Populate images array
        for name in self.data['frames']: # Loop through images in spritesheet
            sprite = self.data['frames'][name]['frame']
            x, y, w, h = sprite['x'], sprite['y'], sprite['w'], sprite['h'] # Coordinates of image within spritesheet
            image = pygame.Surface((w, h), pygame.SRCALPHA) #  create a surface to blit image on
            image.blit(self.sprite_sheet, (0,0), (x,y,w,h)) # Blit image on surface
            image = pygame.transform.scale(image, (64, 64)).convert_alpha() # Rescale and make opaque
            self.images.append(image) # Add image to images   

    def get_sprite_id(self, tile_id):
        if tile_id == 0: pass
        index = tile_id - 1
        if 0 <= index < len(self.images):
            return self.images[index]
        return None  
    
    def draw(self, screen, camera):
         self.index = (self.index+1) % len(self.images)
         screen.blit(self.images[self.index],(self.x - camera.offset_x, self.y - camera.offset_y))

         
