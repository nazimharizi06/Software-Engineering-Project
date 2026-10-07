"""
encounter.py
Campus Capers - Professor/TA Encounter Mechanic

This module handles ONLY encounter logic.

This module determines whether an encounter can happen and resolves
persuasion or theft attempts.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum, auto


# ---------------------------------------------------------
# Encounter Types
# ---------------------------------------------------------

class EncounterAction(Enum):
    PERSUASION = "persuasion"
    THEFT = "theft"


class EncounterStatus(Enum):
    IDLE = auto()
    READY = auto()
    RESOLVED = auto()


class Refusal(Enum):
    NOT_CO_LOCATED = "Player and Professor/TA must be in the same location."
    ALREADY_ATTEMPTED = "Player has already attempted an encounter this turn."


# ---------------------------------------------------------
# Data passed in from the rest of the game
# ---------------------------------------------------------

@dataclass(frozen=True)
class EncounterContext:
    """
    Snapshot of information needed to determine whether an encounter
    can occur.

    Movement/map code is responsible for providing the locations.
    """

    player_name: str
    player_location: str

    target_name: str
    target_location: str

    attempts_used_this_turn: int = 0
    attempts_per_turn: int = 1


@dataclass(frozen=True)
class EncounterResult:
    action: EncounterAction
    success: bool

    base_chance: int
    card_bonus: int
    final_chance: int
    roll: int

    answers_received: bool
    message: str


# ---------------------------------------------------------
# Encounter Rules
# ---------------------------------------------------------

class EncounterResolver:
    """
    Resolves Professor/TA encounters.

    Movement is NOT handled here.

    The player and target locations are supplied by the map/movement
    systems developed elsewhere in the group project.
    """

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def check(self, ctx: EncounterContext) -> Refusal | None:
        """
        Check whether the player is allowed to start an encounter.
        """

        if ctx.player_location != ctx.target_location:
            return Refusal.NOT_CO_LOCATED

        if ctx.attempts_used_this_turn >= ctx.attempts_per_turn:
            return Refusal.ALREADY_ATTEMPTED

        return None

    def resolve(
        self,
        ctx: EncounterContext,
        action: EncounterAction,
        card_bonus: int = 0,
    ) -> EncounterResult:
        """
        Resolve either a persuasion or theft attempt.

        card_bonus is supplied by the card system.
        This module does not manage the player's hand.
        """

        refusal = self.check(ctx)

        if refusal is not None:
            raise ValueError(refusal.value)

        # Initial balancing values.
        # These can be adjusted later by the team.
        if action is EncounterAction.PERSUASION:
            base_chance = 50

        elif action is EncounterAction.THEFT:
            base_chance = 40

        else:
            raise ValueError("Invalid encounter action.")

        # Cards can improve the player's chance.
        final_chance = base_chance + card_bonus

        # Keep probability between 0% and 100%.
        final_chance = max(0, min(100, final_chance))

        roll = self.rng.randint(1, 100)

        success = roll <= final_chance

        if success:
            message = (
                f"{ctx.player_name} successfully used "
                f"{action.value} against {ctx.target_name} "
                "and obtained exam answers."
            )
        else:
            message = (
                f"{ctx.player_name}'s {action.value} attempt "
                f"against {ctx.target_name} failed."
            )

        return EncounterResult(
            action=action,
            success=success,
            base_chance=base_chance,
            card_bonus=card_bonus,
            final_chance=final_chance,
            roll=roll,
            answers_received=success,
            message=message,
        )


# ---------------------------------------------------------
# Encounter Session
# ---------------------------------------------------------

class EncounterSession:
    """
    Tracks the state of one encounter.

    The game can create/use this object when the player interacts
    with a Professor/TA.
    """

    def __init__(self, resolver: EncounterResolver):
        self.resolver = resolver
        self.status = EncounterStatus.IDLE
        self.context: EncounterContext | None = None
        self.last_result: EncounterResult | None = None

    def start(self, ctx: EncounterContext) -> Refusal | None:
        """
        Attempt to start an encounter.
        """

        refusal = self.resolver.check(ctx)

        if refusal is not None:
            return refusal

        self.context = ctx
        self.status = EncounterStatus.READY
        return None

    def attempt(
        self,
        action: EncounterAction,
        card_bonus: int = 0,
    ) -> EncounterResult | None:
        """
        Perform persuasion or theft.
        """

        if self.status is not EncounterStatus.READY:
            return None

        if self.context is None:
            return None

        result = self.resolver.resolve(
            self.context,
            action,
            card_bonus,
        )

        self.last_result = result
        self.status = EncounterStatus.RESOLVED

        return result

    def close(self) -> None:
        """
        Close the encounter so control can return to the main game.
        """

        self.status = EncounterStatus.IDLE
        self.context = None


# ---------------------------------------------------------
# Helper for group-project integration
# ---------------------------------------------------------

def build_context(
    player_name: str,
    player_location: str,
    target_name: str,
    target_location: str,
    attempts_used: int = 0,
) -> EncounterContext:
    """
    Creates the encounter context using information supplied by
    the group's player/movement systems.
    """

    return EncounterContext(
        player_name=player_name,
        player_location=player_location,
        target_name=target_name,
        target_location=target_location,
        attempts_used_this_turn=attempts_used,
    )