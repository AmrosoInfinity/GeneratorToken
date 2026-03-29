import requests

def get_x_token(batch_id: str, event_count: int, batch_timestamp: int, prev_token: str) -> str | None:
    """
    Real traffic capture ke Grab /v2/track.
    Kirim POST dengan header sesuai hasil capture, ambil x-token dari response.
    """
    url = "https://mcd-gateway.grabtaxi.com/v2/track"
    headers = {
        "User-Agent": "Scribe/4.14.0/pax/Android",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/octet-stream",
        "Content-Encoding": "gzip",
        "x-batchId": batch_id,
        "X-EVENT-COUNT": str(event_count),
        "x-batch-timestamp": str(batch_timestamp),
        "x-token": prev_token,   # token lama dikirim, server balas token baru
    }

    try:
        # body bisa kosong atau minimal, karena kita hanya butuh header balasan
        resp = requests.post(url, headers=headers, data=b"", timeout=10)
        resp.raise_for_status()
        return resp.headers.get("x-token")
    except Exception as e:
        print(f"Error capture x-token: {e}")
        return None
