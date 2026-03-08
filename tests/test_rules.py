from rules import (
    TERRAIN_TYPES, RESOURCE_TYPES, valid_resources_for_terrain,
    can_build, BUILDINGS,
    MULTIPLIERS, multiplier_resource, MARKET_CAP, is_multiplier,
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
