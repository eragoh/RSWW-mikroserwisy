from flask import(
    Flask,
    render_template,
    request,
    jsonify
)
import asyncio
import aiohttp
import json

from rabbitmqclient import RClient

app = Flask(__name__)

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
async def arender(html, data):
    task = asyncio.to_thread(render_template, html, data=data)
    return await task

async def get_rmq_response(qname, n=None):
    rclient = RClient()
    try:
        await rclient.connect()
        response = await rclient.call(n, qname=qname)    
    except Exception as e:
        return f"Error: {e}"
    finally:
        await rclient.close()
    
    return json.loads(response.decode())


@app.route('/')
async def index():
    data = {
        'is_authenticated' : True
    }
    return await arender('index.html', data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print('login', request)
    
    data = {

    }
    return render_template('login.html', data=data)

@app.route('/register')
async def register():
    return await arender('register.html', {})

@app.route('/tours/')
async def tours():
    page_number = request.args.get('page')
    page = int(page_number) if (page_number and page_number.isdigit()) else 1
    data = {
        'is_authenticated' : False,
        'page' : page
    }
    return await arender('tours.html', data=data)
  
@app.route('/gettoursparameters/',)
async def toursparameters():
    url = 'http://gateway-api:6543/data/tours/parameters?'  
    parameters = ('country', 'start_date', 'return_date', 'adults', 'children')
    for parameter in parameters:
        arg = request.args.get(parameter)
        if arg:
            url += f'{parameter}={arg}&'  

    return await get_response(url)

@app.route('/tours/<tourname>')
async def tours_detail(tourname):
    return await arender('tour_detail.html', {})

@app.route('/tours/<tourname>/get/')
async def tour_detail(tourname):
    #return await get_rmq_response('data_tour')
    return await get_response(f'http://gateway-api:6543/data/tours/{tourname}')

@app.route('/getcountries/')
async def getcountries():
    return await get_rmq_response('countries')
    #return await get_response(f'http://gateway-api:6543/data/countries')

@app.route('/gettours/')
async def gettours():
    page_number = request.args.get('page')
    page = int(page_number) if (page_number and page_number.isdigit()) else 1
    return await get_response(f'http://gateway-api:6543/data/{page - 1}')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def catch_all(path):
    return await arender('404.html', {})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
