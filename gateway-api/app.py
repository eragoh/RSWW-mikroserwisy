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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
RABBIT_HOST = '180140_rabbitmq-gateway'


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://user:password@180140_travel-mongo:27017/TravelDB"
redis_client = redis.StrictRedis(host='180140_redis-service', port=6379, db=0)
rabbit_connection_params = pika.ConnectionParameters(
    RABBIT_HOST,
    port=5672,
    credentials=pika.PlainCredentials('admin', 'password'))

mongo = PyMongo(app)

# Listen for responses from RabbitMQ
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
    
# Start a separate thread to listen for results
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

# Publish a purchase event directly to RabbitMQ
# def publish_event_to_queue(event, queue):
#     connection = pika.BlockingConnection(rabbit_connection_params)
#     channel = connection.channel()
#     channel.queue_declare(queue=queue, durable=True)
#     channel.queue_declare(queue='result_queue', durable=True)

#     channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(event))
#     connection.close()
        

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
        'payment_queue': ['payment']
    }

    for queue, routing_keys in queues.items():
        channel.queue_declare(queue=queue, durable=True)
        if isinstance(routing_keys, list):
            for routing_key in routing_keys:
                channel.queue_bind(exchange=exchange_name, queue=queue, routing_key=routing_key)
        else:
            channel.queue_bind(exchange=exchange_name, queue=queue, routing_key=routing_keys)



    # # Publish test messages to each queue
    # test_messages = {
    #     'result_queue': {'message': 'Result test'},
    #     'reserve_queue': {'message': 'Reservation test'},
    #     'pay_queue': {'message': 'Payment test'}
    # }
    # for queue, message in test_messages.items():
    #     channel.basic_publish(exchange=exchange_name, routing_key=queues[queue], body=json.dumps(message))

    # # Checking if messages are correctly routed
    # for queue, _ in queues.items():
    #     method_frame, header_frame, body = channel.basic_get(queue=queue, auto_ack=True)
    #     if method_frame:
    #         logger.info(f"Message from {queue}: {json.loads(body)}")
    #     else:
    #         logger.info(f"No message received in {queue}")



    connection.close()


def publish_topic_event(event, routing_key, exchange_name='order'):
    connection = pika.BlockingConnection(rabbit_connection_params)
    channel = connection.channel()
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=json.dumps(event))
    logger.info(f"PUBLISHED: {event} // KEY: {routing_key}")
    connection.close()


def get_seasonal_factor(month):
    if month in [6, 7, 8]:  # Summer
        return 1.2
    elif month in [12, 1, 2]: # Winter
        return 1.1
    return 1.0

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


@app.route('/')
def hello_world():
    return 'Hello, Gateway!'

@app.route('/getprice/')
def getprice():
    sum = 0
    room = request.args.get('room')
    price = float(request.args.get('price'))
    if room == 'Apartament':
        price += 900
    elif room == 'Rodzinny':
        price += 200
    elif room == 'Standardowy':
        price += 400
    elif room == 'Studio':
        price += 0

    data = {}
    for arg in ('adults', 'ch3', 'ch10', 'ch18'):
        data[arg] = int(request.args.get(arg))

    sum += data['adults'] * price
    sum += data['ch3'] * price * 0.5
    sum += data['ch10'] * price * 0.7
    sum += data['ch18'] * price * 0.8   
    return jsonify({'price' : sum})

@app.route('/data/countries')
def get_countries():
    some_data = mongo.db.travelOffers.distinct("country")
    return Response(json_util.dumps(some_data), mimetype='application/json')

