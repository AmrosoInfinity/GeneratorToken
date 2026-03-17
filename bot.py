import os
from telegram.ext import ApplicationBuilder
from generatorToken import register_token_handlers
from chatOpenAi import register_chat_handlers
from appopsPermission import register_appops_handlers
from commandBot import register_command_handlers

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("⚠️ TELEGRAM_BOT_TOKEN belum diset di environment.")

    app = ApplicationBuilder().token(token).build()

    register_token_handlers(app)
    register_chat_handlers(app)
    register_appops_handlers(app)
    register_command_handlers(app)

    print("🤖 Bot sudah berjalan... tekan Ctrl+C untuk berhenti.")
    app.run_polling()

if __name__ == "__main__":
    main()
