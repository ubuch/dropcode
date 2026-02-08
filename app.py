import os
import string
import random
import time
import qrcode
from flask import Flask, request, jsonify, send_file, render_template, make_response
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from database import engine, SessionLocal
from models import Base, Code

UPLOAD_FOLDER = "uploads"
QR_FOLDER = "qrs"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
CODE_LENGTH = 6
LIFE_TIME_SECONDS = 10 * 60
DELETE_AFTER_SECONDS = 15 * 60

Base.metadata.create_all(bind=engine)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def delete_expired_codes():
    db = SessionLocal()
    try:
        now = time.time()

        expired = (
            db.query(Code)
            .filter(or_(Code.status == "expired", Code.expires_at < now))
            .all()
        )
        for code_row in expired:
            if os.path.exists(code_row.file_path):
                os.remove(code_row.file_path)
            if os.path.exists(code_row.qr_path):
                os.remove(code_row.qr_path)
            if now - code_row.expires_at > DELETE_AFTER_SECONDS:
                db.delete(code_row)

        db.commit()
    finally:
        db.close()


with SessionLocal() as db:
    delete_expired_codes()


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

    db = SessionLocal()
    try:

        code = generate_code()

        while db.query(Code).filter(Code.code == code).first() is not None:
            code = generate_code()

        qr_image = generate_qr_code(code)
        qr_path = os.path.join(QR_FOLDER, f"{code}.png")
        qr_image.save(qr_path)

        original_name = secure_filename(file.filename)
        filename = f"{code}_{original_name}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        created_at = time.time()
        expires_at = created_at + LIFE_TIME_SECONDS

        code_row = Code(
            code=code,
            file_path=filepath,
            qr_path=qr_path,
            original_name=original_name,
            created_at=created_at,
            expires_at=expires_at,
            status="active",
        )

        db.add(code_row)
        db.commit()

        return (
            jsonify(
                {
                    "code": code,
                    "qr_url": f"/qr/{code}",
                    "download_url": f"/download/{code}",
                    "expires_at": expires_at,
                }
            ),
            201,
        )
    finally:
        db.close()


@app.route("/download")
def download():
    return render_template("download.html")


def validate_code(code):
    db = SessionLocal()
    try:
        code_row = db.query(Code).filter(Code.code == code).first()

        if not code_row:
            return None, ("Invalid code", 404)

        if code_row.status == "expired":
            return None, ("Code expired", 410)

        if code_row.expires_at < time.time():
            code_row.status = "expired"
            db.commit()
            return None, ("Code expired", 410)

        return code_row, None
    finally:
        db.close()


@app.route("/download/<code>")
def get_image(code):
    code_row, error = validate_code(code)
    if error:
        msg, status = error
        return jsonify(error=msg), status

    response = make_response(send_file(code_row.file_path, as_attachment=False))
    response.headers["X-Filename"] = code_row.original_name

    return response


@app.route("/qr/<code>")
def get_qr_code(code):
    code_row, error = validate_code(code)
    if error:
        msg, status = error
        return jsonify(error=msg), status

    return send_file(code_row.qr_path, mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True)
