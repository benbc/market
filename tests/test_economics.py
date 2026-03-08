from economics import market_income, total_income, multiplier_level
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
