import subprocess
import datetime
import os
import json
import base64

# Simpan config di root/config/
CONFIG_FILE = os.path.join("config", "njwt_config.json")
PRIVATE_KEY_FILE = os.path.join("config", "ec-private.pem")  # private key juga di folder config

def load_njwt():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("njwt")
    return None

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def generate_jwt():
    if not os.path.exists(PRIVATE_KEY_FILE):
        raise FileNotFoundError("⚠️ Private key file tidak ditemukan di config/. Pastikan ec-private.pem tersedia.")

    njwt_string = load_njwt() or "default_njwt"

    header = {"alg": "ES256", "typ": "JWT"}
    payload = {
        "njwt": njwt_string,
        "iat": int(datetime.datetime.utcnow().timestamp()),
        "exp": int((datetime.datetime.utcnow() + datetime.timedelta(days=1)).timestamp()),
        "sub": "8162065b-2753-4e34-8151-b23b06eeb783",
        "aud": "PASSENGER"
    }

    header_b64 = base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}"

    proc = subprocess.run(
        ["openssl", "dgst", "-sha256", "-binary", "-sign", PRIVATE_KEY_FILE],
        input=signing_input.encode(),
        capture_output=True,
        check=True
    )
    signature = proc.stdout
    signature_b64 = base64url_encode(signature)

    return f"{signing_input}.{signature_b64}"
