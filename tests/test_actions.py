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
