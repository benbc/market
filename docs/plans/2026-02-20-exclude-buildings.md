# Exclude Buildings Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Allow users to exclude building types from the solver so it only uses researched tech.

**Architecture:** Add an `excluded_buildings` frozenset parameter threading through `city_placements`, `place_resource_buildings`, `_build_full_placements`, `_score`, and `optimise`. UI gets combined checkbox+pin rows per building. State stores `excluded` as an array of building names.

**Tech Stack:** Python solver, vanilla JS/HTML/CSS frontend.

---

### Task 1: Exclude buildings from combo generation

**Files:**
- Modify: `solver.py:132-153` (`city_placements` and `candidates`)
- Test: `tests/test_solver.py`

**Step 1: Write the failing test**

In `tests/test_solver.py`, add:

```python
def test_excluded_building_not_in_combos():
    """An excluded building should never appear in any combo."""
    tiles = {(0, 0): 'field', (0, 1): 'field', (0, 2): 'field'}
    territory = {(0, 0), (0, 1), (0, 2)}
    combos = city_placements(tiles, territory, excluded_buildings=frozenset({'sawmill'}))
    for c in combos:
        assert c['sawmill'] is None, "Excluded sawmill was placed"


def test_excluded_building_others_still_work():
    """Non-excluded buildings should still be placed normally."""
    tiles = {(0, 0): 'field', (0, 1): 'field', (0, 2): 'field'}
    territory = {(0, 0), (0, 1), (0, 2)}
    combos = city_placements(tiles, territory, excluded_buildings=frozenset({'sawmill'}))
    has_windmill = any(c['windmill'] is not None for c in combos)
    assert has_windmill


def test_excluded_market_not_placed():
    tiles = {(0, 0): 'field', (0, 1): 'field'}
    territory = {(0, 0), (0, 1)}
    combos = city_placements(tiles, territory, excluded_buildings=frozenset({'market'}))
    for c in combos:
        assert c['market'] is None
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_solver.py::test_excluded_building_not_in_combos tests/test_solver.py::test_excluded_building_others_still_work tests/test_solver.py::test_excluded_market_not_placed -v`
Expected: FAIL — `city_placements()` does not accept `excluded_buildings` parameter.

**Step 3: Implement — add `excluded_buildings` parameter to `city_placements`**

In `solver.py`, change the signature at line 132:

```python
def city_placements(tiles: dict, city_territory_positions: set, pinned_positions: frozenset = frozenset(), excluded_buildings: frozenset = frozenset()) -> list:
```

In the `candidates()` function (line 140), add a guard at the top:

```python
    def candidates(building):
        if building in excluded_buildings:
            return [None]
        result = [None]
        # ... rest unchanged
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_solver.py -v`
Expected: All tests pass (existing + new).

**Step 5: Commit**

```bash
git add solver.py tests/test_solver.py
git commit -m "Exclude buildings from combo generation in city_placements"
```

---

### Task 2: Exclude buildings from resource placement

**Files:**
- Modify: `solver.py:56-92` (`place_resource_buildings`)
- Test: `tests/test_solver.py`

**Step 1: Write the failing tests**

```python
def test_excluded_mine_not_placed():
    tiles = {(0, 0): 'mountain+metal', (0, 1): 'field'}
    occupied = {}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'mine'}))
    assert (0, 0) not in result


def test_excluded_farm_not_placed_on_crop():
    tiles = {(0, 0): 'field+crop'}
    occupied = {}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'farm'}))
    assert (0, 0) not in result


def test_excluded_lumber_hut_forest_stays_empty():
    """With lumber_hut excluded and no adjacent windmill, forest gets nothing."""
    tiles = {(0, 0): 'forest'}
    occupied = {}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'lumber_hut'}))
    assert (0, 0) not in result


def test_excluded_lumber_hut_forest_burns_to_farm_if_windmill():
    """With lumber_hut excluded but farm available, forest adjacent to windmill burns to farm."""
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    occupied = {(0, 1): 'windmill'}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'lumber_hut'}))
    assert result[(0, 0)] == 'farm'
    assert (0, 0) in burns


def test_excluded_farm_forest_stays_lumber_hut():
    """With farm excluded, forest always becomes lumber_hut regardless of adjacent windmills."""
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    occupied = {(0, 1): 'windmill'}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'farm'}))
    assert result[(0, 0)] == 'lumber_hut'
    assert (0, 0) not in burns


def test_excluded_both_lumber_hut_and_farm_forest_empty():
    tiles = {(0, 0): 'forest', (0, 1): 'field'}
    occupied = {(0, 1): 'windmill'}
    result, burns = place_resource_buildings(tiles, occupied, excluded_buildings=frozenset({'lumber_hut', 'farm'}))
    assert (0, 0) not in result
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_solver.py::test_excluded_mine_not_placed -v`
Expected: FAIL — `place_resource_buildings()` does not accept `excluded_buildings`.

