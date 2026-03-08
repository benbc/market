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
