import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from utils.token_validate_utils import check_limit, fetch_tokens, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message
from utils.button_ownership_utils import is_button_owner
from utils.chat_timer_utils import set_expire_timer
from utils.captureTraffic import get_x_token

# mapping message_id -> {owner: user_id, expired: bool}
active_button_owner = {}

def token_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Grab", callback_data="grab"),
         InlineKeyboardButton("Gojek", callback_data="gojek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = update.message.reply_text(string.TOKEN_MENU_TEXT, reply_markup=reply_markup)

    active_button_owner[msg.message_id] = {"owner": update.effective_user.id, "expired": False}
    set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)


def handle_grab(query, tz_name, user_id, user_requests, user_blocked, user_timezone, update, context):
    if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
        token = get_x_token(
            file_path="playload/2cd7ad75-3dcb-423f-a8db-00d2beb62851",   # payload hasil capture di repo
            prev_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJuand0IjoiZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNklsOWtaV1poZFd4MElpd2lkSGx3SWpvaVNsZFVJbjAuZXlKaGRXUWlPaUpRUVZOVFJVNUhSVklpTENKamJtWWlPaUpNVXpCMFRGTXhRMUpWWkVwVWFVSkVVbFpLVlZOVldrcFJNRVpWVWxNd2RFeFRNSFJEYXpGS1UxVktTbEpGVGtObFNFWkNVa1ZHYmxKVlRrSmFNRlpEVkZWR2RsSXdUa1JqVldSVVZGUlJOVkZyUms1Uk1ERkNUMGhvUlZaRlJrMVJiV1JQVm10S1FsUldVa05TVm5CdldWUktWbVF3YUc5Wk1EVlBaV3RHTTFSV1VrSmxSVEZGVVZoalMxUlZVa0prTVdSdldUQTFUMUpIWkROVVZsSkNaVVV4UlZGWVpFNVNSVVl6VmpKd1FsVkZNVkpOU0dSRVpERnNSVlpzUmxKU1JWWXpWV3RrV2xZelVuTlVWVnB5WkRCV00xZFZhRXhpTVhCS1pXMXZkMUV3UmxKWFZXeE1ZakZ3U21WdGIzZFNRWEJDVlZkT1JWVlhaRUpTV0dOMldtdGtkRmxZUW5KYVZHUnNWVVpLZG1KcmNGRlZNMFp1V1dzd2VGRXlTa2hXVlRWcVdrVldSVTFFU2xoUmFrSnNaV3M1TWs1cmNGQmpRM1JHWTBka1ZsZHJSakpSYVRsdllXcEZlR1JVWkVSalYzQlhVVzVHVEVOcVNYcGlWR1JWVEhrNU5VOVhlSHBYUjBreFVXdE5OVTVyTVZWVVZVcEdaREJTTTFkVlVsZFZha0pSVVZaR1NVd3dTa0pXVlZKQ1pESldRbEZWVWtKVE1FcHVXak5HYjJFeWNGQlZSa1pTVWtWR2JsUnJjRUpTUlVwSVVWZHNSbEZVVGt4VE1tTkxaVVpzYVZwNlFqWkxlbWd3VWxoc1dWSnFVbTlPVlhONFl6SkZNRXd4Y0dsWFJtaExVMVZ2ZW1KRVFuUmpNM0EyVVZVeGRsRXdiRkpTUkVWeVZEQTFhVTlYUlRGaldGbzFZMVV4VVUweFVYSmpXRUY1WkRJNWMyTXhTblZPZWxwVVQwWndXRlYzY0RSaE1uaHpVMnRXZGxSSVNsSlFWREJMVEZNd2RFeFRNVVpVYTFGblVUQldVMVpGYkVkVFZVNUNWa1ZWZEV4VE1IUk1VVDA5SWl3aVpYTnBJam9pT1daNFFYcHJkblJDTDNsSlNpdFNlWEpIVW5GNFlqbG9TMmhFVEdWSmFsbEZVRTFFYW14TlYxSjZkemhFUzI0eGEwRTlQU0lzSW1WNGNDSTZORGt5T0RNNU1EVXhNaXdpYVdGMElqb3hOemMwTnprd05UQTVMQ0pxZEdraU9pSTVZMkV6WVRJMFppMDBOalEwTFRSbU9ESXRZbVZpT0MwMU5tSmlPV0ZrTjJKa09UTWlMQ0pzYldVaU9pSlFTRTlPUlU1VlRVSkZVaUlzSW01aGJXVWlPaUlpTENKemRXSWlPaUl5T1dFNU9HWmtaQzAyT0RNekxUUTRZbVF0T0RVNU5TMW1NelJpWmpVM1lqUXlOR1lpZlEuVGJxZ0ZBWFJMdkVlWWMxZE4yNjliZlM3NnZNTEFfMTNBa1lZNXBFZEtMTHowM2dfeG5wWTduaHFlVTBYVldIbEZqZWQxTXpzSEQ4ZVdKX1lIaU9pUUZ2SkNtNy1ITnFjbW1pNmlNdXRMaHI4c3dIdWhtV2xxTDlCOHcwUWJKUy0wWjQ5WFVzTThPWnpxbTUwLWJOQ2R3RFhtOWYxaHFicTNEa1FsOHJOUEg2YWdtMkplOU9YaFdIN2Z3TjBwZmhSUkNPdmlMRTVXdTZsbDJQckxVa0YwR0hjbzluQXBDWXBURGxlbGZTbVZtTkJsYUw5VEFZY3FVMlo3RWN3Rl9iakV5SGpQUUhjM0dyR29ycDRWb3R1cmltczdOQUhHSFYyUjh0bU8tN01RX25KSC0zRXhiSmtabTgwLUdEWkhPV0RFN1o5Q3NLcXROSFpIcHZ5VDRpM1VxVTdtM09CRzhpSW9zQmtHanRDU2YxclJUdGVYSjY5d05lUnVHcl9PM0FhMFhqZ3U1Qzczei1PWHFwSkVzQTRrYnhWS3psa1FlWDZqSmw3Z2RUUnlOZlk2MGNEM0tGWVRKTlItdzc1dGl5cU5UeWcydEFuWm84cWc5OEpUNzd3ZU9tZkdzUFpFRW5qbWxYZEhXMU5Wb1RaTGJaRUsyaEN6MkJua0NqZ1RnNXdnQU15aHVwSTUzMWYtMFduVkMwem1zZmVJUF9DdzM0Y195WEVkY3VSc1lkWl9BTmt1SFcxNU9BUHhlTzgxbGVLaXVUUWlkNU92WVlabVZZdW9yTTh4TU9LWFE0MHBUeTlySWk5czlTdkg0NzNBTXBTQVBITXFkNzJ4a1BEaGVWeU50U2NTTS1NNlZpcHFmdFo5NU9Ra3kwaUxtZjRPN3F6X0dwdFRmYjNhc28iLCJpYXQiOjE3NzQ4MDY2NjAsImV4cCI6NDkyODM5MDUxMiwic3ViIjoiMjlhOThmZGQtNjgzMy00OGJkLTg1OTUtZjM0YmY1N2I0MjRmIiwiYXVkIjoiUEFTU0VOR0VSIn0.HBhNkXdgUE2j4_MoxTYccRtGzInr1lg5qYwuQhvGkN3uc8bWZWXj4x9cFHkrzZ6PU9O_KgytqioETPIZTFDmkA",     # token lama dari response sebelumnya
            batch_id="954a7e43-aaa1-4726-a280-c1b4451d0577",
            event_count=122,
            batch_timestamp=1774808569291
        )
        if token:
            query.edit_message_text(string.TOKEN_GRAB.format(token=token), parse_mode="Markdown")
        else:
            query.edit_message_text(string.TOKEN_NOT_FOUND.format(service="Grab"), parse_mode="Markdown")
    save_tmp(user_id, user_requests, user_blocked, user_timezone)


