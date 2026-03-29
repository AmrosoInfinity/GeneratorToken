import requests

def get_x_token(headers=None):
    """
    Kirim request ke endpoint Grab /v2/track dan ambil header x-token dari response.
    """
    url = "https://mcd-gateway.grabtaxi.com/v2/track"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        # Ambil header x-token dari response
        return resp.headers.get("x-token")
    except Exception as e:
        print(f"Error capture x-token: {e}")
        return None
