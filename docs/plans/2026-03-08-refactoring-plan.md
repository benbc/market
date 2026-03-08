# Refactoring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rewrite the market optimizer with clean abstractions: map state, rules, actions, economics, move generation, and optimizer — as described in `docs/plans/2026-03-08-refactoring-design.md`.

**Architecture:** Fresh implementation on a new branch. Six backend modules (`map_state`, `rules`, `actions`, `economics`, `moves`, `optimizer`) built bottom-up in dependency order, each with comprehensive tests. Thin Flask server updated last. Frontend updated minimally to work with the new backend.

**Tech Stack:** Python 3.13, Flask, pytest, uv

**Reference:** The existing `solver.py` contains the old implementation. The game rules are documented in `polytopia_rules.md`. The design rationale is in `docs/plans/2026-03-08-refactoring-design.md`.

---

## Preliminaries

### Task 0: Set up branch and module structure

**Step 1: Create branch**

```bash
git checkout -b refactor/clean-abstractions
```

**Step 2: Create empty module files and test files**

Create these empty files:

- `map_state.py`
- `rules.py`
- `actions.py`
- `economics.py`
- `moves.py`
- `optimizer.py`
- `tests/test_map_state.py`
- `tests/test_rules.py`
- `tests/test_actions.py`
- `tests/test_economics.py`
- `tests/test_moves.py`
- `tests/test_optimizer.py`

**Step 3: Commit**

```bash
git add map_state.py rules.py actions.py economics.py moves.py optimizer.py tests/test_map_state.py tests/test_rules.py tests/test_actions.py tests/test_economics.py tests/test_moves.py tests/test_optimizer.py
git commit -m "Add empty module files for refactoring"
```

---

## Phase 1: Map State

The foundational data structure. All other modules depend on this.

### Task 1: MapState basics — terrain layer

`MapState` is a data class with layered tile data. Start with terrain only.

**Files:**
- Create: `map_state.py`
- Test: `tests/test_map_state.py`

**Step 1: Write failing tests**

```python
# tests/test_map_state.py
from map_state import MapState

def test_empty_map():
    m = MapState()
    assert m.terrain_at((0, 0)) is None

def test_set_and_get_terrain():
    m = MapState(terrain={
        (0, 0): 'land',
        (1, 0): 'mountain',
    })
    assert m.terrain_at((0, 0)) == 'land'
    assert m.terrain_at((1, 0)) == 'mountain'
    assert m.terrain_at((2, 0)) is None

def test_defined_positions():
    m = MapState(terrain={
        (0, 0): 'land',
        (1, 1): 'water',
    })
    assert m.defined_positions() == {(0, 0), (1, 1)}

def test_undefined_positions_excluded():
    m = MapState(terrain={(0, 0): 'land'})
    assert (1, 1) not in m.defined_positions()
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_map_state.py -v`
Expected: FAIL — `cannot import name 'MapState'`

**Step 3: Implement MapState with terrain**

```python
# map_state.py
from dataclasses import dataclass, field

@dataclass(frozen=True)
class MapState:
    terrain: dict = field(default_factory=dict)

    def terrain_at(self, pos):
        return self.terrain.get(pos)

    def defined_positions(self):
        return set(self.terrain.keys())
```

Note: `MapState` is frozen (immutable). Actions will produce new instances.

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_map_state.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add map_state.py tests/test_map_state.py
git commit -m "Add MapState with terrain layer"
```

### Task 2: MapState — resources, buildings, cities layers

Add the remaining layers: resources, buildings, cities, villages, monuments, lighthouses.

**Files:**
- Modify: `map_state.py`
- Test: `tests/test_map_state.py`

**Step 1: Write failing tests**

```python
def test_resource_at():
    m = MapState(
        terrain={(0, 0): 'land'},
        resources={(0, 0): 'forest'},
    )
    assert m.resource_at((0, 0)) == 'forest'
    assert m.resource_at((1, 0)) is None

def test_building_at():
    m = MapState(
        terrain={(0, 0): 'land'},
        buildings={(0, 0): 'sawmill'},
    )
    assert m.building_at((0, 0)) == 'sawmill'
    assert m.building_at((1, 0)) is None

def test_cities():
    cities = [{'id': 1, 'row': 2, 'col': 3, 'population': 1, 'border_level': 1}]
    m = MapState(terrain={(2, 3): 'land'}, cities=tuple(cities))
    assert len(m.cities) == 1
    assert m.cities[0]['id'] == 1

def test_villages():
    m = MapState(
        terrain={(5, 5): 'land'},
        villages=frozenset({(5, 5)}),
    )
    assert (5, 5) in m.villages

def test_occupied_positions():
    m = MapState(
        terrain={(0, 0): 'land', (1, 1): 'land', (2, 2): 'land'},
        buildings={(0, 0): 'sawmill'},
        monuments=frozenset({(1, 1)}),
        lighthouses=frozenset({(2, 2)}),
    )
    occupied = m.occupied_positions()
    assert (0, 0) in occupied  # building
    assert (1, 1) in occupied  # monument
    assert (2, 2) in occupied  # lighthouse
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_map_state.py -v`
Expected: FAIL

**Step 3: Add remaining layers to MapState**

```python
@dataclass(frozen=True)
class MapState:
    terrain: dict = field(default_factory=dict)
    resources: dict = field(default_factory=dict)
    buildings: dict = field(default_factory=dict)
    cities: tuple = ()
    villages: frozenset = field(default_factory=frozenset)
    monuments: frozenset = field(default_factory=frozenset)
    lighthouses: frozenset = field(default_factory=frozenset)

    def terrain_at(self, pos):
        return self.terrain.get(pos)

    def resource_at(self, pos):
        return self.resources.get(pos)

    def building_at(self, pos):
        return self.buildings.get(pos)

    def defined_positions(self):
        return set(self.terrain.keys())

    def occupied_positions(self):
        return set(self.buildings.keys()) | self.monuments | self.lighthouses
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_map_state.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add map_state.py tests/test_map_state.py
git commit -m "Add resources, buildings, cities, villages, monuments, lighthouses to MapState"
```

### Task 3: MapState — territory ownership

Territory ownership determines which tiles belong to which city. This depends on city positions, border levels, and the order of city founding/expansion events. Port the logic from `solver.py:assign_ownership` but adapted to work with `MapState`.

**Files:**
- Modify: `map_state.py`
- Test: `tests/test_map_state.py`

**Step 1: Write failing tests**

```python
def test_city_territory_base():
    """A city with border_level=1 owns a 3x3 area."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(5) for c in range(5)},
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 1, 'border_level': 1},),
    )
    ownership = m.territory_ownership()
    # 3x3 around (2,2) = 9 tiles
    assert ownership[(2, 2)] == 1
    assert ownership[(1, 1)] == 1
    assert ownership[(3, 3)] == 1
    # (0, 0) is outside the 3x3
    assert (0, 0) not in ownership

def test_city_territory_expanded():
    """A city with border_level=2 owns a 5x5 area."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(5) for c in range(5)},
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 1, 'border_level': 2},),
    )
    ownership = m.territory_ownership()
    assert ownership[(0, 0)] == 1
    assert ownership[(4, 4)] == 1

