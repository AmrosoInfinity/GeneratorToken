from support import string

def is_button_owner(context, chat, user_id, state, query):
    """
    Mengecek apakah user_id boleh menekan tombol.
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

    # cek anonymous admin
    admins = context.bot.get_chat_administrators(chat.id)
    anon_ids = [admin.user.id for admin in admins if getattr(admin, "is_anonymous", False)]

    # anonymous admin boleh menekan tombol siapa saja
    if user_id in anon_ids:
        return True

    # bukan pemilik dan bukan anonymous admin
    query.answer(string.NOT_YOUR_BUTTON_MSG, show_alert=True)
    return False
