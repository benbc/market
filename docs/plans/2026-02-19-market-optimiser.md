# Market Optimiser Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a browser + Python tool that accepts a painted terrain grid with city positions and returns optimal Sawmill/Windmill/Forge/Market placements to maximise total Market star income in the ideal end state.

**Architecture:** Vanilla JS frontend for grid painting and city placement; Flask backend with a single POST `/optimize` endpoint; pure-Python solver using coordinate descent over per-city placement combinations.

**Tech Stack:** Python 3, Flask, pytest; vanilla HTML/CSS/JS (no frameworks)

---

### Task 1: Project setup

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `tests/__init__.py`

**Step 1: Create `requirements.txt`**

```
flask
pytest
```

**Step 2: Create `pytest.ini`**

```ini
[pytest]
testpaths = tests
```

**Step 3: Create `tests/__init__.py`**

Empty file.

**Step 4: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: installs without errors.

**Step 5: Verify pytest runs**

```bash
pytest
```

Expected: `no tests ran` (exit 0).

**Step 6: Commit**

```bash
git init
git add .
git commit -m "chore: project setup"
```

---

### Task 2: Terrain constants and eligible buildings

**Files:**
- Create: `solver.py`
- Create: `tests/test_solver.py`

**Step 1: Write failing tests**

```python
# tests/test_solver.py
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
```

**Step 2: Run to verify failure**

```bash
pytest tests/test_solver.py -v
```

Expected: ImportError (solver.py does not exist).

**Step 3: Write minimal implementation**

```python
# solver.py

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
```

**Step 4: Run tests**

```bash
pytest tests/test_solver.py -v
```

Expected: all pass.

**Step 5: Commit**

```bash
git add solver.py tests/test_solver.py
git commit -m "feat: terrain constants and eligible buildings"
```

---

### Task 3: Adjacency primitive

**Files:**
- Modify: `solver.py`
- Modify: `tests/test_solver.py`

**Step 1: Write failing tests**

```python
# add to tests/test_solver.py
from solver import is_adjacent

def test_adjacent_orthogonal():
    assert is_adjacent((0, 0), (0, 1))
    assert is_adjacent((0, 0), (1, 0))

def test_adjacent_diagonal():
    assert is_adjacent((0, 0), (1, 1))
    assert is_adjacent((2, 2), (1, 3))

def test_not_adjacent_same_tile():
    assert not is_adjacent((0, 0), (0, 0))

def test_not_adjacent_two_apart():
    assert not is_adjacent((0, 0), (0, 2))
    assert not is_adjacent((0, 0), (2, 2))
```

**Step 2: Run to verify failure**

```bash
pytest tests/test_solver.py::test_adjacent_orthogonal -v
```

Expected: ImportError.

**Step 3: Implement**

```python
# add to solver.py

def is_adjacent(a: tuple, b: tuple) -> bool:
    """8-directional adjacency (Moore neighbourhood). A tile is not adjacent to itself."""
    dr = abs(a[0] - b[0])
    dc = abs(a[1] - b[1])
    return max(dr, dc) == 1
```

**Step 4: Run tests**

```bash
pytest tests/test_solver.py -v
```

Expected: all pass.

**Step 5: Commit**

```bash
git add solver.py tests/test_solver.py
git commit -m "feat: 8-directional adjacency primitive"
```

---

### Task 4: City territory and tile ownership

**Files:**
- Modify: `solver.py`
- Modify: `tests/test_solver.py`

**Step 1: Write failing tests**

```python
# add to tests/test_solver.py
from solver import city_territory, assign_ownership

def test_territory_3x3():
    tiles = city_territory(row=5, col=5, expanded=False)
    assert len(tiles) == 9
    assert (4, 4) in tiles
    assert (6, 6) in tiles
    assert (3, 5) not in tiles  # outside 3x3

def test_territory_5x5():
    tiles = city_territory(row=5, col=5, expanded=True)
    assert len(tiles) == 25
    assert (3, 3) in tiles
    assert (7, 7) in tiles
    assert (2, 5) not in tiles  # outside 5x5

def test_ownership_single_city():
    cities = [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}]
    tile_positions = [(0, 0), (0, 1), (1, 1)]
    ownership = assign_ownership(tile_positions, cities)
    assert ownership[(0, 0)] == 1
    assert ownership[(0, 1)] == 1
    assert ownership[(1, 1)] == 1

def test_ownership_nearest_city():
    cities = [
        {'id': 1, 'row': 0, 'col': 0, 'expanded': False},
        {'id': 2, 'row': 0, 'col': 6, 'expanded': False},
    ]
    tile_positions = [(0, 2), (0, 4)]
    ownership = assign_ownership(tile_positions, cities)
    assert ownership[(0, 2)] == 1  # closer to city 1
    assert ownership[(0, 4)] == 2  # closer to city 2

def test_ownership_tie_broken_by_order():
    cities = [
        {'id': 1, 'row': 0, 'col': 0, 'expanded': False},
        {'id': 2, 'row': 0, 'col': 2, 'expanded': False},
    ]
    tile_positions = [(0, 1)]  # equidistant
    ownership = assign_ownership(tile_positions, cities)
    assert ownership[(0, 1)] == 1  # first city wins
```

