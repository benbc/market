from rules import TERRAIN_TYPES, RESOURCE_TYPES, valid_resources_for_terrain


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
