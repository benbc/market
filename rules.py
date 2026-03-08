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


TECHS = {
    # Climbing branch
    'climbing': {'tier': 1, 'requires': None, 'unlocks_buildings': [], 'unlocks_actions': []},
    'mining': {'tier': 2, 'requires': 'climbing', 'unlocks_buildings': ['mine'], 'unlocks_actions': []},
    'smithery': {'tier': 3, 'requires': 'mining', 'unlocks_buildings': ['forge'], 'unlocks_actions': []},
    'meditation': {'tier': 2, 'requires': 'climbing', 'unlocks_buildings': [], 'unlocks_actions': []},
    'philosophy': {'tier': 3, 'requires': 'meditation', 'unlocks_buildings': [], 'unlocks_actions': []},
    # Fishing branch
    'fishing': {'tier': 1, 'requires': None, 'unlocks_buildings': [], 'unlocks_actions': []},
    'sailing': {'tier': 2, 'requires': 'fishing', 'unlocks_buildings': [], 'unlocks_actions': []},
    'navigation': {'tier': 3, 'requires': 'sailing', 'unlocks_buildings': [], 'unlocks_actions': []},
    'aquaculture': {'tier': 2, 'requires': 'fishing', 'unlocks_buildings': [], 'unlocks_actions': []},
    'aquatism': {'tier': 3, 'requires': 'aquaculture', 'unlocks_buildings': [], 'unlocks_actions': []},
    # Hunting branch
    'hunting': {'tier': 1, 'requires': None, 'unlocks_buildings': [], 'unlocks_actions': []},
    'forestry': {'tier': 2, 'requires': 'hunting', 'unlocks_buildings': ['lumber_hut'], 'unlocks_actions': ['clear_forest']},
    'mathematics': {'tier': 3, 'requires': 'forestry', 'unlocks_buildings': ['sawmill'], 'unlocks_actions': []},
    'archery': {'tier': 2, 'requires': 'hunting', 'unlocks_buildings': [], 'unlocks_actions': []},
    'spiritualism': {'tier': 3, 'requires': 'archery', 'unlocks_buildings': [], 'unlocks_actions': ['grow_forest']},
    # Organization branch
    'organization': {'tier': 1, 'requires': None, 'unlocks_buildings': [], 'unlocks_actions': []},
    'farming': {'tier': 2, 'requires': 'organization', 'unlocks_buildings': ['farm'], 'unlocks_actions': []},
    'construction': {'tier': 3, 'requires': 'farming', 'unlocks_buildings': ['windmill'], 'unlocks_actions': ['burn_forest']},
    'strategy': {'tier': 2, 'requires': 'organization', 'unlocks_buildings': [], 'unlocks_actions': []},
    'diplomacy': {'tier': 3, 'requires': 'strategy', 'unlocks_buildings': [], 'unlocks_actions': []},
    # Riding branch
    'riding': {'tier': 1, 'requires': None, 'unlocks_buildings': [], 'unlocks_actions': []},
    'roads': {'tier': 2, 'requires': 'riding', 'unlocks_buildings': [], 'unlocks_actions': []},
    'trade': {'tier': 3, 'requires': 'roads', 'unlocks_buildings': ['market'], 'unlocks_actions': []},
    'free_spirit': {'tier': 2, 'requires': 'riding', 'unlocks_buildings': [], 'unlocks_actions': []},
    'chivalry': {'tier': 3, 'requires': 'free_spirit', 'unlocks_buildings': [], 'unlocks_actions': []},
}


def techs_unlocking_building(building):
    """Return set of tech names that unlock the given building."""
    return {name for name, tech in TECHS.items() if building in tech['unlocks_buildings']}


def techs_unlocking_action(action):
    """Return set of tech names that unlock the given action."""
    return {name for name, tech in TECHS.items() if action in tech['unlocks_actions']}


def available_with_techs(techs):
    """Return dict of {'buildings': set, 'actions': set} available with given techs."""
    buildings = set()
    actions = set()
    for tech_name in techs:
        tech = TECHS.get(tech_name)
        if tech:
            buildings.update(tech['unlocks_buildings'])
            actions.update(tech['unlocks_actions'])
    return {'buildings': buildings, 'actions': actions}
