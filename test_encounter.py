import random

from encounter import (
    EncounterAction,
    EncounterResolver,
    EncounterSession,
    EncounterStatus,
    Refusal,
    build_context,
)


def test_player_must_be_with_professor():
    ctx = build_context(
        "Juan",
        "Library",
        "Professor",
        "Science Building"
    )

    resolver = EncounterResolver()

    assert resolver.check(ctx) is Refusal.NOT_CO_LOCATED


def test_player_can_encounter_professor():
    ctx = build_context(
        "Juan",
        "Library",
        "Professor",
        "Library"
    )

    resolver = EncounterResolver()

    assert resolver.check(ctx) is None


def test_only_one_attempt_per_turn():
    ctx = build_context(
        "Juan",
        "Library",
        "Professor",
        "Library",
        attempts_used=1
    )

    resolver = EncounterResolver()

    assert resolver.check(ctx) is Refusal.ALREADY_ATTEMPTED


def test_persuasion_success():
    rng = random.Random()
    rng.randint = lambda a, b: 20

    ctx = build_context(
        "Juan",
        "Library",
        "Professor",
        "Library"
    )

    resolver = EncounterResolver(rng)

    result = resolver.resolve(
        ctx,
        EncounterAction.PERSUASION
    )

    assert result.success
    assert result.answers_received


def test_persuasion_failure():
    rng = random.Random()
    rng.randint = lambda a, b: 90

    ctx = build_context(
        "Juan",
        "Library",
        "Professor",
        "Library"
    )

    resolver = EncounterResolver(rng)

    result = resolver.resolve(
        ctx,
        EncounterAction.PERSUASION
    )

    assert not result.success
    assert not result.answers_received


def test_theft_success():
    rng = random.Random()
    rng.randint = lambda a, b: 20

    ctx = build_context(
        "Juan",
        "Library",
        "Professor",
        "Library"
    )

    resolver = EncounterResolver(rng)

    result = resolver.resolve(
        ctx,
        EncounterAction.THEFT
    )

    assert result.success
    assert result.answers_received


def test_card_bonus_improves_chance():
    rng = random.Random()
    rng.randint = lambda a, b: 55

    ctx = build_context(
        "Juan",
        "Library",
        "Professor",
        "Library"
    )

    resolver = EncounterResolver(rng)

    without_card = resolver.resolve(
        ctx,
        EncounterAction.PERSUASION,
        card_bonus=0
    )

    with_card = resolver.resolve(
        ctx,
        EncounterAction.PERSUASION,
        card_bonus=10
    )

    assert not without_card.success
    assert with_card.success


def test_session_flow():
    ctx = build_context(
        "Juan",
        "Library",
        "Professor",
        "Library"
    )

    session = EncounterSession(EncounterResolver())

    assert session.status is EncounterStatus.IDLE

    session.start(ctx)

    assert session.status is EncounterStatus.READY

    session.attempt(EncounterAction.PERSUASION)

    assert session.status is EncounterStatus.RESOLVED

    session.close()

    assert session.status is EncounterStatus.IDLE


if __name__ == "__main__":
    tests = [
        value
        for name, value in sorted(globals().items())
        if name.startswith("test_")
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print(f"\n{len(tests)} tests passed.")