**Step 3: Implement**

Change `place_resource_buildings` signature:

```python
def place_resource_buildings(tiles: dict, occupied: dict, excluded_buildings: frozenset = frozenset()) -> tuple:
```

Replace the forest/resource logic in the function body:

```python
    for pos, terrain in tiles.items():
        if pos in occupied:
            continue
        if terrain == 'forest':
            lumber_ok = 'lumber_hut' not in excluded_buildings
            farm_ok = 'farm' not in excluded_buildings
            if not lumber_ok and not farm_ok:
                continue
            adj_sawmills = sum(
                1 for opos, bldg in occupied.items()
                if bldg == 'sawmill' and is_adjacent(pos, opos)
            )
            adj_windmills = sum(
                1 for opos, bldg in occupied.items()
                if bldg == 'windmill' and is_adjacent(pos, opos)
            )
            if farm_ok and adj_windmills > adj_sawmills:
                result[pos] = 'farm'
                burns.add(pos)
            elif lumber_ok:
                result[pos] = 'lumber_hut'
            elif farm_ok:
                result[pos] = 'farm'
                burns.add(pos)
        else:
            building = RESOURCE.get(terrain)
            if building and building not in excluded_buildings:
                result[pos] = building
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_solver.py -v`
Expected: All tests pass.

**Step 5: Commit**

```bash
git add solver.py tests/test_solver.py
git commit -m "Exclude buildings from resource placement"
```

---

### Task 3: Thread excluded through scoring and optimise

**Files:**
- Modify: `solver.py:181-317` (`_build_full_placements`, `_score`, `_optimise_once`, `optimise`)
- Test: `tests/test_solver.py`

**Step 1: Write the failing test**

```python
def test_optimise_excludes_sawmill():
    """With sawmill excluded, no sawmill should appear in placements."""
    tiles = {
        (0, 0): 'field', (0, 1): 'field', (0, 2): 'forest',
        (1, 0): 'field', (1, 1): 'field', (1, 2): 'field+crop',
    }
    cities = [{'id': 1, 'row': 1, 'col': 1, 'expanded': False}]
    data = {
        'tiles': [{'row': r, 'col': c, 'terrain': t} for (r, c), t in tiles.items()],
        'cities': cities,
        'excluded': ['sawmill'],
    }
    result = optimise(data)
    for p in result['placements']:
        assert p['building'] != 'sawmill'


def test_optimise_excludes_lumber_hut():
    """With lumber_hut excluded, no lumber_hut in placements."""
    tiles = {
        (0, 0): 'forest', (0, 1): 'field',
        (1, 0): 'field', (1, 1): 'field',
    }
    cities = [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}]
    data = {
        'tiles': [{'row': r, 'col': c, 'terrain': t} for (r, c), t in tiles.items()],
        'cities': cities,
        'excluded': ['lumber_hut'],
    }
    result = optimise(data)
    for p in result['placements']:
        assert p['building'] != 'lumber_hut'
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_solver.py::test_optimise_excludes_sawmill tests/test_solver.py::test_optimise_excludes_lumber_hut -v`
Expected: FAIL — sawmill/lumber_hut still placed because `optimise` doesn't parse or pass `excluded`.

**Step 3: Implement**

In `_build_full_placements` (line 181):

```python
def _build_full_placements(city_assignments: dict, tiles: dict, excluded_buildings: frozenset = frozenset()) -> tuple:
    occupied = dict(city_assignments)
    resources, resource_burns = place_resource_buildings(tiles, occupied, excluded_buildings)
    return {**occupied, **resources}, resource_burns
```

In `_score` (line 191):

```python
def _score(city_assignments: dict, tiles: dict, excluded_buildings: frozenset = frozenset()) -> int:
    placements, _ = _build_full_placements(city_assignments, tiles, excluded_buildings)
    return sum(
        market_income(pos, placements)
        for pos, bldg in placements.items()
        if bldg == 'market'
    )
```

In `_optimise_once` (line 203), add `excluded_buildings` parameter and pass it to `_score`:

```python
def _optimise_once(cities_combos: list, tiles: dict, pinned: dict = None, excluded_buildings: frozenset = frozenset()) -> tuple:
```

Change all `_score(...)` calls inside `_optimise_once` from:
- `_score(candidate, tiles)` to `_score(candidate, tiles, excluded_buildings)`
- `_score(current, tiles)` to `_score(current, tiles, excluded_buildings)`

In `optimise` (line 255), parse excluded and pass it through:

After line 264 (`pinned_positions = ...`), add:

```python
    excluded_buildings = frozenset(data.get('excluded', []))
```

Change the `city_placements` call (line 272) to pass `excluded_buildings`:

