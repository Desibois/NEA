import pygame
from menus import *
from manager import *


pygame.init()
width, height = 1500, 1000
screen = pygame.display.set_mode((width, height))
background_image = pygame.image.load("Images/Background.jpeg")
background_image = pygame.transform.scale(background_image, (width, height)) # scale the background image to the window
pygame.display.set_caption("Keyboard Warriors - Main Menu")  
running = True # Flag for the main loop
Manager = GameManager(screen, "main", background_image) # Manager class will handle gameplay
Manager.settings() # First menu is main menu
menu = Manager.current_menu 
while Manager.running: # Game loop
    menu = Manager.current_menu  
    Manager.render_menu() # Draw and render all menu elements
    pygame.display.flip() # Update display
    for event in pygame.event.get(): # Handle keyboard events
        if event.type == pygame.QUIT: # Quit
            Manager.running = False
        else:
            if menu is not None: 
                menu.handle_event(event) # Handle other events

pygame.quit()