def test_territory_undefined_tiles_excluded():
    """Tiles without terrain are not owned."""
    m = MapState(
        terrain={(2, 2): 'land'},
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 1, 'border_level': 1},),
    )
    ownership = m.territory_ownership()
    assert (2, 2) in ownership
    assert (1, 1) not in ownership  # undefined terrain

def test_overlapping_territories():
    """First city in the list claims contested tiles."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(5) for c in range(5)},
        cities=(
            {'id': 1, 'row': 1, 'col': 1, 'population': 1, 'border_level': 1},
            {'id': 2, 'row': 3, 'col': 3, 'population': 1, 'border_level': 1},
        ),
    )
    ownership = m.territory_ownership()
    # (2, 2) is in both 3x3 areas; first city claims it
    assert ownership[(2, 2)] == 1

def test_tiles_owned_by():
    m = MapState(
        terrain={(r, c): 'land' for r in range(5) for c in range(5)},
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 1, 'border_level': 1},),
    )
    tiles = m.tiles_owned_by(1)
    assert (2, 2) in tiles
    assert (1, 1) in tiles
    assert len(tiles) == 9
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_map_state.py::test_city_territory_base -v`
Expected: FAIL

**Step 3: Implement territory ownership**

Reference `solver.py:40-71` for the existing logic, but simplify — use border_level directly instead of events. (Events are actions that produce a MapState with a certain border_level; the MapState itself just records the result.)

Add to `MapState`:

```python
def territory_ownership(self):
    """Map each defined tile to the id of its owning city. First city claims contested tiles."""
    ownership = {}
    for city in self.cities:
        radius = city['border_level']
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                pos = (city['row'] + dr, city['col'] + dc)
                if pos in self.terrain and pos not in ownership:
                    ownership[pos] = city['id']
    return ownership

def tiles_owned_by(self, city_id):
    """Return set of positions owned by a specific city."""
    return {pos for pos, cid in self.territory_ownership().items() if cid == city_id}
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_map_state.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add map_state.py tests/test_map_state.py
git commit -m "Add territory ownership to MapState"
```

### Task 4: MapState — adjacency helpers

8-directional adjacency (Moore neighbourhood) is used throughout the codebase. Add as utility functions in `map_state.py`.

**Files:**
- Modify: `map_state.py`
- Test: `tests/test_map_state.py`

**Step 1: Write failing tests**

```python
from map_state import is_adjacent, adjacent_positions

def test_adjacent_orthogonal():
    assert is_adjacent((0, 0), (0, 1))
    assert is_adjacent((0, 0), (1, 0))

def test_adjacent_diagonal():
    assert is_adjacent((0, 0), (1, 1))

def test_not_adjacent():
    assert not is_adjacent((0, 0), (0, 2))
    assert not is_adjacent((0, 0), (2, 2))

def test_not_adjacent_to_self():
    assert not is_adjacent((0, 0), (0, 0))

def test_adjacent_positions():
    adj = adjacent_positions((1, 1))
    assert len(adj) == 8
    assert (0, 0) in adj
    assert (1, 2) in adj
    assert (1, 1) not in adj
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_map_state.py::test_adjacent_orthogonal -v`
Expected: FAIL

**Step 3: Implement adjacency**

```python
def is_adjacent(a, b):
    dr = abs(a[0] - b[0])
    dc = abs(a[1] - b[1])
    return max(dr, dc) == 1

def adjacent_positions(pos):
    r, c = pos
    return frozenset(
        (r + dr, c + dc)
        for dr in (-1, 0, 1)
        for dc in (-1, 0, 1)
        if (dr, dc) != (0, 0)
    )
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_map_state.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add map_state.py tests/test_map_state.py
git commit -m "Add adjacency helpers"
```

---

## Phase 2: Rules

Declarative game data and query functions. No mutation. Reference `polytopia_rules.md` for all game values.

### Task 5: Terrain and resource rules

Define terrain types, resource types, and which resources can appear on which terrain.

**Files:**
- Create: `rules.py`
- Test: `tests/test_rules.py`

**Step 1: Write failing tests**

```python
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
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_rules.py -v`
Expected: FAIL

**Step 3: Implement terrain/resource rules**

```python
# rules.py

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
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_rules.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add rules.py tests/test_rules.py
git commit -m "Add terrain and resource rules"
```

### Task 6: Building rules — eligibility

Define buildings and what terrain/resource combinations they can be built on.

**Files:**
- Modify: `rules.py`
- Test: `tests/test_rules.py`

**Step 1: Write failing tests**

```python
from rules import can_build, BUILDINGS

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
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_rules.py -v`
Expected: FAIL

**Step 3: Implement building eligibility**

```python
# Add to rules.py

# Building definitions: name -> {cost, eligible terrain/resource combos, ...}
# Eligibility is a set of (terrain, resource_or_None) tuples.
# resource=None means "any resource or no resource" is NOT the intent;
# each tuple is a specific combination. None means "no resource".
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
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_rules.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add rules.py tests/test_rules.py
git commit -m "Add building eligibility rules"
```

### Task 7: Building rules — multipliers and market income

Define which buildings are multipliers, their resource dependencies, and the market income cap.

**Files:**
- Modify: `rules.py`
- Test: `tests/test_rules.py`

**Step 1: Write failing tests**

```python
from rules import MULTIPLIERS, multiplier_resource, MARKET_CAP, is_multiplier

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
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_rules.py -v`
Expected: FAIL

**Step 3: Implement multiplier rules**

```python
# Add to rules.py

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
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_rules.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add rules.py tests/test_rules.py
git commit -m "Add multiplier and market rules"
```

### Task 8: Building rules — one multiplier per city constraint

**Files:**
- Modify: `rules.py`
- Test: `tests/test_rules.py`

**Step 1: Write failing tests**

```python
from rules import ONE_PER_CITY

def test_one_per_city():
    assert 'sawmill' in ONE_PER_CITY
    assert 'windmill' in ONE_PER_CITY
    assert 'forge' in ONE_PER_CITY
    assert 'market' not in ONE_PER_CITY
    assert 'farm' not in ONE_PER_CITY
```

**Step 2: Run tests, verify fail, implement, verify pass**

```python
# Add to rules.py
ONE_PER_CITY = frozenset({'sawmill', 'windmill', 'forge'})
```

**Step 3: Commit**

```bash
git add rules.py tests/test_rules.py
git commit -m "Add one-per-city constraint"
```

### Task 9: Tech tree

Define the tech tree: which techs exist, their tier, prerequisites, and what they unlock.

**Files:**
- Modify: `rules.py`
- Test: `tests/test_rules.py`

**Step 1: Write failing tests**

```python
from rules import TECHS, techs_unlocking_building, techs_unlocking_action, available_with_techs

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
    # With no techs, can't build anything special
    available = available_with_techs(frozenset())
    assert 'sawmill' not in available['buildings']
    # With mathematics, can build sawmill
    available = available_with_techs(frozenset({'mathematics'}))
    assert 'sawmill' in available['buildings']
    # With forestry, can clear forest
    available = available_with_techs(frozenset({'forestry'}))
    assert 'clear_forest' in available['actions']
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_rules.py -v`
Expected: FAIL

**Step 3: Implement tech tree**

Reference `polytopia_rules.md` for the full tree. Implement the complete tech tree data and query functions. Include all 25 techs with tier, prerequisite, unlocked buildings, and unlocked actions.

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_rules.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add rules.py tests/test_rules.py
git commit -m "Add tech tree"
```

### Task 10: Terrain modification rules and map shapes

Define costs/yields for terrain modifications (clear forest, burn forest, grow forest) and the valid map shapes.

**Files:**
- Modify: `rules.py`
- Test: `tests/test_rules.py`

**Step 1: Write failing tests**

```python
from rules import TERRAIN_ACTIONS, MAP_SHAPES

def test_clear_forest_yield():
    assert TERRAIN_ACTIONS['clear_forest']['cost'] == 0
    assert TERRAIN_ACTIONS['clear_forest']['yield'] == 1

def test_burn_forest_cost():
    assert TERRAIN_ACTIONS['burn_forest']['cost'] == 3

def test_grow_forest_cost():
    assert TERRAIN_ACTIONS['grow_forest']['cost'] == 5

def test_map_shapes():
    # Polytopia maps are squares of specific sizes
    assert all(isinstance(s, int) for s in MAP_SHAPES)
    assert 11 in MAP_SHAPES  # smallest standard map
```

**Step 2: Run tests, verify fail, implement, verify pass**

Reference `polytopia_rules.md` for costs. Look up standard Polytopia map sizes (11x11, 14x14, 18x18, 22x22, 30x30 are the standard sizes — verify with user during implementation if needed).

**Step 3: Commit**

```bash
git add rules.py tests/test_rules.py
git commit -m "Add terrain action rules and map shapes"
```

### Task 11: Harvest rules

Define the harvest actions for animals and fruit.

**Files:**
- Modify: `rules.py`
- Test: `tests/test_rules.py`

**Step 1: Write failing tests**

```python
from rules import HARVEST_ACTIONS

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
```

**Step 2: Run tests, verify fail, implement, verify pass, commit**

```bash
git add rules.py tests/test_rules.py
git commit -m "Add harvest rules"
```

---

## Phase 3: Actions

Action types, validation, and application. Actions transform `MapState`.

### Task 12: Action representation

Define action types as simple data.

**Files:**
- Create: `actions.py`
- Test: `tests/test_actions.py`

**Step 1: Write failing tests**

```python
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
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_actions.py -v`
Expected: FAIL

**Step 3: Implement make_action**

```python
# actions.py

def make_action(action_type, *args):
    return (action_type, *args)
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_actions.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add actions.py tests/test_actions.py
git commit -m "Add action representation"
```

### Task 13: Action application — build

Apply a build action to a `MapState`, producing a new `MapState`.

**Files:**
- Modify: `actions.py`
- Test: `tests/test_actions.py`

**Step 1: Write failing tests**

```python
from actions import apply_action
from map_state import MapState

def test_apply_build():
    m = MapState(terrain={(3, 4): 'land'})
    action = ('build', (3, 4), 'sawmill')
    m2 = apply_action(m, action)
    assert m2.building_at((3, 4)) == 'sawmill'
    # Original unchanged (immutable)
    assert m.building_at((3, 4)) is None

def test_apply_build_preserves_terrain():
    m = MapState(
        terrain={(0, 0): 'land', (1, 1): 'mountain'},
        buildings={(1, 1): 'mine'},
    )
    action = ('build', (0, 0), 'sawmill')
    m2 = apply_action(m, action)
    assert m2.terrain_at((0, 0)) == 'land'
    assert m2.terrain_at((1, 1)) == 'mountain'
    assert m2.building_at((1, 1)) == 'mine'
    assert m2.building_at((0, 0)) == 'sawmill'
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_actions.py -v`
Expected: FAIL

**Step 3: Implement apply_action for build**

```python
# Add to actions.py
from dataclasses import replace
from map_state import MapState

def apply_action(state, action):
    action_type = action[0]
    if action_type == 'build':
        pos, building = action[1], action[2]
        new_buildings = {**state.buildings, pos: building}
        return replace(state, buildings=new_buildings)
    raise ValueError(f"Unknown action type: {action_type}")
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_actions.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add actions.py tests/test_actions.py
git commit -m "Add build action application"
```

### Task 14: Action application — clear_forest, burn_forest, grow_forest

**Files:**
- Modify: `actions.py`
- Test: `tests/test_actions.py`

**Step 1: Write failing tests**

```python
def test_apply_clear_forest():
    m = MapState(
        terrain={(2, 3): 'land'},
        resources={(2, 3): 'forest'},
    )
    action = ('clear_forest', (2, 3))
    m2 = apply_action(m, action)
    assert m2.resource_at((2, 3)) is None
    assert m2.terrain_at((2, 3)) == 'land'

def test_apply_burn_forest():
    m = MapState(
        terrain={(2, 3): 'land'},
        resources={(2, 3): 'forest'},
    )
    action = ('burn_forest', (2, 3))
    m2 = apply_action(m, action)
    assert m2.resource_at((2, 3)) == 'crop'

def test_apply_grow_forest():
    m = MapState(terrain={(2, 3): 'land'})
    action = ('grow_forest', (2, 3))
    m2 = apply_action(m, action)
    assert m2.resource_at((2, 3)) == 'forest'
```

**Step 2: Run tests, verify fail**

**Step 3: Add cases to apply_action**

```python
elif action_type == 'clear_forest':
    pos = action[1]
    new_resources = {p: r for p, r in state.resources.items() if p != pos}
    return replace(state, resources=new_resources)
elif action_type == 'burn_forest':
    pos = action[1]
    new_resources = {**state.resources, pos: 'crop'}
    return replace(state, resources=new_resources)
elif action_type == 'grow_forest':
    pos = action[1]
    new_resources = {**state.resources, pos: 'forest'}
    return replace(state, resources=new_resources)
```

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add actions.py tests/test_actions.py
git commit -m "Add forest modification actions"
```

### Task 15: Action application — found_city, expand_borders, harvest

**Files:**
- Modify: `actions.py`
- Test: `tests/test_actions.py`

**Step 1: Write failing tests**

```python
def test_apply_found_city():
    m = MapState(
        terrain={(5, 5): 'land'},
        villages=frozenset({(5, 5)}),
    )
    action = ('found_city', (5, 5))
    m2 = apply_action(m, action)
    assert len(m2.cities) == 1
    assert m2.cities[0]['row'] == 5
    assert m2.cities[0]['col'] == 5
    assert m2.cities[0]['border_level'] == 1
    assert (5, 5) not in m2.villages

def test_found_city_assigns_id():
    m = MapState(
        terrain={(5, 5): 'land', (8, 8): 'land'},
        villages=frozenset({(5, 5), (8, 8)}),
    )
    m2 = apply_action(m, ('found_city', (5, 5)))
    m3 = apply_action(m2, ('found_city', (8, 8)))
    assert m3.cities[0]['id'] != m3.cities[1]['id']

def test_apply_expand_borders():
    m = MapState(
        terrain={(r, c): 'land' for r in range(5) for c in range(5)},
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 1, 'border_level': 1},),
    )
    action = ('expand_borders', 1)
    m2 = apply_action(m, action)
    assert m2.cities[0]['border_level'] == 2

def test_apply_harvest():
    m = MapState(
        terrain={(4, 5): 'land'},
        resources={(4, 5): 'animal'},
    )
    action = ('harvest', (4, 5))
    m2 = apply_action(m, action)
    assert m2.resource_at((4, 5)) is None
```

**Step 2: Run tests, verify fail**

**Step 3: Implement**

For `found_city`: remove village, add city with auto-generated id, border_level=1, population=1.
For `expand_borders`: find city by id, increment border_level.
For `harvest`: remove resource.

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add actions.py tests/test_actions.py
git commit -m "Add found_city, expand_borders, and harvest actions"
```

### Task 16: Action validation

Validate that an action is legal given the current state and rules. This is distinct from application — validation checks preconditions without changing state.

**Files:**
- Modify: `actions.py`
- Test: `tests/test_actions.py`

**Step 1: Write failing tests**

```python
from actions import validate_action

def test_validate_build_on_eligible_terrain():
    m = MapState(terrain={(0, 0): 'land'})
    assert validate_action(m, ('build', (0, 0), 'sawmill'), techs=frozenset({'mathematics'})) is None

def test_validate_build_on_ineligible_terrain():
    m = MapState(terrain={(0, 0): 'water'})
    result = validate_action(m, ('build', (0, 0), 'sawmill'), techs=frozenset({'mathematics'}))
    assert result is not None  # returns error string

def test_validate_build_without_tech():
    m = MapState(terrain={(0, 0): 'land'})
    result = validate_action(m, ('build', (0, 0), 'sawmill'), techs=frozenset())
    assert result is not None

def test_validate_build_on_occupied():
    m = MapState(terrain={(0, 0): 'land'}, buildings={(0, 0): 'farm'})
    result = validate_action(m, ('build', (0, 0), 'sawmill'), techs=frozenset({'mathematics'}))
    assert result is not None

def test_validate_build_on_undefined():
    m = MapState()
    result = validate_action(m, ('build', (0, 0), 'sawmill'), techs=frozenset({'mathematics'}))
    assert result is not None

def test_validate_clear_forest_requires_forest():
    m = MapState(terrain={(0, 0): 'land'})
    result = validate_action(m, ('clear_forest', (0, 0)), techs=frozenset({'forestry'}))
    assert result is not None

def test_validate_clear_forest_ok():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'forest'})
    assert validate_action(m, ('clear_forest', (0, 0)), techs=frozenset({'forestry'})) is None

def test_validate_found_city_requires_village():
    m = MapState(terrain={(0, 0): 'land'})
    result = validate_action(m, ('found_city', (0, 0)), techs=frozenset())
    assert result is not None

def test_validate_found_city_ok():
    m = MapState(terrain={(0, 0): 'land'}, villages=frozenset({(0, 0)}))
    assert validate_action(m, ('found_city', (0, 0)), techs=frozenset()) is None

def test_validate_build_one_per_city():
    """Cannot build a second sawmill in the same city."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(3) for c in range(3)},
        buildings={(0, 0): 'sawmill'},
        cities=({'id': 1, 'row': 1, 'col': 1, 'population': 1, 'border_level': 1},),
    )
    result = validate_action(m, ('build', (1, 1), 'sawmill'), techs=frozenset({'mathematics'}))
    assert result is not None

