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
    url = "https://gist.githubusercontent.com/<username>/<gist_id>/raw/grab.txt"
    tokens = fetch_tokens(url)
    if tokens:
        token = random.choice(tokens)
        update.message.reply_text(f"=== Token Grab ===\n{token}")
    else:
        update.message.reply_text("Tidak ada token Grab ditemukan.")

def gojek(update, context):
    url = "https://gist.githubusercontent.com/<username>/<gist_id>/raw/gojek.txt"
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
