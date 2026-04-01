import json
import os
import time

DATA_DIR = "data"
SUSPECT_FILE = os.path.join(DATA_DIR, "suspect_users.json")

os.makedirs(DATA_DIR, exist_ok=True)

suspect_users = {}

def load_suspects():
    if os.path.exists(SUSPECT_FILE):
        with open(SUSPECT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_suspects():
    with open(SUSPECT_FILE, "w") as f:
        json.dump(suspect_users, f)

# load saat modul diimport
suspect_users.update(load_suspects())

def record_token_request(user_id: int):
    now = time.time()
    history = suspect_users.get(str(user_id), [])
    history = [t for t in history if now - t < 60]  # hanya simpan 1 menit terakhir
    history.append(now)
    suspect_users[str(user_id)] = history
    save_suspects()

def is_suspect(user_id: int, threshold=5) -> bool:
    history = suspect_users.get(str(user_id), [])
    return len(history) >= threshold

def get_all_suspects(threshold=5):
    return [int(uid) for uid, hist in suspect_users.items() if len(hist) >= threshold]
