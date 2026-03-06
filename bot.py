import os
from telegram.ext import Updater
from generatorToken import register_token_handlers
from chatOpenAi import register_chat_handlers
from appopsPermission import register_appops_handlers
from commandBot import register_command_handlers

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # Register handlers dari modul terpisah
    register_token_handlers(dp)
    register_chat_handlers(dp)
    register_appops_handlers(dp)
    register_command_handlers(dp)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
