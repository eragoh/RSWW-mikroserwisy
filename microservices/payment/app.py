import pika
import json
import random
import logging
import time
import sys

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

def publish_topic_event(rabbit_connection, event, routing_key, exchange_name='order'):
    channel = rabbit_connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=json.dumps(event))
    logger.info(f"PUBLISHED: {event} // KEY: {routing_key}")
    channel.close()

def process_payment(payment_info):
    """Process the payment synchronously."""
    time.sleep(3)  # Simulate processing time
    payment_success = random.choice([True, False])
    return payment_success

def handle_payment_request(ch, method, properties, body):
    payment_info = json.loads(body)
    rabbit_conn = get_rabbit_connection()

    if 'reserved' in payment_info.keys() and payment_info['reserved'] == 'true':
        payment_info.pop('reserved', None)
        result = process_payment(payment_info)
        payment_info['result'] = 'success' if result else 'failure'
        publish_topic_event(rabbit_conn, payment_info, 'reservation_paid')
    else:
        payment_info['reserved'] = 'false'
        publish_topic_event(rabbit_conn, payment_info, 'reservation_info')
    
    rabbit_conn.close()

def listen_to_rabbitmq():
    rabbit_connection = get_rabbit_connection()
    channel = rabbit_connection.channel()
    payment_queue = channel.queue_declare(queue='payment_queue', durable=True).method.queue
    logger.info("Listening...")
    
    def callback(ch, method, properties, body):
        routing_key = method.routing_key
        if routing_key == 'payment':
            handle_payment_request(ch, method, properties, body)
        # Continue consuming messages
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=payment_queue, on_message_callback=callback)
    
    # Start consuming messages in a loop
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping...")
        channel.stop_consuming()
        rabbit_connection.close()

if __name__ == '__main__':
    listen_to_rabbitmq()
