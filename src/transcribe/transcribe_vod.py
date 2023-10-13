import asyncio
import subprocess

import torch

from transcribe.upload_result import upload_data
from transcribe.vod_download import download_video

device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size = 16
compute_type = "float16" if torch.cuda.is_available() else "int8"
model = "large-v2"


def transcribe_vod(vod_id: str):
    download_video(f"https://www.twitch.tv/videos/{vod_id}")

    file = f"./download/v{vod_id}.mp4"
    command = [
        "whisperx",
        f"{file}",
        "--model",
        f"{model}",
        "--device",
        f"{device}",
        "--language",
        "pt",
        "--batch_size",
        f"{batch_size}",
        "--compute_type",
        f"{compute_type}",
        "--output_format",
        "all",
        "--output_dir",
        "./outputs/",
    ]

    print(f"Starting whisper subprocess command for id {vod_id}")
    print(" ".join(command))
    process = subprocess.Popen(
        args=command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    while True:
        output: str = process.stdout.readline()  # type: ignore
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())

    # Get the subprocess return code
    return_code = process.poll()

    # Print the return code
    print("Whisper subprocess command finished with return code: ", return_code)
    if return_code != 0:
        print("Error")
        raise Exception("Whisper subprocess command failed")
    else:
        asyncio.run(upload_results(vod_id))


async def upload_results(vod_id: str):
    tasks = [
        upload_data(f"outputs/v{vod_id}.json", f"{vod_id}/v{vod_id}.json"),
        upload_data(f"outputs/v{vod_id}.srt", f"{vod_id}/v{vod_id}.srt"),
        upload_data(f"outputs/v{vod_id}.tsv", f"{vod_id}/v{vod_id}.tsv"),
        upload_data(f"outputs/v{vod_id}.txt", f"{vod_id}/v{vod_id}.txt"),
        upload_data(f"outputs/v{vod_id}.vtt", f"{vod_id}/v{vod_id}.vtt"),
    ]
    await asyncio.gather(*tasks)
