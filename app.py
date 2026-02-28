from flask import Flask, request, render_template, session, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from config import SECRET_KEY
from modules.db_config import DB_PATH
from database.init_db import init_db
from modules.encryption import decrypt_data
from modules.auth import auth_routes
from modules.qr_scanner import scan_qr_from_camera
import sqlite3
import uuid
import qrcode
import os
from datetime import datetime, timedelta
from pytz import timezone
from pyzbar.pyzbar import decode
from PIL import Image
import cv2


app = Flask(__name__)
app.secret_key = SECRET_KEY

init_db()   # create tables on startup
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.register_blueprint(auth_routes)


class QR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qr_id = db.Column(db.String(100), unique=True, nullable=False)
    data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expiry = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer)



@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        data = request.form["data"].strip()
        expiry_minutes = int(request.form["expiry"])

        qr_id = str(uuid.uuid4())
        expiry_time = datetime.utcnow() + timedelta(minutes=expiry_minutes)

        # Check if data is URL
        is_url = (
            data.startswith("http://")
            or data.startswith("https://")
            or ("." in data and " " not in data)
        )

        if is_url:
            # Add https if missing
            if not data.startswith("http"):
                data = "https://" + data
            qr_content = data  # Direct URL
        else:
            base_url = request.host_url
            qr_content = f"{base_url}verify/{qr_id}"

            new_qr = QR(
                qr_id=qr_id,
                data=data,
                created_at=datetime.utcnow(),
                expiry=expiry_time,
                owner_id=session.get("user_id")
            )
            db.session.add(new_qr)
            db.session.commit()

        img = qrcode.make(qr_content)
        if not os.path.exists("static"):
            os.makedirs("static")
        img_path = f"static/{qr_id}.png"
        img.save(img_path)

        return render_template("qr_result.html", qr_image=img_path, data=data)

    return render_template("generate.html")


@app.route('/camera_feed')
def camera_feed():
    def generate():
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/history")
def history():
    records = QR.query.all()
    ist = timezone("Asia/Kolkata")
    current_time_ist = datetime.utcnow().replace(tzinfo=timezone("UTC")).astimezone(ist)
    # convert created_at and expiry to IST for display
    for r in records:
        r.created_at_ist = r.created_at.replace(tzinfo=timezone("UTC")).astimezone(ist)
        r.expiry_ist = r.expiry.replace(tzinfo=timezone("UTC")).astimezone(ist)
    return render_template(
        "history.html",
        records=records,
        current_time=current_time_ist
    )

@app.route("/verify/<qr_id>")
def verify_qr(qr_id):

    qr = QR.query.filter_by(qr_id=qr_id).first()

    if not qr:
        return render_template("invalid.html")

    if datetime.utcnow() > qr.expiry:
        return render_template("expired.html")

    return render_template("valid.html", data=qr.data)

@app.route("/scan", methods=["GET", "POST"])
def scan_qr():
    if request.method == "POST":
        file = request.files["qr_image"]
        image = Image.open(file)

        decoded_objects = decode(image)

        if not decoded_objects:
            return render_template("scan.html", result="No QR detected")

        qr_content = decoded_objects[0].data.decode("utf-8")

        # If it's a verification URL
        if "/verify/" in qr_content:
            qr_id = qr_content.split("/verify/")[-1]

            qr = QR.query.filter_by(qr_id=qr_id).first()
            if not qr:
                return render_template("scan.html", result="Invalid QR")

            if datetime.utcnow() > qr.expiry:
                return render_template("scan.html", result="QR Expired")

            return render_template("scan.html", result=qr.data)

        # Otherwise normal QR (text or url)
        return render_template("scan.html", result=qr_content)

    return render_template("scan.html")

@app.route("/scan_camera")
def scan_camera():
    return render_template("scan_camera.html")

@app.route("/scan_result")
def scan_result():
    data = request.args.get("data")
    return render_template("scan_result.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
with app.app_context():
    db.create_all()