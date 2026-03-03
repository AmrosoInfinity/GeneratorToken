import os
import requests, random
from telegram.ext import Updater, CommandHandler

def fetch_tokens(raw_url):
    try:
        r = requests.get(raw_url.strip())
        if r.status_code == 200:
            return r.text.strip().splitlines()
        else:
            return []
    except Exception as e:
        return []

def grab(update, context):
    url = "https://gist.githubusercontent.com/AmrosoInfinity/5b19fdb53aa1bfcfa4fc3843165b9471/raw/3bc47a673d15732de67b05e790fb2da3e3d58e29/Grab"
    tokens = fetch_tokens(url)
    if tokens:
        token = random.choice(tokens)
        update.message.reply_text(f"=== Token Grab ===\n{token}")
    else:
        update.message.reply_text("Tidak ada token Grab ditemukan.")

def gojek(update, context):
    url = "https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/81e594b82d518de43c200b1caf041e86783c01fa/Gojek"
    tokens = fetch_tokens(url)
    if tokens:
        token = random.choice(tokens)
        update.message.reply_text(f"=== Token Gojek ===\n{token}")
    else:
        update.message.reply_text("Tidak ada token Gojek ditemukan.")

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # ambil dari GitHub Secrets
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("grab", grab))
    dp.add_handler(CommandHandler("gojek", gojek))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
