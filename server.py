from flask import Flask, request, jsonify
from solver import optimise, assign_ownership

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.post('/optimize')
def optimize():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    result = optimise(data)
    return jsonify(result)

@app.post('/territory')
def territory():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    tile_positions = [(t['row'], t['col']) for t in data.get('tiles', [])]
    cities = data.get('cities', [])
    events = data.get('events')
    ownership = assign_ownership(tile_positions, cities, events)
    return jsonify({
        'ownership': {f"{r},{c}": city_id for (r, c), city_id in ownership.items()}
    })

if __name__ == '__main__':
    app.run(debug=True)
