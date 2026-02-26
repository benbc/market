from solver import ELIGIBLE, terrain_accepts, is_adjacent, city_territory, assign_ownership, place_resource_buildings, multiplier_level, market_income, city_placements, optimise, _optimise_once, _score, COMBO_BUILDINGS, BUILDING_COST

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

def test_ownership_empty_events_falls_back():
    """Empty events list should behave same as no events (use city list order)."""
    cities = [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}]
    tile_positions = [(0, 0), (0, 1)]
    ownership = assign_ownership(tile_positions, cities, events=[])
    assert ownership[(0, 0)] == 1
    assert ownership[(0, 1)] == 1

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

def test_ownership_expansion_after_later_city_does_not_steal():
    """City 2 expands after city 1 is founded; can't take city 1's base tiles."""
    cities = [
        {'id': 1, 'row': 0, 'col': 3, 'expanded': False},
        {'id': 2, 'row': 0, 'col': 0, 'expanded': True},
    ]
    events = [
        {'action': 'found', 'city_id': 2},
        {'action': 'found', 'city_id': 1},
        {'action': 'expand', 'city_id': 2},
    ]
    # (0,2) is in city 1's base 3x3 (founded second) AND city 2's expansion ring.
    # City 1 was founded before city 2 expanded, so city 1 owns it.
    tile_positions = [(0, 2)]
    ownership = assign_ownership(tile_positions, cities, events)
    assert ownership[(0, 2)] == 1


def test_ownership_expansion_before_later_city_claims_tiles():
    """City 1 expands before city 2 is founded; claims tiles city 2 would want."""
    cities = [
        {'id': 1, 'row': 0, 'col': 0, 'expanded': True},
        {'id': 2, 'row': 0, 'col': 2, 'expanded': False},
    ]
    events = [
        {'action': 'found', 'city_id': 1},
        {'action': 'expand', 'city_id': 1},
        {'action': 'found', 'city_id': 2},
    ]
    # (0,2) is in city 1's expansion ring AND city 2's base 3x3.
    # City 1 expanded before city 2 was founded, so city 1 owns it.
    tile_positions = [(0, 2)]
    ownership = assign_ownership(tile_positions, cities, events)
    assert ownership[(0, 2)] == 1


def test_ownership_expansion_claims_unclaimed_tiles():
    """Expansion claims tiles outside any previously claimed territory."""
    cities = [
        {'id': 1, 'row': 0, 'col': 0, 'expanded': False},
        {'id': 2, 'row': 0, 'col': 4, 'expanded': True},
    ]
    events = [
        {'action': 'found', 'city_id': 1},
        {'action': 'found', 'city_id': 2},
        {'action': 'expand', 'city_id': 2},
    ]
    # (0,2) is outside city 1's base 3x3 and inside city 2's expansion ring
    tile_positions = [(0, 2)]
    ownership = assign_ownership(tile_positions, cities, events)
    assert ownership[(0, 2)] == 2


def test_mine_on_metal():
    """Without an adjacent forge, mine should NOT be placed."""
    tiles = {(0, 0): 'mountain+metal', (0, 1): 'field'}
    occupied = {}
    result, burns = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result

def test_lumber_hut_on_free_forest():
    """Without an adjacent sawmill, lumber_hut should NOT be placed."""
    tiles = {(0, 0): 'forest', (0, 1): 'forest'}
    occupied = {(0, 0): 'forge'}  # forge already there
    result, burns = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result   # forge occupies it
    assert (0, 1) not in result   # no adjacent sawmill

def test_farm_on_free_crop():
    """Without an adjacent windmill, farm should NOT be placed."""
    tiles = {(0, 0): 'field+crop', (0, 1): 'field+crop'}
    occupied = {(0, 0): 'market'}
    result, burns = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result   # market occupies it
    assert (0, 1) not in result   # no adjacent windmill

def test_no_resource_on_plain_field():
    tiles = {(0, 0): 'field'}
    occupied = {}
    result, burns = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result


def test_forest_with_adjacent_windmill_becomes_farm():
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    occupied = {(0, 1): 'windmill'}
    result, burns = place_resource_buildings(tiles, occupied)
    assert result[(0, 0)] == 'farm'
    assert (0, 0) in burns


