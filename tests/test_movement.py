
from board import create_boards, resolve_move
from world import World


def test_player_moves_one_tile():
    # Verify the player can move one tile to an adjacent location
    boards = create_boards()
    campus = boards["campus"]

    assert campus.can_step("1", "2") is True


def test_player_cannot_skip_tiles():
    # Verify a player cannot jump across multiple tiles
    boards = create_boards()
    campus = boards["campus"]

    assert campus.can_step("1", "4") is False


def test_player_cannot_move_through_building():
    # Verify building tiles block ordinary movement
    boards = create_boards()
    campus = boards["campus"]

    assert campus.can_step("2", "6") is False


def test_player_enters_building():
    # Verify the special entrance transitions to Kunsela
    boards = create_boards()

    result = resolve_move(boards, "campus", "5", "6")

    assert result == ("kunsela", "K16")


def test_professor_follows_route():
    # Verify the Professor moves to the next tile on the route
    world = World()
    professor = next(
        npc for npc in world.npcs
        if npc.name == "Professor"
    )

    assert professor.tile_id == "1"

    world.advance_npc(professor)

    assert professor.tile_id == "5"


def test_ta_follows_route():
    # Verify the TA moves to the next tile on the route
    world = World()
    ta = next(
        npc for npc in world.npcs
        if npc.name == "TA1"
    )

    assert ta.tile_id == "K9"

    world.advance_npc(ta)

    assert ta.tile_id == "K10"


def test_npc_moves_after_player_turn():
    # Verify NPCs move after the player completes a turn
    world = World()

    professor = next(
        npc for npc in world.npcs
        if npc.name == "Professor"
    )

    moves = world.legal_moves(world.active_player)
    target = next(iter(moves))

    assert world.move_player(0, target) is True
    assert professor.tile_id == "5"
    assert world.turn_number == 1


def test_npc_route_stays_consistent():
    # Verify the Professor follows the same ordered route
    world = World()
    professor = next(
        npc for npc in world.npcs
        if npc.name == "Professor"
    )

    expected_tiles = ["5", "K16", "K17"]

    for expected in expected_tiles:
        world.advance_npc(professor)
        assert professor.tile_id == expected
