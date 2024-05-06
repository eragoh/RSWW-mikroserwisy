import threading
import pika
import json
import logging
import sys
import time

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Connection parameters for RabbitMQ
rabbit_connection_params = pika.ConnectionParameters(
    'rabbitmq-gateway',
    port=5672,
    credentials=pika.PlainCredentials('admin', 'password'))

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
    rabbit_connection = get_rabbit_connection()
    # async with conn.transaction():
    #     await conn.execute("DELETE FROM reservations WHERE trip = $1 AND paid = false", trip_id)
    # await conn.close()
    logger.info("Removed unpaid reservations for trip %s", trip_id)

def handle_reservation_response(rabbit_connection, reservation_info):
    response_event = {
        'event_id': reservation_info['event_id'],
        'username': reservation_info['username'],
        'status': 'RESERVED'
    }
    publish_topic_event(rabbit_connection, response_event, 'result')
    logger.info("Reservation response handled and published.")

def handle_reservation_request(channel, method, properties, body):
    logger.info("HANDLING")
    reservation_info = json.loads(body)
    username = reservation_info['username']
    trip_id = reservation_info['trip_id']
    price = reservation_info['price']

    # db_conn = await get_connection()
    # async with db_conn.transaction():
    #     await db_conn.execute(
    #         "INSERT INTO reservations (username, trip, price, paid) VALUES ($1, $2, $3, false)",
    #         username, trip_id, price
    #     )
    # await db_conn.close()

    rabbit_conn = get_rabbit_connection()
    handle_reservation_response(rabbit_conn, reservation_info)
    rabbit_conn.close()

    timer_thread = threading.Thread(target=start_timer, args=(trip_id,))
    timer_thread.start()

def handle_reservation_paid_request(channel, method, properties, body):
    reservation_info = json.loads(body)
    event_id = reservation_info['event_id']

    # ADD IN DB NEW RESERVATION INFO WITH PAID STATUS

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
        if routing_key == 'reservation_info':
            handle_reservation_info_request(ch, method, properties, body)
        if routing_key == 'reservation_paid':
            handle_reservation_paid_request(ch, method, properties, body)
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
