import subprocess
import datetime
import os
import json
import base64

# Lokasi file config dan key
CONFIG_FILE = os.path.join("config", "njwt_config.json")
PRIVATE_KEY_FILE = os.path.join("config", "ec256-private.pem")
PUBLIC_KEY_FILE = os.path.join("config", "ec256-public.pem")  # optional, untuk verifikasi eksternal

def load_njwt():
    """Ambil string njwt dari file config."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("njwt")
    return None

def base64url_encode(data: bytes) -> str:
    """Encode ke Base64URL tanpa padding '='."""
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def generate_jwt():
    """Generate JWT dengan ES256 signature menggunakan private key."""
    if not os.path.exists(PRIVATE_KEY_FILE):
        raise FileNotFoundError("⚠️ Private key file tidak ditemukan di config/. Pastikan ec256-private.pem tersedia.")

    njwt_string = load_njwt() or "default_njwt"

    # Header & payload
    header = {"alg": "ES256", "typ": "JWT"}
    payload = {
        "njwt": njwt_string,
        "iat": int(datetime.datetime.utcnow().timestamp()),
        "exp": int((datetime.datetime.utcnow() + datetime.timedelta(days=1)).timestamp()),
        "sub": "8162065b-2753-4e34-8151-b23b06eeb783",
        "aud": "PASSENGER"
    }

    # Encode header & payload
    header_b64 = base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}"

    # Sign dengan private key (ES256)
    proc = subprocess.run(
        ["openssl", "dgst", "-sha256", "-binary", "-sign", PRIVATE_KEY_FILE],
        input=signing_input.encode(),
        capture_output=True,
        check=True
    )
    signature = proc.stdout
    signature_b64 = base64url_encode(signature)

    # Gabungkan jadi JWT
    return f"{signing_input}.{signature_b64}"
