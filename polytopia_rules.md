# The Battle of Polytopia — Technology & Building Reference

*Regular tribes only. Current as of the 2025 Balance Pass.*

---

## Technology Costs

Technology is divided into **three tiers** across **five branches**. Each Tier 1 tech splits into two Tier 2 techs, each leading to a Tier 3 tech (25 techs total). Higher tiers require the previous tech in their branch. Tribes starting with a higher-tier tech can research the Tier 2 prerequisite without needing the Tier 1 tech first ("backward research").

### Cost Formula

> **Cost = (Tech Tier) × (Number of Cities) + 4**

| Tier | Base Cost (1 city) | Per extra city | Example (4 cities) |
|------|--------------------|----------------|---------------------|
| T1   | 5★                 | +1★            | 8★                  |
| T2   | 6★                 | +2★            | 12★                 |
| T3   | 7★                 | +3★            | 16★                 |

**Literacy** (unlocked by Philosophy) reduces all research costs by 33%, rounded up.

---

## Complete Tech Tree

### Climbing Branch

| Tech | Tier | Unlocks | Starting Tribe |
|------|------|---------|----------------|
| **Climbing** | T1 | Mountain movement & defence bonus; reveals Metal | Xin-xi |
| Mining | T2 | Mine (5★ → 2 pop; mountain with metal) | — |
| Smithery | T3 | Swordsman (5★); Forge (5★, +2 pop per adj. Mine) | Vengir |
| Meditation | T2 | Mountain Temple (20★); Pacifist task (Altar of Peace) | — |
| Philosophy | T3 | Mind Bender (5★); Literacy (−33% tech costs); Genius task | Ai-Mo |

Ai-Mo starts with Philosophy (T3) and a Mind Bender. They can research Meditation (T2) without needing Climbing first.

### Fishing Branch

| Tech | Tier | Unlocks | Starting Tribe |
|------|------|---------|----------------|
| **Fishing** | T1 | Port (7★ → 1 pop; launches Rafts; city connections over water); Fish (2★ → 1 pop) | Kickoo |
| Sailing | T2 | Scout naval unit; ocean movement | — |
| Navigation | T3 | Bomber naval unit; Starfish harvesting (yields 10★) | — |
| Aquaculture | T2 | Rammer naval unit | — |
| Aquatism | T3 | Water Temple (20★); defence bonus on water/ocean tiles | — |

### Hunting Branch

| Tech | Tier | Unlocks | Starting Tribe |
|------|------|---------|----------------|
| **Hunting** | T1 | Hunt animals (2★ → 1 pop) | Bardur |
| Forestry | T2 | Clear Forest (free, yields 1★); Lumber Hut (3★ → 1 pop) | — |
| Mathematics | T3 | Catapult (8★); Sawmill (5★, +1 pop per adj. Lumber Hut) | — |
| Archery | T2 | Archer (3★); defence bonus on forest tiles | Hoodrick |
| Spiritualism | T3 | Grow Forest (5★); Forest Temple (15★) | — |

### Organization Branch

| Tech | Tier | Unlocks | Starting Tribe |
|------|------|---------|----------------|
| **Organization** | T1 | Harvest Fruit (2★ → 1 pop); reveals Crop resource | Imperius |
| Farming | T2 | Farm (5★ → 2 pop; field with crop) | Zebasi |
| Construction | T3 | Windmill (5★, +1 pop per adj. Farm); Burn Forest (3★ → crop) | — |
| Strategy | T2 | Defender (3★); Peace Treaty | Quetzali |
| Diplomacy | T3 | Cloak (5★); Embassy (5★); Capital Vision | — |

Daggers are not trained directly — they spawn when a Cloak infiltrates an enemy city (number = city level, max 5). On water, Pirates spawn instead. Daggers have Surprise (no retaliation) and are Independent (no population cost).

### Riding Branch