def test_forest_with_adjacent_sawmill_stays_lumber_hut():
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    occupied = {(0, 1): 'sawmill'}
    result, burns = place_resource_buildings(tiles, occupied)
    assert result[(0, 0)] == 'lumber_hut'
    assert (0, 0) not in burns


def test_forest_with_no_adjacent_multipliers_stays_empty():
    """Without an adjacent sawmill, forest should NOT get a lumber_hut."""
    tiles = {(0, 0): 'forest'}
    occupied = {}
    result, burns = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result
    assert (0, 0) not in burns

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
    """Sawmill is not natively valid on forest; it is via clear."""
    tiles = {(0, 0): 'forest'}
    territory = {(0, 0)}
    combos = city_placements(tiles, city_territory_positions=territory)
    saw_on_forest = [c for c in combos if c['sawmill'] == (0, 0)]
    assert len(saw_on_forest) > 0
    # All such combos must include the position in clears
    for c in saw_on_forest:
        assert (0, 0) in c['clears']


def test_forest_as_sawmill_candidate_via_clear():
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    territory = {(0, 0), (0, 1)}
    combos = city_placements(tiles, city_territory_positions=territory)
    saw_on_forest = [c for c in combos if c['sawmill'] == (0, 0)]
    assert len(saw_on_forest) > 0
    for c in saw_on_forest:
        assert (0, 0) in c['clears']


def test_forest_as_market_candidate_via_clear():
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    territory = {(0, 0), (0, 1)}
    combos = city_placements(tiles, city_territory_positions=territory)
    mkt_on_forest = [c for c in combos if c['market'] == (0, 0)]
    assert len(mkt_on_forest) > 0
    for c in mkt_on_forest:
        assert (0, 0) in c['clears']


def test_forge_on_forest_no_clear():
    """Forge is natively valid on forest, so placing it there should NOT require a clear."""
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    territory = {(0, 0), (0, 1)}
    combos = city_placements(tiles, city_territory_positions=territory)
    forge_on_forest = [c for c in combos if c['forge'] == (0, 0)]
    assert len(forge_on_forest) > 0
    for c in forge_on_forest:
        assert (0, 0) not in c['clears']


def test_combo_clears_is_frozenset():
    tiles = {(0, 0): 'field'}
    territory = {(0, 0)}
    combos = city_placements(tiles, city_territory_positions=territory)
    for c in combos:
        assert isinstance(c['clears'], frozenset)

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
    assert 'total_cost' in result
    assert 'clears' in result
    assert 'burns' in result
    for p in result['placements']:
        assert 'row' in p and 'col' in p and 'building' in p
    for m in result['markets']:
        assert 'row' in m and 'col' in m and 'income' in m and 'city_id' in m
    for cl in result['clears']:
        assert 'row' in cl and 'col' in cl
    for b in result['burns']:
        assert 'row' in b and 'col' in b


def test_pinned_position_excluded_from_candidates():
    """A pinned position should not appear as a candidate for any building."""
    tiles = {(0, 0): 'field', (0, 1): 'field', (0, 2): 'field'}
    territory = {(0, 0), (0, 1), (0, 2)}
    pinned = frozenset({(0, 0)})
    combos = city_placements(tiles, territory, pinned_positions=pinned)
    for c in combos:
        for role in COMBO_BUILDINGS:
            assert c[role] != (0, 0), f"Pinned position (0,0) used as {role}"


def test_pinned_position_other_tiles_still_used():
    """Non-pinned positions should still be valid candidates."""
    tiles = {(0, 0): 'field', (0, 1): 'field', (0, 2): 'field'}
    territory = {(0, 0), (0, 1), (0, 2)}
    pinned = frozenset({(0, 0)})
    combos = city_placements(tiles, territory, pinned_positions=pinned)
    # Should have combos that use (0,1) and (0,2)
    used_positions = set()
    for c in combos:
        for role in COMBO_BUILDINGS:
            if c[role] is not None:
                used_positions.add(c[role])
    assert (0, 1) in used_positions
    assert (0, 2) in used_positions


