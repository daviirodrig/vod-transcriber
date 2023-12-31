import os

import pika
from dotenv import load_dotenv

load_dotenv()


def send(message: str, queue: str):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            os.environ["RABBIT_HOST"],
            credentials=pika.PlainCredentials(
                os.environ["RABBIT_USER"], os.environ["RABBIT_PASS"]
            ),
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        ),
    )
    print(" [x] Sent %r" % message)
    connection.close()
