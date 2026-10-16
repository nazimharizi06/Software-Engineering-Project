import pygame
from board import EXITS

class BoardView:
    def __init__(self, display, board):
        self.display = display
        self.board = board

        self.cell_size = 90
        self.origin = (50, 110)

        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

        self.rects = {
            tile_id: pygame.Rect(
                self.origin[0] + tile.column * self.cell_size,
                self.origin[1] + tile.row * self.cell_size,
                self.cell_size,
                self.cell_size,
            )
            for tile_id, tile in board.tiles.items()
        }

    def text(self, value, position, color="black", small=False):
        font = self.small_font if small else self.font
        image = font.render(value, True, color)
        self.display.blit(image, position)

    def tile_at(self, position):
        for tile_id, rect in self.rects.items():
            if rect.collidepoint(position):
                return tile_id

        return None

    def character_layout(self, world):
        """
        Return character circles for this stage.

        Group shared-tile characters so their indicators remain
        individually visible.
        """
        groups = {}

        for character in world.characters:
            if character.stage_id == self.board.stage_id:
                groups.setdefault(character.tile_id, []).append(character)

        layout = []

        for tile_id, characters in groups.items():
            rect = self.rects[tile_id]
            count = len(characters)

            for index, character in enumerate(characters):
                x = rect.centerx + (index - (count - 1) / 2) * 30
                center = (round(x), rect.centery + 8)

                layout.append((character, center, 14))

        return layout

    def character_hit(self, world, character, position):
        for actor, center, radius in self.character_layout(world):
            if actor is character:
                dx = position[0] - center[0]
                dy = position[1] - center[1]

                return dx * dx + dy * dy <= radius * radius

        return False

    def draw_boundaries(self):
        for tile_id, tile in self.board.tiles.items():
            rect = self.rects[tile_id]

            for dx, dy in ((1, 0), (0, 1)):
                neighbor_id = self.board.positions.get(
                    (tile.column + dx, tile.row + dy)
                )

                if neighbor_id is None:
                    continue

                neighbor = self.board.tiles[neighbor_id]

                if tile.building or neighbor.building:
                    continue

                if tile.area == neighbor.area:
                    continue

                if dx:
                    start = rect.topright
                    end = rect.bottomright
                else:
                    start = rect.bottomleft
                    end = rect.bottomright

                pygame.draw.line(
                    self.display, "black", start, end, 6
                )

                if frozenset((tile_id, neighbor_id)) in self.board.doors:
                    if dx:
                        gap_start = (rect.right, rect.centery - 15)
                        gap_end = (rect.right, rect.centery + 15)
                    else:
                        gap_start = (rect.centerx - 15, rect.bottom)
                        gap_end = (rect.centerx + 15, rect.bottom)

                    pygame.draw.line(
                        self.display,
                        "#57b879",
                        gap_start,
                        gap_end,
                        7,
                    )

    def draw(self, world, selected=False, legal_moves=None):
        legal_moves = legal_moves or {}

        self.display.fill("#dadfe5")

        self.text(
            f"{self.board.stage_id.title()} | "
            f"Turn {world.turn_number} | "
            f"Active: {world.active_player.name}",
            (50, 25),
        )

        self.text(
            "Click your black circle, then a highlighted tile.",
            (50, 60),
        )

        room_colors = {
            "outside": "#90b97d",
            "hallway": "#d8d4c9",
            "northwest": "#d6b7a4",
            "northeast": "#a9c9d8",
            "southwest": "#c7b3d9",
            "southeast": "#dfd09f",
        }

        for tile_id, tile in self.board.tiles.items():
            rect = self.rects[tile_id]

            color = (
                "#9298a1"
                if tile.building
                else room_colors[tile.area]
            )

            pygame.draw.rect(self.display, color, rect)
            pygame.draw.rect(self.display, "black", rect, 1)

            if tile_id in legal_moves:
                pygame.draw.rect(
                    self.display,
                    "#f4db45",
                    rect.inflate(-8, -8),
                    4,
                )

            self.text(
                tile_id,
                (rect.x + 6, rect.y + 5),
                small=True,
            )

            if tile.building:
                self.text(
                    "Kunsela",
                    (rect.x + 8, rect.y + 55),
                    small=True,
                )

            if (self.board.stage_id, tile_id) in EXITS:
                self.text(
                    "EXIT",
                    (rect.x + 8, rect.bottom - 22),
                    small=True,
                )

        self.draw_boundaries()

        for character, center, radius in self.character_layout(world):
            is_player = any(
                character is player
                for player in world.players
            )

            pygame.draw.circle(
                self.display,
                "black" if is_player else "white",
                center,
                radius,
            )

            pygame.draw.circle(
                self.display, "black", center, radius, 1
            )

            if not is_player:
                label = (
                    "P"
                    if character.name == "Professor"
                    else character.name
                )

                image = self.small_font.render(
                    label, True, "black"
                )

                self.display.blit(
                    image,
                    image.get_rect(center=center),
                )

            if selected and character is world.active_player:
                pygame.draw.circle(
                    self.display,
                    "#f4db45",
                    center,
                    radius + 4,
                    2,
                )

        sidebar_x = 760

        self.text("Character locations", (sidebar_x, 120))

        for index, character in enumerate(world.characters):
            self.text(
                f"{character.name}: "
                f"{character.stage_id} / {character.tile_id}",
                (sidebar_x, 160 + index * 30),
                small=True,
            )

        self.text(
            "Green wall gaps are doors.",
            (sidebar_x, 300),
            small=True,
        )

class Campus(BoardView):
    pass

class Kunsela(BoardView):
    pass


# from GameStateManager import GameStateManager

# class Campus:
#     def __init__(self, display, gameStateManager):
#         self.display = display
#         self.gameStateManager = gameStateManager
#     def run(self):
#         self.display.fill('green')
#         keys = pygame.key.get_pressed()
#         if keys[pygame.K_e]:
#             self.gameStateManager.set_state('kunsela')   
        
# class Kunsela:
#     def __init__(self, display, gameStateManager):
#         self.display = display
#         self.gameStateManager = gameStateManager
#     def run(self):
#         self.display.fill('red')
#         keys = pygame.key.get_pressed()
#         if keys[pygame.K_e]:
#             self.gameStateManager.set_state('campus')