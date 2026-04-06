import os
import json
import random
import datetime
import uuid
import requests
import time # Penting untuk delay retry
from zoneinfo import ZoneInfo
from telegram import ChatPermissions
from support import string
from support.string import (
    CHECKTOKEN_VALID_MSG,
    CHECKTOKEN_INVALID_MSG,
    CHECKTOKEN_ERROR_MSG,
    CHECKTOKEN_INVALID_PREFIX_MSG,
    CHECKTOKEN_INVALID_LENGTH_MSG,
    CHECKTOKEN_SOURCE_AMROSOL_MSG,
    CHECKTOKEN_SOURCE_EXTERNAL_MSG,
    CHECKTOKEN_SOURCE_UNKNOWN_MSG,
)

# -----------------------------
# Konstanta & Direktori
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(BASE_DIR, "tmp")

PROFILE_URL = "https://p.grabtaxi.com/api/passenger/v3/profile"
USER_AGENT = "Grab/5.397.0 (Android 15; Build 139598668)"

# List User-Agent untuk fetch Gist agar tidak terdeteksi bot statis
GIST_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# -----------------------------
# Utility (Save/Load/Limit Tetap Sama)
# -----------------------------
def tmp_file_for_user(user_id: int) -> str:
    return os.path.join(TMP_DIR, f"user_{user_id}.json")

def save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage=None, last_token=None):
    os.makedirs(TMP_DIR, exist_ok=True)
    data = {
        "user_requests": user_requests,
        "user_blocked": {str(uid): until.isoformat() for uid, until in user_blocked.items()},
        "user_timezone": user_timezone,
        "token_usage": token_usage or {},
        "last_token": last_token or {}
    }
    file = tmp_file_for_user(user_id)
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_tmp(user_id):
    file = tmp_file_for_user(user_id)
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return (
            data.get("user_requests", {}),
            {int(uid): datetime.datetime.fromisoformat(until) for uid, until in data.get("user_blocked", {}).items()},
            data.get("user_timezone", {}),
            data.get("token_usage", {}),
            data.get("last_token", {})
        )
    return {}, {}, {}, {}, {}

# -----------------------------
# HIGH-AVAILABILITY TOKEN FETCHER
# -----------------------------
def fetch_tokens(raw_url: str):
    """Fetcher dengan Retry Logic, Cache Buster, dan Timeout Management."""
    session = requests.Session()
    retries = 3
    
    # Bersihkan URL dan tambahkan Cache Buster
    clean_url = raw_url.split('?')[0]
    
    for attempt in range(retries):
        try:
            # Gunakan identitas berbeda tiap percobaan
            headers = {
                "User-Agent": random.choice(GIST_AGENTS),
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
            
            # Tambahkan query unik agar GitHub tidak kasih data lama (Cached)
            bust_url = f"{clean_url}?t={uuid.uuid4().hex}"
            
            response = session.get(bust_url, headers=headers, timeout=12)
            
            if response.status_code == 200:
                content = response.text.strip()
                if content:
                    tokens = [line.strip() for line in content.splitlines() if line.strip()]
                    if tokens:
                        return tokens
            
            # Jika 404 atau 500, tunggu sebentar sebelum coba lagi
            time.sleep(1.5)
            
        except Exception as e:
            # Log error ke terminal/GitHub Action untuk diagnosa
            print(f"Fetch Attempt {attempt+1} Error: {e}")
            time.sleep(2)
            
    return []

# -----------------------------
# Limit Checker & Validator (Tetap Sama)
# -----------------------------
def check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ["group", "supergroup"]:
        if update.callback_query:
            update.callback_query.edit_message_text("Command ini hanya bisa digunakan di dalam grup.")
        return False

    if user_id in user_blocked:
        until = user_blocked[user_id]
        if datetime.datetime.now(ZoneInfo(tz_name)) < until:
            update.callback_query.edit_message_text(
                string.LIMIT_BLOCKED.format(mention=user.mention_html(), id=user.id, until=until),
                parse_mode="HTML"
            )
            return False
        else:
            del user_blocked[user_id]

    today = datetime.date.today().isoformat()
    key = f"{user_id}_{today}"
    count = user_requests.get(key, 0) + 1
    user_requests[key] = count

    if count > 3:
        user_blocked[user_id] = datetime.datetime.now(ZoneInfo(tz_name)) + datetime.timedelta(hours=12)
        save_tmp(user_id, user_requests, user_blocked, user_timezone)
        update.callback_query.edit_message_text(
            string.LIMIT_EXCEEDED.format(mention=user.mention_html(), id=user.id),
            parse_mode="HTML"
        )
        return False

    remaining = 3 - count
    now = datetime.datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M:%S")
    update.callback_query.edit_message_text(
        string.LIMIT_INFO.format(now=now, count=count, remaining=remaining),
        parse_mode="Markdown"
    )
    save_tmp(user_id, user_requests, user_blocked, user_timezone)
    return True

# ... (Fungsi validate_token & check_grab_token_status tetap sama) ...
def _is_token_format_valid(token: str) -> tuple[bool, str | None]:
    token = token.strip()
    if not token.startswith("ey"):
        return False, CHECKTOKEN_INVALID_PREFIX_MSG
    if len(token) < 1500:
        return False, CHECKTOKEN_INVALID_LENGTH_MSG
    return True, None

def _build_headers(token: str) -> dict:
    return {
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "gzip",
        "accept-language": "id-ID;q=1.0, en-US;q=0.9, en;q=0.8",
        "x-request-id": str(uuid.uuid4()),
        "x-mts-ssid": token,
    }

def validate_token(token: str) -> tuple[bool, str]:
    is_valid_format, error_msg = _is_token_format_valid(token)
    if not is_valid_format:
        return False, error_msg
    try:
        resp = requests.get(PROFILE_URL, headers=_build_headers(token), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            name = data.get("name", "")
            source_info = CHECKTOKEN_SOURCE_AMROSOL_MSG if name == "akun inject doang" else CHECKTOKEN_SOURCE_EXTERNAL_MSG.format(name=name)
            return True, f"{CHECKTOKEN_VALID_MSG.format(length=len(token), status=200)}\n{source_info}"
        return False, f"{CHECKTOKEN_INVALID_MSG.format(length=len(token), status=resp.status_code)}\n{CHECKTOKEN_SOURCE_UNKNOWN_MSG}"
    except Exception as e:
        return False, CHECKTOKEN_ERROR_MSG.format(error=e)

def check_grab_token_status(token: str | None) -> tuple[bool, str]:
    if not token or not isinstance(token, str):
        return False, "⚠️ Token kosong."
    try:
        resp = requests.get(PROFILE_URL, headers=_build_headers(token), timeout=10)
        if resp.status_code == 200:
            return True, f"✅ Token aktif ({resp.status_code})"
        return False, f"⚠️ Token mati ({resp.status_code})"
    except Exception as e:
        return False, f"⚠️ Error API: {e}"
