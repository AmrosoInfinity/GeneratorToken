import os, json, datetime, random, requests
from zoneinfo import ZoneInfo
from telegram import ChatPermissions
from support import string

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp")

def tmp_file_for_user(user_id: int):
    today = datetime.date.today().isoformat()
    return os.path.join(TMP_DIR, f"user_{user_id}_{today}.json")

def save_tmp(user_id, user_requests, user_blocked, user_timezone):
    os.makedirs(TMP_DIR, exist_ok=True)
    data = {
        "user_requests": user_requests,
        "user_blocked": {uid: until.isoformat() for uid, until in user_blocked.items()},
        "user_timezone": user_timezone
    }
    file = tmp_file_for_user(user_id)
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[DEBUG] Menyimpan data user {user_id} ke {file}")

def load_tmp(user_id):
    file = tmp_file_for_user(user_id)
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            user_requests = data.get("user_requests", {})
            user_blocked = {int(uid): datetime.datetime.fromisoformat(until)
                            for uid, until in data.get("user_blocked", {}).items()}
            user_timezone = data.get("user_timezone", {})
        return user_requests, user_blocked, user_timezone
    else:
        user_requests, user_blocked, user_timezone = {}, {}, {}
        save_tmp(user_id, user_requests, user_blocked, user_timezone)
        return user_requests, user_blocked, user_timezone

def check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
    chat = update.effective_chat
    user = update.effective_user

    # hanya untuk grup
    if chat.type not in ["group", "supergroup"]:
        update.callback_query.edit_message_text("Command ini hanya bisa digunakan di dalam grup.")
        return False

    # cek apakah user sudah diblokir
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

    # jika lebih dari 3 kali
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
            except Exception as e:
                print("[DEBUG] Gagal mute:", e)
                update.callback_query.edit_message_text(
                    string.LIMIT_MUTE_FAILED.format(mention=user.mention_html(), id=user.id),
                    parse_mode="HTML"
                )

        # tetap blokir user secara internal
        user_blocked[user_id] = datetime.datetime.now(ZoneInfo(tz_name)) + datetime.timedelta(hours=12)
        save_tmp(user_id, user_requests, user_blocked, user_timezone)
        return False

    # kalau masih <= 3 kali
    remaining = 3 - count
    now = datetime.datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M:%S")
    update.callback_query.edit_message_text(
        string.LIMIT_INFO.format(now=now, count=count, remaining=remaining),
        parse_mode="Markdown"
    )
    save_tmp(user_id, user_requests, user_blocked, user_timezone)
    return True

def fetch_tokens(raw_url: str):
    try:
        url = f"{raw_url}?nocache={random.randint(1, 100000)}"
        r = requests.get(url)
        if r.status_code == 200:
            return r.text.strip().splitlines()
        return []
    except Exception as e:
        print("[DEBUG] Error:", e)
        return []
