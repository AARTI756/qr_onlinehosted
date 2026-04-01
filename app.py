from flask import Flask, request, render_template, session, redirect, send_file
import requests
from flask_sqlalchemy import SQLAlchemy
from modules.auth import auth_routes

import bcrypt
import uuid
import qrcode
import os
from datetime import datetime, timedelta
from pytz import timezone

# ----------------------------
# APP CONFIG
# ----------------------------
app = Flask(__name__)

# ✅ Use environment variable (Render safe)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# ✅ Database config (Render compatible)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.register_blueprint(auth_routes)

# ----------------------------
# HOME
# ----------------------------
@app.route("/")
def home():
    return redirect("/generate")


# ----------------------------
# MODELS
# ----------------------------
class QR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expiry = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer)
    status = db.Column(db.String(20), default="active")

    is_protected = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(200))

    is_one_time = db.Column(db.Boolean, default=False)
    is_used = db.Column(db.Boolean, default=False)


class ScanLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qr_id = db.Column(db.Integer)
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(100))
    location = db.Column(db.String(200))


with app.app_context():
    db.create_all()


# ----------------------------
# GENERATE QR
# ----------------------------
@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        data = request.form["data"].strip()
        expiry_minutes = int(request.form["expiry"])
        password = request.form.get("password")
        one_time = request.form.get("one_time") == "on"

        token = str(uuid.uuid4())
        expiry_time = datetime.utcnow() + timedelta(minutes=expiry_minutes)

        hashed_password = None
        is_protected = False

        if password:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            is_protected = True

        new_qr = QR(
            token=token,
            data=data,
            expiry=expiry_time,
            owner_id=session.get("user_id"),
            is_protected=is_protected,
            password_hash=hashed_password,
            is_one_time=one_time
        )

        db.session.add(new_qr)
        db.session.commit()

        qr_content = f"{request.host_url}verify/{token}"
        img = qrcode.make(qr_content)

        os.makedirs("static", exist_ok=True)

        img_path = f"static/{token}.png"
        img.save(img_path)

        return render_template("qr_result.html", qr_image=img_path, data=data)

    return render_template("generate.html")


# ----------------------------
# LOCATION
# ----------------------------
def get_location(ip):
    try:
        if ip == "127.0.0.1" or ip.startswith("192."):
            return "Local Network"

        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=2).json()

        if res.get("status") == "success":
            city = res.get("city", "")
            country = res.get("country", "")
            return f"{city}, {country}".strip(", ")

        return "Unknown"
    except:
        return "Unknown"


@app.route("/save_location")
def save_location():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    print("GPS Location:", lat, lon)
    return "OK"


# ----------------------------
# HISTORY
# ----------------------------
@app.route("/history")
def history():
    records = QR.query.all()
    ist = timezone("Asia/Kolkata")

    current_time_ist = datetime.utcnow().replace(
        tzinfo=timezone("UTC")
    ).astimezone(ist)

    for r in records:
        r.created_at_ist = r.created_at.replace(
            tzinfo=timezone("UTC")
        ).astimezone(ist)

        r.expiry_ist = r.expiry.replace(
            tzinfo=timezone("UTC")
        ).astimezone(ist)

        logs = ScanLog.query.filter_by(qr_id=r.id).all()
        r.scan_count = len(logs)

        last_scan = ScanLog.query.filter_by(qr_id=r.id)\
            .order_by(ScanLog.scanned_at.desc()).first()

        if last_scan:
            r.last_scanned = last_scan.scanned_at.replace(
                tzinfo=timezone("UTC")
            ).astimezone(ist)
            r.last_location = last_scan.location
        else:
            r.last_scanned = None
            r.last_location = "No scans yet"

    return render_template("history.html", records=records, current_time=current_time_ist)


# ----------------------------
# VERIFY QR
# ----------------------------
@app.route("/verify/<token>", methods=["GET", "POST"])
def verify_qr(token):
    qr = QR.query.filter_by(token=token).first()

    if not qr:
        return render_template("invalid.html")

    if datetime.utcnow() > qr.expiry:
        qr.status = "expired"
        db.session.commit()
        return render_template("expired.html")

    if qr.is_one_time and qr.is_used:
        return render_template("expired.html")

    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if ip:
        ip = ip.split(",")[0].strip()  # ✅ get real user IP only
    location = get_location(ip)

    if qr.is_protected:
        if request.method == "POST":
            entered_password = request.form.get("password")

            if bcrypt.checkpw(entered_password.encode(), qr.password_hash.encode()):
                log = ScanLog(qr_id=qr.id, ip_address=ip, location=location)
                db.session.add(log)

                if qr.is_one_time:
                    qr.is_used = True

                db.session.commit()
                return render_template("valid.html", data=qr.data)

            return render_template("enter_password.html", error="Wrong password")

        return render_template("enter_password.html")

    log = ScanLog(qr_id=qr.id, ip_address=ip, location=location)
    db.session.add(log)

    if qr.is_one_time:
        qr.is_used = True

    db.session.commit()

    return render_template("valid.html", data=qr.data)

# ----------------------------
# SCANNER
# ----------------------------
@app.route("/scan_camera")
def scan_camera():
    return render_template("scan_camera.html")

# ----------------------------
# QR DETAILS
# ----------------------------
@app.route("/qr_details/<int:qr_id>")
def qr_details(qr_id):
    qr = QR.query.get(qr_id)

    if not qr:
        return "QR not found", 404

    logs = ScanLog.query.filter_by(qr_id=qr_id)\
        .order_by(ScanLog.scanned_at.desc()).all()

    ist = timezone("Asia/Kolkata")

    for log in logs:
        log.scanned_at_ist = log.scanned_at.replace(
            tzinfo=timezone("UTC")
        ).astimezone(ist)

    return render_template("qr_details.html", qr=qr, logs=logs)


@app.route("/scan_result")
def scan_result():
    data = request.args.get("data")

    qr_type = detect_qr_type(data) if data else "Unknown"

    return render_template(
        "scan_result.html",
        data=data,
        qr_type=qr_type
    )
# ----------------------------
# DOWNLOAD
# ----------------------------
@app.route("/download/<token>")
def download_qr(token):
    user_id = session.get("user_id")
    if not user_id:
        return "Unauthorized", 401

    record = QR.query.filter_by(token=token, owner_id=user_id).first()
    if not record:
        return "Not found", 404

    file_path = os.path.join("static", f"{token}.png")

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)

    return "File not found", 404

import re

def detect_qr_type(data):
    # URL detection
    if re.match(r'https?://\S+|www\.\S+', data):
        return "URL 🌐"
    
    # Email detection
    elif re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data):
        return "Email 📧"
    
    # Default → Text
    else:
        return "Text 📝"
    
# ----------------------------
# DELETE
# ----------------------------
@app.route("/delete/<token>")
def delete_qr(token):
    user_id = session.get("user_id")
    if not user_id:
        return "Unauthorized", 401

    record = QR.query.filter_by(token=token, owner_id=user_id).first()
    if not record:
        return "Not found", 404

    file_path = os.path.join("static", f"{token}.png")

    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(record)
    db.session.commit()

    return redirect("/history")


# ----------------------------
# RUN (for local only)
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))