def handle_gojek(query, tz_name, user_id, user_requests, user_blocked, user_timezone, update, context):
    if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
        tokens = fetch_tokens("https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek")
        if tokens:
            chosen = random.choice(tokens)
            query.edit_message_text(string.TOKEN_GOJEK.format(token=chosen), parse_mode="Markdown")
        else:
            query.edit_message_text(string.TOKEN_NOT_FOUND.format(service="Gojek"), parse_mode="Markdown")
    save_tmp(user_id, user_requests, user_blocked, user_timezone)


def button_handler(update, context):
    query = update.callback_query
    chat = update.effective_chat
    user_id = query.from_user.id
    data = query.data
    message_id = query.message.message_id

    state = active_button_owner.get(message_id)

    if not is_button_owner(context, chat, user_id, state, query):
        return

    user_requests, user_blocked, user_timezone = load_tmp(user_id)

    if data in ["grab", "gojek"]:
        if chat.type not in ["group", "supergroup"]:
            send_group_only_message(update, "⚠️ Command ini hanya bisa digunakan di dalam grup.")
            return

        if str(user_id) not in user_timezone:
            keyboard = [[InlineKeyboardButton("Set Timezone", callback_data="set_timezone")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            msg = query.edit_message_text(string.NEED_TIMEZONE_TEXT, reply_markup=reply_markup)
            active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
            set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)
            return

        tz_name = user_timezone.get(str(user_id))
        if data == "grab":
            handle_grab(query, tz_name, user_id, user_requests, user_blocked, user_timezone, update, context)
        elif data == "gojek":
            handle_gojek(query, tz_name, user_id, user_requests, user_blocked, user_timezone, update, context)

        if state:
            active_button_owner.pop(message_id, None)

    elif data == "set_timezone":
        keyboard = [
            [InlineKeyboardButton(string.TIMEZONE_WIB, callback_data="tz_Asia/Jakarta")],
            [InlineKeyboardButton(string.TIMEZONE_WITA, callback_data="tz_Asia/Makassar")],
            [InlineKeyboardButton(string.TIMEZONE_WIT, callback_data="tz_Asia/Jayapura")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = query.edit_message_text(string.CHOOSE_TIMEZONE_TEXT, reply_markup=reply_markup)
        active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
        set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)

    elif data.startswith("tz_"):
        tz_name = data.replace("tz_", "")
        user_timezone[str(user_id)] = tz_name
        save_tmp(user_id, user_requests, user_blocked, user_timezone)
        query.edit_message_text(string.TIMEZONE_SET_SUCCESS.format(tz=tz_name), parse_mode="Markdown")
        if state:
            active_button_owner.pop(message_id, None)


def register_token_menu(dp):
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(button_handler))


def register_token_handlers(dp):
    register_token_menu(dp)