def test_validate_build_must_be_in_territory():
    """Cannot build outside city territory."""
    m = MapState(
        terrain={(0, 0): 'land', (5, 5): 'land'},
        cities=({'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1},),
    )
    result = validate_action(m, ('build', (5, 5), 'sawmill'), techs=frozenset({'mathematics'}))
    assert result is not None
```

**Step 2: Run tests, verify fail**

**Step 3: Implement validate_action**

`validate_action(state, action, techs)` returns `None` if legal, or an error string if not. Uses `rules.can_build`, `rules.techs_unlocking_building`, `rules.ONE_PER_CITY`, etc.

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add actions.py tests/test_actions.py
git commit -m "Add action validation"
```

---

## Phase 4: Economics

Evaluation functions: income (state-based), cost and population (action-sequence-based).

### Task 17: Income calculation

Compute market income from a `MapState`. This is the core economic output.

**Files:**
- Create: `economics.py`
- Test: `tests/test_economics.py`

**Step 1: Write failing tests**

```python
from economics import market_income, total_income, multiplier_level
from map_state import MapState

def test_multiplier_level_sawmill():
    m = MapState(
        terrain={(0, 0): 'land', (0, 1): 'land', (1, 0): 'land'},
        buildings={(0, 0): 'sawmill', (0, 1): 'lumber_hut', (1, 0): 'lumber_hut'},
    )
    assert multiplier_level((0, 0), m) == 2

def test_multiplier_level_forge():
    m = MapState(
        terrain={(0, 0): 'land', (0, 1): 'mountain', (1, 0): 'mountain'},
        buildings={(0, 0): 'forge', (0, 1): 'mine', (1, 0): 'mine'},
    )
    # Forge gives +2 per adjacent mine
    assert multiplier_level((0, 0), m) == 4

def test_market_income_simple():
    m = MapState(
        terrain={(0, 0): 'land', (0, 1): 'land', (1, 0): 'land', (1, 1): 'land'},
        buildings={(0, 0): 'sawmill', (0, 1): 'lumber_hut', (1, 0): 'market'},
    )
    # Sawmill level = 1 (one adjacent lumber hut), market adjacent to sawmill
    assert market_income((1, 0), m) == 1

def test_market_income_capped_at_8():
    # Set up a market adjacent to multipliers with very high levels
    terrain = {(r, c): 'land' for r in range(5) for c in range(5)}
    buildings = {
        (2, 2): 'market',
        (1, 1): 'sawmill',
        (1, 2): 'windmill',
        (2, 1): 'forge',
    }
    # Add many resources to inflate levels
    for r in range(5):
        for c in range(5):
            pos = (r, c)
            if pos not in buildings:
                buildings[pos] = 'lumber_hut'
    m = MapState(terrain=terrain, buildings=buildings)
    assert market_income((2, 2), m) <= 8

def test_total_income():
    m = MapState(
        terrain={(0, 0): 'land', (0, 1): 'land', (1, 0): 'land', (1, 1): 'land'},
        buildings={(0, 0): 'sawmill', (0, 1): 'lumber_hut', (1, 0): 'market'},
    )
    assert total_income(m) == 1
```

**Step 2: Run tests, verify fail**

**Step 3: Implement income calculation**

```python
# economics.py
from map_state import is_adjacent, adjacent_positions
from rules import MULTIPLIERS, multiplier_resource, MARKET_CAP, is_multiplier

def multiplier_level(pos, state):
    building = state.building_at(pos)
    resource, weight = multiplier_resource(building)
    return sum(
        weight
        for adj in adjacent_positions(pos)
        if state.building_at(adj) == resource
    )

def market_income(pos, state):
    total = 0
    for adj in adjacent_positions(pos):
        bldg = state.building_at(adj)
        if bldg and is_multiplier(bldg):
            total += multiplier_level(adj, state)
    return min(total, MARKET_CAP)

def total_income(state):
    return sum(
        market_income(pos, state)
        for pos, bldg in state.buildings.items()
        if bldg == 'market'
    )
```

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add economics.py tests/test_economics.py
git commit -m "Add income calculation"
```

### Task 18: Cost calculation

Compute total cost for an action sequence.

**Files:**
- Modify: `economics.py`
- Test: `tests/test_economics.py`

**Step 1: Write failing tests**

```python
from economics import action_cost, sequence_cost

def test_build_cost():
    m = MapState(terrain={(0, 0): 'land'})
    action = ('build', (0, 0), 'sawmill')
    assert action_cost(action, m) == 5

def test_clear_forest_negative_cost():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'forest'})
    action = ('clear_forest', (0, 0))
    assert action_cost(action, m) == -1  # yields 1 star

