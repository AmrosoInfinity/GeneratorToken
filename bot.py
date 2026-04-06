import os
import logging
from telegram.ext import Updater
# Import semua modul handler sesuai nama file kamu
from generatorToken import register_token_handlers
from chatOpenAi import register_chat_handlers
from appopsPermission import register_appops_handlers
from commandBot import register_command_handlers
from checkToken import register_checktoken
from blockHandler import register_block
from suspectHandler import register_suspect
from groupActivity import register_group_activity
from ownerInputToken import register_input_token

def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    raw_owner = os.getenv("BOT_OWNER_ID")

    if not token or not raw_owner:
        raise ValueError("⚠️ TELEGRAM_BOT_TOKEN atau BOT_OWNER_ID belum diset!")

    owner_id = int(raw_owner)
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # --- URUTAN PRIORITAS (PENTING) ---
    
    # 1. Paling Atas: Command Owner (Agar tidak tertelan Chat AI)
    register_input_token(dp, owner_id)
    register_block(dp, owner_id)
    register_suspect(dp, owner_id)

    # 2. Command Fungsional
    register_token_handlers(dp)
    register_checktoken(dp, owner_id)
    register_appops_handlers(dp)
    register_command_handlers(dp)

    # 3. Paling Bawah: Handler Umum/Chat (Catch-all)
    register_group_activity(dp, owner_id)
    register_chat_handlers(dp) 

    print(f"🤖 Bot Giga Byte aktif. Owner ID: {owner_id}")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
