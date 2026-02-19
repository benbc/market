from solver import ELIGIBLE, terrain_accepts

def test_field_accepts_sawmill():
    assert 'sawmill' in ELIGIBLE['field']

def test_field_accepts_windmill():
    assert 'windmill' in ELIGIBLE['field']

def test_field_accepts_forge():
    assert 'forge' in ELIGIBLE['field']

def test_field_accepts_market():
    assert 'market' in ELIGIBLE['field']

def test_field_does_not_accept_farm():
    assert 'farm' not in ELIGIBLE['field']

def test_crop_accepts_farm():
    assert 'farm' in ELIGIBLE['field+crop']

def test_crop_accepts_all_field_buildings():
    for b in ('sawmill', 'windmill', 'forge', 'market'):
        assert b in ELIGIBLE['field+crop']

def test_forest_accepts_lumber_hut():
    assert 'lumber_hut' in ELIGIBLE['forest']

def test_forest_accepts_forge():
    assert 'forge' in ELIGIBLE['forest']

def test_forest_does_not_accept_sawmill():
    assert 'sawmill' not in ELIGIBLE['forest']

def test_metal_accepts_mine():
    assert 'mine' in ELIGIBLE['mountain+metal']

def test_metal_does_not_accept_market():
    assert 'market' not in ELIGIBLE['mountain+metal']

def test_terrain_accepts():
    assert terrain_accepts('field', 'sawmill')
    assert not terrain_accepts('forest', 'market')
