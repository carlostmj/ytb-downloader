from __future__ import annotations

import argparse
import sys

from .config import APP_NAME, default_download_dir
from .downloader import download
from .installer import install_shortcut
from .interactive import run_interactive_mode
from .models import DownloadRequest
from .utils import build_terminal_progress_callback, load_batch_entries, normalize_destination, normalize_video_input


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="Downloader modular para musicas e videos.",
        add_help=False,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--interactive", action="store_true", help="Abre o modo interativo no terminal.")
    mode.add_argument("--gui", action="store_true", help="Abre a interface grafica.")
    mode.add_argument("--install-shortcut", action="store_true", help="Cria atalho de execucao rapida.")

    media = parser.add_mutually_exclusive_group()
    media.add_argument("--mp3", action="store_true", help="Baixa somente audio em MP3.")
    media.add_argument("--mp4", action="store_true", help="Baixa video em MP4.")

    parser.add_argument("--link", help="Link do video.")
    parser.add_argument("--list", help="Caminho de um TXT com um link ou ID por linha.")
    parser.add_argument("--local", help="Pasta de destino do download.")
    parser.add_argument("--audio-quality", default="128", help="Bitrate do MP3 em kbps. Padrao: 128.")
    parser.add_argument("--video-quality", default="best", help="Qualidade do MP4: best, 1080, 720, 480...")
    parser.add_argument("--hide-progress", action="store_true", help="Oculta o progresso detalhado do download.")
    parser.add_argument("-h", "--help", action="store_true", dest="help_requested", help="Mostra esta ajuda e abre o modo interativo.")
    return parser


def run_cli(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.help_requested:
        parser.print_help()
        print()
        return run_interactive_mode()

    if len(sys.argv) == 1:
        return run_interactive_mode()

    if args.gui:
        from .gui import run_gui

        return run_gui()

    if args.interactive:
        return run_interactive_mode()

    if args.install_shortcut:
        print(install_shortcut())
        return 0

    if not args.link and not args.list:
        print("Use --link ou --list para informar o que baixar, ou abra --interactive / --gui.")
        return 1

    destination = normalize_destination(args.local, default_download_dir())
    entries = [normalize_video_input(args.link)] if args.link else load_batch_entries(args.list)
    if not entries:
        print("Nenhum link valido encontrado.")
        return 1

    success_count = 0
    for index, entry in enumerate(entries, start=1):
        if len(entries) > 1:
            print(f"[{index}/{len(entries)}] {entry}")
        request = DownloadRequest(
            link=entry,
            destination=destination,
            audio_only=not args.mp4,
            video_only=args.mp4,
            audio_bitrate=args.audio_quality,
            video_quality=args.video_quality,
        )
        progress_callback = build_terminal_progress_callback(args.hide_progress)
        result = download(request, callback=progress_callback)
        if progress_callback is not None:
            print()
        print(result.message)
        if result.success:
            success_count += 1

    print(f"Destino: {destination}")
    if len(entries) > 1:
        print(f"Fila finalizada: {success_count}/{len(entries)} concluido(s).")
    return 0 if success_count == len(entries) else 1
