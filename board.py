from dataclasses import dataclass

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