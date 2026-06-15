import io
import os
import re
from pathlib import Path

from flask import Flask, jsonify, request, send_file, render_template
from PIL import Image

app = Flask(__name__)

FRAMES_DIR = Path(os.environ.get("FRAMES_DIR", "extracted_frames")).resolve()
THUMB_SIZE = (320, 180)

FILENAME_RE = re.compile(
    r"^(?P<video>.+?)_ts(?P<ts>[\d.]+)s_score(?P<score>[\d.]+)\.(jpg|png)$"
)


def parse_filename(name):
    m = FILENAME_RE.match(name)
    if not m:
        return None
    return {
        "video": m.group("video"),
        "timestamp": float(m.group("ts")),
        "score": float(m.group("score")),
    }


def get_image_info(path):
    info = parse_filename(path.name) or {}
    try:
        with Image.open(path) as img:
            info["width"] = img.width
            info["height"] = img.height
    except Exception:
        info["width"] = 0
        info["height"] = 0
    info["path"] = path.name
    info["size_kb"] = round(path.stat().st_size / 1024, 1)
    return info


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/info")
def info():
    if FRAMES_DIR.exists():
        jpgs = list(FRAMES_DIR.glob("*.jpg"))
        return jsonify({
            "configured": True,
            "folder": str(FRAMES_DIR),
            "count": len(jpgs),
        })
    return jsonify({"configured": False, "folder": None, "count": 0})


@app.route("/api/images")
def list_images():
    images = []
    for p in sorted(FRAMES_DIR.glob("*.jpg")):
        images.append(get_image_info(p))
    return jsonify(images)


@app.route("/api/thumbnail/<path:subpath>")
def thumbnail(subpath):
    full = (FRAMES_DIR / subpath).resolve()
    if not str(full).startswith(str(FRAMES_DIR)):
        return "forbidden", 403
    try:
        img = Image.open(full)
        img.thumbnail(THUMB_SIZE, Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=75)
        buf.seek(0)
        return send_file(buf, mimetype="image/jpeg")
    except Exception as e:
        return str(e), 404


@app.route("/api/image/<path:subpath>")
def full_image(subpath):
    full = (FRAMES_DIR / subpath).resolve()
    if not str(full).startswith(str(FRAMES_DIR)):
        return "forbidden", 403
    return send_file(full, mimetype="image/jpeg")


def hamming(h1, h2):
    if not h1 or not h2 or len(h1) != len(h2):
        return 999
    return sum(c1 != c2 for c1, c2 in zip(h1, h2))


@app.route("/api/dedup", methods=["POST"])
def dedup():
    data = request.get_json()
    groups = data.get("groups", {})
    threshold = data.get("threshold", 60)

    duplicates = []
    for video, imgs in groups.items():
        imgs_sorted = sorted(imgs, key=lambda x: x.get("score", 0), reverse=True)
        keepers = []
        for img in imgs_sorted:
            dh = img.get("dhash")
            if not dh:
                keepers.append(img)
                continue
            is_dup = any(
                hamming(dh, k.get("dhash", "")) <= threshold
                for k in keepers if k.get("dhash")
            )
            if is_dup:
                duplicates.append(img["name"])
            else:
                keepers.append(img)

    return jsonify({"duplicates": duplicates, "count": len(duplicates)})


if __name__ == "__main__":
    print(f"Configured folder: {FRAMES_DIR}")
    print(f"Open http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
