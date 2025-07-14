# Changelog

All notable changes to this project will be documented in this file.

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
and adheres to [Semantic Versioning](https://semver.org/).

> ⚠️ _Note: v1.0.2 marks the first public release of this rebuilt repository. The version number was intentionally preserved from the original project to avoid conflicts with older metadata, tags, and GitHub push protection mechanisms. This clean start eliminates lingering virtual environment history and restores full control over release workflows._

---

## [1.0.2] – 2025-07-11

### 🚀 Added
- 🎵 Audio-only download mode
- 🧠 Codec-aware filename suffixes (e.g. `_av1_opus`) for video outputs
- 📜 Automatic `yt-dlp` version check included in frontend
- ⚠️ Intelligent backend offline detection with graceful fallback messaging
- 🗂️ Enhanced SQLite history records with improved timestamp formatting

### 🧼 Changed
- 🔧 Refactored logging for download routes to improve readability
- 🧪 Reverted Python-native download logic for improved stability
- 🧱 Renamed download files post-process using codec suffix logic
- 📤 Cleaned up GitHub release presentation and README formatting

### 🐞 Fixed
- 🎧 Audio-only flow compatibility issues (especially missing codec tags)
- 🔀 Filename inference issues during metadata injection pass

---

## [1.0.1] – 2025-07-07

### 🚀 Added
- 🎞️ Captured and stored `video_codec` and `audio_codec` via `ffprobe` on each download
- 💽 Displayed codec info directly in the History view table
- 🕰️ Standardized timestamps to Central Daylight Time (CDT) using `toLocaleString('America/Chicago')`
- 📂 Enabled SQLite-backed persistent history with auto-created table on first run
- 🧼 Improved UI and added graceful fallback handling for missing files

---

## [1.0.0] – 2025-07-02

### 🚀 Initial Release
- 🧪 Built a Flask-based web interface for submitting YouTube URLs
- ⚙️ Integrated `yt-dlp` for audio/video downloading
- 🎚️ Added resolution and quality selector (video/audio mode toggle)
- 📈 Implemented download history with progress bar and thumbnail preview
- 🔍 Visualized content type (video 🎥 vs. audio 🎧)

### 🐞 Known Issues
- Cookie upload feature does not currently bypass YouTube rate limits
- Some cloud/VPS instances may trigger bot-detection or throttling