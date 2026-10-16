import asyncio
import pygame


class Lobby:
    def __init__(self, display, gameStateManager):
        # Use the existing game window and state manager
        self.display = display
        self.gameStateManager = gameStateManager
        self.width, self.height = display.get_size()

        # Fonts for the lobby
        self.title_font = pygame.font.Font(None, 75)
        self.heading_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 34)
        self.small_font = pygame.font.Font(None, 27)

        # Temporary lobby information until the server is connected
        self.party_code = "------"
        self.players = ["Host"]
        self.is_host = True

        # Buttons at the bottom of the lobby
        self.start_button = pygame.Rect(850, 590, 300, 70)
        self.leave_button = pygame.Rect(130, 590, 250, 70)

    # Update lobby information when the server sends new data
    def update_lobby(self, party_code, players, is_host):
        self.party_code = party_code
        self.players = players
        self.is_host = is_host

    # Handle button clicks
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

        # Leave the current multiplayer party
            if self.leave_button.collidepoint(event.pos):
                print("Leave Party clicked")

                if self.client is not None:
                    asyncio.create_task(self.client.leave_party())

                self.gameStateManager.set_state("multiplayer_menu")

            # Ask the server to start the game
            elif self.start_button.collidepoint(event.pos):
                if self.is_host and self.client is not None:
                    asyncio.create_task(self.client.start_game())

        return True

    # Draw the lobby every frame
    def run(self):
        self.display.fill((18, 23, 37))

        # Decorative top bar
        pygame.draw.rect(
            self.display, (240, 180, 65), (0, 0, self.width, 12)
        )

        # Lobby title
        title = self.title_font.render(
            "MISSION BRIEFING", True, (255, 200, 75)
        )
        self.display.blit(
            title, title.get_rect(center=(self.width // 2, 85))
        )

        # Party code section
        pygame.draw.rect(
            self.display,
            (35, 43, 60),
            (110, 155, 1060, 130),
            border_radius=12
        )

        code_label = self.text_font.render(
            "PARTY CODE", True, (190, 195, 205)
        )
        self.display.blit(code_label, (145, 180))

        code_text = self.heading_font.render(
            self.party_code, True, (255, 200, 75)
        )
        self.display.blit(code_text, (145, 220))

        # Player roster panel
        pygame.draw.rect(
            self.display,
            (35, 43, 60),
            (110, 320, 1060, 230),
            border_radius=12
        )

        roster_title = self.heading_font.render(
            "YOUR CREW", True, (255, 255, 255)
        )
        self.display.blit(roster_title, (145, 345))

        # Display each connected player
        for index, player in enumerate(self.players):
            player_text = self.text_font.render(
                f"{index + 1}. {player}",
                True,
                (235, 235, 235)
            )
            self.display.blit(
                player_text, (150, 410 + index * 42)
            )

        # Leave Party button
        pygame.draw.rect(
            self.display,
            (150, 55, 60),
            self.leave_button,
            border_radius=10
        )

        leave_text = self.text_font.render(
            "LEAVE PARTY", True, (255, 255, 255)
        )
        self.display.blit(
            leave_text,
            leave_text.get_rect(center=self.leave_button.center)
        )

        # Only the host can start the game
        start_color = (
            (245, 190, 65) if self.is_host else (90, 90, 95)
        )

        pygame.draw.rect(
            self.display,
            start_color,
            self.start_button,
            border_radius=10
        )

        start_text = self.text_font.render(
            "START GAME" if self.is_host else "WAITING FOR HOST",
            True,
            (20, 25, 35) if self.is_host else (220, 220, 220)
        )
        self.display.blit(
            start_text,
            start_text.get_rect(center=self.start_button.center)
        )

        # Status text
        status = self.small_font.render(
            "Waiting for players to join...",
            True,
            (175, 185, 200)
        )
        self.display.blit(
            status,
            status.get_rect(center=(self.width // 2, 690))
        )
