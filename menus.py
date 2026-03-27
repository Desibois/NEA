import pygame


class Button:
    def __init__(self, screen, name, image_path, position, action, manager):
        self.name = name
        self.screen = screen
        self.image_path = image_path
        self.image = pygame.image.load(self.image_path).convert_alpha() # Only loads the opaque areas of the image
        self.position = position
        self.rect = self.image.get_rect(topleft=self.position)
        self.action = action
        self._manager = manager
        self.mixer = manager.mixer # SFX
        self._source_position = position # Original position of button
        self._source_size = self.image.get_size() # Original size of button

    def draw(self): 
        self.screen.blit(self.image, self.position)
    
    def is_clicked(self, event): 
        if event.type != pygame.MOUSEBUTTONDOWN: # Button is not clicked if the mouse is not pressed
            return False

        if not hasattr(event, 'pos'): # If the event does not have an attribute for the position of the even
            return False

        if self.rect.collidepoint(event.pos):  # Relative position of event to the button
            x = event.pos[0] - self.rect.x
            y = event.pos[1] - self.rect.y

            try:
                pixel_alpha = self.image.get_at((x, y)).a # Opaqueness of button image at event position
                if pixel_alpha > 0: # Button has been clicked
                    if self._manager: 
                        sound = self.mixer.Sound("SFX/button.wav")
                        sound.set_volume(self._manager.music_volume)
                        sound.play() # Button click
                        self._manager.handle_action(self.action) # Button do
                    return True
            except IndexError:
                return False
        return False
    
    def handle_event(self, event):
        if self.is_clicked(event): return True
        return False
    
class Slider(Button): # Inherits Button
    def __init__(self, screen, name, position, action, manager, initial=0.5):
        slider_path = "Images/Settings/Buttons/SLIDER.png" 
        dial_path = "Images/Settings/Buttons/DIAL.png"
        self.dial_image = pygame.image.load(dial_path).convert_alpha()
        super().__init__(screen, name, slider_path, position, action, manager) # Button init
        self.dial_rect = self.dial_image.get_rect()
        self._dial_source_image = self.dial_image.copy()
        self._dial_source_size = self.dial_image.get_size()
        self.centre_line = [self.rect.height // 2] * self.rect.width # List of y coordinates for points on the centre line
        self.min_x = self.rect.x
        self.max_x = self.rect.x + self.rect.width - self.dial_rect.width
        self.dragging = False # Flag
        self.value = float(max(0.0, min(1.0, initial))) # ensures value is between 0 and 1
        self.centreline() # Since slider is slanted, this calculates the line accross which the button will slide across
        self.update_dial() # Updates position of dial on slider


    def centreline(self): 
        width = self.rect.width
        height = self.rect.height
        try:
            for x in range(width): # Loop across the slider
                top = None 
                bottom = None
                for y in range(height): # Loop to locate the y value of the slider at that point
                    try:
                        a = self.image.get_at((x, y)).a # Opaque area of slider via alpha values
                    except IndexError:
                        continue
                    if a > 0: # slider is visisble
                        if top is None:
                            top = y
                        bottom = y
                if top is not None and bottom is not None:
                    self.centre_line[x] = (top + bottom) / 2 # Update centre line with new y value for x
        except Exception:
            pass


    def update_dial(self):
        span = max(1, self.max_x - self.min_x) # span cannot be below than 1
        self.dial_rect.x = int(self.min_x + self.value * span)
        rel_x = int(self.dial_rect.x - self.rect.x) # x value of dial relative to slider
        rel_x = max(0, min(rel_x, max(1, self.rect.width) - 1))  # Must be between 0 and 1
        centerline_len = len(self.centre_line)            
        rel_x = min(rel_x, centerline_len - 1)                 
        center = self.centre_line[rel_x] 
        self.dial_rect.y = self.rect.y + int(center) - (self.dial_rect.height // 2) # Centre and update the dial's position on the slider 

    def update_mouse(self, mouse_x): # Calculates the new value based on the mouse's position and updates the dial position
        rel = mouse_x - self.min_x
        span = max(1, self.max_x - self.min_x)
        value = (rel / span)
        value = max(0.0, min(1.0, value))
        if self.value != value: # Update value and execute the adjustment
            self.value = value
            self.update_dial()
            if self._manager:
                self._manager.handle_action(self.action, self.value)
                

    def draw(self): # Overriden button draw method
        super().draw() 
        self.screen.blit(self.dial_image, self.dial_rect.topleft)

    def is_clicked(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or not hasattr(event, 'pos'): return False # Only consider when user is dragging the slider
        if self.dial_rect.collidepoint(event.pos): # If the user clicks on the dial
            self.dragging = True
            return True
        if self.rect.collidepoint(event.pos): # If the user clicks on a position for the dial to go to
            self.update_mouse(event.pos[0])
            return True
        return False

    def handle_event(self, event): # Handle events relate to the slider
        if event.type == pygame.MOUSEBUTTONDOWN: self.is_clicked(event) # When slider is pressed
        if event.type == pygame.MOUSEMOTION and self.dragging: # When slider is dragged
            if hasattr(event, 'pos'):
                self.update_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging: # When slider is let go
            self.dragging = False
            return True
        return False
   
class Menu: # Contains buttons and sliders
    def __init__(self, screen, title, bg_image_path, opened, buttons):
        self.title = title
        self.screen = screen
        self.bg_image = pygame.image.load(bg_image_path)
        self.opened = opened
        self.buttons = buttons if buttons is not None else []
    
    def handle_event(self, event):
        if not self.opened:
            return False

        for widget in self.buttons:
            if widget.handle_event(event): return True
        return False
