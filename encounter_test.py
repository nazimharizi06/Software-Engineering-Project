import unittest
from unittest.mock import Mock

from encounter import (
    EncounterAction,
    EncounterResolver,
    EncounterSession,
    EncounterTracker,
    Refusal,
    ProfessorTA,
    context_for_npc,
)


class EncounterRequirementsTests(unittest.TestCase):
    def setUp(self):
        self.player = "Player 1"

        # Include stage AND tile so equal tile numbers on
        # different maps are not mistaken for one location.
        self.location = "kunsela:K10"

        self.professor = ProfessorTA(
            npc_id="prof-01",
            name="Professor Smith",
            role="Professor",
            location=self.location,
        )

        self.ta = ProfessorTA(
            npc_id="ta-01",
            name="TA Alex",
            role="TA",
            location=self.location,
        )

        self.tracker = EncounterTracker()
        self.tracker.begin_turn(self.player)

    def context(self, npc=None, location=None):
        if npc is None:
            npc = self.professor

        if location is None:
            location = self.location

        return context_for_npc(
            self.player,
            location,
            npc,
        )

    def session(self, roll):
        # Inject a predictable die roll. No random test failures.
        rng = Mock()
        rng.randint.return_value = roll

        resolver = EncounterResolver(rng=rng)

        session = EncounterSession(
            resolver=resolver,
            tracker=self.tracker,
        )

        return session, rng

    def test_same_tile_allows_encounter(self):
        session, _ = self.session(1)

        refusal = session.start(self.context())

        self.assertIsNone(refusal)

    def test_different_tile_blocks_encounter(self):
        session, rng = self.session(1)

        refusal = session.start(
            self.context(location="kunsela:K11")
        )

        self.assertIs(refusal, Refusal.NOT_CO_LOCATED)

        with self.assertRaises(RuntimeError):
            session.attempt(EncounterAction.PERSUASION)

        rng.randint.assert_not_called()
        self.assertEqual(self.tracker.history_for(self.player), [])

    def test_different_stage_blocks_encounter(self):
        session, _ = self.session(1)

        refusal = session.start(
            self.context(location="campus:10")
        )

        self.assertIs(refusal, Refusal.NOT_CO_LOCATED)

    def assert_outcome(self, action, roll, expected_success, base):
        session, rng = self.session(roll)

        self.assertIsNone(session.start(self.context()))

        result = session.attempt(action)

        self.assertIs(result.action, action)
        self.assertEqual(result.base_chance, base)
        self.assertEqual(result.final_chance, base)
        self.assertEqual(result.roll, roll)
        self.assertEqual(result.success, expected_success)
        self.assertEqual(result.answers_received, expected_success)

        rng.randint.assert_called_once_with(1, 100)

        history = self.tracker.history_for(self.player)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].success, expected_success)
        self.assertEqual(history[0].target_id, self.professor.npc_id)

    def test_persuasion_success(self):
        # Exactly at the threshold must succeed.
        self.assert_outcome(
            EncounterAction.PERSUASION,
            roll=50,
            expected_success=True,
            base=50,
        )

    def test_persuasion_failure(self):
        self.assert_outcome(
            EncounterAction.PERSUASION,
            roll=51,
            expected_success=False,
            base=50,
        )

    def test_theft_success(self):
        self.assert_outcome(
            EncounterAction.THEFT,
            roll=40,
            expected_success=True,
            base=40,
        )

    def test_theft_failure(self):
        self.assert_outcome(
            EncounterAction.THEFT,
            roll=41,
            expected_success=False,
            base=40,
        )

    def test_bonus_changes_outcome_for_both_actions(self):
        cases = (
            (EncounterAction.PERSUASION, 55),
            (EncounterAction.THEFT, 45),
        )

        for action, roll in cases:
            with self.subTest(action=action.value):
                rng = Mock()
                rng.randint.return_value = roll
                resolver = EncounterResolver(rng=rng)

                without_bonus = resolver.resolve(
                    self.context(),
                    action,
                    card_bonus=0,
                )

                with_bonus = resolver.resolve(
                    self.context(),
                    action,
                    card_bonus=10,
                )

                self.assertFalse(without_bonus.success)
                self.assertTrue(with_bonus.success)
                self.assertEqual(
                    with_bonus.final_chance,
                    without_bonus.final_chance + 10,
                )

    def test_second_attempt_in_same_session_is_blocked(self):
        session, rng = self.session(1)

        self.assertIsNone(session.start(self.context()))
        session.attempt(EncounterAction.PERSUASION)

        with self.assertRaises(RuntimeError):
            session.attempt(EncounterAction.THEFT)

        self.assertEqual(rng.randint.call_count, 1)
        self.assertEqual(
            len(self.tracker.history_for(self.player)),
            1,
        )

    def test_new_session_cannot_bypass_turn_limit(self):
        # Check that BOTH success and failure consume the attempt.
        for roll in (1, 100):
            with self.subTest(roll=roll):
                self.tracker = EncounterTracker()
                self.tracker.begin_turn(self.player)

                first, _ = self.session(roll)
                self.assertIsNone(first.start(self.context()))
                first.attempt(EncounterAction.PERSUASION)
                first.close()

                # A different NPC still cannot be attempted
                # during the same turn.
                second, rng = self.session(1)

                self.assertIs(
                    second.start(self.context(npc=self.ta)),
                    Refusal.COOLDOWN,
                )

                with self.assertRaises(RuntimeError):
                    second.attempt(EncounterAction.THEFT)

                rng.randint.assert_not_called()
                self.assertEqual(
                    len(self.tracker.history_for(self.player)),
                    1,
                )

    def test_failed_encounter_can_be_retried_next_turn(self):
        first, _ = self.session(100)

        self.assertIsNone(first.start(self.context()))
        result = first.attempt(EncounterAction.PERSUASION)
        self.assertFalse(result.answers_received)

        self.tracker.begin_turn(self.player)

        second, _ = self.session(1)
        self.assertIsNone(second.start(self.context()))

        result = second.attempt(EncounterAction.THEFT)
        self.assertTrue(result.answers_received)

    def test_successful_npc_cannot_award_answers_again(self):
        first, _ = self.session(1)

        self.assertIsNone(first.start(self.context()))
        result = first.attempt(EncounterAction.PERSUASION)
        self.assertTrue(result.answers_received)
        first.close()

        # Advance the turn so this tests the permanent NPC
        # restriction rather than the one-turn cooldown.
        self.tracker.begin_turn(self.player)

        second, rng = self.session(1)
        refusal = second.start(self.context())

        self.assertIsNotNone(
            refusal,
            "A previously successful NPC must be refused "
            "even on a later turn.",
        )

        with self.assertRaises(RuntimeError):
            second.attempt(EncounterAction.THEFT)

        rng.randint.assert_not_called()
        self.assertEqual(
            len(self.tracker.history_for(self.player)),
            1,
        )

    def test_another_npc_can_award_answers_next_turn(self):
        first, _ = self.session(1)

        self.assertIsNone(first.start(self.context()))
        first.attempt(EncounterAction.PERSUASION)

        self.tracker.begin_turn(self.player)

        second, _ = self.session(1)

        self.assertIsNone(
            second.start(self.context(npc=self.ta))
        )

        result = second.attempt(EncounterAction.THEFT)
        self.assertTrue(result.answers_received)

        history = self.tracker.history_for(self.player)

        self.assertEqual(
            [entry.target_id for entry in history],
            [self.professor.npc_id, self.ta.npc_id],
        )

    @unittest.skip(
        "Not implemented: encounter API has no other-player "
        "locations or visibility query."
    )
    def test_visible_other_player_blocks_encounter(self):
        pass

    @unittest.skip(
        "Not implemented: need visibility input to verify that "
        "hidden players do not block encounters."
    )
    def test_hidden_other_player_does_not_block_encounter(self):
        pass

    @unittest.skip(
        "Not implemented: resolver accepts card_bonus, "
        "but no player persuasion/theft stats."
    )
    def test_player_stats_affect_success_chance(self):
        pass


if __name__ == "__main__":
    unittest.main(verbosity=2)