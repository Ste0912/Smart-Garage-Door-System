import requests, os
from telegram import Update
from telegram.ext import ContextTypes

from config.utils import (
    ask_for_admin_pwd,
    check_auth,
    raise_error,
    check_input_format,
    is_admin,
    handle_time_input,
    get_user_data,
    print_response,
    create_temporary_token,
    save_temporary_token_hash,
    start_time_is_before_end_time
)

def get_open_times_stats(telegram_id, user_input, admin_password):
    try:
        split_message = user_input.split(" ")
        try:
            params = {
                "start_time":split_message[1],
                "end_time": split_message[2],
                "admin_username": get_user_data(telegram_id)["username"],
                "admin_password": admin_password
            }
        except:
            return os.getenv("ERROR_MESSAGE")
        collection = None
        try:
            collection = split_message[3]
        except:
            pass
        temp_token = create_temporary_token()
        save_temporary_token_hash(os.getenv("TEMP_TOKEN_PATH"),temp_token)
        params["temp_token"] = temp_token
        if collection is not None:
            response = requests.post(os.getenv("FLASK_URL") + "api/stat/" + f"get_open_times_stats/{collection}", json=params)
        else:
            response = requests.post(os.getenv("FLASK_URL") + "api/stat/" + f"get_open_times_stats/", json=params)
        return print_response(response)
    except Exception as e:
        raise_error(e, __file__, get_open_times_stats.__name__, [telegram_id, user_input, admin_password])
        return

def get_total_open_times(telegram_id, user_input, admin_password):
    try:
        split_message = user_input.split(" ")
        try:
            params = {
                "start_time":split_message[1],
                "end_time": split_message[2],
                "open": split_message[3],
                "admin_username": get_user_data(telegram_id)["username"],
                "admin_password": admin_password
            }
        except:
            return os.getenv("ERROR_MESSAGE")
        print("Checking dates")
        collection = None
        try:
            collection = split_message[4]
        except:
            pass
        temp_token = create_temporary_token()
        save_temporary_token_hash(os.getenv("TEMP_TOKEN_PATH"),temp_token)
        params["temp_token"] = temp_token
        if collection is not None:
            response = requests.post(os.getenv("FLASK_URL") + "api/stat/" + f"get_total_open_times/{collection}", json=params)
        else:
            response = requests.post(os.getenv("FLASK_URL") + "api/stat/" + f"get_total_open_times/", json=params)
        print(f"Response received: {response.json()}")
        return print_response(response)
    except Exception as e:
        raise_error(e, __file__, get_open_times.__name__, [telegram_id, user_input, admin_password])
        return

def get_open_times(telegram_id, user_input, admin_password):
    try:
        split_message = user_input.split(" ")
        try:
            params = {
                "start_time":split_message[1],
                "end_time": split_message[2],
                "open": split_message[3]
            }
        except:
            pass
        try:
            identifier = split_message[4]
            params["admin_username"] = get_user_data(telegram_id)["username"]
            params["admin_password"] = admin_password
        except:
            pass
        temp_token = create_temporary_token()
        save_temporary_token_hash(os.getenv("TEMP_TOKEN_PATH"),temp_token)
        params["temp_token"] = temp_token
        if "admin_password" in params:
            response = requests.post(os.getenv("FLASK_URL") + "api/stat/" + f"get_open_times/{identifier}", json=params)
        else:
            try:
                params["username"] = get_user_data(telegram_id)["username"]
            except:
                params["reg_plate"] = get_user_data(telegram_id)["reg_plate"]
            response = requests.post(os.getenv("FLASK_URL") + "api/stat/" + f"get_open_times/", json=params)
        return print_response(response)
    except Exception as e:
        raise_error(e, __file__, get_open_times.__name__, [telegram_id, user_input, admin_password])
        return

