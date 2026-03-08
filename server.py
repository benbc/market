from flask import Flask, request, jsonify
from map_state import MapState
from optimizer import optimize as run_optimize
from economics import total_income, sequence_cost, market_income, multiplier_level
from rules import MAP_SHAPES, is_multiplier

app = Flask(__name__, static_folder='static', static_url_path='')


@app.route('/')
def index():
    return app.send_static_file('index.html')


def _state_from_json(data):
    """Convert JSON request data into a MapState."""
    terrain = {}
    resources = {}
    for t in data.get('tiles', []):
        pos = (t['row'], t['col'])
        terrain[pos] = t['terrain']
        if 'resource' in t:
            resources[pos] = t['resource']

    cities = tuple(data.get('cities', []))
    villages = frozenset(
        (v['row'], v['col']) for v in data.get('villages', [])
    )
    monuments = frozenset(
        (m['row'], m['col']) for m in data.get('monuments', [])
    )
    lighthouses = frozenset(
        (l['row'], l['col']) for l in data.get('lighthouses', [])
    )
    buildings = {}
    for p in data.get('pinned', []):
        buildings[(p['row'], p['col'])] = p['building']

    return MapState(
        terrain=terrain,
        resources=resources,
        buildings=buildings,
        cities=cities,
        villages=villages,
        monuments=monuments,
        lighthouses=lighthouses,
    )


@app.post('/optimize')
def optimize_endpoint():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    state = _state_from_json(data)
    techs = frozenset(data.get('techs', []))
    initial = state

    def score(state, actions):
        income = total_income(state)
        building_value = sum(
            multiplier_level(pos, state) if is_multiplier(bldg) else 1
            for pos, bldg in state.buildings.items()
        )
        cost = sequence_cost(actions, initial)
        return (income, building_value, -cost)

    result = run_optimize(state, techs, score)

    placements = [
        {'row': pos[0], 'col': pos[1], 'building': bldg}
        for pos, bldg in result['state'].buildings.items()
    ]
    markets = []
    for pos, bldg in result['state'].buildings.items():
        if bldg == 'market':
            markets.append({
                'row': pos[0], 'col': pos[1],
                'income': market_income(pos, result['state']),
            })

    return jsonify({
        'placements': placements,
        'markets': markets,
        'total_income': result['income'],
        'total_cost': sequence_cost(result['actions'], initial),
        'actions': [list(a) for a in result['actions']],
    })


@app.post('/territory')
def territory():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    state = _state_from_json(data)
    ownership = state.territory_ownership()
    return jsonify({
        'ownership': {f"{r},{c}": city_id for (r, c), city_id in ownership.items()}
    })


@app.get('/rules/map-shapes')
def map_shapes():
    return jsonify({'shapes': sorted(MAP_SHAPES)})


if __name__ == '__main__':
    app.run(debug=True)
