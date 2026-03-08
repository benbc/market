from actions import validate_action
from rules import BUILDINGS


def legal_moves(state, techs):
    """Enumerate all legal actions for the given state and tech set."""
    moves = []

    # Found city moves
    for pos in state.villages:
        action = ('found_city', pos)
        if validate_action(state, action, techs) is None:
            moves.append(action)

    # Expand borders moves
    for city in state.cities:
        action = ('expand_borders', city['id'])
        if validate_action(state, action, techs) is None:
            moves.append(action)

    ownership = state.territory_ownership()

    for pos in state.defined_positions():
        if pos not in ownership:
            continue

        # Build moves
        for building in BUILDINGS:
            action = ('build', pos, building)
            if validate_action(state, action, techs) is None:
                moves.append(action)

        # Terrain modification and harvest moves
        for action_type in ('clear_forest', 'burn_forest', 'grow_forest', 'harvest'):
            action = (action_type, pos)
            if validate_action(state, action, techs) is None:
                moves.append(action)

    return moves
