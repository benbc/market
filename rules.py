TERRAIN_TYPES = frozenset({'land', 'mountain', 'water', 'ocean'})

RESOURCE_TYPES = frozenset({'forest', 'crop', 'metal', 'animal', 'fruit'})

_VALID_RESOURCES = {
    'land': frozenset({'forest', 'crop', 'animal', 'fruit'}),
    'mountain': frozenset({'metal'}),
    'water': frozenset(),
    'ocean': frozenset(),
}


def valid_resources_for_terrain(terrain):
    return _VALID_RESOURCES[terrain]
