import asyncio
import asyncpg
import aio_pika
import json
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

async def get_connection():
    return await asyncpg.connect(
        user='postgres', password='postgres', database='travel', host='postgres-db-reservations'
    )

# Setup connection to RabbitMQ using a specific function
async def get_rabbit_connection():
    return await aio_pika.connect_robust(
        "amqp://admin:password@rabbitmq-gateway/"
    )

async def publish_event_to_queue(rabbit_connection, event, queue_name):
    channel = await rabbit_connection.channel()  # Create a new channel
    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(event).encode()),
        routing_key=queue_name
    )
    logger.info(f"Published event to {queue_name} with data: {event}")


async def handle_reservation_response(rabbit_connection, reservation_info):
    response_event = {
        'event_id': reservation_info['event_id'],
        'username': reservation_info['username'],
        'status': 'RESERVED'
    }
    await publish_event_to_queue(rabbit_connection, response_event, 'result_queue')
    logger.info("Reservation response handled and published.")


async def start_timer(trip_id):
    logger.info("--- TIMER STARTED")
    await asyncio.sleep(1)
    logger.info("--- TIMER ENDED")
    await check_and_remove_unpaid_reservation(trip_id)

async def check_and_remove_unpaid_reservation(trip_id):
    conn = await get_connection()
    async with conn.transaction():
        await conn.execute("DELETE FROM reservations WHERE trip = $1 AND paid = false", trip_id)
    await conn.close()

async def handle_reservation_request(message: aio_pika.IncomingMessage):
    logger.info("HANDLING")
    reservation_info = json.loads(message.body)
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

    rabbit_conn = await get_rabbit_connection()
    await handle_reservation_response(rabbit_conn, reservation_info)
    await start_timer(trip_id)
    await rabbit_conn.close()

async def handle_payment_request(message: aio_pika.IncomingMessage):
    payment_info = json.loads(message.body)
    trip_id = payment_info['trip_id']
    success = payment_info['success']

    conn = await get_connection()
    async with conn.transaction():
        if success:
            await conn.execute("UPDATE reservations SET paid = true WHERE trip_id = $1", trip_id)
    await conn.close()

async def listen_to_rabbitmq():
    # Use the dedicated function to connect to RabbitMQ
    connection = await get_rabbit_connection()
    channel = await connection.channel()
    logger.info("LISTENING...")
    # Declare queues
    reservation_queue = await channel.declare_queue('reservation_queue')
    #payment_response_queue = await channel.declare_queue('payment_responses')
    print("XD1")
    # Start consumers
    # await asyncio.gather(
    #     reservation_queue.consume(handle_reservation_request),
    #     #payment_response_queue.consume(handle_payment_response),
    # )
    async with reservation_queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                await handle_reservation_request(message)
    print("XD2")

if __name__ == '__main__':
    logger.info("RESERV-ADD22")
    print("XD0")
    asyncio.run(listen_to_rabbitmq())
