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
