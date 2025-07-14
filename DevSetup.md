# 🧰 WSL Dev Environment Setup Guide

This quickstart sets up a full-stack development environment using WSL, VS Code, GitHub SSH, and Python venv. Designed for fast bootstraps on fresh Windows machines.

---

## 1️⃣ Core Tools Installation

### ✅ WSL (Ubuntu)

Open PowerShell (Admin):

```powershell
wsl --install
```

Restart when prompted.

---

### ✅ Git & VS Code

- Install [Git for Windows](https://git-scm.com/download/win)
- Install [Visual Studio Code](https://code.visualstudio.com/)
  - Enable **WSL extension**
  - Optionally install **Python**, **Pylance**, and **Prettier**

---

## 2️⃣ SSH Key Setup for GitHub

Inside WSL:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
```

Paste the public key into your [GitHub SSH settings](https://github.com/settings/keys)

---

## 3️⃣ Clone Your Project

```bash
git clone git@github.com:jsonvanhalen/JVH-YT-DLP-TOOL.git
cd JVH-YT-DLP-TOOL
code .
```

---

## 4️⃣ Python Virtual Environment

Create and activate:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

Deactivate when done:

```bash
deactivate
```

---

## 5️⃣ Multimedia Tools (FFmpeg / yt-dlp)

Install FFmpeg:

```bash
sudo apt update
sudo apt install ffmpeg
```

Install yt-dlp:

```bash
pip install yt-dlp
```

---

## 6️⃣ Project Runtime

To run the Flask app:

```bash
export FLASK_APP=app.py
flask run
```

---

## 🧪 Daily Dev Routine

See `DailyLaunchGuide.txt` for repeatable workflow:
1. Delete old clone
2. Clone fresh from GitHub
3. Launch VS Code
4. Activate venv
5. Run + develop 🚀
