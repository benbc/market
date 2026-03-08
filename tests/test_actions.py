from actions import make_action, apply_action
from map_state import MapState


def test_build_action():
    a = make_action('build', (3, 4), 'sawmill')
    assert a == ('build', (3, 4), 'sawmill')


def test_clear_forest_action():
    a = make_action('clear_forest', (1, 2))
    assert a == ('clear_forest', (1, 2))


def test_found_city_action():
    a = make_action('found_city', (5, 5))
    assert a == ('found_city', (5, 5))


def test_expand_borders_action():
    a = make_action('expand_borders', 1)
    assert a == ('expand_borders', 1)


def test_burn_forest_action():
    a = make_action('burn_forest', (2, 3))
    assert a == ('burn_forest', (2, 3))


def test_grow_forest_action():
    a = make_action('grow_forest', (2, 3))
    assert a == ('grow_forest', (2, 3))


def test_harvest_action():
    a = make_action('harvest', (4, 5))
    assert a == ('harvest', (4, 5))


def test_apply_build():
    m = MapState(terrain={(3, 4): 'land'})
    action = ('build', (3, 4), 'sawmill')
    m2 = apply_action(m, action)
    assert m2.building_at((3, 4)) == 'sawmill'
    assert m.building_at((3, 4)) is None


def test_apply_build_preserves_terrain():
    m = MapState(
        terrain={(0, 0): 'land', (1, 1): 'mountain'},
        buildings={(1, 1): 'mine'},
    )
    action = ('build', (0, 0), 'sawmill')
    m2 = apply_action(m, action)
    assert m2.terrain_at((0, 0)) == 'land'
    assert m2.terrain_at((1, 1)) == 'mountain'
    assert m2.building_at((1, 1)) == 'mine'
    assert m2.building_at((0, 0)) == 'sawmill'


def test_apply_clear_forest():
    m = MapState(
        terrain={(2, 3): 'land'},
        resources={(2, 3): 'forest'},
    )
    action = ('clear_forest', (2, 3))
    m2 = apply_action(m, action)
    assert m2.resource_at((2, 3)) is None
    assert m2.terrain_at((2, 3)) == 'land'


def test_apply_burn_forest():
    m = MapState(
        terrain={(2, 3): 'land'},
        resources={(2, 3): 'forest'},
    )
    action = ('burn_forest', (2, 3))
    m2 = apply_action(m, action)
    assert m2.resource_at((2, 3)) == 'crop'


def test_apply_grow_forest():
    m = MapState(terrain={(2, 3): 'land'})
    action = ('grow_forest', (2, 3))
    m2 = apply_action(m, action)
    assert m2.resource_at((2, 3)) == 'forest'


def test_apply_found_city():
    m = MapState(
        terrain={(5, 5): 'land'},
        villages=frozenset({(5, 5)}),
    )
    action = ('found_city', (5, 5))
    m2 = apply_action(m, action)
    assert len(m2.cities) == 1
    assert m2.cities[0]['row'] == 5
    assert m2.cities[0]['col'] == 5
    assert m2.cities[0]['border_level'] == 1
    assert (5, 5) not in m2.villages


def test_found_city_assigns_id():
    m = MapState(
        terrain={(5, 5): 'land', (8, 8): 'land'},
        villages=frozenset({(5, 5), (8, 8)}),
    )
    m2 = apply_action(m, ('found_city', (5, 5)))
    m3 = apply_action(m2, ('found_city', (8, 8)))
    assert m3.cities[0]['id'] != m3.cities[1]['id']


def test_apply_expand_borders():
    m = MapState(
        terrain={(r, c): 'land' for r in range(5) for c in range(5)},
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 1, 'border_level': 1},),
    )
    action = ('expand_borders', 1)
    m2 = apply_action(m, action)
    assert m2.cities[0]['border_level'] == 2


def test_apply_harvest():
    m = MapState(
        terrain={(4, 5): 'land'},
        resources={(4, 5): 'animal'},
    )
    action = ('harvest', (4, 5))
    m2 = apply_action(m, action)
    assert m2.resource_at((4, 5)) is None
