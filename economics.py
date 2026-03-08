from map_state import adjacent_positions
from rules import (
    MULTIPLIERS, multiplier_resource, MARKET_CAP, is_multiplier,
    BUILDINGS, TERRAIN_ACTIONS, HARVEST_ACTIONS,
)
from actions import apply_action


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


def action_cost(action, state):
    action_type = action[0]
    if action_type == 'build':
        building = action[2]
        return BUILDINGS[building]['cost']
    if action_type == 'clear_forest':
        return -TERRAIN_ACTIONS['clear_forest']['yield']
    if action_type == 'burn_forest':
        return TERRAIN_ACTIONS['burn_forest']['cost']
    if action_type == 'grow_forest':
        return TERRAIN_ACTIONS['grow_forest']['cost']
    if action_type == 'harvest':
        pos = action[1]
        resource = state.resource_at(pos)
        return HARVEST_ACTIONS[resource]['cost']
    if action_type in ('found_city', 'expand_borders'):
        return 0
    raise ValueError(f"Unknown action type: {action_type}")


BUILDING_POPULATION = {
    'lumber_hut': 1,
    'farm': 2,
    'mine': 2,
}


def action_population(action, state):
    action_type = action[0]
    if action_type == 'build':
        pos, building = action[1], action[2]
        if building in BUILDING_POPULATION:
            return BUILDING_POPULATION[building]
        if is_multiplier(building):
            # Simulate placing the building to compute its level
            from dataclasses import replace
            new_state = replace(state, buildings={**state.buildings, pos: building})
            return multiplier_level(pos, new_state)
        return 0
    if action_type == 'harvest':
        pos = action[1]
        resource = state.resource_at(pos)
        return HARVEST_ACTIONS[resource]['population']
    return 0


def sequence_population(actions, initial_state):
    total = 0
    state = initial_state
    for action in actions:
        total += action_population(action, state)
        state = apply_action(state, action)
    return total


def sequence_cost(actions, initial_state):
    total = 0
    state = initial_state
    for action in actions:
        total += action_cost(action, state)
        state = apply_action(state, action)
    return total
