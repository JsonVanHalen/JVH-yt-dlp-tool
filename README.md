# JVH - YT-DLP Tool  
> Lightweight web-based tool for downloading YouTube videos and audio — now with smart codec detection, and intelligent fallback handling.

![Version](https://img.shields.io/badge/version-1.0.2-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-yellow)

---

## 🧰 Requirements

### ✅ System Dependencies
Manually install the following tools:
- **`ffmpeg` & `ffprobe`** — audio/video processing  
  - Ubuntu: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`
- **`sqlite3`** — lightweight local database engine  
  - Ubuntu: `sudo apt install sqlite3`

### 📦 Python Packages
Install via pip:

```bash
pip install -r requirements.txt
```

---

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/JsonVanHalen/JVH-YT-DLP-Tool.git
cd JVH-YT-DLP-Tool

# (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch the app
python app.py
```

Then visit `http://localhost:5000` in your browser.

---

## 🧾 Versioning & Repo Reset

The project starts at version **1.0.2** to reflect a continuation of development from a previous repository. That original repo was retired due to persistent Git history issues, including flagged secrets and virtual environment artifacts that conflicted with GitHub's push protection policies. This current repository begins with a fresh commit history and a verified release tagged as `v1.0.2`, representing a clean slate for future development.

---

## 🔥 New in v1.0.2

- 🎵 **Audio-only download mode**
- 🧠 **Codec-aware filename suffixes** (e.g. `_av1_opus`) for better organization
- 📜 **Automatic `yt-dlp` version checks** displayed to users
- 🧼 Streamlined logging and cleaner download flow
- 🗂️ Enhanced SQLite history with improved timestamp formatting

---

## 🧪 Example Screenshot

```html
<!-- Replace with actual screenshot -->
![History View with Codec Info](docs/history-with-codecs.png)
```

Shows codec suffixes and enhanced download tracking.

---

## 🧼 Roadmap for Future Enhancements

- 🧠 Intelligent fallback handling for browser-incompatible codecs
- 🔊 Audio stream extraction with `ffmpeg -c:a copy` (no transcoding)
- 📊 Codec usage analytics dashboard
- ☁️ Deployment guides for Render and Fly.io
- 📤 Export/download history to CSV/JSON
- Support for metadata and embedded thumbnails
- ⚠️ **Backend offline detection** for graceful failure messaging

---

## 📄 License

This project is licensed under the MIT License