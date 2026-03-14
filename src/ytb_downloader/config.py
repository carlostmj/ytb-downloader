from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "ytb-downloader"
WINDOW_TITLE = "YTB Downloader"
DOWNLOAD_FOLDER_NAME = "downloads"
HISTORY_FILE_NAME = "history.json"
DEFAULT_TEMPLATE = "%(title)s.%(ext)s"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_download_dir() -> Path:
    return project_root() / DOWNLOAD_FOLDER_NAME


def history_file() -> Path:
    return project_root() / HISTORY_FILE_NAME


def user_bin_dir() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("USERPROFILE", Path.home())) / "bin"
    return Path.home() / ".local" / "bin"


def desktop_entry_dir() -> Path:
    return Path.home() / ".local" / "share" / "applications"


def python_executable() -> str:
    return sys.executable


def project_python_executable() -> str:
    root = project_root()
    if os.name == "nt":
        candidate = root / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = root / ".venv" / "bin" / "python"
    if candidate.exists():
        return str(candidate)
    return python_executable()
