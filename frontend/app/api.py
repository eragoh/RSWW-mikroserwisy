import aiohttp
from flask import Blueprint, request, jsonify
from app import logger

async def get_response(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    json_data = await response.json()
                    logger.info(f"RESPONSE 55: {json_data}")
                    return json_data
    except aiohttp.ClientError as e:
        return {'error': f'Bad request - {e}'}
    return {'error': 'Bad request'}

async def post_response(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    json_data = await response.json()
                    logger.info(f"RESPONSE POST 55: {json_data}")
                    return json_data
    except aiohttp.ClientError as e:
        return {'error': f'Bad request - {e}'}
    return {'error': 'Bad request'}

api = Blueprint('api', __name__)

@api.route('/operations/')
async def operations():
    #return await get_response(f'http://toc-service:7777/operations/')
    return await get_response(f'http://gateway-api:6543/operations/')

@api.route('/getcountries/')
async def getcountries():
    #return await get_rmq_response('countries')
    return await get_response(f'http://gateway-api:6543/data/countries')

@api.route('/tours/<tourname>/get/')
async def tour_detail(tourname):
    #return await get_rmq_response('data_tour')
    return await get_response(f'http://gateway-api:6543/data/tours/{tourname}')

@api.route('/tours/<tourname>/reserved_rooms/')
async def reserved_rooms(tourname):
    #return await get_rmq_response('data_tour')
    return await get_response(f'http://gateway-api:6543/data/reserved_rooms/{tourname}')

@api.route('/gettours/')
async def gettours():
    page_number = request.args.get('page')
    page = int(page_number) if (page_number and page_number.isdigit()) else 1
    return await get_response(f'http://gateway-api:6543/data/{page - 1}')

@api.route('/gettoursparameters/',)
async def toursparameters():
    url = 'http://gateway-api:6543/data/tours/parameters?'  
    parameters = ('country', 'start_date', 'return_date', 'adults', 'children3', 'children10', 'children18', 'departue')
    for parameter in parameters:
        arg = request.args.get(parameter)
        if arg:
            url += f'{parameter}={arg}&'  

    return await get_response(url)

@api.route('/tours/<tourname>/minute/')
async def oneminute_clock(tourname):
    url = f'http://gateway-api:6543/clock/{tourname}'
    return await get_response(url)

@api.route('/getprice/')
async def getprice():

    data = {}
    for arg in ('adults', 'ch3', 'ch10', 'ch18'):
        try:
            val = request.args.get(arg)
            data[arg] = int(val) if val and val.isdigit() else 0
        except:
            data[arg] = 0
    room = request.args.get('room')
    
    try:
        pval = float(request.args.get('price'))
        data['price'] = pval
    except:
        return jsonify({'Error': 'Error'})
    
    data['room'] = room if room else 'Standardowy'
    parameters = ''
    for key in data:
        parameters += f'{key}={data[key]}&'

    url = 'http://gateway-api:6543/getprice?' + parameters
    return await get_response(url)
