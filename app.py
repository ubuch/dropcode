import os
import string
import random
import time
import qrcode
from flask import Flask, request, jsonify, send_file, render_template, make_response
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
QR_FOLDER = "qrs"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
CODE_LENGTH = 6
LIFE_TIME_SECONDS = 10 * 60


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def delete_expired_files():
    now = time.time()
    for folder in (UPLOAD_FOLDER, QR_FOLDER):
        for filename in os.listdir(folder):

            if filename.startswith("."):
                continue

            path = os.path.join(folder, filename)

            file_age = now - os.path.getmtime(path)

            if file_age > LIFE_TIME_SECONDS:
                os.remove(path)


delete_expired_files()

codes = {}


@app.before_request
def cleanup():
    delete_expired_codes()


@app.route("/")
def index():
    return render_template("index.html")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_code(length=CODE_LENGTH, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choices(chars, k=length))


def generate_qr_code(code):
    url = request.host_url + f"download/{code}"
    return qrcode.make(url)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify(error="No file part"), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify(error="No selected file"), 400

    if not allowed_file(file.filename):
        return jsonify(error="Invalid file type"), 400

    code = generate_code()
    while code in codes:
        code = generate_code()

    qr_image = generate_qr_code(code)
    qr_path = os.path.join(QR_FOLDER, f"{code}.png")
    qr_image.save(qr_path)

    original_name = secure_filename(file.filename)
    filename = f"{code}_{original_name}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    created_at = time.time()

    codes[code] = {
        "path": filepath,
        "qr_path": qr_path,
        "original_name": original_name,
        "created_at": created_at,
        "expires_at": created_at + LIFE_TIME_SECONDS,
    }

    return (
        jsonify(
            {
                "code": code,
                "qr_url": f"/qr/{code}",
                "download_url": f"/download/{code}",
                "expires_at": codes[code]["expires_at"],
            }
        ),
        201,
    )


@app.route("/download")
def download():
    return render_template("download.html")


def validate_code(code):
    if code not in codes:
        return jsonify(error="Invalid code"), 404

    if codes[code]["expires_at"] < time.time():
        return jsonify(error="Code expired"), 410

    return None


@app.route("/download/<code>")
def get_image(code):
    code_error = validate_code(code)
    if code_error is not None:
        return code_error

    file_info = codes[code]
    filepath = file_info["path"]
    original_name = file_info["original_name"]

    response = make_response(send_file(filepath, as_attachment=False))
    response.headers["X-Filename"] = original_name
    return response


@app.route("/qr/<code>")
def get_qr_code(code):
    code_error = validate_code(code)
    if code_error is not None:
        return code_error

    return send_file(codes[code]["qr_path"], mimetype="image/png")


def delete_expired_codes():
    now = time.time()
    for code, file_info in list(codes.items()):
        if file_info["expires_at"] < now:
            if os.path.exists(file_info["path"]):
                os.remove(file_info["path"])
            if os.path.exists(file_info["qr_path"]):
                os.remove(file_info["qr_path"])
            del codes[code]


if __name__ == "__main__":
    app.run(debug=True)
