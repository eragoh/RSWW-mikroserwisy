import pytest
import requests

# Poprawny BASE_URL na podstawie nazwy kontenera i portu z docker-compose.yml
BASE_URL = 'http://180140_gateway-api:6543'

def test_getcountries():
    response = requests.get(f'{BASE_URL}/data/countries')
    assert response.status_code == 200

def test_tour_detail():
    response = requests.get(f'{BASE_URL}/data/tours/testtour')
    assert response.status_code == 200

def test_reserved_rooms():
    response = requests.get(f'{BASE_URL}/data/reserved_rooms/testtour')
    assert response.status_code == 200

def test_gettours():
    response = requests.get(f'{BASE_URL}/data/0')
    assert response.status_code == 200

def test_toursparameters():
    params = {
        'country': 'Poland',
        'start_date': '2022-01-01',
        'return_date': '2022-01-10',
        'adults': '2',
        'children3': '1',
        'children10': '0',
        'children18': '0',
        'departue': 'Warsaw'
    }
    response = requests.get(f'{BASE_URL}/data/tours/parameters', params=params)
    assert response.status_code == 200

def test_oneminute_clock():
    response = requests.get(f'{BASE_URL}/clock/testtour')
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
