from support import string

def is_button_owner(context, chat, user_id, state, query):
    """
    Mengecek apakah user_id adalah pemilik tombol.
    - state: dict {owner: user_id, expired: bool}
    - user_id: id user yang menekan tombol
    - chat: effective_chat
    - query: callback_query (untuk query.answer)
    """
    if not state:
        return True  # tidak ada state, anggap bebas

    if state["owner"] == user_id:
        return True  # pemilik tombol

    # cek anonymous admin
    admins = context.bot.get_chat_administrators(chat.id)
    anon_ids = [admin.user.id for admin in admins if getattr(admin, "is_anonymous", False)]

    # hanya izinkan anonymous admin jika dia adalah owner tombol
    if user_id in anon_ids and user_id == state["owner"]:
        return True

    # bukan pemilik
    query.answer(string.NOT_YOUR_BUTTON_MSG, show_alert=True)
    return False
