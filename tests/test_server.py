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
            {'row': 0, 'col': 0, 'terrain': 'field'},
            {'row': 0, 'col': 1, 'terrain': 'field'},
        ],
        'cities': [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}],
    }
    resp = client.post('/optimize', json=payload)
    assert resp.status_code == 200

def test_optimize_returns_expected_keys(client):
    payload = {
        'tiles': [{'row': 0, 'col': 0, 'terrain': 'field'}],
        'cities': [{'id': 1, 'row': 0, 'col': 0, 'expanded': False}],
    }
    data = client.post('/optimize', json=payload).get_json()
    assert 'placements' in data
    assert 'markets' in data
    assert 'total_income' in data

def test_optimize_bad_request(client):
    resp = client.post('/optimize', data='not json', content_type='text/plain')
    assert resp.status_code == 400
