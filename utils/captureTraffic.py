import requests
import os

def get_x_token(prev_token: str, batch_id: str, event_count: int, batch_timestamp: int) -> str | None:
    """
    Kirim payload binary dari repoRoot/playload/disini ke Grab /v2/track.
    Ambil header x-token baru dari response.
    """
    # Path relatif ke repo root
    file_path = os.path.join(os.getcwd(), "playload", "disini", "grab_payload.bin")

    url = "https://mcd-gateway.grabtaxi.com/v2/track"
    headers = {
        "User-Agent": "Scribe/4.14.0/pax/Android",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/octet-stream",
        "Content-Encoding": "gzip",
        "x-token": prev_token,
        "x-batchId": batch_id,
        "X-EVENT-COUNT": str(event_count),
        "x-batch-timestamp": str(batch_timestamp),
    }

    try:
        with open(file_path, "rb") as f:
            data = f.read()

        resp = requests.post(url, headers=headers, data=data, timeout=10)
        resp.raise_for_status()
        return resp.headers.get("x-token")
    except Exception as e:
        print(f"Error capture x-token: {e}")
        return None
