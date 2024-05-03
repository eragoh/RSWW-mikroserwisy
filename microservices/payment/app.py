import asyncio
import aio_pika
import uuid
import json
import random

# Setup connection to RabbitMQ
async def get_rabbit_connection():
    return await aio_pika.connect_robust(
        "amqp://admin:password@rabbitmq-gateway/"
    )

async def send_payment_event(trip_id, payment_success):
    """Send the payment event to the RabbitMQ using aio_pika."""
    connection = await get_rabbit_connection()
    async with connection:
        channel = await connection.channel()  # Creating a channel
        await channel.declare_queue('result_queue')
        await channel.declare_queue('reservation_queue')

        payment_info = {'trip_id': trip_id, 'success': payment_success, 'event_id': str(uuid.uuid4())}
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(payment_info).encode()),
            routing_key='result_queue'
        )
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(payment_info).encode()),
            routing_key='reservation_queue'
        )

async def process_payment(payment_info):
    """Process the payment asynchronously."""
    await asyncio.sleep(3)  # Simulate processing time
    payment_success = random.choice([True, False])
    await send_payment_event(payment_info['trip_id'], payment_success)

async def handle_payment_request(message: aio_pika.IncomingMessage):
    async with message.process():
        payment_info = json.loads(message.body)
        await process_payment(payment_info)

async def listen_to_rabbitmq():
    """Setup and start listening on the RabbitMQ queue."""
    connection = await get_rabbit_connection()
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue('payment_queue')
        queue = await channel.declare_queue('payment_queue')
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await handle_payment_request(message)

if __name__ == '__main__':
    asyncio.run(listen_to_rabbitmq())
