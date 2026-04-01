import os
import json
import time

DATA_DIR = "data"
SUSPECT_FILE = os.path.join(DATA_DIR, "suspect_users.json")
os.makedirs(DATA_DIR, exist_ok=True)

# struktur: {user_id: {"history":[timestamps], "warnings":int}}
user_activity = {}

def load_suspects():
    if os.path.exists(SUSPECT_FILE):
        with open(SUSPECT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_suspects(data):
    with open(SUSPECT_FILE, "w") as f:
        json.dump(data, f)

suspect_log = load_suspects()

def record_check(user_id: int, valid: bool):
    """Catat aktivitas checktoken. Hanya dihitung kalau valid token dari bot."""
    now = time.time()
    if user_id not in user_activity:
        user_activity[user_id] = {"history": [], "warnings": 0}
    if valid:
        # purge history lebih dari 12 jam
        history = [t for t in user_activity[user_id]["history"] if now - t < 43200]
        history.append(now)
        user_activity[user_id]["history"] = history

def should_block(user_id: int, owner_id: int):
    """Cek apakah user harus diblokir sementara"""
    if user_id == owner_id:
        return False
    history = user_activity.get(user_id, {}).get("history", [])
    return len(history) >= 3

def warn_or_suspect(user_id: int, owner_id: int, bot):
    """Naikkan level peringatan atau tandai suspect"""
    if user_id == owner_id:
        return None

    now = time.time()
    entry = user_activity.setdefault(user_id, {"history": [], "warnings": 0})
    if entry["warnings"] < 2:
        entry["warnings"] += 1
        return "warn"
    else:
        suspect_log[str(user_id)] = {
            "last_activity": now,
            "reason": "Memaksa checktoken berkali-kali setelah peringatan"
        }
        save_suspects(suspect_log)
        try:
            bot.send_message(
                chat_id=owner_id,
                text=f"⚠️ User mencurigakan: {user_id}\nAktivitas: {suspect_log[str(user_id)]['reason']}"
            )
        except Exception:
            pass
        return "suspect"
