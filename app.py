import yt_dlp
import os
from flask import Flask, request, send_file, render_template, jsonify

app = Flask(__name__)

# Thư mục lưu video tạm thời
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "Thiếu URL"}), 400

    ydl_opts = {
        # Thử nhiều format, ưu tiên format có sẵn cả video+audio
        "format": "18/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
        "merge_output_format": "mp4",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "noplaylist": True,

        # Giả lập trình duyệt thật để tránh 403
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        },

        # Thêm extractor args để bypass
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
            }
        },

        "retries": 5,
        "ignoreerrors": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Đảm bảo đúng extension sau khi merge
            if not os.path.exists(filename):
                filename = filename.rsplit(".", 1)[0] + ".mp4"

        return send_file(
            filename,
            as_attachment=True,
            download_name=os.path.basename(filename)
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Railway tự set PORT, dùng 5000 nếu chạy local
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)