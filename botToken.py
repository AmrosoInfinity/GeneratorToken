import os
import requests
import random
from telegram.ext import Updater, CommandHandler

def fetch_tokens(raw_url: str):
    try:
        # Tambahkan cache-buster agar tidak kena cache CDN
        url = f"{raw_url}?nocache={random.randint(1, 100000)}"
        r = requests.get(url)
        print(f"[DEBUG] Fetch {url} -> status {r.status_code}")
        if r.status_code == 200:
            # Tampilkan sebagian isi untuk verifikasi di log
            print("[DEBUG] Content sample:", r.text[:200])
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
        update.message.reply_text(f"=== Token Grab ===\n```{token}```",
                                 parse_mode="Markdown"
                                 )
    else:
        update.message.reply_text("Tidak ada token Grab ditemukan.")

def gojek(update, context):
    url = "https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek"
    tokens = fetch_tokens(url)
    if tokens:
        token = random.choice(tokens)
        update.message.reply_text(f"=== Token Gojek ===\n{token}")
    else:
        update.message.reply_text("Tidak ada token Gojek ditemukan.")

# === Handler Chat OpenAI ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # simpan di GitHub Secrets

def ask(update, context):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Gunakan format: /ask <pertanyaan>")
        return

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    json_data = {
        "model": "gpt-4o-mini",   # contoh model ringan
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 200
    }

    try:
        r = requests.post("https://api.openai.com/v1/chat/completions",
                          headers=headers, json=json_data)
        print("[DEBUG] OpenAI response:", r.text)

        if r.status_code == 200:
            answer = r.json()["choices"][0]["message"]["content"]
            update.message.reply_text(answer)
        elif r.status_code == 429:
            update.message.reply_text("AmrosolBot saat ini sedang limit atau quota habis. Coba lagi nanti ya.")
        else:
            update.message.reply_text(f"AmrosolBot error: {r.status_code}")
    except Exception as e:
        update.message.reply_text(f"Terjadi error: {e}")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")  # ambil dari GitHub Secrets
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("grab", grab))
    dp.add_handler(CommandHandler("gojek", gojek))
    dp.add_handler(CommandHandler("ask", ask))  # handler OpenAI

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
