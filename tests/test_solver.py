from solver import ELIGIBLE, terrain_accepts, is_adjacent, city_territory, assign_ownership, place_resource_buildings, multiplier_level, market_income, city_placements, optimise

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

def test_mine_on_metal():
    tiles = {(0, 0): 'mountain+metal', (0, 1): 'field'}
    occupied = {}
    result = place_resource_buildings(tiles, occupied)
    assert result[(0, 0)] == 'mine'

def test_lumber_hut_on_free_forest():
    tiles = {(0, 0): 'forest', (0, 1): 'forest'}
    occupied = {(0, 0): 'forge'}  # forge already there
    result = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result   # forge occupies it
    assert result[(0, 1)] == 'lumber_hut'

def test_farm_on_free_crop():
    tiles = {(0, 0): 'field+crop', (0, 1): 'field+crop'}
    occupied = {(0, 0): 'market'}
    result = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result   # market occupies it
    assert result[(0, 1)] == 'farm'

def test_no_resource_on_plain_field():
    tiles = {(0, 0): 'field'}
    occupied = {}
    result = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result

def test_sawmill_level_no_huts():
    placements = {(1, 1): 'sawmill'}
    assert multiplier_level((1, 1), 'sawmill', placements) == 0

def test_sawmill_level_one_hut():
    placements = {(1, 1): 'sawmill', (1, 2): 'lumber_hut'}
    assert multiplier_level((1, 1), 'sawmill', placements) == 1

def test_sawmill_level_three_huts():
    placements = {
        (1, 1): 'sawmill',
        (0, 0): 'lumber_hut',
        (0, 1): 'lumber_hut',
        (0, 2): 'lumber_hut',
    }
    assert multiplier_level((1, 1), 'sawmill', placements) == 3

def test_windmill_level_two_farms():
    placements = {
        (2, 2): 'windmill',
        (1, 1): 'farm',
        (3, 3): 'farm',
    }
    assert multiplier_level((2, 2), 'windmill', placements) == 2

def test_forge_level_one_mine():
    placements = {(0, 0): 'forge', (0, 1): 'mine'}
    assert multiplier_level((0, 0), 'forge', placements) == 2

def test_forge_level_two_mines():
    placements = {(0, 0): 'forge', (0, 1): 'mine', (1, 0): 'mine'}
    assert multiplier_level((0, 0), 'forge', placements) == 4

def test_non_adjacent_hut_not_counted():
    placements = {(0, 0): 'sawmill', (0, 3): 'lumber_hut'}
    assert multiplier_level((0, 0), 'sawmill', placements) == 0

def test_market_no_adjacent_multipliers():
    placements = {(0, 0): 'market'}
    assert market_income((0, 0), placements) == 0

def test_market_adjacent_sawmill_level_2():
    placements = {
        (0, 0): 'market',
        (0, 1): 'sawmill',
        (0, 2): 'lumber_hut',
        (1, 2): 'lumber_hut',
    }
    assert market_income((0, 0), placements) == 2

def test_market_adjacent_forge_and_sawmill():
    placements = {
        (5, 5): 'market',
        (5, 6): 'sawmill',
        (5, 7): 'lumber_hut',  # adjacent to sawmill, not market
        (5, 4): 'forge',
        (4, 4): 'mine',         # adjacent to forge, not market
    }
    # sawmill level=1, forge level=2 -> total=3
    assert market_income((5, 5), placements) == 3

def test_market_capped_at_8():
    placements = {
        (5, 5): 'market',
        (4, 4): 'sawmill',
        (4, 5): 'sawmill',
        (4, 6): 'sawmill',
    }
    placements.update({
        (3, 3): 'lumber_hut', (3, 4): 'lumber_hut', (3, 5): 'lumber_hut',
        (3, 6): 'lumber_hut',
        (5, 7): 'lumber_hut',
        (4, 7): 'lumber_hut',
    })
    income = market_income((5, 5), placements)
    assert income <= 8

def test_market_diagonal_multiplier_counts():
    placements = {
        (0, 0): 'market',
        (1, 1): 'sawmill',   # diagonal
        (1, 2): 'lumber_hut',
    }
    assert market_income((0, 0), placements) == 1

def _simple_tiles(positions, terrain='field+crop'):
    return {pos: terrain for pos in positions}

def test_single_tile_no_valid_market_alone():
    tiles = _simple_tiles([(0, 0)])
    combos = city_placements(tiles, city_territory_positions={(0, 0)})
    assert all(c['market'] is None for c in combos)

def test_two_adjacent_tiles_market_next_to_sawmill():
    tiles = {(0, 0): 'field', (0, 1): 'field'}
    territory = {(0, 0), (0, 1)}
    combos = city_placements(tiles, city_territory_positions=territory)
    valid = [c for c in combos if c['market'] is not None and c['sawmill'] is not None]
    assert len(valid) >= 2

def test_no_duplicate_tile_usage():
    tiles = {(0, 0): 'field', (0, 1): 'field'}
    territory = {(0, 0), (0, 1)}
    combos = city_placements(tiles, city_territory_positions=territory)
    for c in combos:
        positions = [v for v in c.values() if v is not None]
        assert len(positions) == len(set(positions)), f"Duplicate tile in {c}"

def test_forge_on_forest():
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    territory = {(0, 0), (0, 1)}
    combos = city_placements(tiles, city_territory_positions=territory)
    forge_on_forest = [c for c in combos if c['forge'] == (0, 0)]
    assert len(forge_on_forest) > 0

def test_sawmill_not_on_forest():
    tiles = {(0, 0): 'forest'}
    territory = {(0, 0)}
    combos = city_placements(tiles, city_territory_positions=territory)
    assert all(c['sawmill'] != (0, 0) for c in combos)

def _make_input(tile_list, city_list):
    return {
        'tiles': [{'row': r, 'col': c, 'terrain': t} for (r, c), t in tile_list],
        'cities': city_list,
    }

def test_single_city_simple():
    tile_list = [
        ((0, 0), 'forest'),
        ((0, 1), 'field'),
        ((0, 2), 'mountain+metal'),
        ((1, 0), 'field'),
        ((1, 1), 'field'),
        ((1, 2), 'field+crop'),
        ((2, 0), 'field+crop'),
        ((2, 1), 'field'),
        ((2, 2), 'forest'),
    ]
    cities = [{'id': 1, 'row': 1, 'col': 1, 'expanded': False}]
    result = optimise(_make_input(tile_list, cities))
    assert result['total_income'] > 0
    assert any(m['city_id'] == 1 for m in result['markets'])

def test_two_adjacent_cities_cross_city_interaction():
    tile_list = (
        [((r, c), 'forest') for r in range(3) for c in range(3)]
        + [((r, c), 'field') for r in range(3) for c in range(3, 8)]
    )
    cities = [
        {'id': 1, 'row': 1, 'col': 1, 'expanded': False},
        {'id': 2, 'row': 1, 'col': 5, 'expanded': False},
    ]
    result = optimise(_make_input(tile_list, cities))
    assert result['total_income'] >= 0

def test_result_structure():
    tile_list = [((0, 0), 'field'), ((0, 1), 'field')]
    cities = [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}]
    result = optimise(_make_input(tile_list, cities))
    assert 'placements' in result
    assert 'markets' in result
    assert 'total_income' in result
    for p in result['placements']:
        assert 'row' in p and 'col' in p and 'building' in p
    for m in result['markets']:
        assert 'row' in m and 'col' in m and 'income' in m and 'city_id' in m