**Step 2: Run to verify failure**

```bash
pytest tests/test_solver.py -k "territory or ownership" -v
```

Expected: ImportError.

**Step 3: Implement**

```python
# add to solver.py

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
```

**Step 4: Run tests**

```bash
pytest tests/test_solver.py -v
```

Expected: all pass.

**Step 5: Commit**

```bash
git add solver.py tests/test_solver.py
git commit -m "feat: city territory and tile ownership"
```

---

### Task 5: Resource building placement

**Files:**
- Modify: `solver.py`
- Modify: `tests/test_solver.py`

Resource buildings fill available terrain tiles after production multipliers and Markets are placed.

**Step 1: Write failing tests**

```python
# add to tests/test_solver.py
from solver import place_resource_buildings

def test_mine_on_metal():
    tiles = {(0, 0): 'mountain+metal', (0, 1): 'field'}
    occupied = {}
    result = place_resource_buildings(tiles, occupied)
    assert result[(0, 0)] == 'mine'

def test_lumber_hut_on_free_forest():
    tiles = {(0, 0): 'forest', (0, 1): 'forest'}
    occupied = {(0, 0): 'forge'}  # forge already there
    result = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result   # forge occupies it
    assert result[(0, 1)] == 'lumber_hut'

def test_farm_on_free_crop():
    tiles = {(0, 0): 'field+crop', (0, 1): 'field+crop'}
    occupied = {(0, 0): 'market'}
    result = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result   # market occupies it
    assert result[(0, 1)] == 'farm'

def test_no_resource_on_plain_field():
    tiles = {(0, 0): 'field'}
    occupied = {}
    result = place_resource_buildings(tiles, occupied)
    assert (0, 0) not in result
```

**Step 2: Run to verify failure**

```bash
pytest tests/test_solver.py -k "resource" -v
```

Expected: ImportError.

**Step 3: Implement**

```python
# add to solver.py

def place_resource_buildings(tiles: dict, occupied: dict) -> dict:
    """
    Given a map of pos→terrain and a dict of already-occupied pos→building,
    return a dict of pos→resource_building for every free eligible tile.
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
```

**Step 4: Run tests**

```bash
pytest tests/test_solver.py -v
```

Expected: all pass.

**Step 5: Commit**

```bash
git add solver.py tests/test_solver.py
git commit -m "feat: resource building placement"
```

---

### Task 6: Multiplier level scoring

**Files:**
- Modify: `solver.py`
- Modify: `tests/test_solver.py`

**Step 1: Write failing tests**

```python
# add to tests/test_solver.py
from solver import multiplier_level

def test_sawmill_level_no_huts():
    placements = {(1, 1): 'sawmill'}
    assert multiplier_level((1, 1), 'sawmill', placements) == 0

def test_sawmill_level_one_hut():
    placements = {(1, 1): 'sawmill', (1, 2): 'lumber_hut'}
    assert multiplier_level((1, 1), 'sawmill', placements) == 1

def test_sawmill_level_three_huts():
    placements = {
        (1, 1): 'sawmill',
        (0, 0): 'lumber_hut',
        (0, 1): 'lumber_hut',
        (0, 2): 'lumber_hut',
    }
    assert multiplier_level((1, 1), 'sawmill', placements) == 3

def test_windmill_level_two_farms():
    placements = {
        (2, 2): 'windmill',
        (1, 1): 'farm',
        (3, 3): 'farm',
    }
    assert multiplier_level((2, 2), 'windmill', placements) == 2

def test_forge_level_one_mine():
    placements = {(0, 0): 'forge', (0, 1): 'mine'}
    assert multiplier_level((0, 0), 'forge', placements) == 2

def test_forge_level_two_mines():
    placements = {(0, 0): 'forge', (0, 1): 'mine', (1, 0): 'mine'}
    assert multiplier_level((0, 0), 'forge', placements) == 4

def test_non_adjacent_hut_not_counted():
    placements = {(0, 0): 'sawmill', (0, 3): 'lumber_hut'}
    assert multiplier_level((0, 0), 'sawmill', placements) == 0
```

**Step 2: Run to verify failure**

```bash
pytest tests/test_solver.py -k "level" -v
```

Expected: ImportError.

**Step 3: Implement**

