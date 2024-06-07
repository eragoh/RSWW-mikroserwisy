import psycopg2
from random import randint as rint
import logging
import pika
import sys
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import uuid

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

rabbit_connection_params = pika.ConnectionParameters(
    '180140_rabbitmq-gateway',
    port=5672,
    credentials=pika.PlainCredentials('admin', 'password'))

def get_rabbit_connection():
    return pika.BlockingConnection(rabbit_connection_params)

def get_connection():
    connection = psycopg2.connect(
        dbname="travel",
        user="postgres",
        password="postgres",
        host="toc-postgres"
    )
    return connection

def get_mongo_db():
    mongoclient = MongoClient('mongodb://user:password@travel-mongo:27017/TravelDB')
    return mongoclient.get_default_database()

def publish_topic_event(rabbit_connection, event, routing_key, exchange_name='order'):
    channel = rabbit_connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=json.dumps(event))
    logger.info(f"PUBLISHED: {event} // KEY: {routing_key}")
    channel.close()


def insert(trip, room):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO OPERATION (trip, room)
        VALUES (%s, %s)
        """,
        (trip, room)
    )
    connection.commit()

def handle_operations(ch, method, properties, body):
    operations_info = json.loads(body)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM OPERATION
        """
    )
    results = cursor.fetchall()
    operations_info['operations'] = json.dumps(results[::-1][:10])
    publish_topic_event(get_rabbit_connection(), operations_info, 'result')
    #return jsonify(results[:10])

def handle_countries(ch, method, properties, body):
    info = json.loads(body)
    db = get_mongo_db()
    some_data = db.travelOffers.distinct("country")
    info['countries'] = some_data
    publish_topic_event(get_rabbit_connection(), info, 'result')

def handle_buy_request(ch, method, properties, body):
    logger.info('handle buy request')
    def update_room(room):
        if room == 'Standardowy':
            return 'is_standard'
        if room == 'Apartament':
            return 'is_apartment'
        if room == 'Rodzinny':
            return 'is_family'
        if room == 'Studio':
            return 'is_studio'
        
    try:
        buy_info = json.loads(body)
        trip_id = buy_info['trip_id']
        room = buy_info['room']

        db = get_mongo_db()
        update_query = {
            "$inc": {
                f"room.{update_room(room)}": -1
            }
        }
        result = db.travelOffers.update_one({"_id": ObjectId(trip_id)}, update_query)
        logger.info(f'DB UPDATE: {result}')
        insert(trip_id, room)
    except Exception as error:
        logger.info(f'Error handle_buy: {error}')

def handle_rooms_request(ch, method, properties, body):
    reservation_info = json.loads(body)
    try:
        logger.info('handle rooms request')
        trip_id = reservation_info['trip_id']
        db = get_mongo_db()
        some_data = db.travelOffers.find_one({"_id": ObjectId(trip_id)})
        if some_data is None:
            reservation_info['room'] = {}
        else:
            reservation_info['room'] = some_data['room']
    except:
        reservation_info['room'] = {}
    publish_topic_event(get_rabbit_connection(), reservation_info, 'result')
    

def listen_to_rabbitmq():
    rabbit_connection = get_rabbit_connection()
    channel = rabbit_connection.channel()
    reservation_queue = channel.queue_declare(queue='toc_service_queue', durable=True).method.queue
    logger.info("Listening...")
    
    def callback(ch, method, properties, body):
        routing_key = method.routing_key
        logger.info(f'callback {routing_key}')
        if routing_key == 'buy':
            handle_buy_request(ch, method, properties, body)
        elif routing_key == 'operations':
            handle_operations(ch, method, properties, body)
        elif routing_key == 'countries':
            handle_countries(ch, method, properties, body)
        elif routing_key == 'rooms':
            handle_rooms_request(ch, method, properties, body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=reservation_queue, on_message_callback=callback)
    
    # Start consuming messages in a loop
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping...")
        channel.stop_consuming()
        rabbit_connection.close()

if __name__ == '__main__':
    listen_to_rabbitmq()








#insert into operation(trip, room) values('222', '222');