import subprocess
import os
import json
import base64
import logging

logger = logging.getLogger(__name__)
CONFIG_FILE = os.path.join("config", "njwt_config.json")
PRIVATE_KEY_FILE = os.path.join("config", "ec256-private.pem")

def generate_jwt() -> str:
    """Generate JWT ES256 dengan metadata identik dari config."""
    
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("⚠️ Owner belum input token NJWT!")
    
    # 1. Load Data Config
    with open(CONFIG_FILE, "r") as f:
        cfg = json.load(f)

    # 2. Setup Payload (Full Sinkron)
    header = {"alg": "ES256", "typ": "JWT"}
    payload = {
        "njwt": cfg["njwt"],
        "iat": cfg["iat"],
        "exp": cfg["exp"],
        "sub": cfg["sub"], # <--- Gunakan SUB dari token asli
        "aud": "PASSENGER"
    }

    # 3. Base64URL Encoding
    def b64url(data: dict) -> str:
        json_str = json.dumps(data, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(json_str).decode().rstrip("=")

    header_b64 = b64url(header)
    payload_b64 = b64url(payload)
    signing_input = f"{header_b64}.{payload_b64}"

    # 4. OpenSSL ES256 Signing
    try:
        proc = subprocess.run(
            ["openssl", "dgst", "-sha256", "-binary", "-sign", PRIVATE_KEY_FILE],
            input=signing_input.encode(),
            capture_output=True,
            check=True
        )
        signature_b64 = base64.urlsafe_b64encode(proc.stdout).decode().rstrip("=")
        
        logger.info("✅ JWT ES256 Generated with Full Metadata Sync.")
        return f"{signing_input}.{signature_b64}"

    except Exception as e:
        logger.error(f"Signing Error: {e}")
        raise RuntimeError("Gagal menandatangani token dengan Private Key.")