```python
# add to solver.py

MULTIPLIER_RESOURCE = {
    'sawmill': ('lumber_hut', 1),
    'windmill': ('farm', 1),
    'forge': ('mine', 2),
}

def multiplier_level(pos: tuple, building: str, placements: dict) -> int:
    """
    Compute the level (population output) of a production multiplier.
    placements: dict of pos→building covering all placed buildings.
    """
    resource, weight = MULTIPLIER_RESOURCE[building]
    return sum(
        weight
        for other_pos, other_bldg in placements.items()
        if other_bldg == resource and is_adjacent(pos, other_pos)
    )
```

**Step 4: Run tests**

```bash
pytest tests/test_solver.py -v
```

Expected: all pass.

**Step 5: Commit**

```bash
git add solver.py tests/test_solver.py
git commit -m "feat: multiplier level scoring"
```

---

### Task 7: Market income scoring

**Files:**
- Modify: `solver.py`
- Modify: `tests/test_solver.py`

**Step 1: Write failing tests**

```python
# add to tests/test_solver.py
from solver import market_income

def test_market_no_adjacent_multipliers():
    placements = {(0, 0): 'market'}
    assert market_income((0, 0), placements) == 0

def test_market_adjacent_sawmill_level_2():
    placements = {
        (0, 0): 'market',
        (0, 1): 'sawmill',
        (0, 2): 'lumber_hut',
        (1, 2): 'lumber_hut',
    }
    assert market_income((0, 0), placements) == 2

def test_market_adjacent_forge_and_sawmill():
    placements = {
        (5, 5): 'market',
        (5, 6): 'sawmill',
        (5, 7): 'lumber_hut',  # adjacent to sawmill, not market
        (5, 4): 'forge',
        (4, 4): 'mine',         # adjacent to forge, not market
    }
    # sawmill level=1, forge level=2 → total=3
    assert market_income((5, 5), placements) == 3

def test_market_capped_at_8():
    # Arrange a market with total adjacent multiplier levels = 10
    placements = {
        (5, 5): 'market',
        # Three sawmills each at level 3 = 9 (but cap is 8)
        (4, 4): 'sawmill',
        (4, 5): 'sawmill',
        (4, 6): 'sawmill',
    }
    # Add 3 lumber huts adjacent to each sawmill (but not occupying adjacent tiles)
    placements.update({
        (3, 3): 'lumber_hut', (3, 4): 'lumber_hut', (3, 5): 'lumber_hut',  # for (4,4)
        (3, 6): 'lumber_hut',  # shared by (4,5) and (4,6)
        (5, 7): 'lumber_hut',  # for (4,6)
        (4, 7): 'lumber_hut',  # for (4,6)
    })
    # Don't worry about exact value; just verify cap
    income = market_income((5, 5), placements)
    assert income <= 8

def test_market_diagonal_multiplier_counts():
    placements = {
        (0, 0): 'market',
        (1, 1): 'sawmill',   # diagonal
        (1, 2): 'lumber_hut',
    }
    assert market_income((0, 0), placements) == 1
```

**Step 2: Run to verify failure**

```bash
pytest tests/test_solver.py -k "market_income" -v
```

Expected: ImportError.

**Step 3: Implement**

```python
# add to solver.py

MARKET_CAP = 8

def market_income(pos: tuple, placements: dict) -> int:
    """
    Compute a Market's star income given all placed buildings.
    Income = sum of levels of 8-adjacent Sawmills/Windmills/Forges, capped at MARKET_CAP.
    """
    total = 0
    for other_pos, building in placements.items():
        if building in MULTIPLIER_RESOURCE and is_adjacent(pos, other_pos):
            total += multiplier_level(other_pos, building, placements)
    return min(total, MARKET_CAP)
```

**Step 4: Run tests**

```bash
pytest tests/test_solver.py -v
```

Expected: all pass.

**Step 5: Commit**

```bash
git add solver.py tests/test_solver.py
git commit -m "feat: market income scoring"
```

---

### Task 8: Per-city placement enumeration

**Files:**
- Modify: `solver.py`
- Modify: `tests/test_solver.py`

Enumerate all valid (sawmill_pos, windmill_pos, forge_pos, market_pos) combinations
for a city. Any of the four may be `None` (not placed). Market must be adjacent to
at least one non-None multiplier.

**Step 1: Write failing tests**

