from map_state import MapState
from optimizer import optimize
from economics import total_income, sequence_cost, multiplier_level
from rules import is_multiplier


def _building_score(state, actions):
    income = total_income(state)
    building_value = sum(
        multiplier_level(pos, state) if is_multiplier(bldg) else 1
        for pos, bldg in state.buildings.items()
    )
    return (income, building_value)


def test_full_optimization_from_scratch():
    """Start with terrain + resources + cities, optimize for income."""
    terrain = {(r, c): 'land' for r in range(5) for c in range(5)}
    resources = {
        (0, 1): 'forest', (1, 0): 'forest', (2, 0): 'forest',
        (0, 2): 'crop', (2, 1): 'crop',
    }
    m = MapState(
        terrain=terrain,
        resources=resources,
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 5, 'border_level': 2},),
    )
    techs = frozenset({
        'hunting', 'forestry', 'mathematics',
        'organization', 'farming', 'construction',
        'riding', 'roads', 'trade',
    })

    result = optimize(m, techs, _building_score)
    assert result['income'] > 0
    assert len(result['actions']) > 0


def test_monuments_block_placement():
    """Monuments should prevent buildings from being placed on their tiles."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(3) for c in range(3)},
        monuments=frozenset({(1, 1)}),
        cities=({'id': 1, 'row': 1, 'col': 1, 'population': 5, 'border_level': 1},),
    )
    techs = frozenset({'mathematics', 'trade'})

    result = optimize(m, techs, _building_score)
    assert result['state'].building_at((1, 1)) is None
