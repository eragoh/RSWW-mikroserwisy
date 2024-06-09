import pika
import json
import random
import logging
import time
import sys
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

WATCH_ACTIVITIES = {}
BUY_ACTIVITIES = {}

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

def handle_watch_request(ch, method, properties, body):
    logger.info('handle_watch_request')
    watch_info = json.loads(body)
    rabbit_conn = get_rabbit_connection()

    tourname = watch_info['tourname']
    if tourname in WATCH_ACTIVITIES.keys():
        WATCH_ACTIVITIES[tourname] += 1
    else:
        WATCH_ACTIVITIES[tourname] = 1

    watch_info['result'] = WATCH_ACTIVITIES[tourname]
    publish_topic_event(rabbit_conn, watch_info, 'result')
    logger.info("PUBLISH EVENT (%s)", tourname)
    
    rabbit_conn.close()

def handle_watch_check_request(ch, method, properties, body):
    logger.info('handle_watch_request')
    watch_info = json.loads(body)
    rabbit_conn = get_rabbit_connection()
    tourname = watch_info['tourname']
    if tourname in WATCH_ACTIVITIES.keys():
        watch_info['result'] = WATCH_ACTIVITIES[tourname]
    else:
        watch_info['result'] = 0
    publish_topic_event(rabbit_conn, watch_info, 'result')
    logger.info("PUBLISH EVENT (%s)", tourname)
    rabbit_conn.close()

def handle_watch_end_request(ch, method, properties, body):
    logger.info('handle_watch_end_request')
    watch_info = json.loads(body)
    tourname = watch_info['tourname']
    if tourname in WATCH_ACTIVITIES.keys():
        WATCH_ACTIVITIES[tourname] -= 1
    else:
        WATCH_ACTIVITIES[tourname] = 0
    
    if WATCH_ACTIVITIES[tourname] < 0:
        WATCH_ACTIVITIES[tourname] = 0
    logger.info(f'handle_watch_end_request stop: {WATCH_ACTIVITIES[tourname]}')

def handle_buy_activity_check_request(ch, method, properties, body):
    logger.info('handle_buy_activity_check_request')
    info = json.loads(body)
    tour_id = info['tour_id']
    rabbit_conn = get_rabbit_connection()
    if tour_id in BUY_ACTIVITIES.keys():
        now = datetime.datetime.now()
        t = now - BUY_ACTIVITIES[tour_id]
        info['bought'] = t.seconds < 60
        logger.info(f'TIME {now} {BUY_ACTIVITIES[tour_id]} {t} {t.seconds}')
    else:
        info['bought'] = False
    logger.info("PUBLISH handle_buy_activity_check_request EVENT (%s)", info)
    publish_topic_event(rabbit_conn, info, 'result')

def handle_buy_activity_add_request(ch, method, properties, body):
    logger.info('handle_buy_activity_add_request')
    info = json.loads(body)
    logger.info(info)
    tour_id = info['tour_id']
    BUY_ACTIVITIES[tour_id] = datetime.datetime.now()
    logger.info(BUY_ACTIVITIES[tour_id])

def listen_to_rabbitmq():
    rabbit_connection = get_rabbit_connection()
    channel = rabbit_connection.channel()
    payment_queue = channel.queue_declare(queue='watch_queue', durable=True).method.queue
    logger.info("Listening...")
    
    def callback(ch, method, properties, body):
        routing_key = method.routing_key
        if routing_key == 'watch':
            handle_watch_request(ch, method, properties, body)
        elif routing_key == 'watch_end':
            handle_watch_end_request(ch, method, properties, body)
        elif routing_key == 'watch_check':
            handle_watch_check_request(ch, method, properties, body)
        elif routing_key == 'buy_activity_check':
            handle_buy_activity_check_request(ch, method, properties, body)
        elif routing_key == 'buy_activity_add':
            handle_buy_activity_add_request(ch, method, properties, body)
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
