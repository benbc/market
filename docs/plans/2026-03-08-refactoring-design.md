# Refactoring Design: Clean Abstractions for the Market Optimizer

## Goal

Rework the codebase around clear conceptual building blocks, enabling future improvements (multi-objective optimization, growth order recommendations, richer game rules) without structural changes. Appetite for significant change — no need to preserve historical decisions.

## Design Principles

- No game logic in the frontend; all logic delegated to the server
- Naive implementations first; optimize only when measured performance requires it
- The resulting design should be clean and powerful, with a few important abstractions but no unmotivated additions

## Map Model (`map_state`)

`MapState` is the composite of four layers, queried and manipulated as a unit:

- **Terrain** — immutable base terrain (land, sea, mountain). A tile's terrain may be undefined (absent), meaning it hasn't been explored. Undefined tiles are excluded from all logic.
- **Resources** — mutable: forest, crops, metal, animals, fruit. Can be harvested, burned, cleared, or grown. Separate from terrain (e.g. a mountain tile may or may not have metal).
- **Buildings** — mutable: what's been built where (farms, markets, sawmills, etc.).
- **Cities** — position, population, border level. Founded from villages.

Additionally:

- **Villages** — map features representing unfounded cities.
- **Monuments and lighthouses** — occupy space, preventing other uses. Lighthouses occupy the four corner tiles of the map. No complex rules, just presence.
- **Map shape** — predefined square sizes (not freeform). The set of valid shapes is defined by the rules.

Functions on `MapState`: query by layer (what's at this tile), query by city (what does this city own), apply an action to produce a new state.

## Rules (`rules`)

Declarative game data plus query functions. Pure reference, no mutation.

- **Terrain/resource validity** — what resources can appear on what terrain
- **Building eligibility** — what can be built where (depends on terrain, resource, existing building)
- **Building effects** — adjacency bonuses, population generation
- **Costs** — building costs, terrain modification costs and yields
- **Tech tree** — which techs unlock which buildings/actions, tech cost formula
- **Constraints** — one multiplier per city, market adjacency requirement, market income cap (8 stars/turn)
- **Map shapes** — the valid predefined square sizes

## Actions (`actions`)

Actions are simple data (tuples). An action transforms a `MapState` into a new `MapState`. An action sequence is a list of actions applied in order.

Action types:

- `found_city(position)` — create city from village, claim territory
- `expand_borders(city)` — grow city territory
- `build(position, building)` — place a building on a tile
- `clear_forest(position)` — remove forest, yield 1 star (negative cost)
- `burn_forest(position)` — convert forest tile's resource to crop
- `grow_forest(position)` — add forest resource to a field tile
- `harvest(position)` — remove animal/fruit resource, yield population

Each action has preconditions (derivable from rules given current state) and effects (new map state). The action sequence ordering matters — particularly for city founding and border expansion, which determine territory ownership.

Validation: is this action legal given the current state and rules?
Application: produce a new `MapState` from an action.

## Economics (`economics`)

Two distinct kinds of evaluation:

- **Income** — a property of the final map state. Recurring stars per turn, derived from what's built where (market adjacency, city levels). Purely state-based.
- **Cost** — a property of the action sequence. One-off star expenditure or yield, accumulated over the sequence. The 1-star yield from clearing forest is negative cost, not income.
- **Population** — a property of the action sequence. Each build/harvest changes a city's population, accumulated over the sequence.

Composable functions that the optimizer can consume.

## Move Generation (`moves`)

Given a `MapState` and rules, enumerate all legal actions. Purely about legality, not strategy. The optimizer decides which moves are worth exploring.

The space is naturally bounded by city territories and available tiles (only owned, defined tiles with valid terrain are candidates). Build naive and complete initially; optimize later if needed.

## Optimizer (`optimizer`)

Searches over action sequences to find the best outcome. Takes:

- An initial `MapState`
- Available techs
- A scoring function (provided by caller)

The scoring function consumes economics outputs (income, cost, population) and returns a comparable value. This keeps the optimizer generic — the caller controls the objective (pure income, lexicographic income-then-cost, weighted combination, etc.).

Search strategy: naive tree search initially. The current coordinate descent approach won't directly apply to action sequences, but the problem is tractable given bounded city territories. Build naive, measure, then optimize.

The optimizer produces a full action sequence internally (needed for accurate cost/population accounting), but the presentation layer decides how much to surface to the user.

## Server (`server`)

Thin Flask wrapper. Translates HTTP requests to optimizer/rules calls. Establishes a JSON transport format for `MapState` and actions.

Design principle: no game logic in the frontend. All logic is delegated to the server. The frontend sends state and receives results. Rule-based endpoints (available map shapes, terrain types, etc.) can be added as needed to avoid duplicating game knowledge in JavaScript.

## Frontend (`static/`)

Display and input layer only. Renders map state, collects user input, sends to server. No game logic.

Key changes from current:
- Map shape selection (dropdown of predefined sizes) replaces freeform grid painting
- Terrain painting remains (user defines explored area within the map)
- Results rendering largely unchanged

UX improvements (validating user actions against rules, smarter input) are deferred — the important principle is establishing the architecture that makes them possible without frontend logic duplication.

## Module Dependencies

```
optimizer --> moves + economics
moves -----> actions + rules + map_state
economics -> actions + rules + map_state
actions ---> rules + map_state
rules -----> (standalone)
map_state -> (standalone)
server ----> optimizer + rules + map_state
frontend --> server (HTTP only)
```

Clean layers, no cycles.

## Current Terrain/Resource Split

The current model uses combined strings (`field+crop`, `mountain+metal`). These split into:

| Current         | Terrain    | Resource |
|-----------------|------------|----------|
| `field`         | land       | (none)   |
| `field+crop`    | land       | crop     |
| `forest`        | land       | forest   |
| `mountain`      | mountain   | (none)   |
| `mountain+metal`| mountain   | metal    |
| `water`         | water      | (none)   |
| `ocean`         | ocean      | (none)   |

(Exact terrain type names to be decided during implementation.)
