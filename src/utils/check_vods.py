import json
import os
from typing import Dict, List, Union

import redis
import twitch
from dotenv import load_dotenv
from msg_sender import send

load_dotenv()
helix = twitch.Helix(os.environ["TWITCH_ID"], os.environ["TWITCH_SECRET"])
r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=6379,
    decode_responses=True,
    password=os.environ["REDIS_PASSWORD"],
)


def read(filename) -> Union[Dict, List]:
    with open(filename, "r", encoding="utf-8") as f:
        j = json.load(f)
    return j


def main():
    vods = helix.user(os.environ["STREAMER_NAME"]).videos(type="archive")
    for vod in vods:
        if (bool(r.get(f"to_be_processed:{vod.id}")) is False) and (bool(r.get(f"done_processing:{vod.id}")) is False):
            print(f"Set to process {vod.id}")
            send(vod.id, "vods_to_be_processed")
            r.set(f"to_be_processed:{vod.id}", str(True))
        else:
            print(f"Skipping {vod.id}")


main()
