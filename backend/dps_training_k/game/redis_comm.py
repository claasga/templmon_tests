import os
import json
import redis
import threading
from django.conf import settings

PROCESS_ID = os.environ.get("PROCESS_ID")

redis_client = redis.StrictRedis(
    host=getattr(settings, "REDIS_HOST", "localhost"),
    port=getattr(settings, "REDIS_PORT", 6379),
    db=getattr(settings, "REDIS_DB", 0),
    decode_responses=True,
)


def publish_to_process(target_process_id, data):
    channel = f"process_channel:{target_process_id}"
    message = json.dumps(data)
    redis_client.publish(channel, message)


def start_listener(callback):
    pubsub = redis_client.pubsub()
    channel = f"process_channel:{PROCESS_ID}"
    pubsub.subscribe(channel)
    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            callback(data)


def start_listener_in_thread(callback):
    listener_thread = threading.Thread(
        target=start_listener, args=(callback,), daemon=True
    )
    listener_thread.start()
