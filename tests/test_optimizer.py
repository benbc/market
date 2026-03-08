from optimizer import optimize
from map_state import MapState
from economics import total_income


def test_optimize_single_market():
    """With one market spot adjacent to a pre-built sawmill with lumber huts,
    the optimizer should place the market."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(3) for c in range(3)},
        resources={(0, 1): 'forest', (1, 0): 'forest'},
        buildings={
            (0, 0): 'sawmill',
            (0, 1): 'lumber_hut',
            (1, 0): 'lumber_hut',
        },
        cities=({'id': 1, 'row': 1, 'col': 1, 'population': 5, 'border_level': 1},),
    )
    techs = frozenset({'trade', 'mathematics', 'forestry'})

    def score(state, actions):
        return total_income(state)

    result = optimize(m, techs, score)
    assert result['income'] > 0
    market_actions = [a for a in result['actions'] if a[0] == 'build' and a[2] == 'market']
    assert len(market_actions) > 0
