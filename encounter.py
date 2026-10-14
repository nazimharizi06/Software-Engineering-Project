"""Engine-independent Professor/TA encounter rules for Campus Capers."""
from dataclasses import dataclass
from enum import Enum
import random


class EncounterAction(Enum):
    PERSUASION = 'persuasion'
    THEFT = 'theft'


class EncounterStatus(Enum):
    IDLE = 'idle'
    READY = 'ready'
    RESOLVED = 'resolved'


class Refusal(Enum):
    NOT_CO_LOCATED = 'Player and Professor/TA are in different locations.'
    ALREADY_ATTEMPTED = 'Player has already attempted an encounter this turn.'


@dataclass(frozen=True)
class EncounterContext:
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


class EncounterResolver:
    def __init__(self, rng=None):
        self.rng = rng if rng is not None else random.Random()

    def check(self, ctx):
        if ctx.player_location != ctx.target_location:
            return Refusal.NOT_CO_LOCATED
        if ctx.attempts_used_this_turn >= ctx.attempts_per_turn:
            return Refusal.ALREADY_ATTEMPTED
        return None

    def resolve(self, ctx, action, card_bonus=0):
        refusal = self.check(ctx)
        if refusal is not None:
            raise ValueError(refusal.value)
        if not isinstance(action, EncounterAction):
            raise ValueError('Choose persuasion or theft.')
        base = 50 if action is EncounterAction.PERSUASION else 40
        chance = max(0, min(100, base + int(card_bonus)))
        roll = self.rng.randint(1, 100)
        success = roll <= chance
        return EncounterResult(
            action, success, base, int(card_bonus), chance, roll, success,
            f"{ctx.player_name} {'obtained' if success else 'did not obtain'} exam answers "
            f"from {ctx.target_name} using {action.value} (roll {roll}, needed <= {chance})."
        )


class EncounterSession:
    def __init__(self, resolver=None):
        self.resolver = resolver if resolver is not None else EncounterResolver()
        self.status = EncounterStatus.IDLE
        self.context = None
        self.result = None

    def start(self, ctx):
        if self.status is not EncounterStatus.IDLE:
            raise RuntimeError('Close the previous encounter first.')
        refusal = self.resolver.check(ctx)
        if refusal is None:
            self.context = ctx
            self.status = EncounterStatus.READY
        return refusal

    def attempt(self, action, card_bonus=0):
        if self.status is not EncounterStatus.READY:
            raise RuntimeError('Start a valid encounter first.')
        self.result = self.resolver.resolve(self.context, action, card_bonus)
        self.status = EncounterStatus.RESOLVED
        return self.result

    def close(self):
        self.context = None
        self.result = None
        self.status = EncounterStatus.IDLE


def build_context(player_name, player_location, target_name, target_location,
                  attempts_used=0, attempts_per_turn=1):
    return EncounterContext(player_name, player_location, target_name,
                            target_location, attempts_used, attempts_per_turn)