def test_burn_forest_cost():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'forest'})
    action = ('burn_forest', (0, 0))
    assert action_cost(action, m) == 3

def test_grow_forest_cost():
    m = MapState(terrain={(0, 0): 'land'})
    action = ('grow_forest', (0, 0))
    assert action_cost(action, m) == 5

def test_harvest_cost():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'animal'})
    action = ('harvest', (0, 0))
    assert action_cost(action, m) == 2

def test_sequence_cost():
    m = MapState(
        terrain={(0, 0): 'land', (1, 1): 'land'},
        resources={(0, 0): 'forest'},
    )
    actions = [
        ('clear_forest', (0, 0)),
        ('build', (0, 0), 'sawmill'),
    ]
    assert sequence_cost(actions, m) == -1 + 5  # 4 total
```

**Step 2: Run tests, verify fail**

**Step 3: Implement cost calculation**

`action_cost(action, state)` returns the star cost of a single action.
`sequence_cost(actions, initial_state)` applies actions in sequence, summing costs. Each action is applied to get the state for the next cost calculation.

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add economics.py tests/test_economics.py
git commit -m "Add cost calculation"
```

### Task 19: Population calculation

Compute population changes from an action sequence.

**Files:**
- Modify: `economics.py`
- Test: `tests/test_economics.py`

