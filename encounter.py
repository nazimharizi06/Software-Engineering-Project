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
    COOLDOWN = 'Player must wait until their next turn to attempt another encounter.'


@dataclass(frozen=True)
class ProfessorTA:
    """NPC identity supplied by the game's map/NPC system."""
    npc_id: str
    name: str
    role: str  # "Professor" or "TA"
    location: str


@dataclass(frozen=True)
class EncounterHistoryEntry:
    player_name: str
    target_id: str
    target_name: str
    action: EncounterAction
    success: bool
    turn_number: int
    card_bonus: int
    roll: int


class EncounterTracker:
    """Tracks per-player turn cooldowns and completed encounter history.

    Call begin_turn(player_name) when the game's turn system starts that
    player's next turn. Does not control turns, NPCs, or movement.
    """
    def __init__(self):
        self._turns = {}
        self._attempted_turn = {}
        self.history = []

    def begin_turn(self, player_name):
        self._turns[player_name] = self._turns.get(player_name, 0) + 1

    def can_attempt(self, player_name):
        return self._attempted_turn.get(player_name) != self._turns.get(player_name, 0)

    def record(self, ctx, result):
        player = ctx.player_name
        if not self.can_attempt(player):
            raise ValueError(Refusal.COOLDOWN.value)
        turn = self._turns.get(player, 0)
        self._attempted_turn[player] = turn
        self.history.append(EncounterHistoryEntry(
            player, ctx.target_id or ctx.target_name, ctx.target_name,
            result.action, result.success, turn, result.card_bonus, result.roll
        ))

    def history_for(self, player_name):
        return [entry for entry in self.history if entry.player_name == player_name]


@dataclass(frozen=True)
class EncounterContext:
    player_name: str
    player_location: str
    target_name: str
    target_location: str
    attempts_used_this_turn: int = 0
    attempts_per_turn: int = 1
    target_id: str = ""


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
    def __init__(self, resolver=None, tracker=None):
        self.tracker = tracker
        self.resolver = resolver if resolver is not None else EncounterResolver()
        self.status = EncounterStatus.IDLE
        self.context = None
        self.result = None

    def start(self, ctx):
        if self.status is not EncounterStatus.IDLE:
            raise RuntimeError('Close the previous encounter first.')
        refusal = self.resolver.check(ctx)
        if refusal is None and self.tracker is not None and not self.tracker.can_attempt(ctx.player_name):
            refusal = Refusal.COOLDOWN
        if refusal is None:
            self.context = ctx
            self.status = EncounterStatus.READY
        return refusal

    def attempt(self, action, card_bonus=0):
        if self.status is not EncounterStatus.READY:
            raise RuntimeError('Start a valid encounter first.')
        if self.tracker is not None and not self.tracker.can_attempt(self.context.player_name):
            raise ValueError(Refusal.COOLDOWN.value)
        result = self.resolver.resolve(self.context, action, card_bonus)
        if self.tracker is not None:
            self.tracker.record(self.context, result)
        self.result = result
        self.status = EncounterStatus.RESOLVED
        return self.result

    def close(self):
        self.context = None
        self.result = None
        self.status = EncounterStatus.IDLE


def build_context(player_name, player_location, target_name, target_location,
                  attempts_used=0, attempts_per_turn=1, target_id=""):
    return EncounterContext(player_name, player_location, target_name,
                            target_location, attempts_used, attempts_per_turn, target_id)


def context_for_npc(player_name, player_location, npc, attempts_used=0):
    """Build an encounter using a specific ProfessorTA NPC's identity."""
    return build_context(player_name, player_location, npc.name, npc.location,
                         attempts_used=attempts_used, target_id=npc.npc_id)

