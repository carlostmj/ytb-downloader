from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import history_file
from .models import DownloadRequest, DownloadResult


def load_history(limit: int | None = None) -> list[dict[str, str]]:
    file_path = history_file()
    if not file_path.exists():
        return []

    try:
        history_entries = json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(history_entries, list):
        return []

    entries = [entry for entry in history_entries if isinstance(entry, dict)]
    if limit is None:
        return entries
    return entries[-limit:]


def append_history(request: DownloadRequest, result: DownloadResult) -> None:
    file_path = history_file()
    entries = load_history()
    entries.append(
        {
            "timestamp": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
            "source": request.link,
            "format": "MP3" if request.audio_only else "MP4",
            "quality": request.audio_bitrate if request.audio_only else request.video_quality,
            "status": "Cancelado" if result.cancelled else ("Concluido" if result.success else "Erro"),
            "destination": str(result.destination),
            "message": result.message,
        }
    )
    file_path.write_text(json.dumps(entries[-200:], indent=2, ensure_ascii=False), encoding="utf-8")
