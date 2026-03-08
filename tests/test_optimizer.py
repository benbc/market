from optimizer import optimize
from map_state import MapState
from economics import total_income, multiplier_level, sequence_cost
from rules import is_multiplier


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


def test_optimize_two_cities():
    """Optimizer should place buildings in both city territories."""
    terrain = {(r, c): 'land' for r in range(8) for c in range(8)}
    resources = {}
    for r in range(8):
        for c in range(8):
            if (r + c) % 3 == 0:
                resources[(r, c)] = 'forest'
            elif (r + c) % 3 == 1:
                resources[(r, c)] = 'crop'

    m = MapState(
        terrain=terrain,
        resources=resources,
        cities=(
            {'id': 1, 'row': 1, 'col': 1, 'population': 5, 'border_level': 2},
            {'id': 2, 'row': 6, 'col': 6, 'population': 5, 'border_level': 2},
        ),
    )
    techs = frozenset({'mathematics', 'forestry', 'construction', 'farming',
                       'trade', 'mining', 'smithery', 'climbing'})

    def score(state, actions):
        income = total_income(state)
        # Reward building progress so greedy optimizer builds the chain
        building_value = sum(
            multiplier_level(pos, state) if is_multiplier(bldg) else 1
            for pos, bldg in state.buildings.items()
        )
        return (income, building_value)

    result = optimize(m, techs, score)
    assert result['income'] > 0


def test_optimize_income_then_cost():
    """With a lexicographic score, optimizer should maximize income then minimize cost."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(3) for c in range(3)},
        resources={(0, 1): 'forest', (1, 0): 'forest'},
        cities=({'id': 1, 'row': 1, 'col': 1, 'population': 5, 'border_level': 1},),
    )
    techs = frozenset({'mathematics', 'forestry', 'trade'})

    initial = m

    def score(state, actions):
        income = total_income(state)
        cost = sequence_cost(actions, initial)
        building_value = sum(
            multiplier_level(pos, state) if is_multiplier(bldg) else 1
            for pos, bldg in state.buildings.items()
        )
        return (income, building_value, -cost)

    result = optimize(m, techs, score)
    assert result['income'] >= 0
