from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Tile:
    tile_id: str
    stage_id: str
    column: int
    row: int
    area: str
    building: bool = False
    
class Board:
    def __init__(
        self,
        stage_id,
        columns,
        rows,
        area_for,
        building_tiles=(),
        doors=(),
    ):
        self.stage_id = stage_id
        self.columns = columns
        self.rows = rows
        
        self.tiles = {}
        self.positions = {}
        self.doors = {
            frozenset(pair)
            for pair in doors}
        
        for row in range(rows):
            for column in range(columns):
                number = row * columns + column + 1
                
                tile_id = (
                    str(number)
                    if stage_id == "campus"
                    else f"K{number}"
                )
                
                tile = Tile(
                    tile_id = tile_id,
                    stage_id = stage_id,
                    column = column,
                    row = row,
                    area = area_for(column, row),
                    building = tile_id in building_tiles,
                )
                
                self.tiles[tile_id] = tile
                self.positions[(column, row)] = tile_id
                
    def cardinal_connection(self, source_id, target_id):
        if source_id not in self.tiles or target_id not in self.tiles:
            return False

        source = self.tiles[source_id]
        target = self.tiles[target_id]

        if source.building or target.building:
            return False

        distance = (
            abs(source.column - target.column)
            + abs(source.row - target.row)
        )

        if distance != 1:
            return False

        return (
            source.area == target.area
            or frozenset((source_id, target_id)) in self.doors
        )

    def can_step(self, source_id, target_id):
        if source_id not in self.tiles or target_id not in self.tiles:
            return False

        source = self.tiles[source_id]
        target = self.tiles[target_id]

        if source.building or target.building:
            return False

        dx = target.column - source.column
        dy = target.row - source.row

        if max(abs(dx), abs(dy)) != 1:
            return False

        if dx == 0 or dy == 0:
            return self.cardinal_connection(source_id, target_id)

        horizontal_id = self.positions.get(
            (source.column + dx, source.row)
        )
        vertical_id = self.positions.get(
            (source.column, source.row + dy)
        )

        if horizontal_id is None or vertical_id is None:
            return False

        return all((
            self.cardinal_connection(source_id, horizontal_id),
            self.cardinal_connection(horizontal_id, target_id),
            self.cardinal_connection(source_id, vertical_id),
            self.cardinal_connection(vertical_id, target_id),
        ))
        
    def sight_crosses_edge(self, source_id, target_id, offset):
        """
        offset is the crossing position along an edge, from 0 to 1.
        Door openings occupy the middle third of their edge.
        """
        if not self.cardinal_connection(source_id, target_id):
            return False

        source = self.tiles[source_id]
        target = self.tiles[target_id]

        if source.area == target.area:
            return True

        return 1 / 3 <= offset <= 2 / 3

    def can_see(self, source_id, target_id):
        if source_id not in self.tiles or target_id not in self.tiles:
            return False

        source = self.tiles[source_id]
        target = self.tiles[target_id]

        if source.building or target.building:
            return False

        if source_id == target_id:
            return True

        x = source.column
        y = source.row

        start_x = x + 0.5
        start_y = y + 0.5

        dx = target.column - x
        dy = target.row - y

        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1

        delta_x = 1 / abs(dx) if dx else math.inf
        delta_y = 1 / abs(dy) if dy else math.inf

        next_x = delta_x / 2
        next_y = delta_y / 2

        while (x, y) != (target.column, target.row):
            current_id = self.positions[(x, y)]

            if math.isclose(
                next_x,
                next_y,
                rel_tol=0,
                abs_tol=1e-10,
            ):
                # The ray passes exactly through a tile corner.
                # Require all four surrounding tiles to share an
                # open area, preventing sight through wall corners.
                positions = (
                    (x, y),
                    (x + step_x, y),
                    (x, y + step_y),
                    (x + step_x, y + step_y),
                )

                tiles = [
                    self.tiles[self.positions[position]]
                    for position in positions
                ]

                if (
                    any(tile.building for tile in tiles)
                    or len({tile.area for tile in tiles}) != 1
                ):
                    return False

                x += step_x
                y += step_y

                next_x += delta_x
                next_y += delta_y

            elif next_x < next_y:
                neighbor_id = self.positions[(x + step_x, y)]
                crossing_y = start_y + next_x * dy

                if not self.sight_crosses_edge(
                    current_id,
                    neighbor_id,
                    crossing_y - y,
                ):
                    return False

                x += step_x
                next_x += delta_x

            else:
                neighbor_id = self.positions[(x, y + step_y)]
                crossing_x = start_x + next_y * dx

                if not self.sight_crosses_edge(
                    current_id,
                    neighbor_id,
                    crossing_x - x,
                ):
                    return False

                y += step_y
                next_y += delta_y

        return True

    def tiles_that_see(self, target_id):
        return {
            tile_id
            for tile_id in self.tiles
            if self.can_see(tile_id, target_id)
        }
        
def kunsela_area(column, row):
    if column == 3 or row == 2:
        return  "hallway"
    
    if row < 2:
        return "northwest" if column < 3 else "northeast"
    
    return "southwest" if column < 3 else "southeast"

def create_boards():
    return {
        "campus": Board(
            stage_id = "campus",
            columns = 4,
            rows = 4,
            area_for = lambda column, row: "outside",
            building_tiles=("6", "7"),
        ),
        "kunsela": Board(
            stage_id = "kunsela",
            columns = 7,
            rows = 5,
            area_for = kunsela_area,
            doors = (
                ("K10", "K11"),
                ("K11", "K12"),
                ("K24", "K25"),
                ("K25", "K26"),
            ),
        ),
    }
    
ENTRANCES = {
    ("campus", "5", "6"): ("kunsela", "K16"),
    ("campus", "8", "7"): ("kunsela", "K20"),    
}

EXITS = {
    ("kunsela", "K15"): ("campus", "5"),
    ("kunsela", "K21"): ("campus", "8"),    
}

def resolve_move(boards, stage_id, source_id, target_id):
    entrance = ENTRANCES.get(
        (stage_id, source_id, target_id)
    )
    
    if entrance is not None:
        return entrance
    
    board = boards[stage_id]
    
    if not board.can_step(source_id, target_id):
        return None
    
    return EXITS.get(
        (stage_id, target_id),
        (stage_id, target_id),
    )