import subprocess
import os
import json
import base64
import logging

logger = logging.getLogger(__name__)
CONFIG_FILE = os.path.join("config", "njwt_config.json")
PRIVATE_KEY_FILE = os.path.join("config", "ec256-private.pem")

def generate_jwt() -> str:
    if not os.path.exists(CONFIG_FILE):
        raise ValueError("⚠️ Owner belum input token NJWT via /inputToken")
    
    with open(CONFIG_FILE, "r") as f:
        cfg = json.load(f)

    # Header & Payload (Sinkron dengan Token Asli)
    header = {"alg": "ES256", "typ": "JWT"}
    payload = {
        "njwt": cfg["njwt"],
        "iat": cfg["iat"],
        "exp": cfg["exp"],
        "sub": cfg["sub"],
        "aud": "PASSENGER"
    }

    def b64url(data: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":")).encode()).decode().rstrip("=")

    signing_input = f"{b64url(header)}.{b64url(payload)}"

    try:
        proc = subprocess.run(
            ["openssl", "dgst", "-sha256", "-binary", "-sign", PRIVATE_KEY_FILE],
            input=signing_input.encode(), capture_output=True, check=True
        )
        signature = base64.urlsafe_b64encode(proc.stdout).decode().rstrip("=")
        return f"{signing_input}.{signature}"
    except Exception as e:
        logger.error(f"Signing Error: {e}")
        raise RuntimeError("Gagal generate signature ES256.")
