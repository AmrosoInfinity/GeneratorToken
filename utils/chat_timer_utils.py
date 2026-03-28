import time
import threading
from support import string

def set_expire_timer(context, chat_id, message_id, active_button_owner):
    """
    Menjalankan timer untuk mengubah pesan tombol menjadi kadaluarsa
    setelah 60 detik jika tidak ada interaksi.
    """
    def expire_button():
        time.sleep(60)
        state = active_button_owner.get(message_id)
        if state and not state["expired"]:
            try:
                context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=string.NO_SELECTION_MSG,
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            state["expired"] = True

    threading.Thread(target=expire_button, daemon=True).start()
