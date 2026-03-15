import requests, random, datetime
from telegram.ext import CommandHandler
from telegram import ChatPermissions

# Tracking request per user per hari
user_requests = {}
user_blocked = {}  # simpan user yang diblokir selama 24 jam

def log_request(user_id, username, count, remaining):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open("request.log", "a", encoding="utf-8") as f:
            f.write(f"[{now}] User {username} (ID:{user_id}) request ke-{count}, sisa {remaining}\n")
    except Exception as e:
        print("[DEBUG] Gagal menulis log:", e)

def check_limit(update, context):
    chat = update.effective_chat
    user = update.effective_user

    # Validasi hanya di grup
    if chat.type not in ["group", "supergroup"]:
        update.message.reply_text("Command ini hanya bisa digunakan di dalam grup.")
        return False

    # Cek apakah user sedang diblokir 24 jam
    if user.id in user_blocked:
        until = user_blocked[user.id]
        if datetime.datetime.now() < until:
            update.message.reply_text(
                f"⚠️ User {user.mention_html()} (ID: {user.id}) sedang diblokir hingga {until}.",
                parse_mode="HTML"
            )
            return False
        else:
            # unblock otomatis setelah 24 jam
            del user_blocked[user.id]

    today = datetime.date.today().isoformat()
    key = (user.id, today)

    count = user_requests.get(key, 0) + 1
    user_requests[key] = count

    # Cek status bot
    bot_member = context.bot.get_chat_member(chat.id, context.bot.id)
    is_admin = bot_member.status in ["administrator", "creator"]

    if count > 3:
        if is_admin:
            try:
                # mute user selama 2 jam
                until_date = datetime.datetime.now() + datetime.timedelta(hours=2)
                context.bot.restrict_chat_member(
                    chat_id=chat.id,
                    user_id=user.id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=until_date
                )
                update.message.reply_text(
                    f"⚠️ User {user.mention_html()} (ID: {user.id}) melebihi batas 3 request per hari dan telah di-mute selama 2 jam.",
                    parse_mode="HTML"
                )
            except Exception as e:
                update.message.reply_text(f"Gagal mute user: {e}")

        # blokir request token selama 24 jam (baik admin maupun bukan admin)
        user_blocked[user.id] = datetime.datetime.now() + datetime.timedelta(hours=24)
        return False

    # tampilkan log request ke user
    remaining = 3 - count
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update.message.reply_text(
        f"🕒 Waktu request: {now}\n"
        f"✅ Request ke-{count} hari ini.\n"
        f"🎯 Sisa kesempatan: {remaining if remaining >= 0 else 0}",
        parse_mode="Markdown"
    )

    # simpan log ke file
    log_request(user.id, user.username or user.full_name, count, remaining if remaining >= 0 else 0)

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

def grab(update, context):
    if not check_limit(update, context):
        return
    url = "https://gist.githubusercontent.com/AmrosoInfinity/5b19fdb53aa1bfcfa4fc3843165b9471/raw/Grab"
    tokens = fetch_tokens(url)
    if tokens:
        token = random.choice(tokens)
        update.message.reply_text(f"=== Token Grab ===\n```{token}```", parse_mode="Markdown")
    else:
        update.message.reply_text("Tidak ada token Grab ditemukan.")

def gojek(update, context):
    if not check_limit(update, context):
        return
    url = "https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek"
    tokens = fetch_tokens(url)
    if tokens:
        token = random.choice(tokens)
        update.message.reply_text(f"=== Token Gojek ===\n```{token}```", parse_mode="Markdown")
    else:
        update.message.reply_text("Tidak ada token Gojek ditemukan.")

def register_token_handlers(dp):
    dp.add_handler(CommandHandler("grab", grab))
    dp.add_handler(CommandHandler("gojek", gojek))
