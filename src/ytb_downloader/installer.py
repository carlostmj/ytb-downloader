from __future__ import annotations

import os
from pathlib import Path

from .config import APP_NAME, WINDOW_TITLE, desktop_entry_dir, project_python_executable, project_root, user_bin_dir
from .utils import ensure_directory


def _linux_shortcut_script() -> str:
    package_root = project_root()
    return "\n".join(
        [
            "#!/usr/bin/env bash",
            f'cd "{package_root}"',
            f'export PYTHONPATH="{package_root / "src"}${{PYTHONPATH:+:$PYTHONPATH}}"',
            f'exec "{project_python_executable()}" -m ytb_downloader "$@"',
            "",
        ]
    )


def _windows_shortcut_script() -> str:
    package_root = project_root()
    return "\r\n".join(
        [
            "@echo off",
            f'cd /d "{package_root}"',
            f'"{project_python_executable()}" -m ytb_downloader %*',
            "",
        ]
    )


def install_shortcut() -> str:
    bin_dir = ensure_directory(user_bin_dir())

    if os.name == "nt":
        launcher = bin_dir / f"{APP_NAME}.cmd"
        launcher.write_text(_windows_shortcut_script(), encoding="utf-8")
        return f"Atalho criado em {launcher}. Adicione essa pasta ao PATH se necessario."

    launcher = bin_dir / APP_NAME
    launcher.write_text(_linux_shortcut_script(), encoding="utf-8")
    launcher.chmod(0o755)

    desktop_dir = ensure_directory(desktop_entry_dir())
    desktop_file = desktop_dir / f"{APP_NAME}.desktop"
    desktop_file.write_text(
        "\n".join(
            [
                "[Desktop Entry]",
                "Type=Application",
                f"Name={WINDOW_TITLE}",
                f"Exec={launcher} --gui",
                "Terminal=false",
                "Categories=AudioVideo;Utility;",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return f"Atalhos criados em {launcher} e {desktop_file}."
