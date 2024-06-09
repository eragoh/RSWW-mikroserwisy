from flask import Flask, jsonify, Response, request
from flask_pymongo import PyMongo, ObjectId
from bson import json_util
from datetime import datetime
import requests
import pika
import redis
import json
import threading
import uuid
import asyncio
import logging
import sys
from collections import Counter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
RABBIT_HOST = 'rabbitmq-gateway'

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://user:password@180140_travel-mongo:27017/TravelDB"
redis_client = redis.StrictRedis(host='redis-service', port=6379, db=0)
rabbit_connection_params = pika.ConnectionParameters(
    RABBIT_HOST,
    port=5672,
    credentials=pika.PlainCredentials('admin', 'password'))

mongo = PyMongo(app)

def listen_for_results():
    logger.info("i ASD 0")
    logger.error("e ASD 0")
    logger.debug("d ASD 0")
    try:
        connection = pika.BlockingConnection(rabbit_connection_params)
        channel = connection.channel()
        channel.queue_declare(queue='result_queue', durable=True)

        def callback(ch, method, properties, body):
            result = json.loads(body)
            event_id = result['event_id']
            redis_client.set(event_id, body)

        channel.basic_consume(queue='result_queue', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    except Exception as e:
        logging.error(f"Failed to connect to RabbitMQ: {e}")
    
listener_thread = threading.Thread(target=listen_for_results)
listener_thread.daemon = True
listener_thread.start()

async def get_response_from_redis(event_id):
    while True:
        result = redis_client.get(event_id)
        if result:
            logger.info("GOT EVENT!")
            return json.loads(result)

        await asyncio.sleep(1)  # Delay before checking again

def publish_topic_event(event, routing_key, exchange_name='order'):
    connection = pika.BlockingConnection(rabbit_connection_params)
    channel = connection.channel()
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=json.dumps(event))
    logger.info(f"PUBLISHED: {event} // KEY: {routing_key}")
    connection.close()

async def rabbit_message(routing_key, message, **kwargs):
    event_id = str(uuid.uuid4())
    event = {'event_id' : event_id}
    for kwarg in kwargs:
        event[kwarg] = kwargs[kwarg]
    logger.info("PUBLISH EVENT[%s] (%s) - %s", message, event_id, str(event))
    publish_topic_event(event, routing_key)
    logger.info("WAITING[%s] (%s)", message, event_id)
    try:
        response_event = await asyncio.wait_for(get_response_from_redis(event_id), timeout=10000)
    except asyncio.TimeoutError as e:
        logger.info(f"ERROR[{message}]: {e}")
        return jsonify({'error': f'Timeout while waiting for response: {e}'})
    logger.info("RESPONSE[%s] (%s): %s", message, event_id, str(response_event))
    response_event.pop('event_id', None)
    return response_event

def rabbit_message_no_answer(routing_key, message, **kwargs):
    event_id = str(uuid.uuid4())
    event = {'event_id' : event_id}
    for kwarg in kwargs:
        event[kwarg] = kwargs[kwarg]
    logger.info("PUBLISH EVENT[%s] (%s) - %s", message, event_id, str(event))
    publish_topic_event(event, routing_key)


def get_price(offer):
    base_price = offer.get('price', 4500)
    start_date = datetime.strptime(offer['start_date'], "%Y-%m-%d")
    end_date = datetime.strptime(offer['end_date'], "%Y-%m-%d")
    start_month = start_date.month
    end_month = end_date.month

    # Define a helper function to get seasonal factors
    def get_seasonal_factor(month):
        if month in [6, 7, 8]:  # Summer
            return 1.2
        elif month in [12, 1, 2]: # Winter
            return 1.1
        return 1.0

    # Average the seasonal factors of start and end months
    seasonal_factor = (get_seasonal_factor(start_month) + get_seasonal_factor(end_month)) / 2

    config_adjustment = 0
    if offer['room']['is_family']:
        config_adjustment += 200
    elif offer['room']['is_standard']:
        config_adjustment += 400
    elif offer['room']['is_apartment']:
        config_adjustment += 900

    score_factor = offer['score']/5 * 0.89

    total_price = (base_price + config_adjustment) * seasonal_factor * score_factor
    total_price = round(total_price) + 0.99
    return total_price

