
from pathlib import Path
import pygame


class MainMenu:
    def __init__(self, display, gameStateManager):
        # Use the existing game window and state manager
        self.display = display
        self.gameStateManager = gameStateManager
        self.width, self.height = display.get_size()

        # Locate the background image in the assets folder
        project_folder = Path(__file__).resolve().parent.parent
        image_path = project_folder / "assets" / "main_menu_background.png"

        # Load the artwork and resize it to fit the window
        background = pygame.image.load(str(image_path)).convert()
        self.background = pygame.transform.smoothscale(
            background, (self.width, self.height)
        )

        # Define clickable areas over the buttons in the artwork
        self.buttons = {
            "play": pygame.Rect(490, 335, 330, 95),
            "rules": pygame.Rect(515, 440, 290, 75),
            "quit": pygame.Rect(515, 520, 290, 75)
        }

        # Scale the button positions to match the window size
        scale_x = self.width / 1280
        scale_y = self.height / 720

        for name, rect in self.buttons.items():
            self.buttons[name] = pygame.Rect(
                round(rect.x * scale_x),
                round(rect.y * scale_y),
                round(rect.width * scale_x),
                round(rect.height * scale_y)
            )

        self.hovered_button = None

    # Check mouse movement and button clicks
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered_button = None

            for name, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    self.hovered_button = name
                    break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    return self.button_clicked(name)

        return True

    # Handle each menu button
    def button_clicked(self, name):
        if name == "play":
            self.gameStateManager.set_state("multiplayer_menu")

        elif name == "rules":
            print("How To Play screen coming soon")

        elif name == "quit":
            return False

        return True

    # Draw the homepage every frame
    def run(self):
        self.display.blit(self.background, (0, 0))

        # Highlight whichever button the mouse is hovering over
        if self.hovered_button is not None:
            rect = self.buttons[self.hovered_button]

            highlight = pygame.Surface(rect.size, pygame.SRCALPHA)
            highlight.fill((255, 210, 75, 35))
            self.display.blit(highlight, rect.topleft)

        # Change the cursor when hovering over a button
        mouse_pos = pygame.mouse.get_pos()
        over_button = any(
            rect.collidepoint(mouse_pos)
            for rect in self.buttons.values()
        )

        cursor = (
            pygame.SYSTEM_CURSOR_HAND
            if over_button
            else pygame.SYSTEM_CURSOR_ARROW
        )

        pygame.mouse.set_cursor(cursor)
