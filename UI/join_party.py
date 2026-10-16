
import asyncio
import pygame


class JoinParty:
    def __init__(self, display, gameStateManager):
        # Use the existing window and state manager
        self.display = display
        self.gameStateManager = gameStateManager
        self.width, self.height = display.get_size()
        self.client = None

        # Fonts and colors
        self.title_font = pygame.font.Font(None, 76)
        self.text_font = pygame.font.Font(None, 36)
        self.code_font = pygame.font.Font(None, 70)
        self.small_font = pygame.font.Font(None, 28)

        self.background_color = (15, 22, 34)
        self.gold = (245, 190, 65)

        # Input and button positions
        self.input_rect = pygame.Rect(390, 310, 500, 90)
        self.join_button = pygame.Rect(490, 445, 300, 75)
        self.back_button = pygame.Rect(490, 550, 300, 65)

        # Input state
        self.code = ""
        self.message = ""
        self.waiting = False

    # Process keyboard and mouse input
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.go_back()

            elif event.key == pygame.K_BACKSPACE:
                self.code = self.code[:-1]

            elif event.key == pygame.K_RETURN:
                self.try_join()

            elif len(self.code) < 6:
                character = event.unicode.upper()

                if character in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
                    self.code += character

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.join_button.collidepoint(event.pos):
                self.try_join()

            elif self.back_button.collidepoint(event.pos):
                self.go_back()

        return True

    # Send the entered code to the server
    def try_join(self):
        if self.waiting:
            return

        if len(self.code) != 6:
            self.message = "Enter a six-character party code"
            return

        if self.client is None:
            self.message = "Multiplayer client unavailable"
            return

        self.waiting = True
        self.message = "Connecting to party..."

        asyncio.create_task(self.client.join_party(self.code, "Player"))

    # Return to the multiplayer menu
    def go_back(self):
        self.waiting = False
        self.message = ""
        self.gameStateManager.set_state("multiplayer_menu")

    # Draw the join party screen
    def run(self):
        self.display.fill(self.background_color)

        # Security terminal header
        pygame.draw.rect(
            self.display, self.gold,
            (0, 0, self.width, 12)
        )

        title = self.title_font.render(
            "CAMPUS ACCESS TERMINAL",
            True,
            self.gold
        )
        self.display.blit(
            title,
            title.get_rect(center=(self.width // 2, 120))
        )

        subtitle = self.text_font.render(
            "ENTER YOUR CREW'S ACCESS CODE",
            True,
            (205, 215, 225)
        )
        self.display.blit(
            subtitle,
            subtitle.get_rect(center=(self.width // 2, 230))
        )

        # Code input box
        pygame.draw.rect(
            self.display,
            (35, 48, 65),
            self.input_rect,
            border_radius=12
        )
        pygame.draw.rect(
            self.display,
            self.gold,
            self.input_rect,
            3,
            border_radius=12
        )

        code_text = self.code_font.render(
            self.code or "------",
            True,
            self.gold
        )
        self.display.blit(
            code_text,
            code_text.get_rect(center=self.input_rect.center)
        )

        # Join button
        pygame.draw.rect(
            self.display,
            self.gold,
            self.join_button,
            border_radius=10
        )
        join_text = self.text_font.render(
            "JOIN PARTY",
            True,
            (20, 25, 35)
        )
        self.display.blit(
            join_text,
            join_text.get_rect(center=self.join_button.center)
        )

        # Back button
        pygame.draw.rect(
            self.display,
            (100, 55, 65),
            self.back_button,
            border_radius=10
        )
        back_text = self.text_font.render(
            "BACK",
            True,
            (255, 255, 255)
        )
        self.display.blit(
            back_text,
            back_text.get_rect(center=self.back_button.center)
        )

        # Connection status or error
        if self.message:
            message_text = self.small_font.render(
                self.message,
                True,
                (230, 225, 210)
            )
            self.display.blit(
                message_text,
                message_text.get_rect(
                    center=(self.width // 2, 665)
                )
            )
