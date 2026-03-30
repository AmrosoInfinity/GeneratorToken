import requests
import time
import uuid
import os

def run_replayer():
    url = "https://mcd-gateway.grabtaxi.com/v2/track"
    
    # 1. Load Template Biner (Pastikan file ini ada di repo)
    binary_path = "templates/payload_template.bin"
    if not os.path.exists(binary_path):
        print(f"[!] Error: File {binary_path} tidak ditemukan!")
        return

    with open(binary_path, "rb") as f:
        raw_body = f.read()

    # 2. Ambil Token dari GitHub Secrets (Agar Aman)
    # Masukkan x-token Abang di Settings Repo > Secrets > Actions
    x_token = os.getenv("GRAB_TOKEN")
    
    if not x_token:
        print("[!] Error: GRAB_TOKEN tidak diset di GitHub Secrets!")
        return

    # 3. Generate Header Dinamis
    current_time_ms = str(int(time.time() * 1000))
    headers = {
        "x-token": x_token,
        "User-Agent": "Scribe/4.14.0/pax/Android",
        "x-batchId": str(uuid.uuid4()),
        "X-EVENT-COUNT": "14", # Sesuaikan dengan event di biner Abang
        "x-batch-timestamp": current_time_ms,
        "Content-Type": "application/octet-stream",
        "Content-Encoding": "gzip", # Biner Grab biasanya di-gzip
        "Host": "mcd-gateway.grabtaxi.com",
        "Connection": "Keep-Alive"
    }

    print(f"[*] Mengirim Scribe Traffic pada {current_time_ms}...")

    try:
        # Kirim payload biner asli
        response = requests.post(url, data=raw_body, headers=headers, timeout=15)
        
        print(f"[+] Status Code: {response.status_code}")
        if response.status_code == 200:
            print("[SUCCESS] Traffic berhasil diterima server Grab!")
        else:
            print(f"[FAILED] Respon Server: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Terjadi kendala koneksi: {e}")

if __name__ == "__main__":
    run_replayer()
