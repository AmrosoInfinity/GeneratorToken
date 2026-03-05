import os, requests
from telegram.ext import CommandHandler

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def ask(update, context):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Gunakan format: /ask <pertanyaan>")
        return

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    json_data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 200
    }

    try:
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data)
        if r.status_code == 200:
            answer = r.json()["choices"][0]["message"]["content"]
            update.message.reply_text(answer)
        elif r.status_code == 429:
            update.message.reply_text("AmrosolBot sedang limit/quota habis. Coba lagi nanti.")
        else:
            update.message.reply_text(f"Error: {r.status_code}")
    except Exception as e:
        update.message.reply_text(f"Terjadi error: {e}")

def register_chat_handlers(dp):
    dp.add_handler(CommandHandler("ask", ask))
