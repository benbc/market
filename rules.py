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


BUILDINGS = {
    'sawmill': {
        'cost': 5,
        'eligible': {('land', None), ('land', 'crop')},
    },
    'windmill': {
        'cost': 5,
        'eligible': {('land', None), ('land', 'crop')},
    },
    'forge': {
        'cost': 5,
        'eligible': {('land', None), ('land', 'crop'), ('land', 'forest')},
    },
    'market': {
        'cost': 5,
        'eligible': {('land', None), ('land', 'crop')},
    },
    'lumber_hut': {
        'cost': 3,
        'eligible': {('land', 'forest')},
    },
    'farm': {
        'cost': 5,
        'eligible': {('land', 'crop')},
    },
    'mine': {
        'cost': 5,
        'eligible': {('mountain', 'metal')},
    },
}


def can_build(building, terrain, resource):
    """Check if a building can be placed on a tile with the given terrain and resource."""
    defn = BUILDINGS[building]
    return (terrain, resource) in defn['eligible']


MULTIPLIERS = {
    'sawmill': {'resource': 'lumber_hut', 'weight': 1},
    'windmill': {'resource': 'farm', 'weight': 1},
    'forge': {'resource': 'mine', 'weight': 2},
}

MARKET_CAP = 8


def multiplier_resource(building):
    m = MULTIPLIERS[building]
    return m['resource'], m['weight']


def is_multiplier(building):
    return building in MULTIPLIERS


ONE_PER_CITY = frozenset({'sawmill', 'windmill', 'forge'})
