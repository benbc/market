# Polytopia Market Optimiser — Design

## Problem

Given a snapshot of city territories in a Polytopia game, find the optimal placement
of production multipliers (Sawmill, Windmill, Forge) and Markets to maximise total
Market star income in the ideal end state.

Markets interact across city boundaries: a Sawmill in City A benefits a Market in
City B if they are 8-directionally adjacent. Cities cannot be optimised independently.

## Rules Summary (relevant subset)

### Terrain → eligible buildings

| Terrain       | Can hold                          |
|---------------|-----------------------------------|
| field         | Sawmill, Windmill, Forge, Market  |
| field+crop    | All of field, plus Farm           |
| forest        | Lumber Hut, Forge                 |
| mountain+metal| Mine                              |
| other         | nothing relevant                  |

### Production multipliers (one per city)

| Building | Built on         | Level = …                         |
|----------|------------------|-----------------------------------|
| Sawmill  | field/crop       | number of adjacent Lumber Huts    |
| Windmill | field/crop       | number of adjacent Farms          |
| Forge    | field/crop/forest| 2 × number of adjacent Mines      |

### Market

- Built on field/crop tile
- Must be 8-directionally adjacent to at least one Sawmill, Windmill, or Forge
- Income = sum of levels of all 8-adjacent multipliers, capped at 8★/turn
- Adjacency is global (crosses city territory boundaries)

### City territories

- Default: 3×3 centred on city tile
- Optional expansion to 5×5 (Border Growth choice at level 4 upgrade)
- Overlapping border tiles: assigned to nearest city; ties broken by city definition order

### Ideal end-state assumptions

- Every mountain+metal tile gets a Mine
- Every remaining forest tile gets a Lumber Hut (unless a Forge is placed there)
- Every remaining field+crop tile gets a Farm (unless a Sawmill, Windmill, Forge, or Market is placed there)
- Production multipliers and Markets are placed optimally (subject to one-per-city constraint)

## Architecture

```
browser (vanilla JS + HTML/CSS)
    paint terrain, place cities, load/save JSON
    POST /optimize → { grid, cities }
Flask server (Python)
    solver.py computes optimal placement
    returns building assignments + Market incomes
browser
    overlays result icons on grid, shows summary panel
```

No database. Game state is saved/loaded as JSON by the user.

## Data Model

### Grid

Sparse: only tiles the user has painted exist. Unpainted tiles are ignored by the
solver (not in any city's territory, no building possible).

Each tile: `{ row, col, terrain }` where terrain ∈
`{field, field+crop, forest, mountain+metal, mountain, water, ocean}`.

### City

```json
{ "id": 1, "row": 5, "col": 7, "expanded": false }
```

Territory is auto-derived (3×3 or 5×5). Tile ownership is computed from city
positions using nearest-city with first-come-first-served tie-breaking.

### Solver input/output

Input:
```json
{
  "tiles": [{ "row": 4, "col": 6, "terrain": "field+crop" }, ...],
  "cities": [{ "id": 1, "row": 5, "col": 7, "expanded": false }, ...]
}
```

Output:
```json
{
  "placements": [
    { "row": 4, "col": 6, "building": "Windmill", "city_id": 1 },
    ...
  ],
  "markets": [
    { "row": 5, "col": 6, "city_id": 1, "income": 6 },
    ...
  ],
  "total_income": 14
}
```

## Optimization Algorithm

Coordinate descent with random restarts:

1. For each city, enumerate all valid (Sawmill tile, Windmill tile, Forge tile,
   Market tile) combinations within its territory.
2. Starting from a random valid assignment, iterate: for each city in turn, fix all
   other cities' placements and exhaustively pick the locally-best combination for
   this city. Repeat until no city improves (convergence).
3. Run from several random starting points; return the best result found.

Rationale: territories are small (max 25 tiles), so per-city enumeration is fast.
Coordinate descent converges quickly in practice. Reusable scoring primitives make
algorithm swaps easy in future iterations.

## File Structure

```
markets/
  server.py          Flask app; single POST /optimize endpoint
  solver.py          Optimization logic (pure Python, no game-engine deps)
  static/
    index.html
    app.js           Grid state, painting, city placement, API call, rendering
    style.css
  polytopia_rules.md
  docs/plans/
    2026-02-19-market-optimiser-design.md
```

## UI

- Configurable grid size
- Terrain toolbar: click type, then paint tiles; unpainted = empty
- City tool: click to place/remove city center; toggle Border Growth per city
- Territory boundaries shown as subtle overlay
- "Optimise" button → POST to server → overlay result icons + summary panel
- Download/upload JSON for save/load

## Future Extensions

- Budget optimisation (cost of buildings vs. star income payoff)
- Dynamic play (turn-by-turn recommendations)
- Support for special tribes
