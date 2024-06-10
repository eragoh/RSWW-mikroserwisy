import psycopg2
from random import randint as rint, choice as choice
import logging
import pika
import sys
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import threading
import time
import uuid

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

rabbit_connection_params = pika.ConnectionParameters(
    'rabbitmq-gateway',
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


def insert(trip_id, update):
    connection = get_connection()
    cursor = connection.cursor()

    room_is_standard = update.get('room', {}).get('is_standard', -1)
    room_is_family = update.get('room', {}).get('is_family', -1)
    room_is_apartment = update.get('room', {}).get('is_apartment', -1)
    room_is_studio = update.get('room', {}).get('is_studio', -1)
    price = update.get('price', -1)
    adults = update.get('adults', -1)
    children_under_3 = update.get('children_under_3', -1)
    children_under_10 = update.get('children_under_10', -1)
    children_under_18 = update.get('children_under_18', -1)

    cursor.execute(
        """
        INSERT INTO OPERATION (trip, room_is_standard, room_is_family, room_is_apartment, room_is_studio, price, adults, children_under_3, children_under_10, children_under_18)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (trip_id, room_is_standard, room_is_family, room_is_apartment, room_is_studio, price, adults, children_under_3, children_under_10, children_under_18)
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
    
last_delete_time = 0

def random_mongo_updates():
    global last_delete_time
    while True:
        try:
            db = get_mongo_db()
            # Randomly select a document
            all_ids = [doc['_id'] for doc in db.travelOffers.find()]
            if not all_ids:
                logger.info('No records found to update')
                continue

            random_id = choice(all_ids)

            # 10% chance to delete a record, but only if more than 2 minutes have passed since last deletion
            if time.time() - last_delete_time > 240 and rint(1, 10) == 1:
                db.travelOffers.delete_one({"_id": random_id})
                logger.info(f'Deleted document: {random_id}')
                last_delete_time = time.time()
                # Log deletion as well
                insert(str(random_id), {"room_is_standard": -1, "room_is_family": -1, "room_is_apartment": -1, "room_is_studio": -1, "price": -1, "adults": -1, "children_under_3": -1, "children_under_10": -1, "children_under_18": -1})
            else:
                # Update random fields
                random_update = {}
                selected_field = choice(['adults', 'children', 'price', 'room'])

                if selected_field == 'adults':
                    random_update['adults'] = rint(1, 6)  # Random number of adults
                elif selected_field == 'children':
                    children_under_3 = rint(0, 3)
                    children_under_10 = rint(0, 3)
                    children_under_18 = rint(0, 3)
                    random_update['children'] = children_under_3 + children_under_10 + children_under_18
                    random_update['children_under_3'] = children_under_3
                    random_update['children_under_10'] = children_under_10
                    random_update['children_under_18'] = children_under_18
                elif selected_field == 'price':
                    random_update['price'] = rint(20, 100) * 100  # Random price
                elif selected_field == 'room':
                    random_update['room'] = {
                        "is_standard": rint(0, 20),
                        "is_family": rint(0, 20),
                        "is_apartment": rint(0, 20),
                        "is_studio": rint(0, 20)
                    }

                update_query = {"$set": random_update}
                result = db.travelOffers.update_one({"_id": random_id}, update_query)
                logger.info(f'Updated document: {random_id} with {random_update}')
                
                # Insert the changes into PostgreSQL
                insert(str(random_id), random_update)

            time.sleep(45)
        except Exception as error:
            logger.error(f'Error in random_mongo_updates: {error}')

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
    updater_thread = threading.Thread(target=random_mongo_updates)
    updater_thread.daemon = True
    updater_thread.start()

    listen_to_rabbitmq()








#insert into operation(trip, room) values('222', '222');