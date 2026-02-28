import json
import hashlib
from datetime import datetime
from modules.encryption import decrypt_data

def validate_qr(qr_json_string):

    try:
        payload = json.loads(qr_json_string)

        received_hash = payload.pop("hash")

        recalculated_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()

        if received_hash != recalculated_hash:
            return "TAMPERED", None

        expiry = datetime.fromisoformat(payload["expiry"])

        if datetime.now() > expiry:
            return "EXPIRED", None

        decrypted_data = decrypt_data(payload["data"])

        return "VALID", decrypted_data

    except Exception as e:
        return "INVALID", None