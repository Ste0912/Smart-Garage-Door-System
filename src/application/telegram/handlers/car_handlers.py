from telegram import Update
from telegram.ext import ContextTypes
import requests, os, re
from config.utils import (
    print_response,
    ask_for_admin_pwd,
    get_user_data,
    check_input_format,
    raise_error,
    create_temporary_token,
    save_temporary_token_hash,
    is_admin
)

def register_car(telegram_id, user_input, admin_password):
    try:
        split_message = user_input.split(" ")
        params = {
            "reg_plate":split_message[1],
            "password": split_message[2],
            "uid": split_message[3].replace("_"," "),
            "admin_username": get_user_data(telegram_id)["username"],
            "admin_password": admin_password
        }
        temp_token = create_temporary_token()
        save_temporary_token_hash(os.getenv("TEMP_TOKEN_PATH"),temp_token)
        params["temp_token"] = temp_token
        response = requests.post(os.getenv("FLASK_URL") + "api/car/" + "register", json=params)
        return print_response(response)
    except Exception as e:
        raise_error(e, __file__, register_car.__name__, [telegram_id, user_input, admin_password])
        return

def delete_car(telegram_id, user_input, admin_password):
    try:
        split_message = user_input.split(" ")
        params = {
            "admin_username": get_user_data(telegram_id)["username"],
            "admin_password": admin_password
        }
        temp_token = create_temporary_token()
        save_temporary_token_hash(os.getenv("TEMP_TOKEN_PATH"),temp_token)
        params["temp_token"] = temp_token
        response = requests.post(os.getenv("FLASK_URL") + "api/car/" + "delete/" + split_message[1], json=params)
        return print_response(response)
    except Exception as e:
        raise_error(e, __file__, delete_car.__name__, [telegram_id, user_input, admin_password])
        return

def find_car(telegram_id, user_input, admin_password):
    try:
        split_message = user_input.split(" ")
        params = {
            "admin_username": get_user_data(telegram_id)["username"],
            "admin_password": admin_password
        }
        temp_token = create_temporary_token()
        save_temporary_token_hash(os.getenv("TEMP_TOKEN_PATH"),temp_token)
        params["temp_token"] = temp_token
        if len(split_message) == 1:
            response = requests.post(os.getenv("FLASK_URL") + "api/car/" + "find", json=params)
        elif len(split_message) == 2:
            response = requests.post(os.getenv("FLASK_URL") + "api/car/" + "find/" + split_message[1], json=params)
        return print_response(response)
    except Exception as e:
        raise_error(e, __file__, find_car.__name__, [telegram_id, user_input, admin_password])
        return

async def register_car_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for /register_car reg_plate password uid
    try:
        # Check whether the format is correct
        regex = r'^/register_car\s+([A-Za-z0-9]+)\s+(\S+)\s+(\d+(?:_\d+)*)$' # /register_car reg_plate password uid
        user_input = update.message.text
        if not check_input_format(user_input, regex):
            if not is_admin(update.effective_user.id):
                await update.message.reply_text("You must be logged in as an admin to access this command.")
                return
            else:
                await update.message.reply_text("The correct usage is: /register_car <reg_plate> <password> <uid>")
                return
        response, update, context = ask_for_admin_pwd(update, context, "register_car")
        await update.message.reply_text(response)
        return
    except Exception as e:
        raise_error(e, __file__, register_car_handler.__name__, [update, context])
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
        return

async def delete_car_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for /delete_car identifier
    try:
        # Check whether the format is correct
        regex = r'^/delete_car\s+(?:[A-Za-z0-9]+|\d{3}(?:_\d{3}){3})$' # /delete_car identifier
        user_input = update.message.text
        if not check_input_format(user_input, regex):
            if is_admin(update.effective_user.id):
                await update.message.reply_text(os.getenv("CORRECT_USAGE_MESSAGE") + " /delete_car identifier")
                return
            else:
                await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
                return
        response, update, context = ask_for_admin_pwd(update, context, "delete_car")
        await update.message.reply_text(response)
        return
    except Exception as e:
        raise_error(e, __file__, delete_car_handler.__name__, [update, context])
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
        return

async def find_car_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for /find_car [command]
    try:
        regex = r'^/find_car(?:\s+(?:[A-Za-z0-9]+|\d{3}(?:_\d{3}){3}))?$' # /find_car [command]
        user_input = update.message.text
        if not check_input_format(user_input, regex):
            if is_admin(update.effective_user.id):
                await update.message.reply_text(os.getenv("CORRECT_USAGE_MESSAGE") + " /find_car [command]")
                return
            else:
                await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return
        response, update, context = ask_for_admin_pwd(update, context, "find_car")
        await update.message.reply_text(response)
        return
    except Exception as e:
        raise_error(e, __file__, find_car_handler.__name__, [update, context])
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
        return