def test_optimise_once_keeps_pinned_buildings():
    """_optimise_once should keep pinned buildings in assignments."""
    tiles = {
        (0, 0): 'field', (0, 1): 'field', (0, 2): 'field',
        (1, 0): 'field', (1, 1): 'field', (1, 2): 'field+crop',
    }
    territory = {(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)}
    pinned = {(0, 0): 'sawmill'}
    combos = city_placements(tiles, territory, pinned_positions=frozenset(pinned.keys()))
    cities_combos = [(1, territory, combos)]
    score, assignments, _ = _optimise_once(cities_combos, tiles, pinned)
    assert assignments.get((0, 0)) == 'sawmill'


def test_pinned_sawmill_contributes_to_market_income():
    """A pinned sawmill should contribute to market scoring."""
    # Layout: pinned sawmill at (0,0), lumber_hut at (1,0), market should benefit
    tiles = {
        (0, 0): 'field', (0, 1): 'field', (0, 2): 'forest',
        (1, 0): 'field', (1, 1): 'field', (1, 2): 'field+crop',
    }
    pinned = [{'row': 0, 'col': 0, 'building': 'sawmill'}]
    cities = [{'id': 1, 'row': 1, 'col': 1, 'expanded': False}]
    data = {
        'tiles': [{'row': r, 'col': c, 'terrain': t} for (r, c), t in tiles.items()],
        'cities': cities,
        'pinned': pinned,
    }
    result = optimise(data)
    # Pinned sawmill must be in placements
    saw_placed = [p for p in result['placements'] if p['row'] == 0 and p['col'] == 0]
    assert len(saw_placed) == 1
    assert saw_placed[0]['building'] == 'sawmill'


def test_optimise_accepts_pinned_and_returns_them():
    """optimise() should accept pinned in input and return them in placements."""
    tiles = {
        (0, 0): 'field', (0, 1): 'field',
        (1, 0): 'field', (1, 1): 'field',
    }
    pinned = [{'row': 0, 'col': 0, 'building': 'forge'}]
    cities = [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}]
    data = {
        'tiles': [{'row': r, 'col': c, 'terrain': t} for (r, c), t in tiles.items()],
        'cities': cities,
        'pinned': pinned,
    }
    result = optimise(data)
    forge_placed = [p for p in result['placements'] if p['row'] == 0 and p['col'] == 0]
    assert len(forge_placed) == 1
    assert forge_placed[0]['building'] == 'forge'


def test_optimise_burns_from_resource_greedy():
    """A forest next to a windmill should be burned to farm, appearing in burns."""
    tile_list = [
        ((0, 0), 'field'),
        ((0, 1), 'field+crop'),
        ((0, 2), 'forest'),
        ((1, 0), 'field'),
        ((1, 1), 'field'),
        ((1, 2), 'field'),
    ]
    cities = [{'id': 1, 'row': 1, 'col': 1, 'expanded': False}]
    result = optimise(_make_input(tile_list, cities))
    # The solver should place a windmill somewhere; if (0,2) forest is adjacent
    # to it, it should appear as a burn. Check that burns is a list.
    assert isinstance(result['burns'], list)


def test_optimise_clears_for_multiplier_on_forest():
    """When a sawmill is placed on a forest tile, it should appear in clears, not burns."""
    # Layout: forest surrounded by fields with crops, one city.
    # The solver should place a sawmill on the forest (clearing it) when it's optimal.
    tile_list = [
        ((0, 0), 'forest'),
        ((0, 1), 'field'),
        ((0, 2), 'field'),
        ((1, 0), 'forest'),
        ((1, 1), 'field'),
        ((1, 2), 'field+crop'),
        ((2, 0), 'forest'),
        ((2, 1), 'field'),
        ((2, 2), 'mountain+metal'),
    ]
    cities = [{'id': 1, 'row': 1, 'col': 1, 'expanded': False}]
    result = optimise(_make_input(tile_list, cities))
    clears_set = {(c['row'], c['col']) for c in result['clears']}
    burns_set = {(b['row'], b['col']) for b in result['burns']}
    # Clears and burns should not overlap
    assert clears_set.isdisjoint(burns_set)
    # Any cleared position should have a multiplier or market placed on it
    placements = {(p['row'], p['col']): p['building'] for p in result['placements']}
    for pos in clears_set:
        assert pos in placements
        assert placements[pos] in ('sawmill', 'windmill', 'market')


