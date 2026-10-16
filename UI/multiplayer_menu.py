import asyncio
from pathlib import Path
import pygame


class MultiplayerMenu:
    def __init__(self, display, gameStateManager):
        # Use the same window and state manager as the homepage
        self.display = display
        self.gameStateManager = gameStateManager
        self.width, self.height = display.get_size()

        # Find the background image inside the assets folder
        project_folder = Path(__file__).resolve().parent.parent
        image_path = project_folder / "assets" / "multiplayer_background.png"

        # Load and resize the image to fit the game window
        background = pygame.image.load(str(image_path)).convert()
        self.background = pygame.transform.smoothscale(
            background, (self.width, self.height)
        )

        # Clickable areas over the buttons in the new artwork
        # The original image is 1648 x 928
        original_width = 1648
        original_height = 928

        button_positions = {
            "create": (520, 340, 630, 195),
            "join": (540, 545, 590, 165),
            "back": (610, 735, 420, 105)
        }

        # Scale the button positions to match the game window
        scale_x = self.width / original_width
        scale_y = self.height / original_height

        self.buttons = {}

        for name, (x, y, width, height) in button_positions.items():
            self.buttons[name] = pygame.Rect(
                round(x * scale_x),
                round(y * scale_y),
                round(width * scale_x),
                round(height * scale_y)
            )

        self.hovered_button = None
        self.message = ""
        self.message_font = pygame.font.Font(None, 30)

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
                    self.button_clicked(name)
                    break

        return True

    # Decide what happens when a button is clicked
    def button_clicked(self, name):
        if name == "create":
            #ask the server to create a new party
            asyncio.create_task(self.client.create_party("Host"))
            # Open the lobby when Create Party is clicked
            self.gameStateManager.set_state("lobby")
            

        elif name == "join":
            # Open the Join Party screen when Join Party is clicked
            self.gameStateManager.set_state("join_party")

        elif name == "back":
            self.message = ""
            self.gameStateManager.set_state("main_menu")

    # Draw the multiplayer menu each frame
    def run(self):
        self.display.blit(self.background, (0, 0))

        # Highlight the button the mouse is hovering over
        if self.hovered_button is not None:
            rect = self.buttons[self.hovered_button]

            highlight = pygame.Surface(rect.size, pygame.SRCALPHA)
            highlight.fill((255, 210, 75, 30))
            self.display.blit(highlight, rect.topleft)

        # Display a message when Create or Join is clicked
        if self.message:
            label = self.message_font.render(
                self.message, True, (255, 255, 255)
            )

            label_rect = label.get_rect(
                center=(self.width // 2, self.height - 25)
            )

            pygame.draw.rect(
                self.display,
                (25, 30, 40),
                label_rect.inflate(30, 16),
                border_radius=8
            )

            self.display.blit(label, label_rect)

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