def update_room(room):
    if 'Standardowy' in room:
        return 'is_standard'
    if 'Apartament' in room:
        return 'is_apartment'
    if 'Rodzinny' in room:
        return 'is_family'
    if 'Studio' in room:
        return 'is_studio'

def update_room_back(room):
    if 'is_standard' in room:
        return 'Standardowy'
    if 'is_apartment' in room:
        return 'Apartament'
    if 'is_family' in room:
        return 'Rodzinny'
    if 'is_studio' in room:
        return 'Studio'

@app.route('/')
def hello_world():
    return 'Hello, Gateway!'

@app.route('/getprice/')
def getprice():
    sum = 0
    room = request.args.get('room')
    price = float(request.args.get('price'))
    if 'Apartament' in room:
        price += 900
    elif 'Rodzinny' in room:
        price += 200
    elif 'Standardowy' in room:
        price += 400
    elif 'Studio' in room:
        price += 0

    data = {}
    for arg in ('adults', 'ch3', 'ch10', 'ch18'):
        data[arg] = int(request.args.get(arg))

    sum += data['adults'] * price
    sum += data['ch3'] * price * 0.5
    sum += data['ch10'] * price * 0.7
    sum += data['ch18'] * price * 0.8   
    return jsonify({'price' : sum})

@app.route('/operations/')
async def operations():
    response_event = await rabbit_message('operations', 'operations')
    return response_event

@app.route('/data/countries')
async def get_countries():
    response_event = await rabbit_message('countries', 'countries')
    return Response(json_util.dumps(response_event['countries']), mimetype='application/json')

@app.route('/watch/<tourname>')
async def watch(tourname):
    response_event = await rabbit_message('watch', 'watch',
        tourname=tourname
    )
    return response_event

@app.route('/watch_check/<tourname>')
async def watch_check(tourname):
    response_event = await rabbit_message('watch_check', 'watch_check',
        tourname=tourname                               
    )
    return response_event

@app.route('/watch_end/<tourname>')
async def watch_end(tourname):
    rabbit_message_no_answer('watch_end', 'watch_end',
        tourname=tourname                               
    )
    return jsonify({'State': 'Ok'})

@app.route('/data/reserved_rooms/<tour>')
async def get_tour_reserved_rooms(tour):
    reserved_rooms = await rabbit_message('reserved_rooms', 'reserved_rooms', trip_id=tour)
    to_rooms = await rabbit_message('rooms', 'rooms', trip_id=tour)
    try:
        rooms = {
            key : to_rooms['room'].get(key, 0) - reserved_rooms['results'].get(update_room_back(key), 0)
            for key in ('is_apartment', 'is_family', 'is_standard', 'is_studio')
        }
        return jsonify(rooms)
    except KeyError as e:
        logger.error(f'get_tour_reserved_rooms[KeyError] - {e}')
        return jsonify({'error': f"Key error: {e.args[0]}"}), 400
    except Exception as e:
        logger.error(f'get_tour_reserved_rooms[Exception] - {e}')
        return jsonify({'error': str(e)}), 400


@app.route('/data/tours/<tour>') #mongo
def get_data_tour(tour):
    try:
        some_data = mongo.db.travelOffers.find_one({"_id": ObjectId(tour)})
        some_data['price'] = get_price(some_data)
    except:
        return get_data()
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(some_data), mimetype='application/json')


