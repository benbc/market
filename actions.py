from dataclasses import replace

from rules import (
    can_build, techs_unlocking_building, techs_unlocking_action,
    ONE_PER_CITY, HARVEST_ACTIONS,
)


def make_action(action_type, *args):
    return (action_type, *args)


def apply_action(state, action):
    action_type = action[0]
    if action_type == 'build':
        pos, building = action[1], action[2]
        new_buildings = {**state.buildings, pos: building}
        return replace(state, buildings=new_buildings)
    if action_type == 'found_city':
        pos = action[1]
        next_id = max((c['id'] for c in state.cities), default=0) + 1
        new_city = {'id': next_id, 'row': pos[0], 'col': pos[1], 'population': 1, 'border_level': 1}
        new_cities = state.cities + (new_city,)
        new_villages = state.villages - {pos}
        return replace(state, cities=new_cities, villages=new_villages)
    if action_type == 'expand_borders':
        city_id = action[1]
        new_cities = tuple(
            {**c, 'border_level': c['border_level'] + 1} if c['id'] == city_id else c
            for c in state.cities
        )
        return replace(state, cities=new_cities)
    if action_type == 'harvest':
        pos = action[1]
        new_resources = {p: r for p, r in state.resources.items() if p != pos}
        return replace(state, resources=new_resources)
    if action_type == 'clear_forest':
        pos = action[1]
        new_resources = {p: r for p, r in state.resources.items() if p != pos}
        return replace(state, resources=new_resources)
    if action_type == 'burn_forest':
        pos = action[1]
        new_resources = {**state.resources, pos: 'crop'}
        return replace(state, resources=new_resources)
    if action_type == 'grow_forest':
        pos = action[1]
        new_resources = {**state.resources, pos: 'forest'}
        return replace(state, resources=new_resources)
    raise ValueError(f"Unknown action type: {action_type}")


def validate_action(state, action, techs):
    """Return None if action is legal, or an error string if not."""
    action_type = action[0]

    if action_type == 'build':
        pos, building = action[1], action[2]
        if state.terrain_at(pos) is None:
            return f"No terrain at {pos}"
        ownership = state.territory_ownership()
        if pos not in ownership:
            return f"{pos} is not in any city's territory"
        if pos in state.occupied_positions():
            return f"{pos} is already occupied"
        required_techs = techs_unlocking_building(building)
        if required_techs and not required_techs & techs:
            return f"Missing tech for {building}"
        terrain = state.terrain_at(pos)
        resource = state.resource_at(pos)
        if not can_build(building, terrain, resource):
            return f"Cannot build {building} on {terrain}/{resource}"
        if building in ONE_PER_CITY:
            city_id = ownership[pos]
            city_tiles = state.tiles_owned_by(city_id)
            for t in city_tiles:
                if state.building_at(t) == building:
                    return f"City {city_id} already has a {building}"
        return None

    if action_type in ('clear_forest', 'burn_forest'):
        pos = action[1]
        if state.resource_at(pos) != 'forest':
            return f"No forest at {pos}"
        required_techs = techs_unlocking_action(action_type)
        if required_techs and not required_techs & techs:
            return f"Missing tech for {action_type}"
        ownership = state.territory_ownership()
        if pos not in ownership:
            return f"{pos} is not in any city's territory"
        return None

    if action_type == 'grow_forest':
        pos = action[1]
        if state.terrain_at(pos) != 'land':
            return f"Can only grow forest on land"
        if state.resource_at(pos) is not None:
            return f"Tile {pos} already has a resource"
        if pos in state.occupied_positions():
            return f"{pos} is already occupied"
        required_techs = techs_unlocking_action(action_type)
        if required_techs and not required_techs & techs:
            return f"Missing tech for grow_forest"
        ownership = state.territory_ownership()
        if pos not in ownership:
            return f"{pos} is not in any city's territory"
        return None

    if action_type == 'found_city':
        pos = action[1]
        if pos not in state.villages:
            return f"No village at {pos}"
        return None

    if action_type == 'expand_borders':
        city_id = action[1]
        for c in state.cities:
            if c['id'] == city_id:
                return None
        return f"No city with id {city_id}"

    if action_type == 'harvest':
        pos = action[1]
        resource = state.resource_at(pos)
        if resource not in HARVEST_ACTIONS:
            return f"No harvestable resource at {pos}"
        h = HARVEST_ACTIONS[resource]
        if h['tech'] not in techs:
            return f"Missing tech {h['tech']} for harvesting {resource}"
        ownership = state.territory_ownership()
        if pos not in ownership:
            return f"{pos} is not in any city's territory"
        return None

    return f"Unknown action type: {action_type}"
