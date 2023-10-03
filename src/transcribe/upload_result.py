import asyncio
import os

import aiohttp
from dotenv import load_dotenv

load_dotenv()


async def upload_data(file: str | bytes, filename: str) -> None:
    if isinstance(file, str):
        with open(file, "rb") as f:
            data = f.read()

    BASE_URL = f"https://drive.deta.sh/v1/{os.environ['project_id']}/{os.environ['drive_name']}"
    headers = {
        "X-API-Key": os.environ["DETA_DRIVE_KEY"],
    }

    params = {
        "name": filename,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/files",
            params=params,
            headers=headers,
            data=data,
        ) as resp:
            print(f"{filename}", resp.status)