def search(request):
    country = request.args.get('country')
    start_date  = request.args.get('start_date')
    return_date = request.args.get('return_date')
    adults      = request.args.get('adults')
    children3   = request.args.get('children3')
    children10  = request.args.get('children10')
    children18  = request.args.get('children18')
    departue    = request.args.get('departue')
    search_dict = {}
    try:
        if country:
            search_dict['country'] = country
        if departue:
            search_dict['departure_location'] = departue
        if start_date:
            search_dict['start_date'] = {'$gte': start_date}
        if return_date:
            search_dict['end_date'] = {'$lte': return_date}
        if adults:
            search_dict['adults'] = {'$gte': int(adults)}
        if children3:
            search_dict['children_under_3'] = {'$gte': int(children3)}
        if children10:
            search_dict['children_under_10'] = {'$gte': int(children10)}
        if children18:
            search_dict['children_under_18'] = {'$gte': int(children18)}
        logger.info(f'SEARCH: {search_dict}')
        some_data = [
            {**offer, 'price': get_price(offer)} 
            for offer in 
            list(mongo.db.travelOffers.find(search_dict))
        ]
    except:
        return None
    
    return some_data

@app.route('/data/tours/parameters') #mongo
def get_parametrized_data():
    some_data = search(request)
    if some_data is None:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(some_data), mimetype='application/json')

def get_tour(tour_id):
    some_data = mongo.db.travelOffers.find_one({"_id": ObjectId(tour_id)})
    country = some_data['country']
    departure_location = some_data['departure_location']
    score = some_data['score']
    return country, departure_location, score

def get_recommendation_value(tour, sorted_countries, sorted_departure_locations, sorted_rooms, sorted_score):
    value = 0
    country_c = 1.5
    dl_c = 1.2
    room_c = 0.5
    score_c = 0.6
    for country, count in sorted_countries:
        if country == tour['country']:
            value += count * country_c
            break
    for dl, count in sorted_departure_locations:
        if dl == tour['departure_location']:
            value += count * dl_c
            break
    for room, count in sorted_rooms:
        uroom = update_room(room)
        if tour['room'][uroom] > 0:
            value += count * room_c
            break
    for score, count in sorted_score:
        if tour['score'] == score:
            value += count * score_c
            break
    return value

def recommended_tours(tours, mytours_data):
    logger.info(f'TOURS: {tours}')

    mytours = []
    for result in mytours_data:
        tour_result = get_tour(result[2])
        mytours.append({
            'room': result[4],
            'country': tour_result[0],
            'departure_location': tour_result[1],
            'score': tour_result[2],
        })
    countries_count = Counter(item['country'] for item in mytours)
    sorted_countries = sorted(countries_count.items(), key=lambda x: x[1], reverse=True)
    departure_locations_count = Counter(item['departure_location'] for item in mytours)
    sorted_departure_locations = sorted(departure_locations_count.items(), key=lambda x: x[1], reverse=True)
    rooms_count = Counter(item['room'] for item in mytours)
    sorted_rooms = sorted(rooms_count.items(), key=lambda x: x[1], reverse=True)
    score_count = Counter(item['room'] for item in mytours)
    sorted_scores = sorted(score_count.items(), key=lambda x: x[1], reverse=True)

    sorted_tours = sorted(tours, key=lambda x: get_recommendation_value(x, sorted_countries, sorted_departure_locations, sorted_rooms, sorted_scores), reverse=True)
    return sorted_tours

@app.route('/data/tours/parameters/login') #mongo
async def get_parametrized_recommended_data():
    username = request.args.get('username')
    some_data = search(request)
    response_event = await rabbit_message('myreservations', 'get_parametrized_recommended_data',
        username = username
    )

    tours = recommended_tours(some_data, response_event['results'])

    if some_data is None:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(tours), mimetype='application/json')

@app.route('/data/<page>') #mongo
def get_data_page(page):
    try:
        some_data = [
            {**offer, 'price': get_price(offer)}
            for offer in 
            list(mongo.db.travelOffers.find().skip(int(page) * 10).limit(10))
        ]
    except:
        return get_data()
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    
    return Response(json_util.dumps(some_data), mimetype='application/json')

