from map_state import MapState


def test_empty_map():
    m = MapState()
    assert m.terrain_at((0, 0)) is None


def test_set_and_get_terrain():
    m = MapState(terrain={
        (0, 0): 'land',
        (1, 0): 'mountain',
    })
    assert m.terrain_at((0, 0)) == 'land'
    assert m.terrain_at((1, 0)) == 'mountain'
    assert m.terrain_at((2, 0)) is None


def test_defined_positions():
    m = MapState(terrain={
        (0, 0): 'land',
        (1, 1): 'water',
    })
    assert m.defined_positions() == {(0, 0), (1, 1)}


def test_undefined_positions_excluded():
    m = MapState(terrain={(0, 0): 'land'})
    assert (1, 1) not in m.defined_positions()


def test_resource_at():
    m = MapState(
        terrain={(0, 0): 'land'},
        resources={(0, 0): 'forest'},
    )
    assert m.resource_at((0, 0)) == 'forest'
    assert m.resource_at((1, 0)) is None


def test_building_at():
    m = MapState(
        terrain={(0, 0): 'land'},
        buildings={(0, 0): 'sawmill'},
    )
    assert m.building_at((0, 0)) == 'sawmill'
    assert m.building_at((1, 0)) is None


def test_cities():
    cities = [{'id': 1, 'row': 2, 'col': 3, 'population': 1, 'border_level': 1}]
    m = MapState(terrain={(2, 3): 'land'}, cities=tuple(cities))
    assert len(m.cities) == 1
    assert m.cities[0]['id'] == 1


def test_villages():
    m = MapState(
        terrain={(5, 5): 'land'},
        villages=frozenset({(5, 5)}),
    )
    assert (5, 5) in m.villages


def test_occupied_positions():
    m = MapState(
        terrain={(0, 0): 'land', (1, 1): 'land', (2, 2): 'land'},
        buildings={(0, 0): 'sawmill'},
        monuments=frozenset({(1, 1)}),
        lighthouses=frozenset({(2, 2)}),
    )
    occupied = m.occupied_positions()
    assert (0, 0) in occupied  # building
    assert (1, 1) in occupied  # monument
    assert (2, 2) in occupied  # lighthouse
