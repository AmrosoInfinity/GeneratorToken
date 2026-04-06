import os
import logging
from telegram.ext import Updater

# Import semua modul handler
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
        level=logging.INFO # Ubah ke INFO untuk produksi, DEBUG untuk cari error
    )
    logger = logging.getLogger(__name__)

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    raw_owner = os.getenv("BOT_OWNER_ID")

    if not token or not raw_owner:
        raise ValueError("⚠️ Environment variable (TOKEN/OWNER_ID) belum lengkap.")

    # Pastikan owner_id adalah integer
    owner_id = int(raw_owner)

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # --- URUTAN REGISTRASI (SANGAT PENTING) ---
    
    # 1. Prioritas Utama: Perintah Administratif/Owner
    register_input_token(dp, owner_id)
    register_block(dp, owner_id)
    register_suspect(dp, owner_id)

    # 2. Perintah Fungsional
    register_token_handlers(dp)
    register_checktoken(dp, owner_id)
    register_appops_handlers(dp)
    register_command_handlers(dp)

    # 3. Handler Umum (Catch-all) - Taruh paling bawah
    # group_activity & chat_handlers biasanya punya filter yang luas
    register_group_activity(dp, owner_id)
    register_chat_handlers(dp) 

    print("🤖 Bot Giga Byte sudah berjalan...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