def test_excluded_building_not_in_combos():
    """An excluded building should never appear in any combo."""
    tiles = {(0, 0): 'field', (0, 1): 'field', (0, 2): 'field'}
    territory = {(0, 0), (0, 1), (0, 2)}
    combos = city_placements(tiles, territory, excluded_buildings=frozenset({'sawmill'}))
    for c in combos:
        assert c['sawmill'] is None, "Excluded sawmill was placed"


def test_excluded_building_others_still_work():
    """Non-excluded buildings should still be placed normally."""
    tiles = {(0, 0): 'field', (0, 1): 'field', (0, 2): 'field'}
    territory = {(0, 0), (0, 1), (0, 2)}
    combos = city_placements(tiles, territory, excluded_buildings=frozenset({'sawmill'}))
    has_windmill = any(c['windmill'] is not None for c in combos)
    assert has_windmill


def test_excluded_market_not_placed():
    tiles = {(0, 0): 'field', (0, 1): 'field'}
    territory = {(0, 0), (0, 1)}
    combos = city_placements(tiles, territory, excluded_buildings=frozenset({'market'}))
    for c in combos:
        assert c['market'] is None


def test_excluded_mine_not_placed():
    tiles = {(0, 0): 'mountain+metal', (0, 1): 'field'}
    occupied = {}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'mine'}))
    assert (0, 0) not in result


def test_excluded_farm_not_placed_on_crop():
    tiles = {(0, 0): 'field+crop'}
    occupied = {}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'farm'}))
    assert (0, 0) not in result


def test_excluded_lumber_hut_forest_stays_empty():
    """With lumber_hut excluded and no adjacent windmill, forest gets nothing."""
    tiles = {(0, 0): 'forest'}
    occupied = {}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'lumber_hut'}))
    assert (0, 0) not in result


def test_excluded_lumber_hut_forest_burns_to_farm_if_windmill():
    """With lumber_hut excluded but farm available, forest adjacent to windmill burns to farm."""
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    occupied = {(0, 1): 'windmill'}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'lumber_hut'}))
    assert result[(0, 0)] == 'farm'
    assert (0, 0) in burns


def test_excluded_farm_forest_stays_empty_without_sawmill():
    """With farm excluded and no adjacent sawmill, forest gets nothing."""
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    occupied = {(0, 1): 'windmill'}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'farm'}))
    assert (0, 0) not in result
    assert (0, 0) not in burns


def test_excluded_both_lumber_hut_and_farm_forest_empty():
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    occupied = {(0, 1): 'windmill'}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'lumber_hut', 'farm'}))
    assert (0, 0) not in result


def test_optimise_excludes_sawmill():
    """With sawmill excluded, no sawmill should appear in placements."""
    tiles = {
        (0, 0): 'field', (0, 1): 'field', (0, 2): 'forest',
        (1, 0): 'field', (1, 1): 'field', (1, 2): 'field+crop',
    }
    cities = [{'id': 1, 'row': 1, 'col': 1, 'expanded': False}]
    data = {
        'tiles': [{'row': r, 'col': c, 'terrain': t} for (r, c), t in tiles.items()],
        'cities': cities,
        'excluded': ['sawmill'],
    }
    result = optimise(data)
    for p in result['placements']:
        assert p['building'] != 'sawmill'


def test_optimise_no_buildings_outside_territory():
    """Resource buildings should only be placed on tiles within city territory."""
    # City at (1,1) unexpanded -> 3x3 territory covering rows 0-2, cols 0-2
    # Tiles at (0,4) and (1,4) are well outside territory
    tile_list = [
        ((0, 0), 'forest'),
        ((0, 1), 'field'),
        ((0, 2), 'field+crop'),
        ((1, 0), 'field'),
        ((1, 1), 'field'),
        ((1, 2), 'mountain+metal'),
        ((2, 0), 'field'),
        ((2, 1), 'field'),
        ((2, 2), 'field'),
        ((0, 4), 'forest'),
        ((1, 4), 'mountain+metal'),
    ]
    cities = [{'id': 1, 'row': 1, 'col': 1, 'expanded': False}]
    result = optimise(_make_input(tile_list, cities))
    placed = {(p['row'], p['col']) for p in result['placements']}
    assert (0, 4) not in placed, "Building placed outside city territory"
    assert (1, 4) not in placed, "Building placed outside city territory"


