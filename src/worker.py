import functools
import os
import threading

import pika
import redis
from dotenv import load_dotenv

from transcribe.transcribe_vod import transcribe_vod

load_dotenv()
r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=6379,
    decode_responses=True,
    password=os.environ["REDIS_PASSWORD"],
)

def ack_message(ch, delivery_tag, vod_id):
    """Note that `ch` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).
    """
    if ch.is_open:
        print(f"ACKing message {vod_id}")
        r.set(f"done_processing:{vod_id}", str(True))
        r.set(f"to_be_processed:{vod_id}", str(False))
        ch.basic_ack(delivery_tag)
    else:
        # Channel is already closed, so we can't ACK this message;
        # log and/or do something that makes sense for your app in this case.
        pass


def do_work(ch, delivery_tag, body):
    vod_id = str(body.decode())
    transcribe_vod(vod_id)
    cb = functools.partial(ack_message, ch, delivery_tag, vod_id)
    ch.connection.add_callback_threadsafe(cb)


def on_message(ch, method_frame, _header_frame, body, args):
    thrds = args
    delivery_tag = method_frame.delivery_tag
    t = threading.Thread(target=do_work, args=(ch, delivery_tag, body))
    t.start()
    thrds.append(t)


parameters = pika.ConnectionParameters(
    os.environ["RABBIT_HOST"],
    credentials=pika.PlainCredentials(
        os.environ["RABBIT_USER"], os.environ["RABBIT_PASS"]
    ),
)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()
channel.queue_declare(queue="vods_to_be_processed", durable=True)

channel.basic_qos(prefetch_count=1)

threads = []
on_message_callback = functools.partial(on_message, args=(threads))
channel.basic_consume("vods_to_be_processed", on_message_callback)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()

# Wait for all to complete
for thread in threads:
    thread.join()

connection.close()
