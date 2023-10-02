from yt_dlp import YoutubeDL as yt_dlp


def download_video(url: str):
    ydl_opts = {
        "external_downloader": {"default": "aria2c"},
        "extract_flat": "discard_in_playlist",
        "format": "Audio_Only",
        "fragment_retries": 10,
        "ignoreerrors": "only_download",
        "outtmpl": {"default": "./download/%(id)s.%(ext)s"},
        "postprocessors": [
            {"key": "FFmpegConcat", "only_multi_video": True, "when": "playlist"}
        ],
        "retries": 10,
    }
    with yt_dlp(ydl_opts) as ydl:
        ydl.download([url])
