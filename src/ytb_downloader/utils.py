from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

YOUTUBE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
YOUTUBE_WATCH_PREFIX = "https://www.youtube.com/watch?v="
YOUTUBE_ID_FROM_URL_PATTERN = re.compile(r"(?:watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})")


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


def dedupe_entries(entries: list[str]) -> list[str]:
    unique_entries: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if entry not in seen:
            unique_entries.append(entry)
            seen.add(entry)
    return unique_entries


def display_video_input(entry: str) -> str:
    match = YOUTUBE_ID_FROM_URL_PATTERN.search(entry)
    if match:
        return match.group(1)
    return entry


def open_in_file_manager(path: Path) -> bool:
    target = str(path)
    try:
        if os.name == "nt":
            os.startfile(target)  # type: ignore[attr-defined]
            return True
        if sys.platform == "darwin":
            subprocess.Popen(["open", target])
            return True
        subprocess.Popen(["xdg-open", target])
        return True
    except Exception:
        return False
