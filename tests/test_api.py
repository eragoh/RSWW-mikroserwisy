import pytest
from frontend.app.api import api
from flask import Flask

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(api, url_prefix='/api')
    with app.test_client() as client:
        yield client

def test_getcountries(client):
    response = client.get('/api/getcountries/')
    assert response.status_code == 200

def test_tour_detail(client):
    response = client.get('/api/tours/testtour/get/')
    assert response.status_code == 200

def test_getprice(client):
    response = client.get('/api/getprice?adults=2&ch3=1&ch10=0&ch18=0&price=100')
    assert response.status_code == 200
