from telegram import Update
from telegram.ext import ContextTypes
import requests, os, re
from config.utils import (
    ask_for_admin_pwd,
    get_user_data,
    print_response,
    check_input_format,
    raise_error,
    create_temporary_token,
    save_temporary_token_hash,
    is_admin
)

def register_pedestrian(telegram_id, user_input, admin_password):
    try:
        split_message = user_input.split(" ")
        try:
            params = {
                "username":split_message[1],
                "password": split_message[2],
                "uid": split_message[3].replace("_"," "),
                "admin_username": get_user_data(telegram_id)["username"],
                "admin_password": admin_password
            }
        except:
            return os.getenv("ERROR_MESSAGE")
        temp_token = create_temporary_token()
        save_temporary_token_hash(os.getenv("TEMP_TOKEN_PATH"),temp_token)
        params["temp_token"] = temp_token
        response = requests.post(os.getenv("FLASK_URL") + "api/pedestrian/" + "register", json=params)
        return print_response(response)
    except Exception as e:
        raise_error(e, __file__, register_pedestrian.__name__, [telegram_id, user_input, admin_password])
        return

def delete_pedestrian(telegram_id, user_input, admin_password):
    try:
        split_message = user_input.split(" ")
        params = {
            "admin_username": get_user_data(telegram_id)["username"],
            "admin_password": admin_password
        }
        temp_token = create_temporary_token()
        save_temporary_token_hash(os.getenv("TEMP_TOKEN_PATH"),temp_token)
        params["temp_token"] = temp_token
        response = requests.post(os.getenv("FLASK_URL") + "api/pedestrian/" + "delete/" + split_message[1], json=params)
        return print_response(response)
    except Exception as e:
        raise_error(e, __file__, delete_pedestrian.__name__, [telegram_id, user_input, admin_password])
        return

def find_pedestrian(telegram_id, user_input, admin_password):
    try:
        split_message = user_input.split(" ")
        params = {
            "admin_username": get_user_data(telegram_id)["username"],
            "admin_password": admin_password
        }
        temp_token = create_temporary_token()
        save_temporary_token_hash(os.getenv("TEMP_TOKEN_PATH"),temp_token)
        params["temp_token"] = temp_token
        if len(split_message) < 2:
            response = requests.post(os.getenv("FLASK_URL") + "api/pedestrian/" + "find", json=params)
        else:
            response = requests.post(os.getenv("FLASK_URL") + "api/pedestrian/" + "find/" + split_message[1], json=params)
        return print_response(response)
    except Exception as e:
        raise_error(e, __file__, find_pedestrian.__name__, [telegram_id, user_input, admin_password])
        return

async def register_pedestrian_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for /register_pedestrian username password uid
    try:
        regex = r'^/register_pedestrian\s+([A-Za-z]+)\s+(\S+)\s+(\d+(?:_\d+)*)$' # /register_pedestrian username password uid
        user_input = update.message.text
        if not check_input_format(user_input, regex):
            if is_admin(update.effective_user.id):
                await update.message.reply_text(os.getenv("CORRECT_USAGE_MESSAGE") + " /register_pedestrian [username] [password] [uid]")
            else:
                await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return
        response, update, context = ask_for_admin_pwd(update, context, "register_pedestrian")
        await update.message.reply_text(response)
        return
    except Exception as e:
        raise_error(e, __file__, register_pedestrian_handler.__name__, [update, context])
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
        return

async def delete_pedestrian_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for /delete_pedestrian identifier
    try:
        regex = r'^/delete_pedestrian\s+(?:[A-Za-z0-9]+|\d{3}(?:_\d{3}){3})$' # /delete_pedestrian identifier
        user_input = update.message.text
        if not check_input_format(user_input, regex):
            if is_admin(update.effective_user.id):
                await update.message.reply_text(os.getenv("CORRECT_USAGE_MESSAGE") + " /delete_pedestrian identifier")
            else:
                await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return
        response, update, context = ask_for_admin_pwd(update, context, "delete_pedestrian")
        await update.message.reply_text(response)
        return
    except Exception as e:
        raise_error(e, __file__, delete_pedestrian_handler.__name__, [update, context])
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
        return

async def find_pedestrian_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for /find_pedestrian [command]
    try:
        # Check whether the format is correct
        regex = r'^/find_pedestrian(?:\s+(?:[A-Za-z0-9]+|\d{3}(?:_\d{3}){3}))?$' # /find_pedestrian [command]
        user_input = update.message.text
        if not check_input_format(user_input, regex):
            if is_admin(update.effective_user.id):
                await update.message.reply_text(os.getenv("CORRECT_USAGE_MESSAGE") + " /find_pedestrian [command]")
            else:
                await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return
        response, update, context = ask_for_admin_pwd(update, context, "find_pedestrian")
        await update.message.reply_text(response)
        return
    except Exception as e:
        raise_error(e, __file__, find_pedestrian_handler.__name__, [update, context])
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
        return