```python
# add to tests/test_solver.py
from solver import city_placements

def _simple_tiles(positions, terrain='field+crop'):
    return {pos: terrain for pos in positions}

def test_single_tile_no_valid_market_alone():
    # One field tile: can place Sawmill or Market but Market needs adjacent multiplier
    tiles = _simple_tiles([(0, 0)])
    combos = city_placements(tiles, city_territory_positions={(0, 0)})
    # Market alone at (0,0) with no adjacent multiplier is invalid
    # But sawmill at (0,0) with no market is valid
    market_combos = [c for c in combos if c['market'] is not None]
    # No valid market combos since there's no adjacent multiplier
    assert all(c['market'] is None for c in combos)

def test_two_adjacent_tiles_market_next_to_sawmill():
    tiles = {(0, 0): 'field', (0, 1): 'field'}
    territory = {(0, 0), (0, 1)}
    combos = city_placements(tiles, city_territory_positions=territory)
    # Should include: sawmill@(0,0) + market@(0,1) and vice versa
    valid = [c for c in combos if c['market'] is not None and c['sawmill'] is not None]
    assert len(valid) >= 2

def test_no_duplicate_tile_usage():
    tiles = {(0, 0): 'field', (0, 1): 'field'}
    territory = {(0, 0), (0, 1)}
    combos = city_placements(tiles, city_territory_positions=territory)
    for c in combos:
        positions = [v for v in c.values() if v is not None]
        assert len(positions) == len(set(positions)), f"Duplicate tile in {c}"

def test_forge_on_forest():
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    territory = {(0, 0), (0, 1)}
    combos = city_placements(tiles, city_territory_positions=territory)
    forge_on_forest = [c for c in combos if c['forge'] == (0, 0)]
    assert len(forge_on_forest) > 0

def test_sawmill_not_on_forest():
    tiles = {(0, 0): 'forest'}
    territory = {(0, 0)}
    combos = city_placements(tiles, city_territory_positions=territory)
    assert all(c['sawmill'] != (0, 0) for c in combos)
```

**Step 2: Run to verify failure**

```bash
pytest tests/test_solver.py -k "city_placements" -v
```

Expected: ImportError.

**Step 3: Implement**

```python
# add to solver.py
from itertools import product as iproduct

MULTIPLIERS = ('sawmill', 'windmill', 'forge')

def city_placements(tiles: dict, city_territory_positions: set) -> list:
    """
    Enumerate all valid (sawmill, windmill, forge, market) tile assignments for one city.
    tiles: dict of pos→terrain for all tiles in the game (not just this city).
    city_territory_positions: set of positions belonging to this city.
    Returns list of dicts with keys sawmill, windmill, forge, market (values: pos or None).
    """
    # Candidate positions for each role (must be in this city's territory)
    def candidates(building):
        return [None] + [
            pos for pos in city_territory_positions
            if pos in tiles and terrain_accepts(tiles[pos], building)
        ]

    saw_cands = candidates('sawmill')
    win_cands = candidates('windmill')
    for_cands = candidates('forge')
    mkt_cands = candidates('market')

    results = []
    for saw, win, frg, mkt in iproduct(saw_cands, win_cands, for_cands, mkt_cands):
        # No two roles on the same tile
        placed = [p for p in (saw, win, frg, mkt) if p is not None]
        if len(placed) != len(set(placed)):
            continue
        # Market must be adjacent to at least one multiplier (if market is placed)
        if mkt is not None:
            multiplier_positions = [p for p in (saw, win, frg) if p is not None]
            if not any(is_adjacent(mkt, mp) for mp in multiplier_positions):
                continue
        results.append({'sawmill': saw, 'windmill': win, 'forge': frg, 'market': mkt})
    return results
```

**Step 4: Run tests**

```bash
pytest tests/test_solver.py -v
```

Expected: all pass.

**Step 5: Commit**

```bash
git add solver.py tests/test_solver.py
git commit -m "feat: per-city placement enumeration"
```

---

### Task 9: Coordinate descent solver

**Files:**
- Modify: `solver.py`
- Modify: `tests/test_solver.py`

**Step 1: Write failing tests**

```python
# add to tests/test_solver.py
from solver import optimise

def _make_input(tile_list, city_list):
    return {
        'tiles': [{'row': r, 'col': c, 'terrain': t} for (r, c), t in tile_list],
        'cities': city_list,
    }

def test_single_city_simple():
    """
    3x3 city at (1,1). Fields and one forest with metal.
    Expect a Market and at least one multiplier placed, with income > 0.
    """
    tile_list = [
        ((0, 0), 'forest'),
        ((0, 1), 'field'),
        ((0, 2), 'mountain+metal'),
        ((1, 0), 'field'),
        ((1, 1), 'field'),   # city centre
        ((1, 2), 'field+crop'),
        ((2, 0), 'field+crop'),
        ((2, 1), 'field'),
        ((2, 2), 'forest'),
    ]
    cities = [{'id': 1, 'row': 1, 'col': 1, 'expanded': False}]
    result = optimise(_make_input(tile_list, cities))
    assert result['total_income'] > 0
    assert any(m['city_id'] == 1 for m in result['markets'])

def test_two_adjacent_cities_cross_city_interaction():
    """
    Two 3x3 cities side by side. A Lumber Hut in city 1 should be able to
    boost a Sawmill in city 2.
    """
    # City 1 at (1,1), city 2 at (1,5) — territories don't overlap
    tile_list = (
        [((r, c), 'forest') for r in range(3) for c in range(3)]
        + [((r, c), 'field') for r in range(3) for c in range(3, 8)]
    )
    cities = [
        {'id': 1, 'row': 1, 'col': 1, 'expanded': False},
        {'id': 2, 'row': 1, 'col': 5, 'expanded': False},
    ]
    result = optimise(_make_input(tile_list, cities))
    assert result['total_income'] >= 0  # just verify it runs without error

def test_result_structure():
    tile_list = [((0, 0), 'field'), ((0, 1), 'field')]
    cities = [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}]
    result = optimise(_make_input(tile_list, cities))
    assert 'placements' in result
    assert 'markets' in result
    assert 'total_income' in result
    for p in result['placements']:
        assert 'row' in p and 'col' in p and 'building' in p
    for m in result['markets']:
        assert 'row' in m and 'col' in m and 'income' in m and 'city_id' in m
```

