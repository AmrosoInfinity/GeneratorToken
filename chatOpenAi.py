import os
import requests
from telegram.ext import CommandHandler

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

def call_openai(query: str, max_tokens: int = 200, temperature: float = 0.7) -> str:
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": query}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        r = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()

        if "choices" in data and data["choices"]:
            choice = data["choices"][0]
            # FIX: cek apakah ada "message" atau "delta"
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"].strip()
            elif "delta" in choice and "content" in choice["delta"]:
                return choice["delta"]["content"].strip()
        return "Model tidak mengembalikan jawaban."
    except requests.exceptions.HTTPError as e:
        if r.status_code == 429:
            return "AmrosolBot sedang limit/quota habis. Coba lagi nanti."
        return f"Error HTTP {r.status_code}: {r.text}"
    except Exception as e:
        return f"Terjadi error: {e}"

def ask(update, context):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("Gunakan format: /ask <pertanyaan>")
        return

    answer = call_openai(query)
    update.message.reply_text(answer)

def register_chat_handlers(dp):
    dp.add_handler(CommandHandler("ask", ask))
