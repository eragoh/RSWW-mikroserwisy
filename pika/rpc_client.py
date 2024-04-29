import asyncio
import aio_pika
import uuid

class RClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.waiter = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            "amqp://admin:password@172.18.0.4"
        )
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(
            exclusive=True
        )
        await self.callback_queue.consume(self.on_response)

    async def close(self):
        await self.connection.close()

    def on_response(self, message):
        if self.waiter and not self.waiter.done():
            self.waiter.set_result(message.body)
        else:
            message.ack()

    async def call(self, n, qname):
        if not self.connection:
            raise RuntimeError("Connection is not established")

        self.waiter = asyncio.Future()

        corr_id = str(uuid.uuid4())
        body = str(n).encode('utf-8')  # Encode the message body to bytes
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=body,
                             reply_to=self.callback_queue.name,
                             correlation_id=corr_id),
            routing_key=qname,
        )

        response = await asyncio.wait_for(self.waiter, timeout=None)
        return response

async def main():
    rclient = RClient()
    await rclient.connect()

    print("[x] Requesting fib(30)")
    response = await rclient.call("662ea0579fa221bd94f15f9a", "data_tour")
    print(f"[.] Got {response}")

    print("[x] Requesting fib(10)")
    response = await rclient.call(10, "countries")
    print(f"[.] Got {response}")

    await rclient.close()


if __name__ == "__main__":
    asyncio.run(main())
