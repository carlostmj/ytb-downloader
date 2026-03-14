from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class DownloadRequest:
    link: str
    destination: Path
    audio_only: bool
    video_only: bool = False
    audio_bitrate: str = "128"
    video_quality: str = "best"
    filename_template: str = "%(title)s.%(ext)s"


@dataclass(slots=True)
class DownloadResult:
    success: bool
    message: str
    destination: Path
    cancelled: bool = False
