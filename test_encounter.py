"""Run with: python3 test_encounter.py"""
from encounter import EncounterAction, EncounterResolver, EncounterSession, EncounterStatus, Refusal, EncounterTracker, ProfessorTA, context_for_npc, build_context


class FixedRandom:
    def __init__(self, roll):
        self.roll = roll

    def randint(self, low, high):
        return self.roll


def test_player_must_be_with_professor():
    ctx = build_context('Juan', 'Campus Center', 'Professor', 'Cayan Library')
    assert EncounterResolver().check(ctx) is Refusal.NOT_CO_LOCATED


def test_player_can_encounter_professor():
    ctx = build_context('Juan', 'Cayan Library', 'Professor', 'Cayan Library')
    assert EncounterResolver().check(ctx) is None


def test_only_one_attempt_per_turn():
    ctx = build_context('Juan', 'Cayan Library', 'Professor', 'Cayan Library', attempts_used=1)
    assert EncounterResolver().check(ctx) is Refusal.ALREADY_ATTEMPTED


def test_persuasion_success():
    ctx = build_context('Juan', 'Cayan Library', 'Professor', 'Cayan Library')
    result = EncounterResolver(FixedRandom(20)).resolve(ctx, EncounterAction.PERSUASION)
    assert result.success and result.answers_received


def test_persuasion_failure():
    ctx = build_context('Juan', 'Cayan Library', 'Professor', 'Cayan Library')
    result = EncounterResolver(FixedRandom(90)).resolve(ctx, EncounterAction.PERSUASION)
    assert not result.success and not result.answers_received


def test_theft_success():
    ctx = build_context('Juan', 'Donovan Hall', 'TA', 'Donovan Hall')
    assert EncounterResolver(FixedRandom(20)).resolve(ctx, EncounterAction.THEFT).success


def test_card_bonus_improves_chance():
    ctx = build_context('Juan', 'Cayan Library', 'Professor', 'Cayan Library')
    resolver = EncounterResolver(FixedRandom(55))
    assert not resolver.resolve(ctx, EncounterAction.PERSUASION).success
    assert resolver.resolve(ctx, EncounterAction.PERSUASION, card_bonus=10).success


def test_session_flow():
    ctx = build_context('Juan', 'Cayan Library', 'Professor', 'Cayan Library')
    session = EncounterSession(EncounterResolver(FixedRandom(20)))
    assert session.status is EncounterStatus.IDLE
    assert session.start(ctx) is None
    assert session.status is EncounterStatus.READY
    session.attempt(EncounterAction.PERSUASION)
    assert session.status is EncounterStatus.RESOLVED
    session.close()
    assert session.status is EncounterStatus.IDLE


def test_cooldown_blocks_second_attempt_until_next_turn():
    tracker = EncounterTracker()
    tracker.begin_turn('Juan')
    ctx = build_context('Juan', 'Cayan Library', 'Professor', 'Cayan Library')
    session = EncounterSession(EncounterResolver(FixedRandom(20)), tracker)
    assert session.start(ctx) is None
    session.attempt(EncounterAction.PERSUASION)
    session.close()
    assert session.start(ctx) is Refusal.COOLDOWN
    tracker.begin_turn('Juan')
    assert session.start(ctx) is None


def test_npc_identity_and_location():
    npc = ProfessorTA('prof-01', 'Professor Smith', 'Professor', 'Donovan Hall')
    ctx = context_for_npc('Juan', 'Donovan Hall', npc)
    assert ctx.target_id == 'prof-01'
    assert ctx.target_name == 'Professor Smith'
    assert EncounterResolver().check(ctx) is None


def test_encounter_history_records_result_and_target():
    tracker = EncounterTracker()
    tracker.begin_turn('Juan')
    npc = ProfessorTA('ta-02', 'TA Alex', 'TA', 'Cayan Library')
    session = EncounterSession(EncounterResolver(FixedRandom(90)), tracker)
    assert session.start(context_for_npc('Juan', 'Cayan Library', npc)) is None
    result = session.attempt(EncounterAction.THEFT, card_bonus=5)
    assert not result.success
    assert len(tracker.history_for('Juan')) == 1
    entry = tracker.history_for('Juan')[0]
    assert (entry.target_id, entry.target_name, entry.action, entry.success) == (
        'ta-02', 'TA Alex', EncounterAction.THEFT, False)
    assert entry.turn_number == 1 and entry.card_bonus == 5
    assert tracker.history_for('Jaxsen') == []


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"\n{len(tests)} tests passed.")