**Step 1: Write failing tests**

```python
from economics import action_population, sequence_population

def test_build_lumber_hut_population():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'forest'})
    assert action_population(('build', (0, 0), 'lumber_hut'), m) == 1

def test_build_farm_population():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'crop'})
    assert action_population(('build', (0, 0), 'farm'), m) == 2

def test_build_mine_population():
    m = MapState(terrain={(0, 0): 'mountain'}, resources={(0, 0): 'metal'})
    assert action_population(('build', (0, 0), 'mine'), m) == 2

def test_build_sawmill_population_depends_on_adjacency():
    """Sawmill population = number of adjacent lumber huts."""
    m = MapState(
        terrain={(0, 0): 'land', (0, 1): 'land', (1, 0): 'land'},
        resources={(0, 1): 'forest', (1, 0): 'forest'},
        buildings={(0, 1): 'lumber_hut', (1, 0): 'lumber_hut'},
    )
    assert action_population(('build', (0, 0), 'sawmill'), m) == 2

def test_harvest_population():
    m = MapState(terrain={(0, 0): 'land'}, resources={(0, 0): 'animal'})
    assert action_population(('harvest', (0, 0)), m) == 1
```

**Step 2: Run tests, verify fail**

**Step 3: Implement population calculation**

Resource buildings have fixed population (lumber_hut=1, farm=2, mine=2). Multipliers give population equal to their level when built. Harvesting gives 1 population.

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add economics.py tests/test_economics.py
git commit -m "Add population calculation"
```

---

## Phase 5: Move Generation

### Task 20: Legal move enumeration

Given a `MapState` and techs, enumerate all legal actions.

**Files:**
- Create: `moves.py`
- Test: `tests/test_moves.py`

**Step 1: Write failing tests**

```python
from moves import legal_moves
from map_state import MapState

