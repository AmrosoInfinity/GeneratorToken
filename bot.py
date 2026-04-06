import os
import logging
from telegram.ext import Updater

# Import SEMUA modul kamu
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
    owner_id = int(raw_owner) if raw_owner else 0

    if not token or not owner_id:
        logger.error("❌ Environment Variables (TOKEN/OWNER_ID) belum lengkap!")
        return

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    logger.info("🛠 Memulai registrasi semua handler...")

    # --- KELOMPOK 1: PRIORITAS TINGGI (Owner & Fitur Utama) ---
    # Taruh di paling atas agar '/inputToken' dan '/token' langsung terdeteksi
    register_input_token(dp, owner_id)
    register_block(dp, owner_id)
    register_suspect(dp, owner_id)
    register_token_handlers(dp)
    
    # --- KELOMPOK 2: FITUR FUNGSIONAL ---
    register_checktoken(dp, owner_id)
    register_appops_handlers(dp)
    register_command_handlers(dp)

    # --- KELOMPOK 3: HANDLER UMUM (Catch-all) ---
    # Taruh di paling bawah karena fitur ini biasanya membaca semua teks/chat
    register_group_activity(dp, owner_id)
    register_chat_handlers(dp) 

    logger.info("✅ Semua fitur (Token, AI, AppOps, Group) telah dimuat!")
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