@app.route('/watch/<tourname>')
async def watch(tourname):
    event_id = str(uuid.uuid4())
    event = {
        'event_id': event_id,
        'tourname': tourname,
    }
    logger.info("WATCH (%s) - %s", tourname, event_id)
    publish_topic_event(event, 'watch')

    logger.info("WAITING")
    try:
        response_event = await asyncio.wait_for(get_response_from_redis(event_id), timeout=10000)
    except asyncio.TimeoutError as e:
        logger.info(f"ERROR: {e}")
        return jsonify({'error': f'Timeout while waiting for response: {e}'})
    
    response_event.pop('event_id', None)
    logger.info(f"RESPONSE[watch]: {response_event}")
    
    return response_event

@app.route('/watch_end/<tourname>')
async def watch_end(tourname):
    event_id = str(uuid.uuid4())
    event = {
        'event_id': event_id,
        'tourname': tourname,
    }
    logger.info("WATCH END (%s) - %s", tourname, event_id)
    publish_topic_event(event, 'watch_end')
  
    return jsonify({'State': 'Ok'})

@app.route('/watch_check/<tourname>')
async def watch_check(tourname):
    event_id = str(uuid.uuid4())
    event = {
        'event_id': event_id,
        'tourname': tourname,
    }
    logger.info("WATCH END (%s) - %s", tourname, event_id)
    publish_topic_event(event, 'watch_check')
  
    logger.info("WAITING")
    try:
        response_event = await asyncio.wait_for(get_response_from_redis(event_id), timeout=10000)
    except asyncio.TimeoutError as e:
        logger.info(f"ERROR: {e}")
        return jsonify({'error': f'Timeout while waiting for response: {e}'})
    
    response_event.pop('event_id', None)
    logger.info(f"RESPONSE[watch_check]: {response_event}")
    
    return response_event


@app.route('/data/reserved_rooms/<tour>')
async def get_tour_reserved_rooms(tour):
    event_id = str(uuid.uuid4())
    event = {
        'event_id': event_id,
        'trip_id': tour,

    }

    logger.info("CHECK RESERVED ROOMS FROM (%s) - %s", tour, event_id)
    #publish_event_to_queue(event, 'reservation_queue')
    publish_topic_event(event, 'reserved_rooms')

    logger.info("WAITING")
    try:
        response_event = await asyncio.wait_for(get_response_from_redis(event_id), timeout=10000)
    except asyncio.TimeoutError as e:
        logger.info(f"ERROR: {e}")
        return jsonify({'error': f'Timeout while waiting for response: {e}'})

    response_event.pop('event_id', None)
    logger.info(f"RESPONSE[get_tour_reserved_rooms]: {response_event}")
    return response_event


@app.route('/data/tours/<tour>')
def get_data_tour(tour):
    try:
        some_data = mongo.db.travelOffers.find_one({"_id": ObjectId(tour)})
        some_data['price'] = get_price(some_data)
    except:
        return get_data()
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(some_data), mimetype='application/json')

@app.route('/data/<page>')
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

@app.route('/data/tours/parameters')
def get_parametrized_data():
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
        some_data = [
            {**offer, 'price': get_price(offer)} 
            for offer in 
            list(mongo.db.travelOffers.find(search_dict))
        ]
    except:
        return jsonify({"error": "No data found"}), 404
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(some_data), mimetype='application/json')


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
    logger.info("RESERV-ADD")
    username = request.args.get('username')
    trip_id = request.args.get('trip_id')
    price = request.args.get('price')
    room = request.args.get('room')
    adults  = request.args.get('adults')
    ch3  = request.args.get('ch3')
    ch10 = request.args.get('ch10')
    ch18 = request.args.get('ch18')
    event_id = str(uuid.uuid4())
    event = {
        'event_id': event_id,
        'username': username,
        'trip_id': trip_id,
        'price': price,
        'room': room,
        'adults': adults,
        'ch3': ch3,
        'ch10': ch10,
        'ch18': ch18,
    }

    logger.info("PUBLISH RESERVATION: %s", event_id)
    #publish_event_to_queue(event, 'reservation_queue')
    publish_topic_event(event, 'reservation_add')

    logger.info("WAITING")
    try:
        response_event = await asyncio.wait_for(get_response_from_redis(event_id), timeout=10000)
    except asyncio.TimeoutError as e:
        logger.info(f"ERROR: {e}")
        return jsonify({'error': f'Timeout while waiting for response: {e}'})

    response_event.pop('event_id', None)
    logger.info(f"RESPONSE: {response_event}")
    return response_event