```python
        combos = city_placements(tiles, territory_in_game, pinned_positions, excluded_buildings)
```

Change the `_optimise_once` call (line 282):

```python
        score, placements, city_selected = _optimise_once(cities_combos, tiles, pinned, excluded_buildings)
```

Change the `_build_full_placements` call (line 288):

```python
    full, resource_burns = _build_full_placements(best_placements, tiles, excluded_buildings)
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_solver.py -v`
Expected: All tests pass.

**Step 5: Commit**

```bash
git add solver.py tests/test_solver.py
git commit -m "Thread excluded buildings through scoring and optimise"
```

---

### Task 4: UI — combined building rows with checkboxes

**Files:**
- Modify: `static/index.html:23-30`
- Modify: `static/app.js:33-38, 173-193, 229-253`
- Modify: `static/style.css`

**Step 1: Update HTML — combined checkbox+button rows**

Replace the Buildings section in `index.html` (lines 23-30) with:

```html
    <h2>Buildings</h2>
    <div class="building-row">
      <input type="checkbox" class="building-toggle" data-building="sawmill" checked>
      <button class="tool-btn" data-tool="pin-sawmill">Sawmill</button>
    </div>
    <div class="building-row">
      <input type="checkbox" class="building-toggle" data-building="windmill" checked>
      <button class="tool-btn" data-tool="pin-windmill">Windmill</button>
    </div>
    <div class="building-row">
      <input type="checkbox" class="building-toggle" data-building="forge" checked>
      <button class="tool-btn" data-tool="pin-forge">Forge</button>
    </div>
    <div class="building-row">
      <input type="checkbox" class="building-toggle" data-building="market" checked>
      <button class="tool-btn" data-tool="pin-market">Market</button>
    </div>
    <div class="building-row">
      <input type="checkbox" class="building-toggle" data-building="lumber_hut" checked>
      <button class="tool-btn" data-tool="pin-lumber_hut">Lumber Hut</button>
    </div>
    <div class="building-row">
      <input type="checkbox" class="building-toggle" data-building="farm" checked>
      <button class="tool-btn" data-tool="pin-farm">Farm</button>
    </div>
    <div class="building-row">
      <input type="checkbox" class="building-toggle" data-building="mine" checked>
      <button class="tool-btn" data-tool="pin-mine">Mine</button>
    </div>
```

**Step 2: Update CSS — building row layout and disabled style**

Add to `style.css`:

```css
.building-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.building-row .tool-btn {
  flex: 1;
}

.tool-btn:disabled {
  opacity: 0.4;
  cursor: default;
}
```

**Step 3: Update JS — excluded state, checkbox handlers, payload, save/load**

In `app.js`, add `excluded` to state (line 38):

```javascript
let state = {
  rows: 10,
  cols: 10,
  tiles: {},
  cities: [],
  pinned: {},
  excluded: [],  // building names excluded from solver
};
```

Add checkbox handler after the toolbar section (after line 180):

```javascript
// --- Building toggles ---

function updateBuildingToggles() {
  document.querySelectorAll('.building-toggle').forEach(cb => {
    const building = cb.dataset.building;
    const excluded = state.excluded.includes(building);
    cb.checked = !excluded;
    const btn = cb.parentElement.querySelector('.tool-btn');
    btn.disabled = excluded;
    if (excluded && activeTool === btn.dataset.tool) {
      activeTool = null;
      document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
      document.getElementById('active-tool-label').textContent = 'none';
    }
  });
}

document.querySelectorAll('.building-toggle').forEach(cb => {
  cb.addEventListener('change', () => {
    const building = cb.dataset.building;
    if (cb.checked) {
      state.excluded = state.excluded.filter(b => b !== building);
    } else {
      if (!state.excluded.includes(building)) {
        state.excluded.push(building);
      }
    }
    updateBuildingToggles();
  });
});
```

In the optimise payload (line 193), add `excluded`:

```javascript
  const payload = { tiles: tilesArr, cities: state.cities, pinned: pinnedArr, excluded: state.excluded };
```

In the load handler (after `if (!state.pinned) state.pinned = {};`), add:

```javascript
      if (!state.excluded) state.excluded = [];
      updateBuildingToggles();
```

At the end of the init section (after `renderGrid()`), add:

```javascript
updateBuildingToggles();
```

**Step 4: Manual test**

1. Open the app
2. Uncheck Sawmill — its pin button should grey out
3. Run optimise — no sawmill should appear in results
4. Save and reload — excluded state should persist

**Step 5: Commit**

```bash
git add static/index.html static/app.js static/style.css
git commit -m "Add building exclusion UI with combined checkbox+pin rows"
```

---

### Task 5: Final verification

**Step 1: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All tests pass.

**Step 2: Commit any remaining changes**

If clean, no action needed.