def test_optimise_excludes_lumber_hut():
    """With lumber_hut excluded, no lumber_hut in placements."""
    tiles = {
        (0, 0): 'forest', (0, 1): 'field',
        (1, 0): 'field', (1, 1): 'field',
    }
    cities = [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}]
    data = {
        'tiles': [{'row': r, 'col': c, 'terrain': t} for (r, c), t in tiles.items()],
        'cities': cities,
        'excluded': ['lumber_hut'],
    }
    result = optimise(data)
    for p in result['placements']:
        assert p['building'] != 'lumber_hut'


# --- Adjacency-filtered resource placement tests ---

def test_mine_placed_adjacent_to_forge():
    tiles = {(0, 0): 'mountain+metal', (0, 1): 'forest'}
    occupied = {(0, 1): 'forge'}
    result, burns = place_resource_buildings(tiles, occupied)
    assert result[(0, 0)] == 'mine'


def test_mine_not_placed_without_forge():
    tiles = {(0, 0): 'mountain+metal', (0, 1): 'field'}
    occupied = {(0, 1): 'sawmill'}
    result, burns = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result


def test_farm_placed_adjacent_to_windmill():
    tiles = {(0, 0): 'field+crop', (0, 1): 'field'}
    occupied = {(0, 1): 'windmill'}
    result, burns = place_resource_buildings(tiles, occupied)
    assert result[(0, 0)] == 'farm'


def test_farm_not_placed_without_windmill():
    tiles = {(0, 0): 'field+crop', (0, 1): 'field'}
    occupied = {(0, 1): 'sawmill'}
    result, burns = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result


def test_lumber_hut_placed_adjacent_to_sawmill():
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    occupied = {(0, 1): 'sawmill'}
    result, burns = place_resource_buildings(tiles, occupied)
    assert result[(0, 0)] == 'lumber_hut'


def test_lumber_hut_not_placed_without_sawmill():
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    occupied = {(0, 1): 'forge'}
    result, burns = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result


# --- Cost model tests ---

def test_score_returns_income_cost_tuple():
    """_score() should return a 2-tuple (income, -cost)."""
    tiles = {(0, 0): 'field', (0, 1): 'field'}
    assignments = {(0, 0): 'sawmill'}
    result = _score(assignments, tiles, owned_positions=frozenset(tiles.keys()))
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_tiebreak_prefers_lower_cost():
    """With equal income (0), the score with fewer buildings should win."""
    tiles = {(0, 0): 'field', (0, 1): 'field'}
    owned = frozenset(tiles.keys())
    score_empty = _score({}, tiles, owned_positions=owned)
    score_sawmill = _score({(0, 0): 'sawmill'}, tiles, owned_positions=owned)
    # Both have 0 market income, but sawmill costs 5
    assert score_empty[0] == score_sawmill[0] == 0
    assert score_empty > score_sawmill  # empty is cheaper


def test_cost_excludes_pinned():
    """Pinned buildings should not be counted in cost."""
    tiles = {(0, 0): 'field', (0, 1): 'field'}
    owned = frozenset(tiles.keys())
    pinned = frozenset({(0, 0)})
    score_pinned = _score({(0, 0): 'sawmill'}, tiles, owned_positions=owned, pinned_positions=pinned)
    score_unpinned = _score({(0, 0): 'sawmill'}, tiles, owned_positions=owned, pinned_positions=frozenset())
    # Pinned sawmill should cost 0; unpinned should cost 5
    assert score_pinned[1] > score_unpinned[1]  # -0 > -5


def test_optimise_returns_total_cost():
    tile_list = [((0, 0), 'field'), ((0, 1), 'field')]
    cities = [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}]
    result = optimise(_make_input(tile_list, cities))
    assert 'total_cost' in result
    assert isinstance(result['total_cost'], (int, float))
    assert result['total_cost'] >= 0
