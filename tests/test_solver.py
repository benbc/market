from solver import ELIGIBLE, terrain_accepts, is_adjacent, city_territory, assign_ownership

def test_field_accepts_sawmill():
    assert 'sawmill' in ELIGIBLE['field']

def test_field_accepts_windmill():
    assert 'windmill' in ELIGIBLE['field']

def test_field_accepts_forge():
    assert 'forge' in ELIGIBLE['field']

def test_field_accepts_market():
    assert 'market' in ELIGIBLE['field']

def test_field_does_not_accept_farm():
    assert 'farm' not in ELIGIBLE['field']

def test_crop_accepts_farm():
    assert 'farm' in ELIGIBLE['field+crop']

def test_crop_accepts_all_field_buildings():
    for b in ('sawmill', 'windmill', 'forge', 'market'):
        assert b in ELIGIBLE['field+crop']

def test_forest_accepts_lumber_hut():
    assert 'lumber_hut' in ELIGIBLE['forest']

def test_forest_accepts_forge():
    assert 'forge' in ELIGIBLE['forest']

def test_forest_does_not_accept_sawmill():
    assert 'sawmill' not in ELIGIBLE['forest']

def test_metal_accepts_mine():
    assert 'mine' in ELIGIBLE['mountain+metal']

def test_metal_does_not_accept_market():
    assert 'market' not in ELIGIBLE['mountain+metal']

def test_terrain_accepts():
    assert terrain_accepts('field', 'sawmill')
    assert not terrain_accepts('forest', 'market')

def test_adjacent_orthogonal():
    assert is_adjacent((0, 0), (0, 1))
    assert is_adjacent((0, 0), (1, 0))

def test_adjacent_diagonal():
    assert is_adjacent((0, 0), (1, 1))
    assert is_adjacent((2, 2), (1, 3))

def test_not_adjacent_same_tile():
    assert not is_adjacent((0, 0), (0, 0))

def test_not_adjacent_two_apart():
    assert not is_adjacent((0, 0), (0, 2))
    assert not is_adjacent((0, 0), (2, 2))

def test_territory_3x3():
    tiles = city_territory(row=5, col=5, expanded=False)
    assert len(tiles) == 9
    assert (4, 4) in tiles
    assert (6, 6) in tiles
    assert (3, 5) not in tiles  # outside 3x3

def test_territory_5x5():
    tiles = city_territory(row=5, col=5, expanded=True)
    assert len(tiles) == 25
    assert (3, 3) in tiles
    assert (7, 7) in tiles
    assert (2, 5) not in tiles  # outside 5x5

def test_ownership_single_city():
    cities = [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}]
    tile_positions = [(0, 0), (0, 1), (1, 1)]
    ownership = assign_ownership(tile_positions, cities)
    assert ownership[(0, 0)] == 1
    assert ownership[(0, 1)] == 1
    assert ownership[(1, 1)] == 1

def test_ownership_nearest_city():
    cities = [
        {'id': 1, 'row': 0, 'col': 0, 'expanded': True},
        {'id': 2, 'row': 0, 'col': 6, 'expanded': True},
    ]
    tile_positions = [(0, 2), (0, 4)]
    ownership = assign_ownership(tile_positions, cities)
    assert ownership[(0, 2)] == 1  # closer to city 1
    assert ownership[(0, 4)] == 2  # closer to city 2

def test_ownership_tie_broken_by_order():
    cities = [
        {'id': 1, 'row': 0, 'col': 0, 'expanded': False},
        {'id': 2, 'row': 0, 'col': 2, 'expanded': False},
    ]
    tile_positions = [(0, 1)]  # equidistant
    ownership = assign_ownership(tile_positions, cities)
    assert ownership[(0, 1)] == 1  # first city wins
