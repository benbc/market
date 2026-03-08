from moves import legal_moves
from actions import apply_action
from economics import total_income, sequence_cost


def optimize(initial_state, techs, score_fn, max_depth=20):
    """
    Greedy optimizer: repeatedly pick the best legal action until
    no improvement or max_depth reached.
    """
    state = initial_state
    actions_taken = []

    for _ in range(max_depth):
        best_action = None
        best_score = score_fn(state, actions_taken)
        best_state = state

        for action in legal_moves(state, techs):
            new_state = apply_action(state, action)
            new_actions = actions_taken + [action]
            s = score_fn(new_state, new_actions)
            if s > best_score:
                best_score = s
                best_action = action
                best_state = new_state

        if best_action is None:
            break

        actions_taken.append(best_action)
        state = best_state

    return {
        'state': state,
        'actions': actions_taken,
        'income': total_income(state),
    }
