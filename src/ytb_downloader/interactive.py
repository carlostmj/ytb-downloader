from __future__ import annotations

from .config import default_download_dir
from .downloader import download
from .models import DownloadRequest
from .utils import build_terminal_progress_callback, normalize_destination, normalize_video_input


def run_interactive_mode() -> int:
    print("=== YTB Downloader / modo interativo ===")
    try:
        link = input("Cole o link do video: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nOperacao cancelada pelo usuario.")
        return 130

    if not link:
        print("Nenhum link informado.")
        return 1

    try:
        media_type = input("Digite 'mp3' para audio ou 'mp4' para video [mp3/mp4]: ").strip().lower()
        audio_quality = input("Bitrate do MP3 em kbps [128]: ").strip()
        video_quality = input("Qualidade do MP4 [best/1080/720/480]: ").strip()
        custom_dir = input("Pasta de destino (vazio = padrao do projeto): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nOperacao cancelada pelo usuario.")
        return 130

    audio_only = media_type != "mp4"

    destination = normalize_destination(custom_dir or None, default_download_dir())
    request = DownloadRequest(
        link=normalize_video_input(link),
        destination=destination,
        audio_only=audio_only,
        audio_bitrate=audio_quality or "128",
        video_quality=video_quality or "best",
    )
    progress_callback = build_terminal_progress_callback(hide_progress=False)
    result = download(request, callback=progress_callback)
    if progress_callback is not None:
        print()
    print(result.message)
    print(f"Destino: {result.destination}")
    return 0 if result.success else 1
