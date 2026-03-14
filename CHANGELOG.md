# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

### Added

- GUI action to open the download folder directly from the app.
- GUI queue stop control to finish the current item and halt the remaining queue safely.
- CLI batch summary listing failed entries after the queue finishes.
- Shared deduplication for repeated items in TXT imports and CLI batch processing.
- Persistent download history stored locally and displayed inside the GUI.

### Changed

- CLI now accepts `--link` together with `--list`, merging both sources into a single deduplicated queue.
- GUI now blocks queue-editing actions while downloads are running to avoid inconsistent state.
- GUI stop control now performs real in-progress cancellation instead of only stopping after the current item.

### Fixed

- Queue handling now avoids duplicate entries with the same source, format, and quality.
- GUI batch display now shows cleaner video identifiers for imported YouTube URLs.

## [0.1.0] - 2026-03-13

### Added

- Modular project structure with shared download core using `yt-dlp`.
- CLI mode for direct downloads with `--mp3`, `--mp4`, `--link`, `--list`, `--audio-quality`, `--video-quality`, and `--hide-progress`.
- Interactive terminal mode opened by default when no arguments are passed.
- Desktop GUI with support for:
  - direct URL input
  - raw YouTube video IDs
  - queue management
  - TXT batch import
  - configurable audio and video quality
- Linux and Windows shortcut installer support.
- Default download directory inside the project root at `downloads/`.
- Batch TXT parsing with one URL or video ID per line and support for comment lines starting with `#`.

### Changed

- Default MP3 quality set to `128 kbps`.
- Terminal download progress updated to a single-line style instead of printing many lines.
- GUI opening restricted to explicit `--gui`, while plain `ytb-downloader` now opens interactive mode.

### Fixed

- Graceful cancellation handling in interactive mode for `Ctrl+C` and closed stdin.
- Launcher behavior so the command can use the project virtual environment automatically when available.
