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


def test_city_territory_base():
    """A city with border_level=1 owns a 3x3 area."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(5) for c in range(5)},
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 1, 'border_level': 1},),
    )
    ownership = m.territory_ownership()
    # 3x3 around (2,2) = 9 tiles
    assert ownership[(2, 2)] == 1
    assert ownership[(1, 1)] == 1
    assert ownership[(3, 3)] == 1
    # (0, 0) is outside the 3x3
    assert (0, 0) not in ownership


def test_city_territory_expanded():
    """A city with border_level=2 owns a 5x5 area."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(5) for c in range(5)},
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 1, 'border_level': 2},),
    )
    ownership = m.territory_ownership()
    assert ownership[(0, 0)] == 1
    assert ownership[(4, 4)] == 1


def test_territory_undefined_tiles_excluded():
    """Tiles without terrain are not owned."""
    m = MapState(
        terrain={(2, 2): 'land'},
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 1, 'border_level': 1},),
    )
    ownership = m.territory_ownership()
    assert (2, 2) in ownership
    assert (1, 1) not in ownership  # undefined terrain


def test_overlapping_territories():
    """First city in the list claims contested tiles."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(5) for c in range(5)},
        cities=(
            {'id': 1, 'row': 1, 'col': 1, 'population': 1, 'border_level': 1},
            {'id': 2, 'row': 3, 'col': 3, 'population': 1, 'border_level': 1},
        ),
    )
    ownership = m.territory_ownership()
    # (2, 2) is in both 3x3 areas; first city claims it
    assert ownership[(2, 2)] == 1


def test_tiles_owned_by():
    m = MapState(
        terrain={(r, c): 'land' for r in range(5) for c in range(5)},
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 1, 'border_level': 1},),
    )
    tiles = m.tiles_owned_by(1)
    assert (2, 2) in tiles
    assert (1, 1) in tiles
    assert len(tiles) == 9
