import os
import string
import random
import time
from flask import Flask, request, jsonify, send_file, render_template, make_response
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
CODE_LENGTH = 6

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("index.html")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


codes = {}


def generate_code(length=CODE_LENGTH, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choices(chars, k=length))


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

    original_name = secure_filename(file.filename)
    filename = f"{code}_{original_name}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    codes[code] = {
        "path": filepath,
        "original_name": original_name,
        "created_at": time.time(),
    }

    return jsonify({"code": code}), 201


@app.route("/download")
def download():
    return render_template("download.html")


@app.route("/download/<code>")
def return_image(code):
    if code not in codes:
        return jsonify(error="Invalid code"), 404

    file_info = codes[code]
    filepath = file_info["path"]
    original_name = file_info["original_name"]

    response = make_response(send_file(filepath, as_attachment=False))
    response.headers["X-Filename"] = original_name
    return response


if __name__ == "__main__":
    app.run(debug=True)
