from dataclasses import replace


def make_action(action_type, *args):
    return (action_type, *args)


def apply_action(state, action):
    action_type = action[0]
    if action_type == 'build':
        pos, building = action[1], action[2]
        new_buildings = {**state.buildings, pos: building}
        return replace(state, buildings=new_buildings)
    raise ValueError(f"Unknown action type: {action_type}")
