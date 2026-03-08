from dataclasses import replace


def make_action(action_type, *args):
    return (action_type, *args)


def apply_action(state, action):
    action_type = action[0]
    if action_type == 'build':
        pos, building = action[1], action[2]
        new_buildings = {**state.buildings, pos: building}
        return replace(state, buildings=new_buildings)
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
