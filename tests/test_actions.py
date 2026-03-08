from actions import make_action


def test_build_action():
    a = make_action('build', (3, 4), 'sawmill')
    assert a == ('build', (3, 4), 'sawmill')


def test_clear_forest_action():
    a = make_action('clear_forest', (1, 2))
    assert a == ('clear_forest', (1, 2))


def test_found_city_action():
    a = make_action('found_city', (5, 5))
    assert a == ('found_city', (5, 5))


def test_expand_borders_action():
    a = make_action('expand_borders', 1)
    assert a == ('expand_borders', 1)


def test_burn_forest_action():
    a = make_action('burn_forest', (2, 3))
    assert a == ('burn_forest', (2, 3))


def test_grow_forest_action():
    a = make_action('grow_forest', (2, 3))
    assert a == ('grow_forest', (2, 3))


def test_harvest_action():
    a = make_action('harvest', (4, 5))
    assert a == ('harvest', (4, 5))
