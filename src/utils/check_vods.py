import json
import os
from typing import Dict, Iterable, List, Union

import twitch
from dotenv import load_dotenv

from utils.msg_sender import send

load_dotenv()
helix = twitch.Helix(os.environ["TWITCH_ID"], os.environ["TWITCH_SECRET"])

def read(filename) -> Union[Dict, List]:
    with open(filename, "r", encoding="utf-8") as f:
        j = json.load(f)
    return j


processed: List = read("processed.json")

def main():
    vods = helix.user(os.environ["STREAMER_NAME"]).videos(type='archive', first=100)
    not_processed = [x.id for x in vods if x.id not in processed]
    print(not_processed)
    for vod in not_processed:
        send(vod, 'vods_to_be_processed')

main()