@app.route('/data/login/<page>') #mongo
async def get_data_login_page(page):
    username = request.args.get('username')
    try:
        some_data = [
            {**offer, 'price': get_price(offer)}
            for offer in 
            list(mongo.db.travelOffers.find())
        ]
        response_event = await rabbit_message('myreservations', 'get_parametrized_recommended_data',
            username = username
        )
        tours = recommended_tours(some_data, response_event['results'])
    except:
        return get_data()
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    page = int(page)
    logger.info('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    logger.info('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    logger.info('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    logger.info(tours)
    logger.info(f'{len(tours)} | {10 * page} | {10 * (page + 1)}')
    logger.info(tours[10 * page : 10 * (page + 1)])
    logger.info('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    logger.info('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    logger.info('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    return Response(json_util.dumps(tours[10 * page : 10 * (page + 1)]), mimetype='application/json')

@app.route('/data/')
def get_data():
    some_data = [
            {**offer, 'price': get_price(offer)} 
            for offer in 
            list(mongo.db.travelOffers.find().limit(10))
        ]
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(some_data), mimetype='application/json')

@app.route('/reservation/add/')
async def add_reservation():
    response_event = await rabbit_message('reservation_add', 'reservation_add',
        username=request.args.get('username'),
        trip_id=request.args.get('trip_id'),
        price=request.args.get('price'),
        room=request.args.get('room'),
        adults=request.args.get('adults'),
        ch3=request.args.get('ch3'),
        ch10=request.args.get('ch10'),
        ch18=request.args.get('ch18')                                     
    )
    return response_event

@app.route('/reservation/check/')
async def check_reservation():
    response_event = await rabbit_message('check_reservation', 'check_reservation',
        username=request.args.get('username'),
        trip_id=request.args.get('trip_id'),
        room=request.args.get('room')
    )
    return response_event

@app.route('/reservation/pay/', methods=['POST'])
async def pay_reservation():
    response_event = await rabbit_message('payment', 'payment',
        trip_id = request.form.get('trip_id'),
        card_number = request.form.get('card_number'),
        price = request.form.get('price'),
        room = request.form.get('room')              
    )
    return response_event

@app.route('/getmytours/')
async def getmytours():
    response_event = await rabbit_message('myreservations', 'myreservations',
        username = request.args.get('username')
    )
    tours = [
        {
            'name':   result[2],
            'price':  result[3],
            'room':   result[4],
            'paid':   result[5],
            'adults': result[6],
            'ch3':    result[7],
            'ch10':   result[8],
            'ch18':   result[9],
        }
        for result in response_event['results']
    ]
    logger.info(f"RESPONSE TOURS: {tours}")
    return jsonify(tours)


def setup_topic_exchange_and_queues(exchange_name='order'):
    connection = pika.BlockingConnection(rabbit_connection_params)
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)

    # Declare queues and bind with routing keys based on patterns
    queues = {
        'result_queue': ['result', 'reservation_paid'],
        'reservation_queue': [
            'reservation_add',
            'reservation_info',
            'reservation_paid',
            'myreservations',
            'reserved_rooms',
            'check_reservation',
        ],
        'watch_queue': ['watch', 'watch_end', 'watch_check'],
        'payment_queue': ['payment'],
        'toc_service_queue': ['buy', 'operations', 'countries', 'rooms']
    }

    for queue, routing_keys in queues.items():
        channel.queue_declare(queue=queue, durable=True)
        if isinstance(routing_keys, list):
            for routing_key in routing_keys:
                channel.queue_bind(exchange=exchange_name, queue=queue, routing_key=routing_key)
        else:
            channel.queue_bind(exchange=exchange_name, queue=queue, routing_key=routing_keys)

    connection.close()

logger.debug(f"NAME: %s", __name__)
logger.info(f"ASD 1")
setup_topic_exchange_and_queues()
logger.info(f"ASD 2")
