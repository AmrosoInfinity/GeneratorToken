import json
import os

DATA_DIR = "data"
BLOCK_FILE = os.path.join(DATA_DIR, "blocked_users.json")

# pastikan folder data ada
os.makedirs(DATA_DIR, exist_ok=True)

def load_blocked_users():
    if os.path.exists(BLOCK_FILE):
        with open(BLOCK_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_blocked_users(blocked_users):
    with open(BLOCK_FILE, "w") as f:
        json.dump(list(blocked_users), f)

blocked_users = load_blocked_users()

def block_user(user_id: int):
    blocked_users.add(user_id)
    save_blocked_users(blocked_users)

def unblock_user(user_id: int):
    blocked_users.discard(user_id)
    save_blocked_users(blocked_users)

def is_blocked(user_id: int) -> bool:
    return user_id in blocked_users
