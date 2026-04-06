import subprocess
import datetime
import os
import json
import base64

CONFIG_FILE = "njwt_config.json"
PRIVATE_KEY_FILE = "ec-private.pem"  # file private key lokal

def load_njwt():
    """Ambil string njwt dari file config."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("njwt")
    return None

def base64url_encode(data: bytes) -> str:
    """Encode ke Base64URL tanpa padding."""
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def generate_jwt():
    if not os.path.exists(PRIVATE_KEY_FILE):
        raise FileNotFoundError("⚠️ Private key file tidak ditemukan. Pastikan ec-private.pem tersedia.")

    njwt_string = load_njwt() or "default_njwt"

    # Header dan payload
    header = {"alg": "ES256", "typ": "JWT"}
    payload = {
        "njwt": njwt_string,
        "iat": int(datetime.datetime.utcnow().timestamp()),
        "exp": int((datetime.datetime.utcnow() + datetime.timedelta(days=1)).timestamp()),
        "sub": "8162065b-2753-4e34-8151-b23b06eeb783",
        "aud": "PASSENGER"
    }

    # Encode header & payload ke Base64URL
    header_b64 = base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}"

    # Generate signature manual via openssl
    proc = subprocess.run(
        ["openssl", "dgst", "-sha256", "-binary", "-sign", PRIVATE_KEY_FILE],
        input=signing_input.encode(),
        capture_output=True,
        check=True
    )
    signature = proc.stdout

    # Base64URL encode signature
    signature_b64 = base64url_encode(signature)

    # Gabungkan jadi JWT
    token = f"{signing_input}.{signature_b64}"
    return token