async def get_open_times_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for /get_open_times start_time end_time (exit|enter) [identifier]
    try:
        # Check whether the format is correct
        regex = r'^\/get_open_times\s+([0-9]{2}_[0-9]{2}_[0-9]{2}-[0-9]{2}:[0-9]{2}:[0-9]{2})\s+([0-9]{2}_[0-9]{2}_[0-9]{2}-[0-9]{2}:[0-9]{2}:[0-9]{2})\s+(enter|exit)(?:\s+(\S+))?$'
        user_input = update.message.text
        if not check_input_format(user_input, regex):
            if is_admin(update.effective_user.id):
                await update.message.reply_text(os.getenv("CORRECT_USAGE_MESSAGE") + " /get_open_times start_time end_time (exit|enter) [identifier]")
            elif check_auth(update.effective_user.id):
                await update.message.reply_text(os.getenv("CORRECT_USAGE_MESSAGE") + " /get_open_times start_time end_time (exit|enter)")
            else:
                await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return
        if not is_admin(update.effective_user.id) and not check_auth(update.effective_user.id):
            await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return
        if not start_time_is_before_end_time(user_input.split()[1], user_input.split()[2]):
            await update.message.reply_text("Start time must be before end time.")
            return
        if is_admin(update.effective_user.id):
            if isinstance(handle_time_input(user_input.split()[1]), str) or \
                isinstance(handle_time_input(user_input.split()[2]), str):
                await update.message.reply_text(handle_time_input(user_input.split()[1]))
                return
            response, update, context = ask_for_admin_pwd(update, context, "get_open_times")
        elif check_auth(update.effective_user.id):
            if isinstance(handle_time_input(user_input.split()[1]), str) and \
                isinstance(handle_time_input(user_input.split()[2]), str):
                await update.message.reply_text(handle_time_input(user_input.split()[1]))
                return
            response = get_open_times(update.effective_user.id, user_input, None)
        await update.message.reply_text(response)
        return
    except Exception as e:
        raise_error(e, __file__, get_open_times_handler.__name__, [update, context])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=os.getenv("ERROR_MESSAGE"))
        return

async def get_total_open_times_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for /get_total_open_times start_time end_time (exit|enter) [collection]
    try:
        # Check whether the format is correct
        regex = r'^\/get_total_open_times\s+([0-9]{2}_[0-9]{2}_[0-9]{2}-[0-9]{2}:[0-9]{2}:[0-9]{2})\s+([0-9]{2}_[0-9]{2}_[0-9]{2}-[0-9]{2}:[0-9]{2}:[0-9]{2})\s+(enter|exit)(?:\s+(pedestrians|cars))?$'
        user_input = update.message.text
        if not check_input_format(user_input, regex):
            if is_admin(update.effective_user.id):
                await update.message.reply_text(os.getenv("CORRECT_USAGE_MESSAGE") + " /get_total_open_times start_time end_time (exit|enter) [collection]")
                return
            else:
                await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
                return
        if not is_admin(update.effective_user.id) and not check_auth(update.effective_user.id):
            await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return    
        if not start_time_is_before_end_time(user_input.split()[1], user_input.split()[2]):
            await update.message.reply_text("Start time must be before end time.")
            return
        if is_admin(update.effective_user.id):
            if isinstance(handle_time_input(user_input.split()[1]), str) or \
                isinstance(handle_time_input(user_input.split()[2]), str):
                await update.message.reply_text(handle_time_input(user_input.split()[1]))
                return
            response, update, context = ask_for_admin_pwd(update, context, "get_total_open_times")
        else:
            await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return
        await update.message.reply_text(response)
        return
    except Exception as e:
        raise_error(e, __file__, get_total_open_times_handler.__name__, [update, context])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=os.getenv("ERROR_MESSAGE"))
        return

async def get_open_times_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for /get_open_times_stats start_time end_time [collection]
    try:
        # Check whether the format is correct
        regex = r'^\/get_open_times_stats\s+([0-9]{2}_[0-9]{2}_[0-9]{2}-[0-9]{2}:[0-9]{2}:[0-9]{2})\s+([0-9]{2}_[0-9]{2}_[0-9]{2}-[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\s+(pedestrians|cars))?$'
        user_input = update.message.text
        if not check_input_format(user_input, regex):
            if is_admin(update.effective_user.id):
                await update.message.reply_text(os.getenv("CORRECT_USAGE_MESSAGE") + " /get_open_times_stats start_time end_time [collection]")
                return
            else:
                await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
                return
        if not is_admin(update.effective_user.id) and not check_auth(update.effective_user.id):
            await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return
        if not start_time_is_before_end_time(user_input.split()[1], user_input.split()[2]):
            await update.message.reply_text("Start time must be before end time.")
            return
        if is_admin(update.effective_user.id):
            if isinstance(handle_time_input(user_input.split()[1]), str) or \
                isinstance(handle_time_input(user_input.split()[2]), str):
                await update.message.reply_text(handle_time_input(user_input.split()[1]))
                return
            response, update, context = ask_for_admin_pwd(update, context, "get_open_times_stats")
        else:
            await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return
        await update.message.reply_text(response)
        return
    except Exception as e:
        raise_error(e, __file__, get_open_times_stats_handler.__name__, [update, context])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=os.getenv("ERROR_MESSAGE"))
        return