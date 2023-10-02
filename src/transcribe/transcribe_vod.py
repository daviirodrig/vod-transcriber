import torch
import whisperx
from vod_download import download_video

device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size = 16
compute_type = "float16"


def transcribe_vod(vod_id: str):
    download_video(f"https://www.twitch.tv/videos/{vod_id}")
    file = f"./download/v{vod_id}.mp4"
    # audio = whisperx.load_audio(file)
    model = whisperx.load_model(
        "large-v2",
        device=device,
        language="pt",  # compute_type=compute_type, language="pt"
    )
    import gc

    gc.collect()
    torch.cuda.empty_cache()
    first_result = model.transcribe(file, batch_size=batch_size, language="pt")

    print(first_result["segments"])  # before alignment

    # delete model if low on GPU resources
    # import gc; gc.collect(); torch.cuda.empty_cache();

    # 2. Align whisper output
    model_a, metadata = whisperx.load_align_model(
        language_code=first_result["language"], device=device
    )
    second_result = whisperx.align(
        first_result["segments"],
        model_a,
        metadata,
        file,
        device,
        return_char_alignments=False,
    )

    print(second_result["segments"])  # after alignment
    second_result["language"] = metadata["language"]  # type: ignore

    output_format = "all"
    output_dir = "./"
    output_writer = whisperx.transcribe.get_writer(output_format, output_dir)
    output_writer(
        first_result,  # type: ignore
        output_dir,  # type: ignore
        {"max_line_width": None, "max_line_count": None, "highlight_words": False},
    )
