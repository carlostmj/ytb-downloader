from __future__ import annotations

import re
from typing import Callable

from .models import DownloadRequest, DownloadResult
from .utils import ensure_directory

ProgressCallback = Callable[[str], None]


def _progress_hook(callback: ProgressCallback | None):
    def hook(data: dict) -> None:
        if callback is None:
            return
        status = data.get("status")
        if status == "downloading":
            downloaded = data.get("_percent_str", "").strip()
            speed = data.get("_speed_str", "").strip()
            callback(f"Baixando... {downloaded} {speed}".strip())
        elif status == "finished":
            callback("Download concluido, processando arquivo...")

    return hook


def normalize_bitrate(raw_value: str | int | None) -> str:
    value = str(raw_value or "128").strip().lower().replace("kbps", "").replace("k", "")
    digits = re.sub(r"[^0-9]", "", value)
    return digits or "128"


def normalize_video_quality(raw_value: str | int | None) -> str:
    value = str(raw_value or "best").strip().lower()
    if value in {"best", "max", "original"}:
        return "best"
    digits = re.sub(r"[^0-9]", "", value)
    return digits or "best"


def build_options(request: DownloadRequest, callback: ProgressCallback | None = None) -> dict:
    ensure_directory(request.destination)
    output_path = str(request.destination / request.filename_template)
    options = {
        "outtmpl": output_path,
        "noplaylist": True,
        "progress_hooks": [_progress_hook(callback)],
        "quiet": True,
        "no_warnings": True,
    }

    if request.audio_only:
        options.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": normalize_bitrate(request.audio_bitrate),
                    }
                ],
            }
        )
    else:
        video_quality = normalize_video_quality(request.video_quality)
        video_format = "bestvideo+bestaudio/best"
        if video_quality != "best":
            video_format = f"bestvideo[height<={video_quality}]+bestaudio/best[height<={video_quality}]"
        options.update(
            {
                "format": video_format,
                "merge_output_format": "mp4",
            }
        )

    return options


def download(request: DownloadRequest, callback: ProgressCallback | None = None) -> DownloadResult:
    try:
        from yt_dlp import YoutubeDL

        options = build_options(request, callback)
        with YoutubeDL(options) as ydl:
            ydl.download([request.link])
        return DownloadResult(
            success=True,
            message="Download finalizado com sucesso.",
            destination=request.destination,
        )
    except Exception as exc:  # pragma: no cover - depende do ambiente
        return DownloadResult(
            success=False,
            message=f"Falha no download: {exc}",
            destination=request.destination,
        )
