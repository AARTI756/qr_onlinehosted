import qrcode
import os
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from modules.encryption import encrypt_data

def generate_secure_qr(user_id, raw_data, base_url, expiry_minutes=5):    
    qr_id = str(uuid.uuid4())
    created_at = datetime.now()
    expiry = created_at + timedelta(minutes=expiry_minutes)

    encrypted_payload = encrypt_data(raw_data)

    payload = {
        "qr_id": qr_id,
        "owner_id": user_id,
        "created_at": created_at.isoformat(),
        "expiry": expiry.isoformat(),
        "data": encrypted_payload
    }

    # Generate integrity hash
    hash_value = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()

    payload["hash"] = hash_value

    qr_json = json.dumps(payload)

    # ✅ Create folder safely
    folder_path = os.path.join("static", "qr_codes")
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"{qr_id}.png")

    qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=10,
    border=4,
        )

    verification_url = f"{base_url}verify/{qr_id}"
    qr.add_data(verification_url)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)

    return qr_id, file_path, encrypted_payload, hash_value, expiry