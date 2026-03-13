from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

YOUTUBE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
YOUTUBE_WATCH_PREFIX = "https://www.youtube.com/watch?v="


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def normalize_destination(raw_path: str | None, fallback: Path) -> Path:
    if raw_path:
        return ensure_directory(Path(raw_path).expanduser().resolve())
    return ensure_directory(fallback.resolve())


def build_terminal_progress_callback(hide_progress: bool) -> Callable[[str], None] | None:
    if hide_progress:
        return None

    def callback(message: str) -> None:
        print(f"\r{message:<100}", end="", flush=True)

    return callback


def normalize_video_input(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return ""
    if YOUTUBE_ID_PATTERN.fullmatch(cleaned):
        return f"{YOUTUBE_WATCH_PREFIX}{cleaned}"
    return cleaned


def load_batch_entries(file_path: str) -> list[str]:
    entries: list[str] = []
    for raw_line in Path(file_path).read_text(encoding="utf-8").splitlines():
        cleaned = normalize_video_input(raw_line)
        if cleaned and not cleaned.startswith("#"):
            entries.append(cleaned)
    return entries
