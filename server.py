from flask import Flask, request, jsonify
from solver import optimise

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

if __name__ == '__main__':
    app.run(debug=True)
