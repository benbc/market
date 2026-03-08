from moves import legal_moves
from map_state import MapState


def test_no_moves_on_empty_map():
    m = MapState()
    assert legal_moves(m, techs=frozenset()) == []


def test_build_on_eligible_tile():
    m = MapState(
        terrain={(0, 0): 'land'},
        cities=({'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset({'mathematics'}))
    assert ('build', (0, 0), 'sawmill') in moves


def test_no_build_without_tech():
    m = MapState(
        terrain={(0, 0): 'land'},
        cities=({'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset())
    build_moves = [a for a in moves if a[0] == 'build']
    assert len(build_moves) == 0


def test_clear_forest_move():
    m = MapState(
        terrain={(0, 0): 'land'},
        resources={(0, 0): 'forest'},
        cities=({'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset({'forestry'}))
    assert ('clear_forest', (0, 0)) in moves


def test_found_city_move():
    m = MapState(
        terrain={(5, 5): 'land'},
        villages=frozenset({(5, 5)}),
    )
    moves = legal_moves(m, techs=frozenset())
    assert ('found_city', (5, 5)) in moves


def test_no_build_outside_territory():
    m = MapState(
        terrain={(0, 0): 'land', (5, 5): 'land'},
        cities=({'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset({'mathematics'}))
    sawmill_positions = [a[1] for a in moves if a[0] == 'build' and a[2] == 'sawmill']
    assert (0, 0) in sawmill_positions
    assert (5, 5) not in sawmill_positions


def test_no_build_on_occupied():
    m = MapState(
        terrain={(0, 0): 'land'},
        buildings={(0, 0): 'farm'},
        cities=({'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset({'mathematics'}))
    build_at_0_0 = [a for a in moves if a[0] == 'build' and a[1] == (0, 0)]
    assert len(build_at_0_0) == 0


def test_one_per_city_constraint():
    """If a city already has a sawmill, can't build another."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(3) for c in range(3)},
        buildings={(0, 0): 'sawmill'},
        cities=({'id': 1, 'row': 1, 'col': 1, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset({'mathematics'}))
    sawmill_moves = [a for a in moves if a[0] == 'build' and a[2] == 'sawmill']
    assert len(sawmill_moves) == 0
