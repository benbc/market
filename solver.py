ELIGIBLE = {
    'field': {'sawmill', 'windmill', 'forge', 'market'},
    'field+crop': {'sawmill', 'windmill', 'forge', 'market', 'farm'},
    'forest': {'lumber_hut', 'forge'},
    'mountain+metal': {'mine'},
    'mountain': set(),
    'water': set(),
    'ocean': set(),
    'empty': set(),
}

def terrain_accepts(terrain: str, building: str) -> bool:
    return building in ELIGIBLE.get(terrain, set())

def is_adjacent(a: tuple, b: tuple) -> bool:
    """8-directional adjacency (Moore neighbourhood). A tile is not adjacent to itself."""
    dr = abs(a[0] - b[0])
    dc = abs(a[1] - b[1])
    return max(dr, dc) == 1

def city_territory(row: int, col: int, expanded: bool) -> set:
    """Return set of (row, col) positions in a city's territory."""
    radius = 2 if expanded else 1
    return {
        (row + dr, col + dc)
        for dr in range(-radius, radius + 1)
        for dc in range(-radius, radius + 1)
    }

def chebyshev(a: tuple, b: tuple) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def assign_ownership(tile_positions: list, cities: list) -> dict:
    """
    Map each tile position to the id of its owning city.
    Nearest city wins; ties broken by city order (first in list).
    Tiles not in any city's territory are omitted.
    """
    ownership = {}
    for pos in tile_positions:
        best_city = None
        best_dist = float('inf')
        for city in cities:
            city_pos = (city['row'], city['col'])
            territory = city_territory(city['row'], city['col'], city['expanded'])
            if pos not in territory:
                continue
            dist = chebyshev(pos, city_pos)
            if dist < best_dist:
                best_dist = dist
                best_city = city['id']
        if best_city is not None:
            ownership[pos] = best_city
    return ownership

def place_resource_buildings(tiles: dict, occupied: dict) -> tuple:
    """
    Given a map of pos->terrain and a dict of already-occupied pos->building,
    return (resources, burns) where:
      resources: dict of pos->resource_building for every free eligible tile
      burns: set of forest positions that should be burned (converted to farm)
    For forests, chooses between lumber_hut and farm based on adjacent multipliers.
    """
    RESOURCE = {
        'mountain+metal': 'mine',
        'field+crop': 'farm',
    }
    result = {}
    burns = set()
    for pos, terrain in tiles.items():
        if pos in occupied:
            continue
        if terrain == 'forest':
            # Count adjacent sawmills and windmills to decide keep vs burn
            adj_sawmills = sum(
                1 for opos, bldg in occupied.items()
                if bldg == 'sawmill' and is_adjacent(pos, opos)
            )
            adj_windmills = sum(
                1 for opos, bldg in occupied.items()
                if bldg == 'windmill' and is_adjacent(pos, opos)
            )
            if adj_windmills > adj_sawmills:
                result[pos] = 'farm'
                burns.add(pos)
            else:
                result[pos] = 'lumber_hut'
        else:
            building = RESOURCE.get(terrain)
            if building:
                result[pos] = building
    return result, burns

MULTIPLIER_RESOURCE = {
    'sawmill': ('lumber_hut', 1),
    'windmill': ('farm', 1),
    'forge': ('mine', 2),
}

def multiplier_level(pos: tuple, building: str, placements: dict) -> int:
    """
    Compute the level (population output) of a production multiplier.
    placements: dict of pos->building covering all placed buildings.
    """
    resource, weight = MULTIPLIER_RESOURCE[building]
    return sum(
        weight
        for other_pos, other_bldg in placements.items()
        if other_bldg == resource and is_adjacent(pos, other_pos)
    )

MARKET_CAP = 8

def market_income(pos: tuple, placements: dict) -> int:
    """
    Compute a Market's star income given all placed buildings.
    Income = sum of levels of 8-adjacent Sawmills/Windmills/Forges, capped at MARKET_CAP.
    """
    total = 0
    for other_pos, building in placements.items():
        if building in MULTIPLIER_RESOURCE and is_adjacent(pos, other_pos):
            total += multiplier_level(other_pos, building, placements)
    return min(total, MARKET_CAP)

from itertools import product as iproduct

MULTIPLIERS = ('sawmill', 'windmill', 'forge')
COMBO_BUILDINGS = ('sawmill', 'windmill', 'forge', 'market')

FIELD_CROP_ELIGIBLE = ELIGIBLE['field+crop']

def city_placements(tiles: dict, city_territory_positions: set, pinned_positions: frozenset = frozenset()) -> list:
    """
    Enumerate all valid (sawmill, windmill, forge, market) tile assignments for one city.
    tiles: dict of pos->terrain for all tiles in the game (not just this city).
    city_territory_positions: set of positions belonging to this city.
    Returns list of dicts with keys sawmill, windmill, forge, market, burns.
    burns is a frozenset of positions where forest must be burned for the placement.
    """
    def candidates(building):
        result = [None]
        for pos in city_territory_positions:
            if pos in pinned_positions:
                continue
            if pos not in tiles:
                continue
            terrain = tiles[pos]
            if terrain_accepts(terrain, building):
                result.append(pos)
            elif terrain == 'forest' and building in FIELD_CROP_ELIGIBLE:
                # Forest can be burned to field+crop, making it eligible
                result.append(pos)
        return result

    saw_cands = candidates('sawmill')
    win_cands = candidates('windmill')
    for_cands = candidates('forge')
    mkt_cands = candidates('market')

    results = []
    for saw, win, frg, mkt in iproduct(saw_cands, win_cands, for_cands, mkt_cands):
        # No two roles on the same tile
        placed = [p for p in (saw, win, frg, mkt) if p is not None]
        if len(placed) != len(set(placed)):
            continue
        # Market must be adjacent to at least one multiplier (if market is placed)
        if mkt is not None:
            multiplier_positions = [p for p in (saw, win, frg) if p is not None]
            if not any(is_adjacent(mkt, mp) for mp in multiplier_positions):
                continue
        # Compute which forest positions need burning
        burns = frozenset(
            pos for pos, building in ((saw, 'sawmill'), (win, 'windmill'), (frg, 'forge'), (mkt, 'market'))
            if pos is not None and tiles.get(pos) == 'forest' and not terrain_accepts('forest', building)
        )
        results.append({'sawmill': saw, 'windmill': win, 'forge': frg, 'market': mkt, 'burns': burns})
    return results

