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
        return True

    # kalau ID sama persis dengan owner → izinkan
    if state["owner"] == user_id:
        return True

    # cek apakah user ini anonymous admin
    admins = context.bot.get_chat_administrators(chat.id)
    anon_ids = [admin.user.id for admin in admins if getattr(admin, "is_anonymous", False)]

    # kalau anonymous admin tapi bukan owner → tolak
    if user_id in anon_ids and user_id != state["owner"]:
        query.answer(string.NOT_YOUR_BUTTON_MSG, show_alert=True)
        return False

    # kalau bukan anonymous admin dan bukan owner → tolak
    query.answer(string.NOT_YOUR_BUTTON_MSG, show_alert=True)
    return False