**Step 2: Run to verify failure**

```bash
pytest tests/test_solver.py -k "optimise or single_city or two_adjacent or result_structure" -v
```

Expected: ImportError.

**Step 3: Implement**

```python
# add to solver.py
import random

def _build_full_placements(city_assignments: dict, tiles: dict) -> dict:
    """
    Given per-city production/market assignments (pos→building),
    fill remaining eligible tiles with resource buildings.
    Returns a single dict of pos→building covering everything.
    """
    occupied = dict(city_assignments)
    resources = place_resource_buildings(tiles, occupied)
    return {**occupied, **resources}

def _score(city_assignments: dict, tiles: dict) -> int:
    """Total Market income given current city assignments."""
    placements = _build_full_placements(city_assignments, tiles)
    return sum(
        market_income(pos, placements)
        for pos, bldg in placements.items()
        if bldg == 'market'
    )

def _random_assignment(combos: list) -> dict:
    return random.choice(combos) if combos else {}

def _optimise_once(cities_combos: list, tiles: dict) -> tuple:
    """
    One run of coordinate descent from a random start.
    cities_combos: list of (city_id, territory_positions, combos_list)
    Returns (score, city_assignments dict pos→building)
    """
    # Start: random combo per city
    current = {}  # pos → building
    city_selected = []
    for city_id, territory, combos in cities_combos:
        chosen = _random_assignment(combos)
        city_selected.append((city_id, territory, combos, chosen))
        for role, pos in chosen.items():
            if pos is not None:
                current[pos] = role

    improved = True
    while improved:
        improved = False
        for i, (city_id, territory, combos, chosen) in enumerate(city_selected):
            # Remove this city's current assignments from global placements
            partial = {p: b for p, b in current.items() if p not in territory or b not in ('sawmill', 'windmill', 'forge', 'market')}

            best_score = -1
            best_combo = chosen
            for combo in combos:
                candidate = dict(partial)
                for role, pos in combo.items():
                    if pos is not None:
                        candidate[pos] = role
                s = _score(candidate, tiles)
                if s > best_score:
                    best_score = s
                    best_combo = combo

            new_assignments = dict(partial)
            for role, pos in best_combo.items():
                if pos is not None:
                    new_assignments[pos] = role

            if best_combo != chosen:
                improved = True
            city_selected[i] = (city_id, territory, combos, best_combo)
            current = new_assignments

    return _score(current, tiles), current, city_selected

def optimise(data: dict, restarts: int = 5) -> dict:
    """
    Main solver entry point.
    data: {'tiles': [...], 'cities': [...]}
    Returns {'placements': [...], 'markets': [...], 'total_income': int}
    """
    tiles = {(t['row'], t['col']): t['terrain'] for t in data['tiles']}
    cities = data['cities']
    all_positions = list(tiles.keys())
    ownership = assign_ownership(all_positions, cities)

    # Build per-city territory sets and enumerate combos
    cities_combos = []
    for city in cities:
        territory = city_territory(city['row'], city['col'], city['expanded'])
        territory_in_game = {p for p in territory if p in tiles and ownership.get(p) == city['id']}
        combos = city_placements(tiles, territory_in_game)
        if not combos:
            combos = [{'sawmill': None, 'windmill': None, 'forge': None, 'market': None}]
        cities_combos.append((city['id'], territory_in_game, combos))

    best_score = -1
    best_placements = {}

    for _ in range(restarts):
        score, placements, _ = _optimise_once(cities_combos, tiles)
        if score > best_score:
            best_score = score
            best_placements = placements

    full = _build_full_placements(best_placements, tiles)

    placement_list = [
        {'row': pos[0], 'col': pos[1], 'building': bldg}
        for pos, bldg in full.items()
    ]
    markets_list = []
    for pos, bldg in full.items():
        if bldg == 'market':
            city_id = ownership.get(pos)
            markets_list.append({
                'row': pos[0], 'col': pos[1],
                'city_id': city_id,
                'income': market_income(pos, full),
            })

    return {
        'placements': placement_list,
        'markets': markets_list,
        'total_income': best_score,
    }
```

**Step 4: Run tests**

```bash
pytest tests/test_solver.py -v
```

