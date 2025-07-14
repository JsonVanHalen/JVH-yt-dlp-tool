# app.py

from flask import Flask, render_template, request, send_file, after_this_request, jsonify
from datetime import datetime, timezone
from pathlib import Path
import yt_dlp, os, re, glob, sqlite3, tempfile, shutil, subprocess
import time, json, sqlite3

app = Flask(__name__)
app.config['EXPLAIN_TEMPLATE_LOADING'] = True

def get_codecs(filepath):
    def probe(stream_type):
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'error',
                '-select_streams', f'{stream_type}:0',
                '-show_entries', 'stream=codec_name',
                '-of', 'json', filepath
            ], capture_output=True, text=True)
            streams = json.loads(result.stdout).get('streams', [])
            return streams[0]['codec_name'] if streams else None
        except Exception:
            return None

    return probe('v'), probe('a')  # video_codec, audio_codec

def init_db():
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            yt_video_id TEXT UNIQUE,
            title TEXT,
            url TEXT,
            mode TEXT,
            quality TEXT,
            filename TEXT,
            thumbnail TEXT,
            video_codec TEXT,
            audio_codec TEXT,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def upsert_download(info, filename, video_codec, audio_codec):
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO downloads (
            yt_video_id, title, url, mode, quality, filename, thumbnail,
            video_codec, audio_codec, downloaded_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(yt_video_id) DO UPDATE SET
            title = excluded.title,
            url = excluded.url,
            mode = excluded.mode,
            quality = excluded.quality,
            filename = excluded.filename,
            thumbnail = excluded.thumbnail,
            video_codec = excluded.video_codec,
            audio_codec = excluded.audio_codec,
            downloaded_at = CURRENT_TIMESTAMP
    ''', (
        info.get("id"),
        info.get("title"),
        info.get("webpage_url"),
        info.get("mode"),
        info.get("quality"),
        filename,
        info.get("thumbnail"),
        video_codec,
        audio_codec
    ))
    conn.commit()
    conn.close()

def log_download(info, mode, quality_or_bitrate, filename, video_codec, audio_codec):
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    
    # Grab fields from yt-dlp metadata
    yt_video_id = info.get("id")
    title = info.get("title")
    url = info.get("webpage_url")
    # mode = info.get("mode")  # You may be injecting this manually
    # quality = info.get("quality")  # Also may be set by you
    thumbnail = info.get("thumbnail")

    c.execute('''
        INSERT INTO downloads (
            yt_video_id, title, url, mode, quality,
            filename, thumbnail, video_codec, audio_codec, downloaded_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(yt_video_id) DO UPDATE SET
            title = excluded.title,
            url = excluded.url,
            mode = excluded.mode,
            quality = excluded.quality,
            filename = excluded.filename,
            thumbnail = excluded.thumbnail,
            video_codec = excluded.video_codec,
            audio_codec = excluded.audio_codec,
            downloaded_at = CURRENT_TIMESTAMP
    ''', (
        yt_video_id, title, url, mode, quality_or_bitrate,
        filename, thumbnail, video_codec, audio_codec
    ))

    conn.commit()
    conn.close()

def sanitize(s):
    return re.sub(r'[^\w\-_.]', '', s).lower()

def append_codecs_to_existing_filename(filename, video_codec=None, audio_codec=None):
    if not filename:
        return None  # Or fallback/default handling
  
    base, ext = os.path.splitext(filename)
    
    parts = [sanitize(video_codec)]
    if audio_codec and sanitize(audio_codec) != sanitize(video_codec):
        parts.append(sanitize(audio_codec))
    
    codec_suffix = "__" + "_".join(filter(None, parts)) if parts else ""
    return f"{base}{codec_suffix}{ext}"

def extract_video_info(url):
    try:
        result = subprocess.run([
            'yt-dlp',
            '--extractor-args', 'youtube:player_client=web',
            '--force-ipv4',
            '--dump-json',
            '-f', 'bv*+ba/b',
            '--quiet',
            url
        ], capture_output=True, text=True, check=True)

        info = json.loads(result.stdout)
        return {
            'title':       info.get('title'),
            'thumbnail':   info.get('thumbnail'),
            'duration':    info.get('duration'),
            'uploader':    info.get('uploader'),
            'upload_date': info.get('upload_date'),
            'resolutions': sorted({
                f['height'] for f in info.get('formats', [])
                if f.get('vcodec') != 'none' and f.get('height')
            }, reverse=True)
        }
    except subprocess.CalledProcessError as e:
        print("🔥 CLI call failed:", e.stderr)
        return {'error': 'Could not extract video info'}

def embed_metadata(url):
    command = [
        "yt-dlp",
        "--embed-metadata",
        "--no-download",
        url
    ]
    subprocess.run(command, check=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url           = request.form['url'].strip()
        mode          = request.form.get('format', 'video')
        quality       = request.form.get('quality', 'best')
        audio_bitrate = request.form.get('audio_bitrate', '192')

         # 0) Initialize DB if it doesn't exist
        init_db()  # ✅ Create the table if it doesn't exist

        # 1) Create a temp directory for this download
        workdir = tempfile.mkdtemp(prefix="ytdl_")

        # 2) Choose yt-dlp format and filename suffix
        if mode == 'audio':
            fmt, suffix = 'bestaudio/best', f'_audio_{audio_bitrate}kbps'
            print("*******************************************************")
            print("Bitrate, Format, Suffix: " + audio_bitrate + ", " + fmt + ", " + f'_audio_{audio_bitrate}kbps')
            print("*******************************************************")
        else:
            fmt = 'bestvideo+bestaudio/best' if quality=='best' \
                  else f"bestvideo[height<={quality}]+bestaudio/best"
            suffix = '_best' if quality=='best' else f'_{quality}p'

        # 3) Point yt-dlp at the temp directory
        outtmpl = os.path.join(workdir, "%(title).100s" + suffix + ".%(ext)s") # os.path.join(workdir, f"%(title).100s{suffix}.%(ext)s")
        ydl_opts = {
            'format': fmt,
            'outtmpl': outtmpl,
            'restrictfilenames': True,
            'quiet': True
        }
        if mode == 'video':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mkv',  # Convert to MKV
            }]
            ydl_opts['merge_output_format'] = 'mkv'
            # ydl_opts['noplaylist'] = True  # Download only the single video, not playlists
        if mode == 'audio':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': str(audio_bitrate)
            }]

        try:
            # 4) Download into workdir
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

            # ✅ Extract original filepath before renaming
            requested = info.get("requested_downloads", [{}])[0]
            original_path = requested.get("filepath")

            # Optional: print for sanity check
            print("🎯 Original path for metadata pass:", original_path)

            # ✅ Run yt-dlp again to embed metadata (doesn't quite work yet, future enhancement)
            subprocess.run([
                "yt-dlp",
                "--embed-metadata",
                "--no-download",
                url
            ], check=True)

            # 5) Locate the produced file
            files = glob.glob(os.path.join(workdir, '*'))
            if not files:
                raise FileNotFoundError("No file found in temp folder")
            full_path = max(files, key=os.path.getmtime)
            basename  = os.path.basename(full_path)

            video_codec, audio_codec = get_codecs(full_path)

            # 6) Log to history (use real info so thumbnail is saved)
            log_download(info,
                         mode,
                         quality if mode=='video' else audio_bitrate,
                         basename,
                         video_codec,
                         audio_codec
                         )

            # 7) Schedule cleanup of tempdir after response
            @after_this_request
            def cleanup(response):
                try:
                    shutil.rmtree(workdir)
                except Exception:
                    pass
                return response

            # 8) Stream file back to browser
            filename = os.path.basename(full_path)
            print("*******************************************************")
            print(f"Downloaded: {filename}")
            print("🔍 Filename before codec append:", repr(filename))
            print("*******************************************************")
            if mode == 'audio':
                final_filename = filename
            else:
                final_filename = append_codecs_to_existing_filename(filename, video_codec, audio_codec)
            print("*******************************************************")
            print(f"full_path: {full_path}")
            print(f"final_filename: {final_filename}")
            print("*******************************************************")
            return send_file(full_path, as_attachment=True, download_name=final_filename)

        except Exception as e:
            shutil.rmtree(workdir, ignore_errors=True)
            return f"Download failed: {e}", 500

    return render_template('index.html')

@app.route("/exists")
def file_exists():
    from pathlib import Path

    filename = request.args.get("file")
    if not filename:
        return jsonify({"exists": False})

    # Prevent directory traversal and ensure local path
    base = Path("downloads").resolve()
    full_path = Path(filename).resolve()

    if not str(full_path).startswith(str(base)):
        return jsonify({"exists": False})

    # print("Requested file:", filename, flush=True)
    # print("Resolved path:", full_path, flush=True)

    return jsonify({"exists": full_path.exists()})

@app.route('/preview', methods=['POST'])
def preview():
    data = request.get_json(silent=True)
    url = request.form.get('url') or (data and data.get('url'))
    if not url:
        return jsonify({'error': 'Missing URL'}), 400
    url = url.strip()

    try:
        ### This one worked for preview but seems to break downloads
        # result = subprocess.run([
        #     'yt-dlp',
        #     '--extractor-args', 'youtube:player_client=android;formats=missing_pot',
        #     '--skip-download',
        #     '--dump-json',
        #     '--force-ipv4',
        #     url
        # ], capture_output=True, text=True, check=True)
        result = subprocess.run([
            'yt-dlp',
            '--extractor-args', 'youtube:player_client=android;formats=missing_pot',
            '--skip-download',
            '--dump-json',
            '--quiet',
            '--no-warnings',
            '--force-ipv4',
            '--quiet',
            url
        ], capture_output=True, text=True, check=True)

        print("stdout:", repr(result.stdout))
        print("stderr:", result.stderr)

        info = json.loads(result.stdout)

        formats = info.get('formats', [])
        resolutions = sorted({
            f['height'] for f in formats
            if f.get('vcodec') != 'none' and f.get('height')
        }, reverse=True)

        return jsonify({
            'title':       info.get('title'),
            'thumbnail':   info.get('thumbnail'),
            'duration':    info.get('duration'),
            'uploader':    info.get('uploader'),
            'upload_date': info.get('upload_date'),
            'resolutions': resolutions
        })
    except subprocess.CalledProcessError as e:
        print("Preview subprocess error:", e.stderr)
        return jsonify({'error': 'yt-dlp failed'}), 500
    except Exception as e:
        print("Preview error:", e)
        return jsonify({'error': 'Could not extract video info'}), 500

@app.route('/history')
def get_history():
    try:
        conn = sqlite3.connect('history.db')
        c = conn.cursor()
        c.execute("""
            SELECT title, mode, quality, downloaded_at, url, thumbnail, filename, video_codec, audio_codec
            FROM downloads
            ORDER BY downloaded_at DESC
            LIMIT 10
        """)
        rows = c.fetchall()
        history = [{
            'title':         r[0],
            'mode':          r[1],
            'quality':       r[2],
            'downloaded_at': r[3],
            'url':           r[4],
            'thumbnail':     r[5],
            'filename':      r[6],
            'video_codec':   r[7],
            'audio_codec':   r[8]
        } for r in rows]
        return jsonify(history)
    except Exception as e:
        print("History fetch error:", e)
        return jsonify({'error': 'Could not load history'}), 500
     
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

def batch_download_from_json(json_file='video_urls.json'):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            video_urls = data.get('videos', [])
            mode = data.get('mode', 'video')
            quality = data.get('quality', 'best')
            audio_bitrate = data.get('audio_bitrate', '192')

            for url in video_urls:
                print(f"[+] Downloading: {url}")
                # Mimic the POST behavior from index()
                with app.test_request_context(method='POST', data={
                    'url': url,
                    'format': mode,
                    'quality': quality,
                    'audio_bitrate': audio_bitrate
                }):
                    response = index()
                    print(f"[✓] Done: {url}")

    except Exception as e:
        print(f"[!] Batch download failed: {e}")

@app.route("/inspect", methods=["GET"])
def inspect_file():
    path = request.args.get("file")
    if not path:
        return jsonify({"error": "Missing ?file= parameter"}), 400

    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, check=True
        )
        video_codec = result.stdout.strip()

        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
             "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, check=True
        )
        audio_codec = result.stdout.strip()

        return jsonify({
            "file": path,
            "video_codec": video_codec or None,
            "audio_codec": audio_codec or None
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"ffprobe failed", "details": e.stderr}), 500


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'batch':
        batch_download_from_json()
    else:
        app.run(debug=True)
