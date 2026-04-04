import os
import json
import random
import datetime
import uuid
import requests
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

# -----------------------------
# Utility untuk file tmp per user
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
        user_requests = data.get("user_requests", {})
        user_blocked = {
            int(uid): datetime.datetime.fromisoformat(until)
            for uid, until in data.get("user_blocked", {}).items()
        }
        user_timezone = data.get("user_timezone", {})
        token_usage = data.get("token_usage", {})
        last_token = data.get("last_token", {})
        return user_requests, user_blocked, user_timezone, token_usage, last_token
    else:
        user_requests, user_blocked, user_timezone, token_usage, last_token = {}, {}, {}, {}, {}
        save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)
        return user_requests, user_blocked, user_timezone, token_usage, last_token

# -----------------------------
# Limit checker untuk grup
# -----------------------------
def check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ["group", "supergroup"]:
        update.callback_query.edit_message_text("Command ini hanya bisa digunakan di dalam grup.")
        return False

    # cek blokir
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

    # hitung request harian
    today = datetime.date.today().isoformat()
    key = f"{user_id}_{today}"
    count = user_requests.get(key, 0) + 1
    user_requests[key] = count

    bot_member = context.bot.get_chat_member(chat.id, context.bot.id)
    is_admin = bot_member.status in ["administrator", "creator"]

    if count > 3:
        if is_admin:
            until_date = datetime.datetime.now(ZoneInfo(tz_name)) + datetime.timedelta(minutes=30)
            try:
                context.bot.restrict_chat_member(
                    chat_id=chat.id,
                    user_id=user.id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=until_date
                )
                update.callback_query.edit_message_text(
                    string.LIMIT_EXCEEDED.format(mention=user.mention_html(), id=user.id),
                    parse_mode="HTML"
                )
            except Exception:
                update.callback_query.edit_message_text(
                    string.LIMIT_MUTE_FAILED.format(mention=user.mention_html(), id=user.id),
                    parse_mode="HTML"
                )

        user_blocked[user_id] = datetime.datetime.now(ZoneInfo(tz_name)) + datetime.timedelta(hours=12)
        save_tmp(user_id, user_requests, user_blocked, user_timezone)
        return False

    remaining = 3 - count
    now = datetime.datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M:%S")
    update.callback_query.edit_message_text(
        string.LIMIT_INFO.format(now=now, count=count, remaining=remaining),
        parse_mode="Markdown"
    )
    save_tmp(user_id, user_requests, user_blocked, user_timezone)
    return True

# -----------------------------
# Token fetcher
# -----------------------------
def fetch_tokens(raw_url: str):
    try:
        url = f"{raw_url}?nocache={random.randint(1, 100000)}"
        r = requests.get(url)
        if r.status_code == 200:
            return r.text.strip().splitlines()
        return []
    except Exception:
        return []

# -----------------------------
# Token validator (profile-based)
# -----------------------------
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
    """Validasi token dengan memanggil API profile Grab."""
    is_valid_format, error_msg = _is_token_format_valid(token)
    if not is_valid_format:
        return False, error_msg

    try:
        resp = requests.get(PROFILE_URL, headers=_build_headers(token), timeout=10)
        status_code = resp.status_code
        if status_code == 200:
            data = resp.json()
            name = data.get("name", "")

            # Tentukan sumber berdasarkan nilai name
            if name == "akun inject doang":
                source_info = CHECKTOKEN_SOURCE_AMROSOL_MSG
            else:
                source_info = CHECKTOKEN_SOURCE_EXTERNAL_MSG.format(name=name)

            return True, f"{CHECKTOKEN_VALID_MSG.format(length=len(token), status=status_code)}\n{source_info}"
        else:
            # Jika invalid, sumber dianggap unknown
            source_info = CHECKTOKEN_SOURCE_UNKNOWN_MSG
            return False, f"{CHECKTOKEN_INVALID_MSG.format(length=len(token), status=status_code)}\n{source_info}"
    except Exception as e:
        return False, CHECKTOKEN_ERROR_MSG.format(error=e)
