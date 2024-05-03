import pika
import redis
import json
import threading
import uuid
import asyncio
from flask import Flask, request, jsonify

app = Flask(__name__)

# Redis client for storing results
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Publish a purchase event directly to RabbitMQ
def publish_purchase_event(event):
    connection = pika.BlockingConnection(pika.ConnectionParameters('172.21.0.4', credentials=pika.PlainCredentials('admin', 'password')))
    channel = connection.channel()

    # Ensure the queues exist
    channel.queue_declare(queue='event_queue')
    channel.queue_declare(queue='result_queue')

    # Publish the event to the event queue
    channel.basic_publish(exchange='', routing_key='event_queue', body=json.dumps(event))

    connection.close()

# Listen for responses from RabbitMQ
def listen_for_results():
    connection = pika.BlockingConnection(pika.ConnectionParameters('172.21.0.4', credentials=pika.PlainCredentials('admin', 'password')))
    channel = connection.channel()

    # Declare or assert the queue
    channel.queue_declare(queue='result_queue')

    # Callback to handle messages
    def callback(ch, method, properties, body):
        result = json.loads(body)
        event_id = result['event_id']

        # Store the result in Redis
        redis_client.set(event_id, body)

    # Consume messages from the result queue
    channel.basic_consume(queue='result_queue', on_message_callback=callback, auto_ack=True)

    # Start consuming
    channel.start_consuming()

# Start a separate thread to listen for results
listener_thread = threading.Thread(target=listen_for_results)
listener_thread.daemon = True
listener_thread.start()

async def get_result_from_redis(event_id):
    while True:
        result = redis_client.get(event_id)
        if result:
            return json.loads(result)

        await asyncio.sleep(1)  # Delay before checking again

@app.route('/buy/', methods=['POST'])
async def buy():
    # Parse the incoming request data
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400

    # Generate a unique event ID
    event_id = str(uuid.uuid4())

    # Create an event from the request data
    event = {
        'event_id': event_id,
        'price': data.get('price'),
        'item_id': data.get('item_id'),
        'username': data.get('username')
    }

    # Publish the event to RabbitMQ
    publish_purchase_event(event)

    try:
        result = await asyncio.wait_for(get_result_from_redis(event_id), timeout=45)
    except asyncio.TimeoutError:
        return jsonify({'error': 'Timeout while waiting for result'}), 500

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True)