@app.route('/reservation/check/')
async def check_reservation():
    username = request.args.get('username')
    trip_id = request.args.get('trip_id')
    room = request.args.get('room')
    event_id = str(uuid.uuid4())
    event = {
        'event_id': event_id,
        'username': username,
        'trip_id': trip_id,
        'room': room,
    }

    logger.info("CHECK RESERVATION: %s", event_id)
    publish_topic_event(event, 'check_reservation')

    logger.info("WAITING")
    try:
        response_event = await asyncio.wait_for(get_response_from_redis(event_id), timeout=10000)
    except asyncio.TimeoutError as e:
        logger.info(f"ERROR: {e}")
        return jsonify({'error': f'Timeout while waiting for response: {e}'})

    response_event.pop('event_id', None)
    logger.info(f"RESPONSE: {response_event}")
    return response_event


@app.route('/reservation/pay/', methods=['POST'])
async def pay_reservation():
    logger.info("RESERV-PAY")
    trip_id = request.form.get('trip_id')
    card_number = request.form.get('card_number')
    price = request.form.get('price')
    room = request.form.get('room')
    event_id = str(uuid.uuid4())
    event = {
        'event_id': event_id,
        'trip_id': trip_id,
        'card_number': card_number,
        'price': price,
        'room': room
    }

    logger.info("PUBLISH PAYMENT: %s", event_id)
    #publish_event_to_queue(event, 'reservation_queue')
    publish_topic_event(event, 'payment')

    logger.info("WAITING")
    try:
        response_event = await asyncio.wait_for(get_response_from_redis(event_id), timeout=10000)
    except asyncio.TimeoutError as e:
        logger.info(f"ERROR: {e}")
        return jsonify({'error': f'Timeout while waiting for response: {e}'})

    response_event.pop('event_id', None)
    logger.info(f"RESPONSE: {response_event}")
    return response_event

@app.route('/getmytours/')
async def getmytours():
    username = request.args.get('username')
    event_id = str(uuid.uuid4())
    event = {
        'event_id': event_id,
        'username': username
    }
    logger.info("PUBLISH getmytours: %s", event_id)
    publish_topic_event(event, 'myreservations')
    logger.info("WAITING")
    try:
        response_event = await asyncio.wait_for(get_response_from_redis(event_id), timeout=10000)
    except asyncio.TimeoutError as e:
        logger.info(f"ERROR: {e}")
        return jsonify({'error': f'Timeout while waiting for response: {e}'})
    logger.info(f"RESPONSE: {response_event}")
    
    #event jakis tam event, ktory zwraca rezerwacje klienta

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
    # tours = [
    #     { "name": '663a2114bda936e962f8f4c0', "paid": False, "price": 0},
    #     { "name": '663a2114bda936e962f8f4c1', "paid": True, "price": 9.99},
    # ]
    return jsonify(tours)
# @app.route('/reservation/pay/', methods=['POST'])
# def pay_reservation():
#     trip_id = request.form.get('trip_id')
#     card_number = request.form.get('card_number')
#     price = request.form.get('price')

#     payment_data = {
#         'trip_id': trip_id,
#         'card_number': card_number,
#         'price': price
#     }

#     response = requests.post("http://reservation-service:5674/reservation/pay", data=payment_data)

#     if response.status_code not in {200, 202}:
#         return jsonify({"error": "Payment failed"}), response.status_code

#     return jsonify(response.json()), response.status_code

logger.debug(f"NAME: %s", __name__)
logger.info(f"ASD 1")
setup_topic_exchange_and_queues()
logger.info(f"ASD 2")