def test_no_moves_on_empty_map():
    m = MapState()
    assert legal_moves(m, techs=frozenset()) == []

def test_build_on_eligible_tile():
    m = MapState(
        terrain={(0, 0): 'land'},
        cities=({'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset({'mathematics'}))
    assert ('build', (0, 0), 'sawmill') in moves

def test_no_build_without_tech():
    m = MapState(
        terrain={(0, 0): 'land'},
        cities=({'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset())
    build_moves = [a for a in moves if a[0] == 'build']
    assert len(build_moves) == 0

def test_clear_forest_move():
    m = MapState(
        terrain={(0, 0): 'land'},
        resources={(0, 0): 'forest'},
        cities=({'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset({'forestry'}))
    assert ('clear_forest', (0, 0)) in moves

def test_found_city_move():
    m = MapState(
        terrain={(5, 5): 'land'},
        villages=frozenset({(5, 5)}),
    )
    moves = legal_moves(m, techs=frozenset())
    assert ('found_city', (5, 5)) in moves

def test_no_build_outside_territory():
    m = MapState(
        terrain={(0, 0): 'land', (5, 5): 'land'},
        cities=({'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset({'mathematics'}))
    sawmill_positions = [a[1] for a in moves if a[0] == 'build' and a[2] == 'sawmill']
    assert (0, 0) in sawmill_positions
    assert (5, 5) not in sawmill_positions

def test_no_build_on_occupied():
    m = MapState(
        terrain={(0, 0): 'land'},
        buildings={(0, 0): 'farm'},
        cities=({'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset({'mathematics'}))
    build_at_0_0 = [a for a in moves if a[0] == 'build' and a[1] == (0, 0)]
    assert len(build_at_0_0) == 0

def test_one_per_city_constraint():
    """If a city already has a sawmill, can't build another."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(3) for c in range(3)},
        buildings={(0, 0): 'sawmill'},
        cities=({'id': 1, 'row': 1, 'col': 1, 'population': 1, 'border_level': 1},),
    )
    moves = legal_moves(m, techs=frozenset({'mathematics'}))
    sawmill_moves = [a for a in moves if a[0] == 'build' and a[2] == 'sawmill']
    assert len(sawmill_moves) == 0
```

**Step 2: Run tests, verify fail**

**Step 3: Implement legal_moves**

```python
# moves.py
from map_state import MapState
from actions import validate_action
from rules import BUILDINGS, TERRAIN_ACTIONS

def legal_moves(state, techs):
    """Enumerate all legal actions for the given state and tech set."""
    moves = []

    # Found city moves
    for pos in state.villages:
        action = ('found_city', pos)
        if validate_action(state, action, techs) is None:
            moves.append(action)

    # Expand borders moves
    for city in state.cities:
        action = ('expand_borders', city['id'])
        if validate_action(state, action, techs) is None:
            moves.append(action)

    ownership = state.territory_ownership()

    for pos in state.defined_positions():
        # Build moves — only in owned territory
        if pos in ownership:
            for building in BUILDINGS:
                action = ('build', pos, building)
                if validate_action(state, action, techs) is None:
                    moves.append(action)

        # Terrain modification moves — only in owned territory
        if pos in ownership:
            for action_type in ('clear_forest', 'burn_forest', 'grow_forest', 'harvest'):
                action = (action_type, pos)
                if validate_action(state, action, techs) is None:
                    moves.append(action)

    return moves
```

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add moves.py tests/test_moves.py
git commit -m "Add legal move enumeration"
```

---

## Phase 6: Optimizer

### Task 21: Naive optimizer — scaffolding

Build the optimizer interface: takes initial state, techs, scoring function, returns best action sequence and final state.

**Files:**
- Create: `optimizer.py`
- Test: `tests/test_optimizer.py`

**Step 1: Write failing tests**

Start with a trivial case: one tile, one possible building.

```python
from optimizer import optimize
from map_state import MapState
from economics import total_income

def test_optimize_single_market():
    """With one market spot adjacent to a pre-built sawmill with lumber huts,
    the optimizer should place the market."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(3) for c in range(3)},
        resources={(0, 1): 'forest', (1, 0): 'forest'},
        buildings={
            (0, 0): 'sawmill',
            (0, 1): 'lumber_hut',
            (1, 0): 'lumber_hut',
        },
        cities=({'id': 1, 'row': 1, 'col': 1, 'population': 5, 'border_level': 1},),
    )
    techs = frozenset({'trade', 'mathematics', 'forestry'})

    def score(state, actions):
        return total_income(state)

    result = optimize(m, techs, score)
    assert result['income'] > 0
    # Should have placed a market somewhere adjacent to the sawmill
    market_actions = [a for a in result['actions'] if a[0] == 'build' and a[2] == 'market']
    assert len(market_actions) > 0
```

**Step 2: Run tests, verify fail**

**Step 3: Implement naive optimizer**

The initial optimizer does a breadth-first or greedy search over action sequences. Start with a simple greedy approach: at each step, try all legal moves, pick the one that gives the best score improvement, repeat until no improvement.

```python
# optimizer.py
from moves import legal_moves
from actions import apply_action
from economics import total_income, sequence_cost

def optimize(initial_state, techs, score_fn, max_depth=20):
    """
    Greedy optimizer: repeatedly pick the best legal action until
    no improvement or max_depth reached.
    """
    state = initial_state
    actions_taken = []

    for _ in range(max_depth):
        best_action = None
        best_score = score_fn(state, actions_taken)
        best_state = state

        for action in legal_moves(state, techs):
            new_state = apply_action(state, action)
            new_actions = actions_taken + [action]
            s = score_fn(new_state, new_actions)
            if s > best_score:
                best_score = s
                best_action = action
                best_state = new_state

        if best_action is None:
            break

        actions_taken.append(best_action)
        state = best_state

    return {
        'state': state,
        'actions': actions_taken,
        'income': total_income(state),
    }
```

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add optimizer.py tests/test_optimizer.py
git commit -m "Add naive greedy optimizer"
```

### Task 22: Optimizer — multi-city test

Test the optimizer with multiple cities to verify it handles territory correctly.

**Files:**
- Modify: `tests/test_optimizer.py`

**Step 1: Write failing tests**

```python
def test_optimize_two_cities():
    """Optimizer should place buildings in both city territories."""
    terrain = {(r, c): 'land' for r in range(8) for c in range(8)}
    resources = {}
    for r in range(8):
        for c in range(8):
            if (r + c) % 3 == 0:
                resources[(r, c)] = 'forest'
            elif (r + c) % 3 == 1:
                resources[(r, c)] = 'crop'

    m = MapState(
        terrain=terrain,
        resources=resources,
        cities=(
            {'id': 1, 'row': 1, 'col': 1, 'population': 5, 'border_level': 2},
            {'id': 2, 'row': 6, 'col': 6, 'population': 5, 'border_level': 2},
        ),
    )
    techs = frozenset({'mathematics', 'forestry', 'construction', 'farming',
                       'trade', 'mining', 'smithery', 'climbing'})

    def score(state, actions):
        return total_income(state)

    result = optimize(m, techs, score)
    assert result['income'] > 0
```

**Step 2: Run test, verify it passes or debug**

This tests the integration of territory ownership with the optimizer. May need to increase max_depth or adjust the greedy strategy.

**Step 3: Commit**

```bash
git add tests/test_optimizer.py
git commit -m "Add multi-city optimizer test"
```

### Task 23: Optimizer — lexicographic scoring

Test that the optimizer can use compound scoring (income first, then minimize cost).

**Files:**
- Modify: `tests/test_optimizer.py`

**Step 1: Write failing tests**

```python
from economics import sequence_cost

def test_optimize_income_then_cost():
    """With a lexicographic score, optimizer should maximize income then minimize cost."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(3) for c in range(3)},
        resources={(0, 1): 'forest', (1, 0): 'forest'},
        cities=({'id': 1, 'row': 1, 'col': 1, 'population': 5, 'border_level': 1},),
    )
    techs = frozenset({'mathematics', 'forestry', 'trade'})

    def score(state, actions):
        income = total_income(state)
        cost = sequence_cost(actions, m)
        return (income, -cost)

    result = optimize(m, techs, score)
    assert result['income'] >= 0
```

**Step 2: Run test, verify pass**

**Step 3: Commit**

```bash
git add tests/test_optimizer.py
git commit -m "Add lexicographic scoring test"
```

---

## Phase 7: Server and Frontend

### Task 24: Update server

Replace the old solver import with the new modules. Keep the same HTTP interface as much as possible for backward compatibility with the frontend.

**Files:**
- Modify: `server.py`
- Test: manual testing via browser

**Step 1: Update server.py**

```python
from flask import Flask, request, jsonify
from map_state import MapState
from optimizer import optimize
from economics import total_income, sequence_cost
from rules import MAP_SHAPES, TERRAIN_TYPES, RESOURCE_TYPES, BUILDINGS

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

def _state_from_json(data):
    """Convert JSON request data into a MapState."""
    terrain = {}
    resources = {}
    for t in data.get('tiles', []):
        pos = (t['row'], t['col'])
        terrain[pos] = t['terrain']
        if 'resource' in t:
            resources[pos] = t['resource']

    cities = tuple(data.get('cities', []))
    villages = frozenset(
        (v['row'], v['col']) for v in data.get('villages', [])
    )
    monuments = frozenset(
        (m['row'], m['col']) for m in data.get('monuments', [])
    )
    lighthouses = frozenset(
        (l['row'], l['col']) for l in data.get('lighthouses', [])
    )
    buildings = {}
    for p in data.get('pinned', []):
        buildings[(p['row'], p['col'])] = p['building']

    return MapState(
        terrain=terrain,
        resources=resources,
        buildings=buildings,
        cities=cities,
        villages=villages,
        monuments=monuments,
        lighthouses=lighthouses,
    )

@app.post('/optimize')
def optimize_endpoint():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    state = _state_from_json(data)
    techs = frozenset(data.get('techs', []))

    def score(state, actions):
        income = total_income(state)
        cost = sequence_cost(actions, state)
        return (income, -cost)

    result = optimize(state, techs, score)

    # Format response for frontend
    placements = [
        {'row': pos[0], 'col': pos[1], 'building': bldg}
        for pos, bldg in result['state'].buildings.items()
    ]
    markets = []
    for pos, bldg in result['state'].buildings.items():
        if bldg == 'market':
            from economics import market_income
            markets.append({
                'row': pos[0], 'col': pos[1],
                'income': market_income(pos, result['state']),
            })

    return jsonify({
        'placements': placements,
        'markets': markets,
        'total_income': result['income'],
        'total_cost': sequence_cost(result['actions'], state),
        'actions': [list(a) for a in result['actions']],
    })

@app.post('/territory')
def territory():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    state = _state_from_json(data)
    ownership = state.territory_ownership()
    return jsonify({
        'ownership': {f"{r},{c}": city_id for (r, c), city_id in ownership.items()}
    })

@app.get('/rules/map-shapes')
def map_shapes():
    return jsonify({'shapes': sorted(MAP_SHAPES)})

if __name__ == '__main__':
    app.run(debug=True)
```

**Step 2: Run server and verify manually**

Run: `uv run python server.py`

**Step 3: Commit**

```bash
git add server.py
git commit -m "Update server to use new modules"
```

### Task 25: Update frontend for new data format

The frontend needs to send terrain and resources as separate fields, and handle the new response format. This is a minimal update — keep the existing UI structure, just adapt the data layer.

**Files:**
- Modify: `static/app.js`
- Modify: `static/index.html` (add map size selector)

**Step 1: Update app.js**

Key changes:
- Split `terrain` field into `terrain` + `resource` when sending to server
- Add map size selector
- Handle new response format (actions list)
- Send techs instead of excluded buildings

This task requires careful reading of the existing `app.js` to understand the current data flow, then making targeted changes. The full details depend on the current frontend structure.

**Step 2: Test manually in browser**

**Step 3: Commit**

```bash
git add static/app.js static/index.html
git commit -m "Update frontend for new data format"
```

---

## Phase 8: Cleanup and Verification

### Task 26: End-to-end testing

Create an integration test that exercises the full stack (minus the HTTP layer).

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write integration tests**

```python
from map_state import MapState
from optimizer import optimize
from economics import total_income, sequence_cost

def test_full_optimization_from_scratch():
    """Start with terrain + resources + cities, optimize for income."""
    terrain = {(r, c): 'land' for r in range(5) for c in range(5)}
    resources = {
        (0, 1): 'forest', (1, 0): 'forest', (2, 0): 'forest',
        (0, 2): 'crop', (2, 1): 'crop',
    }
    m = MapState(
        terrain=terrain,
        resources=resources,
        cities=({'id': 1, 'row': 2, 'col': 2, 'population': 5, 'border_level': 2},),
    )
    techs = frozenset({
        'hunting', 'forestry', 'mathematics',
        'organization', 'farming', 'construction',
        'riding', 'roads', 'trade',
    })

    def score(state, actions):
        return (total_income(state), -sequence_cost(actions, m))

    result = optimize(m, techs, score)
    assert result['income'] > 0
    assert len(result['actions']) > 0

def test_monuments_block_placement():
    """Monuments should prevent buildings from being placed on their tiles."""
    m = MapState(
        terrain={(r, c): 'land' for r in range(3) for c in range(3)},
        monuments=frozenset({(1, 1)}),
        cities=({'id': 1, 'row': 1, 'col': 1, 'population': 5, 'border_level': 1},),
    )
    techs = frozenset({'mathematics', 'trade'})

    def score(state, actions):
        return total_income(state)

    result = optimize(m, techs, score)
    assert result['state'].building_at((1, 1)) is None
```

**Step 2: Run all tests**

Run: `uv run pytest -v`
Expected: ALL PASS

**Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "Add integration tests"
```

### Task 27: Remove old solver

Once everything is working, remove the old `solver.py` and `tests/test_solver.py`.

**Step 1: Delete old files**

```bash
git rm solver.py tests/test_solver.py
```

**Step 2: Run all tests to confirm nothing depends on old code**

Run: `uv run pytest -v`
Expected: ALL PASS

**Step 3: Commit**

```bash
git commit -m "Remove old solver"
```

### Task 28: Final review

Run full test suite, check for any remaining issues, ensure the server starts cleanly.

**Step 1: Run tests**

```bash
uv run pytest -v
```

**Step 2: Start server**

```bash
uv run python server.py
```

**Step 3: Manual browser test**

Verify the frontend works end-to-end.
