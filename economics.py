from map_state import adjacent_positions
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
