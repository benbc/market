from economics import market_income, total_income, multiplier_level, action_cost, sequence_cost, action_population, sequence_population
from map_state import MapState


def test_multiplier_level_sawmill():
    m = MapState(
        terrain={(0, 0): 'land', (0, 1): 'land', (1, 0): 'land'},
        buildings={(0, 0): 'sawmill', (0, 1): 'lumber_hut', (1, 0): 'lumber_hut'},
    )
    assert multiplier_level((0, 0), m) == 2


def test_multiplier_level_forge():
    m = MapState(
        terrain={(0, 0): 'land', (0, 1): 'mountain', (1, 0): 'mountain'},
        buildings={(0, 0): 'forge', (0, 1): 'mine', (1, 0): 'mine'},
    )
    assert multiplier_level((0, 0), m) == 4


def test_market_income_simple():
    m = MapState(
        terrain={(0, 0): 'land', (0, 1): 'land', (1, 0): 'land', (1, 1): 'land'},
        buildings={(0, 0): 'sawmill', (0, 1): 'lumber_hut', (1, 0): 'market'},
    )
    assert market_income((1, 0), m) == 1


def test_market_income_capped_at_8():
    terrain = {(r, c): 'land' for r in range(5) for c in range(5)}
    buildings = {
        (2, 2): 'market',
        (1, 1): 'sawmill',
        (1, 2): 'windmill',
        (2, 1): 'forge',
    }
    for r in range(5):
        for c in range(5):
            pos = (r, c)
            if pos not in buildings:
                buildings[pos] = 'lumber_hut'
    m = MapState(terrain=terrain, buildings=buildings)
    assert market_income((2, 2), m) <= 8


def test_total_income():
    m = MapState(
        terrain={(0, 0): 'land', (0, 1): 'land', (1, 0): 'land', (1, 1): 'land'},
        buildings={(0, 0): 'sawmill', (0, 1): 'lumber_hut', (1, 0): 'market'},
    )
    assert total_income(m) == 1


def test_build_cost():
    m = MapState(terrain={(0, 0): 'land'})
    action = ('build', (0, 0), 'sawmill')
    assert action_cost(action, m) == 5


def test_clear_forest_negative_cost():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'forest'})
    action = ('clear_forest', (0, 0))
    assert action_cost(action, m) == -1


def test_burn_forest_cost():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'forest'})
    action = ('burn_forest', (0, 0))
    assert action_cost(action, m) == 3


def test_grow_forest_cost():
    m = MapState(terrain={(0, 0): 'land'})
    action = ('grow_forest', (0, 0))
    assert action_cost(action, m) == 5


def test_harvest_cost():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'animal'})
    action = ('harvest', (0, 0))
    assert action_cost(action, m) == 2


def test_sequence_cost():
    m = MapState(
        terrain={(0, 0): 'land', (1, 1): 'land'},
        resources={(0, 0): 'forest'},
    )
    actions = [
        ('clear_forest', (0, 0)),
        ('build', (0, 0), 'sawmill'),
    ]
    assert sequence_cost(actions, m) == -1 + 5


def test_build_lumber_hut_population():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'forest'})
    assert action_population(('build', (0, 0), 'lumber_hut'), m) == 1


def test_build_farm_population():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'crop'})
    assert action_population(('build', (0, 0), 'farm'), m) == 2


def test_build_mine_population():
    m = MapState(terrain={(0, 0): 'mountain'}, resources={(0, 0): 'metal'})
    assert action_population(('build', (0, 0), 'mine'), m) == 2


def test_build_sawmill_population_depends_on_adjacency():
    """Sawmill population = number of adjacent lumber huts."""
    m = MapState(
        terrain={(0, 0): 'land', (0, 1): 'land', (1, 0): 'land'},
        resources={(0, 1): 'forest', (1, 0): 'forest'},
        buildings={(0, 1): 'lumber_hut', (1, 0): 'lumber_hut'},
    )
    assert action_population(('build', (0, 0), 'sawmill'), m) == 2


def test_harvest_population():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'animal'})
    assert action_population(('harvest', (0, 0)), m) == 1