import random

def _build_full_placements(city_assignments: dict, tiles: dict) -> tuple:
    """
    Given per-city production/market assignments (pos->building),
    fill remaining eligible tiles with resource buildings.
    Returns (placements dict pos->building, burns set of burned positions).
    """
    occupied = dict(city_assignments)
    resources, resource_burns = place_resource_buildings(tiles, occupied)
    return {**occupied, **resources}, resource_burns

def _score(city_assignments: dict, tiles: dict) -> int:
    """Total Market income given current city assignments."""
    placements, _ = _build_full_placements(city_assignments, tiles)
    return sum(
        market_income(pos, placements)
        for pos, bldg in placements.items()
        if bldg == 'market'
    )

def _random_assignment(combos: list) -> dict:
    return random.choice(combos) if combos else {}

def _optimise_once(cities_combos: list, tiles: dict, pinned: dict = None) -> tuple:
    """
    One run of coordinate descent from a random start.
    cities_combos: list of (city_id, territory_positions, combos_list)
    pinned: dict of (r,c)->building for buildings that must stay fixed
    Returns (score, city_assignments dict pos->building)
    """
    if pinned is None:
        pinned = {}
    current = dict(pinned)
    city_selected = []
    for city_id, territory, combos in cities_combos:
        chosen = _random_assignment(combos)
        city_selected.append((city_id, territory, combos, chosen))
        for role in COMBO_BUILDINGS:
            pos = chosen.get(role)
            if pos is not None:
                current[pos] = role

    improved = True
    while improved:
        improved = False
        for i, (city_id, territory, combos, chosen) in enumerate(city_selected):
            partial = {p: b for p, b in current.items()
                       if p not in territory or b not in COMBO_BUILDINGS or p in pinned}

            best_score = -1
            best_combo = chosen
            for combo in combos:
                candidate = dict(partial)
                for role in COMBO_BUILDINGS:
                    pos = combo.get(role)
                    if pos is not None:
                        candidate[pos] = role
                s = _score(candidate, tiles)
                if s > best_score:
                    best_score = s
                    best_combo = combo

            new_assignments = dict(partial)
            for role in COMBO_BUILDINGS:
                pos = best_combo.get(role)
                if pos is not None:
                    new_assignments[pos] = role

            if best_combo != chosen:
                improved = True
            city_selected[i] = (city_id, territory, combos, best_combo)
            current = new_assignments

    return _score(current, tiles), current, city_selected

def optimise(data: dict, restarts: int = 5) -> dict:
    """
    Main solver entry point.
    data: {'tiles': [...], 'cities': [...]}
    Returns {'placements': [...], 'markets': [...], 'total_income': int}
    """
    tiles = {(t['row'], t['col']): t['terrain'] for t in data['tiles']}
    cities = data['cities']
    pinned = {(p['row'], p['col']): p['building'] for p in data.get('pinned', [])}
    pinned_positions = frozenset(pinned.keys())
    all_positions = list(tiles.keys())
    ownership = assign_ownership(all_positions, cities)

    cities_combos = []
    for city in cities:
        territory = city_territory(city['row'], city['col'], city['expanded'])
        territory_in_game = {p for p in territory if p in tiles and ownership.get(p) == city['id']}
        combos = city_placements(tiles, territory_in_game, pinned_positions)
        if not combos:
            combos = [{'sawmill': None, 'windmill': None, 'forge': None, 'market': None, 'burns': frozenset()}]
        cities_combos.append((city['id'], territory_in_game, combos))

    best_score = -1
    best_placements = {}
    best_city_selected = []

    for _ in range(restarts):
        score, placements, city_selected = _optimise_once(cities_combos, tiles, pinned)
        if score > best_score:
            best_score = score
            best_placements = placements
            best_city_selected = city_selected

    full, resource_burns = _build_full_placements(best_placements, tiles)

    # Collect burns from multiplier/market combos
    combo_burns = set()
    for _city_id, _territory, _combos, chosen in best_city_selected:
        combo_burns |= set(chosen.get('burns', frozenset()))

    all_burns = combo_burns | resource_burns

    placement_list = [
        {'row': pos[0], 'col': pos[1], 'building': bldg}
        for pos, bldg in full.items()
    ]
    markets_list = []
    for pos, bldg in full.items():
        if bldg == 'market':
            city_id = ownership.get(pos)
            markets_list.append({
                'row': pos[0], 'col': pos[1],
                'city_id': city_id,
                'income': market_income(pos, full),
            })
    burns_list = [{'row': pos[0], 'col': pos[1]} for pos in all_burns]

    return {
        'placements': placement_list,
        'markets': markets_list,
        'total_income': best_score,
        'burns': burns_list,
    }
