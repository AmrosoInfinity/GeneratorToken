import os, json, datetime, random, requests
from zoneinfo import ZoneInfo
from telegram import ChatPermissions

TMP_DIR = "tmp"
user_requests = {}
user_blocked = {}
user_timezone = {}

def tmp_file_for_today():
    today = datetime.date.today().isoformat()
    return os.path.join(TMP_DIR, f"requests-{today}.json")

def save_tmp():
    os.makedirs(TMP_DIR, exist_ok=True)
    data = {
        "user_requests": user_requests,
        "user_blocked": {uid: until.isoformat() for uid, until in user_blocked.items()},
        "user_timezone": user_timezone
    }
    with open(tmp_file_for_today(), "w", encoding="utf-8") as f:
        json.dump(data, f)

def load_tmp():
    global user_requests, user_blocked, user_timezone
    file = tmp_file_for_today()
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            user_requests = data.get("user_requests", {})
            user_blocked = {int(uid): datetime.datetime.fromisoformat(until)
                            for uid, until in data.get("user_blocked", {}).items()}
            user_timezone = data.get("user_timezone", {})
    else:
        user_requests, user_blocked, user_timezone = {}, {}, {}

def check_limit(update, context, tz_name):
    load_tmp()
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ["group", "supergroup"]:
        update.callback_query.edit_message_text("Command ini hanya bisa digunakan di dalam grup.")
        return False

    if user.id in user_blocked:
        until = user_blocked[user.id]
        if datetime.datetime.now(ZoneInfo(tz_name)) < until:
            update.callback_query.edit_message_text(
                f"⚠️ User {user.mention_html()} (ID: {user.id}) sedang diblokir hingga {until}.",
                parse_mode="HTML"
            )
            return False
        else:
            del user_blocked[user.id]

    today = datetime.date.today().isoformat()
    key = (user.id, today)
    count = user_requests.get(str(key), 0) + 1
    user_requests[str(key)] = count

    bot_member = context.bot.get_chat_member(chat.id, context.bot.id)
    is_admin = bot_member.status in ["administrator", "creator"]

    if count > 3:
        if is_admin:
            until_date = datetime.datetime.now(ZoneInfo(tz_name)) + datetime.timedelta(hours=2)
            context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            update.callback_query.edit_message_text(
                f"⚠️ User {user.mention_html()} (ID: {user.id}) melebihi batas 3 request per hari dan telah di-mute selama 2 jam.",
                parse_mode="HTML"
            )
        user_blocked[user.id] = datetime.datetime.now(ZoneInfo(tz_name)) + datetime.timedelta(hours=24)
        save_tmp()
        return False

    remaining = 3 - count
    now = datetime.datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M:%S")
    update.callback_query.edit_message_text(
        f"🕒 Waktu request: {now}\n"
        f"✅ Request ke-{count} hari ini.\n"
        f"🎯 Sisa kesempatan: {remaining if remaining >= 0 else 0}",
        parse_mode="Markdown"
    )
    save_tmp()
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
