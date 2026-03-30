def remove_user_token_message(context, chat_id, message_id):
    """
    Menghapus pesan user yang berisi token setelah diproses.
    """
    try:
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        return True
    except Exception as e:
        print(f"Gagal hapus pesan token: {e}")
        return False