| Tech | Tier | Unlocks | Starting Tribe |
|------|------|---------|----------------|
| **Riding** | T1 | Rider (3★) | Oumaji |
| Roads | T2 | Roads (3★); Bridge (7★); Network task (Grand Bazaar) | Yădakk |
| Trade | T3 | Market (5★); Wealth task (Emperor's Tomb) | — |
| Free Spirit | T2 | Temple (20★ → 1 pop + growing points); Disband ability | — |
| Chivalry | T3 | Knight (8★); Destroy ability (removes buildings, free) | — |

---

## Building Costs & Outputs

### Resource Harvesting

| Action | Cost | Output | Requires |
|--------|------|--------|----------|
| Harvest Fruit | 2★ | 1 pop | Organization; fruit tile in city borders |
| Hunt | 2★ | 1 pop | Hunting; animal in forest in city borders |
| Fish | 2★ | 1 pop | Fishing; fish tile in city borders |
| Harvest Starfish | Free | 10★ | Navigation; unit on Starfish tile (takes a turn) |

### Resource Buildings

| Building | Cost | Output | Built On | Tech |
|----------|------|--------|----------|------|
| Lumber Hut | 3★ | 1 pop | Forest tile | Forestry |
| Mine | 5★ | 2 pop | Mountain with metal | Mining |
| Farm | 5★ | 2 pop | Field with crop | Farming |
| Port | 7★ | 1 pop | Shallow water / flooded field | Fishing |

### Production Multipliers

One per city. Built on field tiles (Forge can also be built on forest).

| Building | Cost | Output | Adjacency Bonus From | Tech |
|----------|------|--------|----------------------|------|
| Sawmill | 5★ | +1 pop per adj. Lumber Hut | Lumber Huts | Mathematics |
| Windmill | 5★ | +1 pop per adj. Farm | Farms | Construction |
| Forge | 5★ | +2 pop per adj. Mine | Mines | Smithery |

### Income & Infrastructure

| Building | Cost | Output | Notes | Tech |
|----------|------|--------|-------|------|
| Market | 5★ | 1★/turn for each level of each adj. Sawmill, Windmill, or Forge (max 8) | Built on field tiles; must be next to at least one of these buildings. A building's "level" = its population output (e.g. a Sawmill adjacent to 3 Lumber Huts = level 3). The Market's total income is the sum of levels of all adjacent production buildings, capped at 8★/turn. | Trade |
| Embassy | 5★ | 2★/turn to each party (4★ with Peace Treaty) | Built in another tribe's capital; must not be at war | Diplomacy |
| Road | 3★ | City connection (+1 pop to both cities) | Enables faster movement | Roads |
| Bridge | 7★ | City connection over water | Spans 1-tile water gap; not diagonal | Roads |

### Temples

All temples produce 1 population. They grow every 2 turns, gaining 100 points per level of growth.

| Type | Cost | Built On | Tech |
|------|------|----------|------|
| Temple | 20★ | Field tile | Free Spirit |
| Forest Temple | 15★ | Forest tile | Spiritualism |
| Mountain Temple | 20★ | Mountain tile | Meditation |
| Water Temple | 20★ | Shallow water | Aquatism |

### Monuments

Awarded for completing specific tasks. Each monument provides 3 population and 400 points. Can be built on field or shallow water. One per task per game.

### Terrain Abilities

| Ability | Cost | Effect | Tech |
|---------|------|--------|------|
| Clear Forest | Free | Removes forest; yields 1★ | Forestry |
| Burn Forest | 3★ | Converts forest to field with crop | Construction |
| Grow Forest | 5★ | Creates forest on a field tile | Spiritualism |
| Destroy | Free | Removes a building (no refund) | Chivalry |
| Disband | Free | Removes own unit; returns half its cost (rounded down) | Free Spirit |

---

## City Upgrades

Upgrading to level N requires N population. Each upgrade gives +1★/turn income and +1 unit capacity.

| Level | Option A | Option B |
|-------|----------|----------|
| 2 | Workshop (+1★/turn) | Explorer (reveals nearby tiles) |
| 3 | City Wall (defence bonus) | Resources (5★) |
| 4 | Population Growth (+3 pop) | Border Growth (expands city borders) |
| 5+ | Park (+1★/turn + points) | Super Unit (Giant) |

Human player capitals produce +1★/turn base income. Cities under siege produce no income.

---

## Unit Training Costs

### Land Units

| Unit | Cost | Tech | Key Traits |
|------|------|------|------------|
| Warrior | 2★ | None (start) | Dash, Fortify |
| Rider | 3★ | Riding (T1) | Dash, Escape, Fortify |
| Archer | 3★ | Archery (T2) | Dash, Fortify; ranged (range 2) |
| Defender | 3★ | Strategy (T2) | Dash, Fortify; high defence |
| Swordsman | 5★ | Smithery (T3) | Dash |
| Mind Bender | 5★ | Philosophy (T3) | Heal, Convert |
| Cloak | 5★ | Diplomacy (T3) | Hide, Infiltrate, Scout, Creep |
| Catapult | 8★ | Mathematics (T3) | Ranged (range 3); Stiff (no retaliation) |
| Knight | 8★ | Chivalry (T3) | Dash, Persist (extra attack on kill), Fortify |
| Giant | Free | City upgrade (level 4+) | Super unit; becomes Juggernaut on water |

### Naval Units

Land units become Rafts when moved onto a Port (Giants become Juggernauts). Rafts can be upgraded in friendly territory:

| Unit | Tech | Notes |
|------|------|-------|
| Raft | Sailing (T1) | No attack; movement 2; base naval form |
| Scout | Fishing (T2) | Ranged (range 2); Scout ability |
| Rammer | Aquaculture (T2) | Melee naval unit |
| Bomber | Navigation (T3) | Splash damage; Stiff (no retaliation) |
| Juggernaut | — | Giant on water; Stomp (splash damage on move) |

---

## Starting Conditions

### Starting Stars (2025 Balance Pass)

| Stars | Tribes |
|-------|--------|
| 7★ | Xin-xi, Hoodrick, Quetzali, Yădakk |
| 6★ | Oumaji |
| 5★ | Imperius, Bardur, Kickoo, Zebasi, and other regular tribes |
| 2★ | Luxidoor (starts with level 3 capital instead of a tech) |

### Starting Techs

| Tribe | Starting Tech | Tier |
|-------|---------------|------|
| Xin-xi | Climbing | T1 |
| Imperius | Organization | T1 |
| Bardur | Hunting | T1 |
| Oumaji | Riding | T1 |
| Kickoo | Fishing | T1 |
| Hoodrick | Archery | T2 |
| Luxidoor | None (level 3 capital) | — |
| Vengir | Smithery | T3 |
| Zebasi | Farming | T2 |
| Ai-Mo | Philosophy (+ Mind Bender) | T3 |
| Quetzali | Strategy (+ Defender) | T2 |
| Yădakk | Roads | T2 |

---

*This reference covers regular tribes only. Special tribes (Aquarion, ∑∫ỹriȱŋ, Polaris, Cymanti) have unique tech trees, units, and buildings. Sources: Polytopia Wiki, official Polytopia blog, 2025 Balance Pass notes.*
