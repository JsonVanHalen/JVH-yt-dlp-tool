# 🛣️ Project Roadmap

This roadmap outlines completed milestones and future goals for the JVH-YT-DLP-Tool project. The focus remains on stability, usability, and extensibility, with room for experimentation as the project evolves.

---

## ✅ Completed (v1.0.2)

- Rebased and cleaned up Git history after conflict recovery
- Reinstated accurate source files and restored v1.0.2 baseline
- Upsert functionality for SQLite history records
- Timestamp standardization with timezone awareness
- `.venv/` exclusion from commits via improved `.gitignore`
- Packaging script updated to exclude `.venv/` and `.venv` artifacts
- Metadata cleanup and repo polish
- Audio-only and subtitle support stabilized
- Version tagging flow revalidated

---

## 🛠️ In Progress

- Polish: Improve error handling and user feedback messages
- Polish: Enhance layout/UI responsiveness for mobile
- Fix: Finalize cookie upload flow from client to backend
- Optimize: Clean timestamp formatting across history and display

---

## 🧭 Next Goals (v1.1.0 Target)

- ☁️ Enable seamless cloud/headless deployment (Codespace or Fly.io)
- 🔐 Add authentication layer for shared/multi-user instances
- 🧪 Write unit tests for `download_video()` and key flows
- 🔄 Persistent cookie support via session storage or OAuth2
- ⏳ Real-time progress bars for download status
- 📁 Whisper-based subtitle generation (experimental)
- 🐳 Optional Docker setup (stretch)

---

## 💡 Ideas & Stretch Goals

- Streamable preview before download
- Custom output templates (filename control, tags)
- Expanded platform support (Vimeo, SoundCloud, etc.)
- Usage analytics dashboard (formats, volumes, trends)
- GitHub Actions: release automation and test runner
