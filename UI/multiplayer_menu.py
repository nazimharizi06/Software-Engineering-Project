
import pygame


class MultiplayerMenu:
    def __init__(self, display, gameStateManager):
        # Use the same window and state manager as the homepage
        self.display = display
        self.gameStateManager = gameStateManager

        self.width, self.height = display.get_size()

        # Set up fonts for the screen
        self.title_font = pygame.font.Font(None, 75)
        self.button_font = pygame.font.Font(None, 42)

        # Back button position
        self.back_button = pygame.Rect(40, 620, 180, 65)

    # Handle clicks on the Back button
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.collidepoint(event.pos):
                self.gameStateManager.set_state("main_menu")

        return True

    # Draw the multiplayer screen
    def run(self):
        self.display.fill((22, 29, 47))

        title = self.title_font.render(
            "MULTIPLAYER", True, (255, 195, 65)
        )

        self.display.blit(
            title,
            title.get_rect(center=(self.width // 2, 170))
        )

        message = self.button_font.render(
            "Create Party / Join Party - Coming Next",
            True,
            (245, 240, 225)
        )

        self.display.blit(
            message,
            message.get_rect(center=(self.width // 2, 350))
        )

        # Draw the Back button
        pygame.draw.rect(
            self.display,
            (245, 195, 80),
            self.back_button,
            border_radius=8
        )

        back_text = self.button_font.render(
            "BACK", True, (20, 25, 35)
        )

        self.display.blit(
            back_text,
            back_text.get_rect(center=self.back_button.center)
        )
