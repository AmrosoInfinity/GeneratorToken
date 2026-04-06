import subprocess
import os
import json
import base64
import logging

logger = logging.getLogger(__name__)
CONFIG_FILE = os.path.join("config", "njwt_config.json")
PRIVATE_KEY_FILE = os.path.join("config", "ec256-private.pem")

def b64url(data: dict) -> str:
    """Helper untuk encode dict ke Base64URL string."""
    json_str = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(json_str).decode().rstrip("=")

def generate_jwt() -> str:
    # 1. Cek keberadaan file config
    if not os.path.exists(CONFIG_FILE):
        raise ValueError("⚠️ Konfigurasi token tidak ditemukan. Silakan /inputToken kembali.")
    
    # 2. Cek keberadaan Private Key (Sangat Penting!)
    if not os.path.exists(PRIVATE_KEY_FILE):
        raise FileNotFoundError("❌ File private key (ec256-private.pem) hilang di folder config.")

    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
            
        # 3. Ambil dan validasi data (pastikan iat/exp adalah integer)
        # Kami menggunakan .get() agar tidak crash jika key hilang
        njwt_val = cfg.get("njwt")
        iat_val = cfg.get("iat")
        exp_val = cfg.get("exp")
        sub_val = cfg.get("sub")

        if not all([njwt_val, iat_val, exp_val, sub_val]):
            raise KeyError(f"Data di config tidak lengkap. (iat: {iat_val}, exp: {exp_val})")

        # 4. Konstruksi Header & Payload
        header = {"alg": "ES256", "typ": "JWT"}
        payload = {
            "njwt": str(njwt_val),
            "iat": int(iat_val), # Paksa ke integer
            "exp": int(exp_val), # Paksa ke integer
            "sub": str(sub_val),
            "aud": "PASSENGER"
        }

        # 5. Siapkan signing input
        signing_input = f"{b64url(header)}.{b64url(payload)}"

        # 6. Digital Signing menggunakan OpenSSL
        proc = subprocess.run(
            ["openssl", "dgst", "-sha256", "-binary", "-sign", PRIVATE_KEY_FILE],
            input=signing_input.encode(),
            capture_output=True,
            check=True
        )
        
        signature = base64.urlsafe_b64encode(proc.stdout).decode().rstrip("=")
        
        logger.info("✅ JWT ES256 successfully generated with synced iat/exp.")
        return f"{signing_input}.{signature}"

    except subprocess.CalledProcessError as e:
        logger.error(f"OpenSSL Error: {e.stderr.decode()}")
        raise RuntimeError("Gagal melakukan digital signing. Pastikan Private Key valid.")
    except Exception as e:
        logger.error(f"Generate JWT Error: {e}")
        raise RuntimeError(f"Gagal memproses token: {str(e)}")
