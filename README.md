# Campus Capers — Professor/TA Encounter Mechanic

## 1. Overview

The Professor/TA Encounter Mechanic is a feature developed for Campus Capers, a turn-based strategy game where players explore a college campus and compete to obtain exam answers before other players.

This feature allows players to interact with Professors or Teaching Assistants (TAs) and attempt to obtain exam answers through persuasion or theft.

The mechanic uses probability-based calculations to determine whether an encounter succeeds or fails. Cards collected during gameplay can provide bonuses that increase the player's chance of success.

The encounter system is designed to operate independently from the game's map, movement, networking, and card inventory systems.

## 2. Encounter Actions

### Persuasion

Players can attempt to convince a Professor or TA to provide exam answers.

- Base success probability: 50%.
- Card bonuses can increase the success probability.
- Successful persuasion awards exam answers.
- Failed persuasion does not award answers.

### Theft

Players can attempt to steal exam answers from a Professor or TA.

- Base success probability: 40%.
- Card bonuses can increase the success probability.
- Successful theft awards exam answers.
- Failed theft does not award answers.

## 3. Encounter Requirements

Before an encounter begins, the system checks whether the player meets the required conditions.

- The player and Professor/TA must be at the same location.
- The player must have an available encounter attempt.
- Players cannot attempt multiple encounters during the same turn.

If a requirement is not satisfied, the encounter is rejected.

## 4. Encounter Cooldown

The encounter cooldown system prevents players from repeatedly attempting to obtain exam answers during the same turn.

After a player completes an encounter attempt, the system records that the player has used their attempt.

The player becomes eligible for another encounter when their next turn begins.

This prevents repeated attempts and helps maintain balanced gameplay.

## 5. Professor/TA Identification

The system supports multiple Professors and Teaching Assistants.

Each NPC can be identified using information such as:

- Unique NPC identifier.
- NPC name.
- Role (Professor or TA).
- Current campus location.

This allows the encounter mechanic to distinguish between different NPCs and determine which one the player is interacting with.

NPC locations are provided by the team's map and movement systems.

## 6. Encounter History

The encounter history system records completed encounter attempts.

Recorded information includes:

- Player name.
- Professor/TA involved.
- Encounter action (persuasion or theft).
- Success or failure.
- Turn number.
- Card bonus applied.
- Random roll used to determine the result.

Encounter history can be used for testing, debugging, and reviewing player actions.

## 7. Probability and Card Bonuses

Each encounter action has a base probability of success.

The final probability is calculated using the following formula:

**Final Success Chance = Base Success Chance + Card Bonus**

The final chance is restricted to a range between 0% and 100%.

| Action | Base Chance | Card Bonus | Final Chance |
|---|---|---|---|
| Persuasion | 50% | +10% | 60% |
| Persuasion | 50% | +20% | 70% |
| Theft | 40% | +10% | 50% |
| Theft | 40% | +20% | 60% |

The system generates a random number between 1 and 100. An encounter succeeds when the roll is within the calculated success probability.

## 8. Encounter Process

1. A player moves to a location containing a Professor or TA.
2. The encounter system verifies that the player can initiate an encounter.
3. The player selects persuasion or theft.
4. The system applies any available card bonuses.
5. A random roll determines success or failure.
6. The encounter result is returned to the game.
7. The encounter is recorded in the history.
8. The player's encounter attempt is marked as used until their next turn.

## 9. Encounter States

The encounter system uses three states:

| State | Description |
|---|---|
| `IDLE` | No encounter is currently active. |
| `READY` | An encounter is available and waiting for the player to select an action. |
| `RESOLVED` | The encounter attempt has been completed and its result determined. |

## 10. Project Files

### encounter.py

Contains the Professor/TA encounter logic, including:

- Persuasion and theft.
- Probability calculations.
- Card bonus support.
- Location validation.
- Encounter cooldown.
- Professor/TA identification.
- Encounter history.
- Encounter session management.

### test_encounter.py

Contains automated tests verifying that the encounter mechanic functions correctly.

## 11. Testing

Run the following command from the project directory:

`python3 test_encounter.py`

The original eight tests verify:

- Player and Professor/TA location requirements.
- Successful and unsuccessful persuasion.
- Successful theft.
- Card bonus effects.
- Encounter attempt restrictions.
- Encounter session transitions.

Three additional tests cover:

- Encounter cooldown.
- Professor/TA identification.
- Encounter history.

**Reported test results for the updated version: 11 tests passed, 0 failed.**

These tests verify the encounter logic independently. Full integration testing with the other Campus Capers systems is still required.

## 12. Integration With Other Game Systems

The encounter mechanic is designed to connect with the following team features:

**Map and Movement System — Henry Yerdon**

Provides player and NPC locations to determine whether an encounter is allowed.

**Card Inventory System — Jaxsen Jasewicz**

Provides bonuses that affect persuasion and theft success probabilities.

**Networking System — Nazim Harizi**

Will eventually allow encounter actions and results to be synchronized during multiplayer gameplay.

The encounter mechanic does not directly control player movement, map generation, card inventory, or networking.

## 13. Current Development Status

The encounter mechanic has been developed with persuasion, theft, card bonuses, encounter restrictions, cooldown, NPC identification, and encounter history.

The original implementation passed eight automated tests. The updated version was reported to pass eleven automated tests.

The feature is awaiting independent testing by Henry Yerdon and integration with the team's other systems.

## 14. Future Improvements

Potential future enhancements include:

- Witness detection to prevent or penalize theft when another player is nearby.
- Unique exam answers associated with individual Professors or TAs.
- Different difficulty levels for individual NPCs.
- Additional card effects and penalties.
- Integration with the complete multiplayer game.
