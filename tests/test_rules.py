from rules import (
    TERRAIN_TYPES, RESOURCE_TYPES, valid_resources_for_terrain,
    can_build, BUILDINGS,
    MULTIPLIERS, multiplier_resource, MARKET_CAP, is_multiplier,
    ONE_PER_CITY,
    TECHS, techs_unlocking_building, techs_unlocking_action, available_with_techs,
    TERRAIN_ACTIONS, MAP_SHAPES,
    HARVEST_ACTIONS,
)


def test_terrain_types():
    assert 'land' in TERRAIN_TYPES
    assert 'mountain' in TERRAIN_TYPES
    assert 'water' in TERRAIN_TYPES
    assert 'ocean' in TERRAIN_TYPES


def test_resource_types():
    for r in ('forest', 'crop', 'metal', 'animal', 'fruit'):
        assert r in RESOURCE_TYPES


def test_forest_on_land():
    assert 'forest' in valid_resources_for_terrain('land')


def test_crop_on_land():
    assert 'crop' in valid_resources_for_terrain('land')


def test_metal_on_mountain():
    assert 'metal' in valid_resources_for_terrain('mountain')


def test_no_resources_on_water():
    assert len(valid_resources_for_terrain('water')) == 0


def test_no_resources_on_ocean():
    assert len(valid_resources_for_terrain('ocean')) == 0


def test_animal_on_land():
    assert 'animal' in valid_resources_for_terrain('land')


def test_fruit_on_land():
    assert 'fruit' in valid_resources_for_terrain('land')


def test_sawmill_on_land():
    assert can_build('sawmill', terrain='land', resource=None)


def test_sawmill_on_land_with_crop():
    assert can_build('sawmill', terrain='land', resource='crop')


def test_sawmill_not_on_mountain():
    assert not can_build('sawmill', terrain='mountain', resource=None)


def test_lumber_hut_requires_forest():
    assert can_build('lumber_hut', terrain='land', resource='forest')
    assert not can_build('lumber_hut', terrain='land', resource=None)


def test_farm_requires_crop():
    assert can_build('farm', terrain='land', resource='crop')
    assert not can_build('farm', terrain='land', resource=None)


def test_mine_requires_metal():
    assert can_build('mine', terrain='mountain', resource='metal')
    assert not can_build('mine', terrain='mountain', resource=None)


def test_forge_on_forest():
    assert can_build('forge', terrain='land', resource='forest')


def test_forge_on_land():
    assert can_build('forge', terrain='land', resource=None)


def test_market_on_land():
    assert can_build('market', terrain='land', resource=None)


def test_market_on_crop():
    assert can_build('market', terrain='land', resource='crop')


def test_market_not_on_forest():
    assert not can_build('market', terrain='land', resource='forest')


def test_multipliers():
    assert 'sawmill' in MULTIPLIERS
    assert 'windmill' in MULTIPLIERS
    assert 'forge' in MULTIPLIERS
    assert 'market' not in MULTIPLIERS


def test_multiplier_resource_sawmill():
    resource, weight = multiplier_resource('sawmill')
    assert resource == 'lumber_hut'
    assert weight == 1


def test_multiplier_resource_forge():
    resource, weight = multiplier_resource('forge')
    assert resource == 'mine'
    assert weight == 2


def test_market_cap():
    assert MARKET_CAP == 8


def test_is_multiplier():
    assert is_multiplier('sawmill')
    assert not is_multiplier('market')
    assert not is_multiplier('farm')


def test_one_per_city():
    assert 'sawmill' in ONE_PER_CITY
    assert 'windmill' in ONE_PER_CITY
    assert 'forge' in ONE_PER_CITY
    assert 'market' not in ONE_PER_CITY
    assert 'farm' not in ONE_PER_CITY


def test_tech_tiers():
    assert TECHS['climbing']['tier'] == 1
    assert TECHS['mining']['tier'] == 2
    assert TECHS['smithery']['tier'] == 3


def test_tech_prerequisites():
    assert TECHS['mining']['requires'] == 'climbing'
    assert TECHS['climbing']['requires'] is None


def test_techs_unlocking_building():
    assert techs_unlocking_building('mine') == {'mining'}
    assert techs_unlocking_building('sawmill') == {'mathematics'}
    assert techs_unlocking_building('market') == {'trade'}


def test_techs_unlocking_action():
    assert techs_unlocking_action('clear_forest') == {'forestry'}
    assert techs_unlocking_action('burn_forest') == {'construction'}
    assert techs_unlocking_action('grow_forest') == {'spiritualism'}


def test_available_with_techs():
    available = available_with_techs(frozenset())
    assert 'sawmill' not in available['buildings']
    available = available_with_techs(frozenset({'mathematics'}))
    assert 'sawmill' in available['buildings']
    available = available_with_techs(frozenset({'forestry'}))
    assert 'clear_forest' in available['actions']


def test_clear_forest_yield():
    assert TERRAIN_ACTIONS['clear_forest']['cost'] == 0
    assert TERRAIN_ACTIONS['clear_forest']['yield'] == 1


def test_burn_forest_cost():
    assert TERRAIN_ACTIONS['burn_forest']['cost'] == 3


def test_grow_forest_cost():
    assert TERRAIN_ACTIONS['grow_forest']['cost'] == 5


def test_map_shapes():
    assert all(isinstance(s, int) for s in MAP_SHAPES)
    assert 11 in MAP_SHAPES


def test_harvest_animal():
    h = HARVEST_ACTIONS['animal']
    assert h['cost'] == 2
    assert h['population'] == 1
    assert h['tech'] == 'hunting'


def test_harvest_fruit():
    h = HARVEST_ACTIONS['fruit']
    assert h['cost'] == 2
    assert h['population'] == 1
    assert h['tech'] == 'organization'