Expected: all pass.

**Step 5: Commit**

```bash
git add solver.py tests/test_solver.py
git commit -m "feat: coordinate descent solver"
```

---

### Task 10: Flask server

**Files:**
- Create: `server.py`
- Create: `tests/test_server.py`

**Step 1: Write failing tests**

```python
# tests/test_server.py
import json
import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_optimize_returns_200(client):
    payload = {
        'tiles': [
            {'row': 0, 'col': 0, 'terrain': 'field'},
            {'row': 0, 'col': 1, 'terrain': 'field'},
        ],
        'cities': [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}],
    }
    resp = client.post('/optimize', json=payload)
    assert resp.status_code == 200

def test_optimize_returns_expected_keys(client):
    payload = {
        'tiles': [{'row': 0, 'col': 0, 'terrain': 'field'}],
        'cities': [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}],
    }
    data = client.post('/optimize', json=payload).get_json()
    assert 'placements' in data
    assert 'markets' in data
    assert 'total_income' in data

def test_optimize_bad_request(client):
    resp = client.post('/optimize', data='not json', content_type='text/plain')
    assert resp.status_code == 400
```

**Step 2: Run to verify failure**

```bash
pytest tests/test_server.py -v
```

Expected: ImportError.

**Step 3: Implement**

```python
# server.py
from flask import Flask, request, jsonify
from solver import optimise

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.post('/optimize')
def optimize():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    result = optimise(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

**Step 4: Run tests**

```bash
pytest tests/test_server.py -v
```

Expected: all pass.

**Step 5: Commit**

```bash
git add server.py tests/test_server.py
git commit -m "feat: Flask server with /optimize endpoint"
```

---

### Task 11: HTML grid and CSS

**Files:**
- Create: `static/index.html`
- Create: `static/style.css`

No tests for UI. Verify visually by opening in browser.

**Step 1: Create `static/style.css`**

```css
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: monospace;
  display: flex;
  height: 100vh;
  overflow: hidden;
}

#sidebar {
  width: 200px;
  padding: 12px;
  border-right: 1px solid #ccc;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
}

#sidebar h2 { font-size: 14px; margin-bottom: 4px; }

.tool-btn {
  display: block;
  width: 100%;
  padding: 6px;
  text-align: left;
  cursor: pointer;
  border: 1px solid #ccc;
  background: #f5f5f5;
  font-family: monospace;
  font-size: 12px;
}

.tool-btn.active { background: #333; color: #fff; border-color: #333; }

#main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

#toolbar {
  padding: 8px 12px;
  border-bottom: 1px solid #ccc;
  display: flex;
  gap: 8px;
  align-items: center;
}

#toolbar button {
  padding: 4px 12px;
  cursor: pointer;
  font-family: monospace;
}

#grid-container {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

#grid {
  display: inline-grid;
  gap: 1px;
  background: #ccc;
}

.tile {
  width: 36px;
  height: 36px;
  background: #eee;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  position: relative;
  user-select: none;
}

.tile:hover { filter: brightness(0.85); }

