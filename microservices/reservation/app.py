import threading
import pika
import json
import logging
import sys
import time
import psycopg2
import uuid
# from pymongo import MongoClient
# from bson.objectid import ObjectId

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Connection parameters for RabbitMQ
rabbit_connection_params = pika.ConnectionParameters(
    '180140_rabbitmq-gateway',
    port=5672,
    credentials=pika.PlainCredentials('admin', 'password'))

def get_connection():
    connection = psycopg2.connect(
        dbname="travel",
        user="postgres",
        password="postgres",
        host="180140_postgres-db-reservations"
    )
    return connection

def get_rabbit_connection():
    return pika.BlockingConnection(rabbit_connection_params)

def publish_topic_event(rabbit_connection, event, routing_key, exchange_name='order'):
    channel = rabbit_connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=json.dumps(event))
    logger.info(f"PUBLISHED: {event} // KEY: {routing_key}")
    channel.close()

def start_timer(trip_id):
    logger.info("--- TIMER STARTED")
    time.sleep(60)  # You can use time.sleep() for blocking sleep
    logger.info("--- TIMER ENDED")
    check_and_remove_unpaid_reservation(trip_id)

def check_and_remove_unpaid_reservation(trip_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM RESERVATIONS WHERE trip = %s AND paid = false
            """,
            (trip_id,)
        )

        connection.commit()
        logger.info(f"Removed unpaid reservations for trip: {trip_id}")

    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(f"Błąd podczas usuwania rezerwacji: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()
    # async with conn.transaction():
    #     await conn.execute("DELETE FROM reservations WHERE trip = $1 AND paid = false", trip_id)
    # await conn.close()

def handle_reservation_response(rabbit_connection, reservation_info, status):
    response_event = {
        'event_id': reservation_info['event_id'],
        'username': reservation_info['username'],
        'status': 'RESERVED' if status else 'TAKEN'
    }
    publish_topic_event(rabbit_connection, response_event, 'result')
    logger.info("Reservation response handled and published.")

def insert_into_reservations(username, trip_id, price, paid, room, adults, ch3, ch10, ch18):
    status = True
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO RESERVATIONS (username, trip, price, paid, room, adults, ch3, ch10, ch18) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (username, trip_id, price, paid, room, adults, ch3, ch10, ch18)
        )

        connection.commit()
        logger.info("Rezerwacja dodana pomyślnie.")

    except (Exception, psycopg2.DatabaseError) as error:
        status = False
        logger.info(f"Błąd podczas dodawania rezerwacji: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()
    
    return status

def update_room(room):
    if 'Standardowy' in room:
        return 'Standardowy'
    if 'Apartament' in room:
        return 'Apartament'
    if 'Rodzinny' in room:
        return 'Rodzinny'
    if 'Studio' in room:
        return 'Studio'

def handle_reservation_request(channel, method, properties, body):        
    logger.info("HANDLING")
    reservation_info = json.loads(body)
    username = reservation_info['username']
    trip_id = reservation_info['trip_id']
    price = float(reservation_info['price'])
    room = update_room(reservation_info['room'])
    adults  = int(reservation_info['adults'])
    ch3  = int(reservation_info['ch3'])
    ch10 = int(reservation_info['ch10'])
    ch18 = int(reservation_info['ch18'])

    status = insert_into_reservations(username, trip_id, price, False, room, adults, ch3, ch10, ch18)

    # db_conn = await get_connection()
    # async with db_conn.transaction():
    #     await db_conn.execute(
    #         "INSERT INTO reservations (username, trip, price, paid) VALUES ($1, $2, $3, false)",
    #         username, trip_id, price
    #     )
    # await db_conn.close()

    rabbit_conn = get_rabbit_connection()
    handle_reservation_response(rabbit_conn, reservation_info, status)
    rabbit_conn.close()

    timer_thread = threading.Thread(target=start_timer, args=(trip_id,))
    timer_thread.start()

def handle_reservation_paid_request(channel, method, properties, body):  
    reservation_info = json.loads(body)
    event_id = reservation_info['event_id']
    trip_id = reservation_info['trip_id']
    result = reservation_info['result']
    room = update_room(reservation_info['room'])
    if result == 'success':
        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE RESERVATIONS
                SET paid = %s
                WHERE trip = %s AND room = %s
                """,
                (True, trip_id, room)
            )

            connection.commit()
            logger.info("Rezerwacja została opłacona pomyślnie.")

            event = {
                'event_id': str(uuid.uuid4()),
                'trip_id': trip_id,
                'room': room
            }
            publish_topic_event(get_rabbit_connection(), event, 'buy')

            # mongoclient = MongoClient('mongodb://user:password@travel-mongo:27017/TravelDB')
            # db = mongoclient.get_default_database()
            # update_query = {
            #     "$set": {
            #         f"room.{update_room(room)}": False
            #     }
            # }
            # result = db.travelOffers.update_one({"_id": ObjectId(trip_id)}, update_query)
            # logger.info(f'DB UPDATE: {result}')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.info(f"Błąd podczas opłacania rezerwacji: {error}")

        finally:
            if connection:
                cursor.close()
            connection.close()

    # ADD IN DB NEW RESERVATION INFO WITH PAID STATUS

