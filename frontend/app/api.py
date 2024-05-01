import aiohttp
from flask import Blueprint, request

async def get_response(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    json_data = await response.json()
                    return json_data
    except aiohttp.ClientError as e:
        return f"Bad request - {e}"
    return "Bad request"

api = Blueprint('api', __name__)

@api.route('/getcountries/')
async def getcountries():
    #return await get_rmq_response('countries')
    return await get_response(f'http://gateway-api:6543/data/countries')

@api.route('/tours/<tourname>/get/')
async def tour_detail(tourname):
    #return await get_rmq_response('data_tour')
    return await get_response(f'http://gateway-api:6543/data/tours/{tourname}')

@api.route('/gettours/')
async def gettours():
    page_number = request.args.get('page')
    page = int(page_number) if (page_number and page_number.isdigit()) else 1
    return await get_response(f'http://gateway-api:6543/data/{page - 1}')

@api.route('/gettoursparameters/',)
async def toursparameters():
    url = 'http://gateway-api:6543/data/tours/parameters?'  
    parameters = ('country', 'start_date', 'return_date', 'adults', 'children')
    for parameter in parameters:
        arg = request.args.get(parameter)
        if arg:
            url += f'{parameter}={arg}&'  

    return await get_response(url)

@api.route('/tours/<tourname>/minute/')
async def oneminute_clock(tourname):
    url = f'http://gateway-api:6543/clock/{tourname}'
    return await get_response(url)
