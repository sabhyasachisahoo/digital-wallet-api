import base64
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def client():
    # Set up app context and test client
    app = create_app()
    with app.app_context():
        db.drop_all()       # Reset DB before each test
        db.create_all()
        test_client = app.test_client()
        yield test_client   # Yield for testing
        db.session.remove() # Cleanup

def auth_header(username, password):
    token = base64.b64encode(f'{username}:{password}'.encode()).decode()
    return {'Authorization': f'Basic {token}'}

def test_register_and_fund(client):
    # Register
    res = client.post('/register', json={"username": "ashu", "password": "hunter2"})
    assert res.status_code == 201

    # Fund wallet
    res = client.post('/fund', headers=auth_header("ashu", "hunter2"), json={"amt": 500})
    assert res.status_code == 200
    assert res.get_json()['balance'] == 500

def test_payment_between_users(client):
    # Register both users
    client.post('/register', json={"username": "ashu", "password": "hunter2"})
    client.post('/register', json={"username": "priya", "password": "123456"})

    # Fund ashu's wallet
    client.post('/fund', headers=auth_header("ashu", "hunter2"), json={"amt": 1000})

    # Pay to priya
    res = client.post('/pay', headers=auth_header("ashu", "hunter2"), json={"to": "priya", "amt": 300})
    assert res.status_code == 200
    assert res.get_json()['balance'] == 700

def test_add_and_buy_product(client):
    client.post('/register', json={"username": "ashu", "password": "hunter2"})
    client.post('/fund', headers=auth_header("ashu", "hunter2"), json={"amt": 1000})

    # Add a product
    res = client.post('/product', headers=auth_header("ashu", "hunter2"), json={
        "name": "USB Cable",
        "price": 200,
        "description": "Fast charging USB-C"
    })
    assert res.status_code == 201
    product_id = res.get_json()['id']

    # Buy the product
    res = client.post('/buy', headers=auth_header("ashu", "hunter2"), json={"product_id": product_id})
    assert res.status_code == 200
    assert "Product purchased" in res.get_json()['message']
