from __future__ import annotations

from .cli import build_parser, run_cli


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return run_cli(args, parser)
