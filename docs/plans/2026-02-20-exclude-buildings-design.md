# Exclude buildings from solver

## Context

The solver places all building types. A player may not have researched certain techs, making some buildings unavailable. We need a way to exclude buildings so the solver only uses what's actually available.

## Data model

`state.excluded` in the UI: a JS `Set` of building name strings. Sent as `excluded: ["sawmill", "lumber_hut"]` in the optimise payload. Defaults to empty (all buildings available). Saved/loaded with state.

## Solver changes

### `city_placements(tiles, territory, pinned_positions, excluded_buildings)`

In `candidates()`, skip buildings in the excluded set. If sawmill is excluded, no combo will include a sawmill placement.

### `place_resource_buildings(tiles, occupied, excluded_buildings)`

Skip placing a resource building if it's excluded. Forest logic:
- Both lumber_hut and farm excluded: forest stays empty.
- Only lumber_hut excluded: forests adjacent to windmills still burn to farm.
- Only farm excluded: forests always become lumber_hut.

### `_build_full_placements` / `_score`

Pass `excluded_buildings` through to `place_resource_buildings`.

### `optimise()`

Parse `data.get('excluded', [])` into a `frozenset`, pass to `city_placements` and down through scoring.

## UI changes

### Combined building rows

Replace the current separate building pin buttons with combined rows in the "Buildings" section. Each row has:
- A checkbox (checked = available, unchecked = excluded)
- A pin tool button (disabled when building is excluded)

All checkboxes start checked. Unchecking adds to `state.excluded`.

### Payload

Include `excluded: [...]` in the optimise fetch payload.

### Save/load

Persist `state.excluded` as an array. On load, default to `[]` if missing (backward compat).

## Files to modify

- `solver.py` — `city_placements()`, `place_resource_buildings()`, `_build_full_placements()`, `_score()`, `optimise()`
- `tests/test_solver.py` — new tests for exclusion
- `static/index.html` — combined building rows with checkboxes
- `static/app.js` — excluded state, checkbox handling, payload, save/load
- `static/style.css` — disabled button styles (if needed)