def handle_myreservations(channel, method, properties, body):
    reservation_info = json.loads(body)
    event_id = reservation_info['event_id']
    username = reservation_info['username']
    logger.info(f'MY RESERVATIONS - {username}')

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT * FROM RESERVATIONS WHERE username = %s
            """,
            (username,)
        )
        results = cursor.fetchall()
        logger.info(f"Znaleziono rezerwacje: {results}.")
    
        rabbit_conn = get_rabbit_connection()
        return_event = {
            'event_id': event_id,
            'results': results
        }
        publish_topic_event(rabbit_conn, return_event, 'result')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(f"Błąd podczas opłacania rezerwacji: {error}")

    finally:
        if connection:
            cursor.close()
        connection.close()
    
def handle_check_rooms_reservation(channel, method, properties, body):
    reservation_info = json.loads(body)
    event_id = reservation_info['event_id']
    trip_id = reservation_info['trip_id']
    logger.info(f'CHECK ROOMS RESERVATION - {trip_id}')

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT room, COUNT(*) FROM RESERVATIONS WHERE trip = %s AND paid = %s GROUP BY room
            """,
            (trip_id, False)
        )
        room_counts = cursor.fetchall()
        results = {room_type: count for room_type, count in room_counts}
        logger.info(f"Znaleziono pokoje: {results}.")
    
        rabbit_conn = get_rabbit_connection()
        return_event = {
            'event_id': event_id,
            'results': results
        }
        publish_topic_event(rabbit_conn, return_event, 'result')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(f"Błąd podczas sprawdzania dostępnych pokoji: {error}")

    finally:
        if connection:
            cursor.close()
        connection.close()

def handle_check_rooms_reservation2(channel, method, properties, body):
    reservation_info = json.loads(body)
    event_id = reservation_info['event_id']
    trip_id = reservation_info['trip_id']
    logger.info(f'CHECK ROOMS RESERVATION - {trip_id}')

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT room FROM RESERVATIONS WHERE trip = %s
            """,
            (trip_id,)
        )
        results = cursor.fetchall()
        logger.info(f"Znaleziono pokoje: {results}.")
    
        rabbit_conn = get_rabbit_connection()
        return_event = {
            'event_id': event_id,
            'results': results
        }
        publish_topic_event(rabbit_conn, return_event, 'result')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(f"Błąd podczas sprawdzania dostępnych pokoji: {error}")

    finally:
        if connection:
            cursor.close()
        connection.close()
    
def handle_check_reservation(channel, method, properties, body):
    reservation_info = json.loads(body)
    event_id = reservation_info['event_id']
    username = reservation_info['username']
    trip_id = reservation_info['trip_id']
    room = reservation_info['room']
    logger.info(f'CHECK RESERVATION - {trip_id}')

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT * FROM RESERVATIONS WHERE trip = %s AND username = %s AND room = %s
            """,
            (trip_id, username, room)
        )
        result = cursor.fetchone()
        logger.info(f"Znaleziono rezerwację: {result}.")
    
        rabbit_conn = get_rabbit_connection()
        return_event = {
            'event_id': event_id,
            'result': result
        }
        publish_topic_event(rabbit_conn, return_event, 'result')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(f"Błąd podczas sprawdzania dostępnych pokoji: {error}")

    finally:
        if connection:
            cursor.close()
        connection.close()
    

def handle_reservation_info_request(channel, method, properties, body):
    reservation_info = json.loads(body)
    event_id = reservation_info['event_id']

    # CHECK IN DB IF RESERVED BY THIS USER
    is_reserved = True

    rabbit_conn = get_rabbit_connection()

    if is_reserved:
        reservation_info['reserved'] = 'true'
        publish_topic_event(rabbit_conn, reservation_info, 'payment')
    else:
        payment_return_event = {
        'event_id': event_id,
        'result': 'Not reserved'
        }
        publish_topic_event(rabbit_conn, payment_return_event, 'result')

    rabbit_conn.close()
    logger.info("Payment for trip processed successfully. Reserved: %s", is_reserved)


def listen_to_rabbitmq():
    rabbit_connection = get_rabbit_connection()
    channel = rabbit_connection.channel()
    reservation_queue = channel.queue_declare(queue='reservation_queue', durable=True).method.queue
    logger.info("Listening...")
    
    def callback(ch, method, properties, body):
        routing_key = method.routing_key
        if routing_key == 'reservation_add':
            handle_reservation_request(ch, method, properties, body)
        elif routing_key == 'reservation_info':
            handle_reservation_info_request(ch, method, properties, body)
        elif routing_key == 'reservation_paid':
            handle_reservation_paid_request(ch, method, properties, body)
        elif routing_key == 'myreservations':
            handle_myreservations(ch, method, properties, body)
        elif routing_key == 'reserved_rooms':
            handle_check_rooms_reservation(ch, method, properties, body)
        elif routing_key == 'check_reservation':
            handle_check_reservation(ch, method, properties, body)
        # Continue consuming messages
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
