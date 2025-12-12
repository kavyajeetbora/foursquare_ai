# app.py  (updated version with CORS)
from flask import Flask, send_from_directory, request, Response, abort
from pathlib import Path

app = Flask(__name__, static_folder='.')

BASE_DIR = Path(__file__).parent

# ---------- ADD THIS CORS HELPER ----------
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Range'
    response.headers['Access-Control-Expose-Headers'] = 'Accept-Ranges, Content-Range, Content-Length'
    return response

@app.after_request
def after_request(response):
    return add_cors_headers(response)
# -------------------------------------------

@app.route("/")
def index():
    return {"status": "Server is running"}  

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)

@app.route("/tiles/<path:filename>")
def pmtiles(filename):
    file_path = BASE_DIR / filename
    if not file_path.exists() or file_path.suffix != ".pmtiles":
        abort(404)

    file_size = file_path.stat().st_size
    range_header = request.headers.get("Range", None)

    if not range_header:
        response = send_from_directory(BASE_DIR, filename, mimetype="application/octet-stream")
        response.headers["Accept-Ranges"] = "bytes"
        return add_cors_headers(response)

    # Handle Range request
    if not range_header.startswith("bytes="):
        abort(400)

    start_str, end_str = range_header[6:].split("-")
    start = int(start_str) if start_str else 0
    end = int(end_str) if end_str else file_size - 1

    if start >= file_size or end >= file_size or start > end:
        abort(416)

    length = end - start + 1

    def generate():
        with open(file_path, "rb") as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                chunk = f.read(min(65536, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(length),
        "Content-Type": "application/octet-stream",
    }

    return Response(generate(), status=206, headers=headers, mimetype="application/octet-stream")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)