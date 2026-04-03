from flask import Flask, request, render_template, session, redirect, send_file
import requests
from flask_sqlalchemy import SQLAlchemy
from modules.auth import auth_routes
import cv2
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

    # ✅ Get real IP
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        ip = ip.split(",")[0].strip()

    location = get_location(ip)

    # 🔐 PASSWORD PROTECTED FLOW
    if qr.is_protected:
        if request.method == "POST":
            entered_password = request.form.get("password")

            if bcrypt.checkpw(entered_password.encode(), qr.password_hash.encode()):
                
                # ✅ Save scan log
                log = ScanLog(qr_id=qr.id, ip_address=ip, location=location)
                db.session.add(log)

                if qr.is_one_time:
                    qr.is_used = True

                db.session.commit()

                # ✅ CLEAN PROCESSING (FIXED)
                data, qr_type, is_url, is_malicious = process_qr_data(qr.data)

                return render_template(
                    "valid.html",
                    data=data,
                    qr_type=qr_type,
                    is_url=is_url,
                    is_malicious=is_malicious
                )

            return render_template("enter_password.html", error="Wrong password")

        return render_template("enter_password.html")

    # 🔓 NORMAL FLOW
    log = ScanLog(qr_id=qr.id, ip_address=ip, location=location)
    db.session.add(log)

    if qr.is_one_time:
        qr.is_used = True

    db.session.commit()

    # ✅ CLEAN PROCESSING (FIXED)
    data, qr_type, is_url, is_malicious = process_qr_data(qr.data)

    return render_template(
        "valid.html",
        data=data,
        qr_type=qr_type,
        is_url=is_url,
        is_malicious=is_malicious
    )


# SCANNER
# ----------------------------
@app.route("/scan_camera")
def scan_camera():
    return render_template("scan_camera.html")

@app.route("/scan_upload", methods=["POST"])
def scan_upload():
    file = request.files.get("file")

    if not file:
        return "No file uploaded"

    filename = str(uuid.uuid4()) + ".png"
    filepath = os.path.join("static", filename)
    file.save(filepath)

    image = cv2.imread(filepath)

    if image is None:
        return "Invalid image"

    # 📷 Step 1: Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 📷 Step 2: Noise reduction
    blurred = cv2.GaussianBlur(gray, (5,5), 0)

    # 🔍 Step 3: Detect QR
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(blurred)

    if data:
        os.remove(filepath)  # ✅ delete file after processing
        return redirect(f"/scan_result?data={data}")
    else:
        os.remove(filepath)  # ✅ delete file even if failed
        return "No QR detected"


from urllib.parse import urlparse

def is_malicious_url(url):
    url = url.strip().lower()

    # ✅ Normalize (important!)
    if not url.startswith("http"):
        url = "http://" + url

    parsed = urlparse(url)
    domain = parsed.netloc

    # ✅ Trusted domains
    trusted_domains = [
        "qr-onlinehosted.onrender.com",
        "localhost",
        "127.0.0.1"
    ]

    if any(td in domain for td in trusted_domains):
        return False

    # 🚨 Suspicious keywords
    suspicious_keywords = [
        "login", "verify", "update", "bank",
        "secure", "account", "password", "confirm", "signin"
    ]

    if any(word in url for word in suspicious_keywords):
        return True

    # 🚨 Heuristic 1: too many hyphens
    if domain.count("-") >= 2:
        return True

    # 🚨 Heuristic 2: long domain
    if len(domain) > 25:
        return True

    return False
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
    raw_data = request.args.get("data")

    data, qr_type, is_url, is_malicious = process_qr_data(raw_data)

    return render_template(
        "scan_result.html",
        data=data,
        qr_type=qr_type,
        is_url=is_url,
        is_malicious=is_malicious
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
    raw = data.strip()   # ✅ keep original
    lower = raw.lower()  # only for checking

    url_pattern = r'^(https?://|www\.)\S+'
    domain_pattern = r'^[a-z0-9\-]+\.[a-z]{2,}'

    if re.match(url_pattern, lower) or re.match(domain_pattern, lower):
        return "URL 🌐"

    elif re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', raw):
        return "Email 📧"

    return "Text 📝"

def process_qr_data(raw_data):
    if not raw_data:
        return "", "Unknown", False, False

    qr_type = detect_qr_type(raw_data)

    data = raw_data.strip()

    # Normalize URL
    if "URL" in qr_type and not data.startswith("http"):
        data = "http://" + data

    is_url = ("URL" in qr_type)

    # Only check malicious for URLs
    is_malicious = is_malicious_url(data) if is_url else False

    return data, qr_type, is_url, is_malicious

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