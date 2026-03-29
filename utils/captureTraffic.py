import requests

def get_x_token(file_path: str, x_token: str, batch_id: str, event_count: int, batch_timestamp: int) -> str | None:
    """
    Kirim payload binary dari file_path ke Grab /v2/track.
    Sertakan header x-token lama, ambil x-token baru dari response.
    """
    url = "https://mcd-gateway.grabtaxi.com/v2/track"
    headers = {
        "User-Agent": "Scribe/4.14.0/pax/Android",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/octet-stream",
        "Content-Encoding": "gzip",
        "x-token": x_token,  # token lama dikirim
        "x-batchId": batch_id,
        "X-EVENT-COUNT": str(event_count),
        "x-batch-timestamp": str(batch_timestamp),
    }

    try:
        with open(file_path, "rb") as f:
            data = f.read()

        resp = requests.post(url, headers=headers, data=data, timeout=10)
        resp.raise_for_status()
        return resp.headers.get("x-token")  # token baru dari response
    except Exception as e:
        print(f"Error capture x-token: {e}")
        return None
