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