.tile.terrain-field        { background: #d4c483; }
.tile.terrain-field-crop   { background: #c8b400; }
.tile.terrain-forest       { background: #4a7c59; }
.tile.terrain-mountain     { background: #888; }
.tile.terrain-metal        { background: #666; }
.tile.terrain-water        { background: #6ab0de; }
.tile.terrain-ocean        { background: #2a6099; }

.tile .city-marker {
  position: absolute;
  top: 1px; left: 1px;
  font-size: 10px;
  background: rgba(255,255,255,0.8);
  border-radius: 2px;
  padding: 0 2px;
  line-height: 1.2;
}

.tile .result-icon {
  position: absolute;
  bottom: 1px; right: 1px;
  font-size: 10px;
  background: rgba(255,255,0,0.8);
  border-radius: 2px;
  padding: 0 2px;
}

#summary {
  padding: 8px 12px;
  border-top: 1px solid #ccc;
  font-size: 12px;
  min-height: 40px;
}
```

**Step 2: Create `static/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Polytopia Market Optimiser</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div id="sidebar">
    <h2>Terrain</h2>
    <button class="tool-btn" data-tool="field">Field</button>
    <button class="tool-btn" data-tool="field+crop">Field+Crop</button>
    <button class="tool-btn" data-tool="forest">Forest</button>
    <button class="tool-btn" data-tool="mountain">Mountain</button>
    <button class="tool-btn" data-tool="mountain+metal">Mountain+Metal</button>
    <button class="tool-btn" data-tool="water">Water</button>
    <button class="tool-btn" data-tool="ocean">Ocean</button>
    <button class="tool-btn" data-tool="empty">Erase</button>
    <hr>
    <h2>Cities</h2>
    <button class="tool-btn" data-tool="city">Place City</button>
    <hr>
    <h2>Actions</h2>
    <button id="btn-optimise">Optimise</button>
    <button id="btn-clear-result">Clear Result</button>
    <button id="btn-save">Save JSON</button>
    <button id="btn-load">Load JSON</button>
    <input type="file" id="file-input" accept=".json" style="display:none">
    <hr>
    <div id="grid-size">
      <label>Rows: <input type="number" id="rows-input" value="10" min="3" max="40"></label>
      <label>Cols: <input type="number" id="cols-input" value="10" min="3" max="40"></label>
      <button id="btn-resize">Resize</button>
    </div>
  </div>

  <div id="main">
    <div id="toolbar">
      <span>Active tool: <strong id="active-tool-label">none</strong></span>
      <span id="hover-info"></span>
    </div>
    <div id="grid-container">
      <div id="grid"></div>
    </div>
    <div id="summary">No optimisation run yet.</div>
  </div>

  <script src="app.js"></script>
</body>
</html>
```

**Step 3: Verify visually**

```bash
python server.py
```

Open `http://localhost:5000` — should show sidebar and empty grid area.

**Step 4: Commit**

```bash
git add static/
git commit -m "feat: HTML structure and CSS"
```

---

### Task 12: Grid state and terrain painting (JS)

**Files:**
- Create: `static/app.js`

**Step 1: Create `static/app.js`**

```javascript
// static/app.js

const TERRAIN_EMOJI = {
  'field':          '🌾',
  'field+crop':     '🌽',
  'forest':         '🌲',
  'mountain':       '⛰️',
  'mountain+metal': '⛏️',
  'water':          '🌊',
  'ocean':          '🌐',
  'empty':          '',
};

const TERRAIN_CLASS = {
  'field':          'terrain-field',
  'field+crop':     'terrain-field-crop',
  'forest':         'terrain-forest',
  'mountain':       'terrain-mountain',
  'mountain+metal': 'terrain-metal',
  'water':          'terrain-water',
  'ocean':          'terrain-ocean',
  'empty':          '',
};

const BUILDING_ABBR = {
  sawmill:     'SAW',
  windmill:    'WIN',
  forge:       'FRG',
  market:      'MKT',
  lumber_hut:  'LH',
  farm:        'FM',
  mine:        'MN',
};

let state = {
  rows: 10,
  cols: 10,
  tiles: {},     // "r,c" → terrain string
  cities: [],    // {id, row, col, expanded}
};

let activeTool = null;
let isMouseDown = false;
let resultPlacements = {};  // "r,c" → building string
let resultMarkets = [];     // [{row, col, city_id, income}]
let nextCityId = 1;

// --- Grid rendering ---

function renderGrid() {
  const grid = document.getElementById('grid');
  grid.style.gridTemplateColumns = `repeat(${state.cols}, 36px)`;
  grid.innerHTML = '';

  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const key = `${r},${c}`;
      const terrain = state.tiles[key] || 'empty';
      const div = document.createElement('div');
      div.className = `tile ${TERRAIN_CLASS[terrain] || ''}`;
      div.dataset.r = r;
      div.dataset.c = c;

      // Terrain emoji
      if (terrain !== 'empty') {
        div.textContent = TERRAIN_EMOJI[terrain] || '';
      }

      // City marker
      const city = state.cities.find(ct => ct.row === r && ct.col === c);
      if (city) {
        const marker = document.createElement('span');
        marker.className = 'city-marker';
        marker.textContent = `C${city.id}${city.expanded ? '+' : ''}`;
        marker.title = 'Right-click to toggle expansion';
        div.appendChild(marker);
      }

      // Result icon
      const bldg = resultPlacements[key];
      if (bldg) {
        const icon = document.createElement('span');
        icon.className = 'result-icon';
        icon.textContent = BUILDING_ABBR[bldg] || bldg;
        div.appendChild(icon);
      }

      div.addEventListener('mousedown', onTileMouseDown);
      div.addEventListener('mouseenter', onTileMouseEnter);
      div.addEventListener('contextmenu', onTileRightClick);
      grid.appendChild(div);
    }
  }
}

// --- Tile interaction ---

function applyTool(r, c) {
  const key = `${r},${c}`;
  if (activeTool === 'city') {
    const existingIdx = state.cities.findIndex(ct => ct.row === r && ct.col === c);
    if (existingIdx >= 0) {
      state.cities.splice(existingIdx, 1);
    } else {
      state.cities.push({ id: nextCityId++, row: r, col: c, expanded: false });
    }
  } else if (activeTool === 'empty') {
    delete state.tiles[key];
  } else if (activeTool) {
    state.tiles[key] = activeTool;
  }
  renderGrid();
}

function onTileMouseDown(e) {
  if (e.button !== 0) return;
  isMouseDown = true;
  const r = +e.currentTarget.dataset.r;
  const c = +e.currentTarget.dataset.c;
  applyTool(r, c);
}

function onTileMouseEnter(e) {
  if (!isMouseDown) return;
  if (activeTool === 'city') return;  // don't drag-place cities
  const r = +e.currentTarget.dataset.r;
  const c = +e.currentTarget.dataset.c;
  applyTool(r, c);
  document.getElementById('hover-info').textContent = `(${r}, ${c})`;
}

function onTileRightClick(e) {
  e.preventDefault();
  const r = +e.currentTarget.dataset.r;
  const c = +e.currentTarget.dataset.c;
  const city = state.cities.find(ct => ct.row === r && ct.col === c);
  if (city) {
    city.expanded = !city.expanded;
    renderGrid();
  }
}

document.addEventListener('mouseup', () => { isMouseDown = false; });

// --- Toolbar ---

document.querySelectorAll('.tool-btn[data-tool]').forEach(btn => {
  btn.addEventListener('click', () => {
    activeTool = btn.dataset.tool;
    document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('active-tool-label').textContent = activeTool;
  });
});

// --- Optimise ---

document.getElementById('btn-optimise').addEventListener('click', async () => {
  const tilesArr = Object.entries(state.tiles).map(([key, terrain]) => {
    const [r, c] = key.split(',').map(Number);
    return { row: r, col: c, terrain };
  });
  const payload = { tiles: tilesArr, cities: state.cities };

  const resp = await fetch('/optimize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const result = await resp.json();

  resultPlacements = {};
  for (const p of result.placements) {
    resultPlacements[`${p.row},${p.col}`] = p.building;
  }
  resultMarkets = result.markets;

  const summary = result.markets
    .map(m => `City ${m.city_id}: ${m.income}★/turn`)
    .join(' | ');
  document.getElementById('summary').textContent =
    `Total: ${result.total_income}★/turn  |  ${summary}`;

  renderGrid();
});

// --- Clear result ---

document.getElementById('btn-clear-result').addEventListener('click', () => {
  resultPlacements = {};
  resultMarkets = [];
  document.getElementById('summary').textContent = 'No optimisation run yet.';
  renderGrid();
});

// --- Save / Load ---

document.getElementById('btn-save').addEventListener('click', () => {
  const json = JSON.stringify(state, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'polytopia-game.json';
  a.click();
});

document.getElementById('btn-load').addEventListener('click', () => {
  document.getElementById('file-input').click();
});

document.getElementById('file-input').addEventListener('change', e => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    try {
      state = JSON.parse(ev.target.result);
      nextCityId = (state.cities.reduce((m, c) => Math.max(m, c.id), 0)) + 1;
      resultPlacements = {};
      resultMarkets = [];
      renderGrid();
    } catch {
      alert('Invalid JSON file');
    }
  };
  reader.readAsText(file);
});

// --- Resize ---

document.getElementById('btn-resize').addEventListener('click', () => {
  state.rows = +document.getElementById('rows-input').value;
  state.cols = +document.getElementById('cols-input').value;
  renderGrid();
});

// --- Init ---

renderGrid();
```

**Step 2: Verify visually**

```bash
python server.py
```

Open `http://localhost:5000`. Paint some terrain tiles, place a city, click Optimise, verify result icons appear and summary bar updates.

**Step 3: Commit**

```bash
git add static/app.js
git commit -m "feat: vanilla JS grid editor with terrain painting, city placement, and result rendering"
```

---

### Task 13: End-to-end smoke test

**Files:**
- Modify: `tests/test_server.py`

**Step 1: Write test**

```python
def test_end_to_end_realistic(client):
    """
    A small realistic layout: 3x3 city with fields, a crop, and a forest.
    Expect total_income > 0 and a market placement returned.
    """
    payload = {
        'tiles': [
            {'row': 0, 'col': 0, 'terrain': 'forest'},
            {'row': 0, 'col': 1, 'terrain': 'field'},
            {'row': 0, 'col': 2, 'terrain': 'field+crop'},
            {'row': 1, 'col': 0, 'terrain': 'field'},
            {'row': 1, 'col': 1, 'terrain': 'field'},  # city centre
            {'row': 1, 'col': 2, 'terrain': 'field+crop'},
            {'row': 2, 'col': 0, 'terrain': 'field+crop'},
            {'row': 2, 'col': 1, 'terrain': 'field'},
            {'row': 2, 'col': 2, 'terrain': 'mountain+metal'},
        ],
        'cities': [{'id': 1, 'row': 1, 'col': 1, 'expanded': False}],
    }
    data = client.post('/optimize', json=payload).get_json()
    assert data['total_income'] > 0
    assert len(data['markets']) == 1
    market = data['markets'][0]
    assert 0 <= market['income'] <= 8
```

**Step 2: Run**

```bash
pytest tests/ -v
```

Expected: all pass.

**Step 3: Commit**

```bash
git add tests/test_server.py
git commit -m "test: end-to-end smoke test"
```
