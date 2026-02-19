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

def place_resource_buildings(tiles: dict, occupied: dict) -> dict:
    """
    Given a map of pos->terrain and a dict of already-occupied pos->building,
    return a dict of pos->resource_building for every free eligible tile.
    Resource buildings: mine (mountain+metal), lumber_hut (forest), farm (field+crop).
    Plain fields get nothing.
    """
    RESOURCE = {
        'mountain+metal': 'mine',
        'forest': 'lumber_hut',
        'field+crop': 'farm',
    }
    result = {}
    for pos, terrain in tiles.items():
        if pos in occupied:
            continue
        building = RESOURCE.get(terrain)
        if building:
            result[pos] = building
    return result

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

def city_placements(tiles: dict, city_territory_positions: set) -> list:
    """
    Enumerate all valid (sawmill, windmill, forge, market) tile assignments for one city.
    tiles: dict of pos->terrain for all tiles in the game (not just this city).
    city_territory_positions: set of positions belonging to this city.
    Returns list of dicts with keys sawmill, windmill, forge, market (values: pos or None).
    """
    def candidates(building):
        return [None] + [
            pos for pos in city_territory_positions
            if pos in tiles and terrain_accepts(tiles[pos], building)
        ]

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
        results.append({'sawmill': saw, 'windmill': win, 'forge': frg, 'market': mkt})
    return results
