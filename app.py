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
        "format": "18/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "merge_output_format": "mp4",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        # Trả về đường dẫn file sau khi tải
        "noplaylist": True,
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