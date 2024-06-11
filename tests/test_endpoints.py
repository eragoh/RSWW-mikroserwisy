import pytest
import requests
import uuid

# Poprawny BASE_URL na podstawie nazwy kontenera i portu z docker-compose.yml
BASE_URL = 'http://180140_gateway-api:6543'

def test_test():
    assert 1 == 1

def test_getcountries():
    response = requests.get(f'{BASE_URL}/data/countries')
    assert response.status_code == 200

def test_tours_detail():
    response = requests.get(f'{BASE_URL}/data/tours/tourtest')
    assert response.status_code == 200
    assert len(response.json()) == 10

def test_reserved_rooms():
    response = requests.get(f'{BASE_URL}/data/reserved_rooms/testtour')
    assert response.status_code == 200

def test_gettours():
    response = requests.get(f'{BASE_URL}/data/0')
    assert response.status_code == 200

def test_toursparameters():
    params = {
        'country': 'Albania',
    }
    response = requests.get(f'{BASE_URL}/data/tours/parameters', params=params)
    assert response.status_code == 200

def test_getprice():
    params = {
        'adults': '2',
        'ch3': '1',
        'ch10': '0',
        'ch18': '0',
        'price': '100',
        'room': 'Standardowy'
    }
    response = requests.get(f'{BASE_URL}/getprice', params=params)
    assert response.status_code == 200

def test_gettours():
    response = requests.get(f'{BASE_URL}/data')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'

def test_operations():
    response = requests.get(f'{BASE_URL}/operations')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'

def test_watch():
    response = requests.get(f'{BASE_URL}/watch/tour')
    assert response.status_code == 200

def test_data_page():
    response = requests.get(f'{BASE_URL}/data/2')
    assert response.status_code == 200
    assert len(response.json()) == 10

def test_add_taken_reservation():
    params = {
        'username': 'username',
        'trip_id': 'trip_id',
        'adults': '2',
        'ch3': '1',
        'ch10': '0',
        'ch18': '0',
        'price': '100',
        'room': 'Standardowy'
    }
    response = requests.get(f'{BASE_URL}/reservation/add', params=params)
    response = requests.get(f'{BASE_URL}/reservation/add', params=params)
    assert response.status_code == 200
    assert response.json()['status'] == 'TAKEN'
    
def test_add_reservation():
    params = {
        'username': 'username',
        'trip_id': str(uuid.uuid4()),
        'adults': '2',
        'ch3': '1',
        'ch10': '0',
        'ch18': '0',
        'price': '100',
        'room': 'Standardowy'
    }
    response = requests.get(f'{BASE_URL}/reservation/add', params=params)
    assert response.status_code == 200
    assert response.json()['status'] == 'RESERVED'

def test_check_reservation():
    params = {
        'username': 'username',
        'trip_id': 'trip_id',
        'room': 'Standardowy'
    }
    response = requests.get(f'{BASE_URL}/reservation/check', params=params)
    assert response.status_code == 200
    assert response.json()['result'] != None

def test_check_no_reservation():
    params = {
        'username': 'username',
        'trip_id': str(uuid.uuid4()),
        'room': 'Standardowy'
    }
    response = requests.get(f'{BASE_URL}/reservation/check', params=params)
    assert response.status_code == 200
    assert response.json()['result'] == None

def test_reservation_pay():
    params = {
        'trip_id': 'trip_id',
        'card_number': 'card_number',
        'price': '100',
        'room': 'Standardowy'
    }
    response = requests.post(f'{BASE_URL}/reservation/pay/', json=params)
    assert response.status_code == 200

def test_getmytours():
    params = {
        'username': 'user9',
    }
    response = requests.get(f'{BASE_URL}/getmytours/', params=params)
    assert response.status_code == 200
