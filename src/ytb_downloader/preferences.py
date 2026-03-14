from __future__ import annotations

import json
from typing import Any

from .config import default_download_dir, preferences_file

DEFAULT_PREFERENCES = {
    "destination": str(default_download_dir()),
    "media_format": "mp3",
    "audio_quality": "128",
    "video_quality": "best",
    "auto_open_folder": False,
    "show_completion_popup": True,
    "history_limit": 12,
}


def load_preferences() -> dict[str, Any]:
    file_path = preferences_file()
    if not file_path.exists():
        return DEFAULT_PREFERENCES.copy()

    try:
        raw_data = json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_PREFERENCES.copy()

    preferences = DEFAULT_PREFERENCES.copy()
    if isinstance(raw_data, dict):
        for key, value in raw_data.items():
            if key in preferences:
                preferences[key] = value
    return preferences


def save_preferences(preferences: dict[str, Any]) -> None:
    merged = DEFAULT_PREFERENCES.copy()
    for key in merged:
        merged[key] = preferences.get(key, merged[key])
    preferences_file().write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
