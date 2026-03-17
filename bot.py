import os
from telegram.ext import ApplicationBuilder
from generatorToken import register_token_handlers
from chatOpenAi import register_chat_handlers
from appopsPermission import register_appops_handlers
from commandBot import register_command_handlers

def main():
    # Ambil token dari environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("⚠️ TELEGRAM_BOT_TOKEN belum diset di environment.")

    # Inisialisasi Application (pengganti Updater)
    app = ApplicationBuilder().token(token).build()

    # Register semua handler dari modul terpisah
    register_token_handlers(app)       # tombol /token (Grab/Gojek + timezone)
    register_chat_handlers(app)        # modul chatOpenAi
    register_appops_handlers(app)      # modul appopsPermission
    register_command_handlers(app)     # modul commandBot

    # Jalankan bot
    print("🤖 Bot sudah berjalan... tekan Ctrl+C untuk berhenti.")
    app.run_polling()

if __name__ == "__main__":
    main()
