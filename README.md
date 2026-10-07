## Professor/TA Encounter Mechanic

Developer: Juan Puig

The encounter mechanic allows a player to interact with a Professor or TA
and attempt to obtain exam answers.

### Encounter Options

- Persuasion
- Theft

The encounter system determines whether the attempt succeeds or fails.
Cards collected by the player can provide bonuses that affect the chance
of a successful encounter.

### Integration

The encounter system does not control player or Professor/TA movement.
The movement system provides the current locations of the player and NPC.

The card system provides any card bonus used during the encounter.

Inputs:
- Player name
- Player location
- Professor/TA name
- Professor/TA location
- Encounter action (persuasion or theft)
- Card bonus

Outputs:
- Success or failure
- Whether exam answers were obtained
- Encounter result message

### Testing

Run the encounter tests with:

python3 test_encounter.py
