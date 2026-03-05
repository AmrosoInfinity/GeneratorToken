import requests, random
from telegram.ext import CommandHandler

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
    url = "https://gist.githubusercontent.com/AmrosoInfinity/5b19fdb53aa1bfcfa4fc3843165b9471/raw/Grab"
    tokens = fetch_tokens(url)
    if tokens:
        token = random.choice(tokens)
        update.message.reply_text(f"=== Token Grab ===\n```{token}```", parse_mode="Markdown")
    else:
        update.message.reply_text("Tidak ada token Grab ditemukan.")

def gojek(update, context):
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
