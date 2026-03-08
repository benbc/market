import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_optimize_returns_200(client):
    payload = {
        'tiles': [
            {'row': 0, 'col': 0, 'terrain': 'land'},
            {'row': 0, 'col': 1, 'terrain': 'land'},
        ],
        'cities': [{'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1}],
        'techs': ['mathematics', 'trade', 'forestry'],
    }
    resp = client.post('/optimize', json=payload)
    assert resp.status_code == 200

def test_optimize_returns_expected_keys(client):
    payload = {
        'tiles': [{'row': 0, 'col': 0, 'terrain': 'land'}],
        'cities': [{'id': 1, 'row': 0, 'col': 0, 'population': 1, 'border_level': 1}],
        'techs': [],
    }
    data = client.post('/optimize', json=payload).get_json()
    assert 'placements' in data
    assert 'markets' in data
    assert 'total_income' in data

def test_optimize_bad_request(client):
    resp = client.post('/optimize', data='not json', content_type='text/plain')
    assert resp.status_code == 400

def test_end_to_end_realistic(client):
    """
    A small realistic layout: 3x3 city with land, crops, forest, and metal.
    Expect total_income > 0 and a market placement returned.
    """
    payload = {
        'tiles': [
            {'row': 0, 'col': 0, 'terrain': 'land', 'resource': 'forest'},
            {'row': 0, 'col': 1, 'terrain': 'land'},
            {'row': 0, 'col': 2, 'terrain': 'land', 'resource': 'crop'},
            {'row': 1, 'col': 0, 'terrain': 'land'},
            {'row': 1, 'col': 1, 'terrain': 'land'},
            {'row': 1, 'col': 2, 'terrain': 'land', 'resource': 'crop'},
            {'row': 2, 'col': 0, 'terrain': 'land', 'resource': 'crop'},
            {'row': 2, 'col': 1, 'terrain': 'land'},
            {'row': 2, 'col': 2, 'terrain': 'mountain', 'resource': 'metal'},
        ],
        'cities': [{'id': 1, 'row': 1, 'col': 1, 'population': 5, 'border_level': 1}],
        'techs': ['mathematics', 'trade', 'forestry', 'farming', 'construction',
                  'mining', 'smithery', 'climbing'],
    }
    data = client.post('/optimize', json=payload).get_json()
    assert data['total_income'] > 0
    assert len(data['markets']) >= 1
    market = data['markets'][0]
    assert 0 <= market['income'] <= 8
