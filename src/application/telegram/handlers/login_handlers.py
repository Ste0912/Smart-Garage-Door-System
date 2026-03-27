from telegram import Update
from telegram.ext import ContextTypes
import os

from config.utils import (
    check_input_format,
    logged_in_users,
    query_db,
    verify_password, 
    update_logged_in_users, 
    remove_from_logged_in
)

async def login_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /login {username or regPlate} password"""
    try:
        # Check whether the format is correct
        regex = r'^/login\s+(\S+)\s+(\S+)$'
        user_input = update.message.text
        if not check_input_format(user_input, regex):
            await update.message.reply_text(os.getenv("CORRECT_USAGE_MESSAGE") + " /login {username or regPlate} password")
            return

        # Take the {username or regPlate} and password from the message
        value = user_input.split(" ")[1]
        password = user_input.split(" ")[2]

        # Check if the user exists in the database
        users = query_db(["pedestrians", "cars"], [{"profile.username": value},{"profile.reg_plate": value}])
        if not users or len(users) == 0:
            await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return
        else:
            user = users[0]

        # Verify the user's password        
        if not verify_password(user["profile"]["password"], password):
            await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return        
        
        telegram_id = update.effective_user.id
        update_state = update_logged_in_users(telegram_id, user)
        if update_state["already_logged_in"]:
            await update.message.reply_text(os.getenv("ALREADY_LOGGED_IN_MESSAGE"))
            return
        else:
            if user["type"] == "pedestrian":
                await update.message.reply_text(f"You've logged in as {user['profile']['username']}!")
            elif user["type"] == "car":
                await update.message.reply_text(f"You've logged in as {user['profile']['reg_plate']}!")
            else:
                await update.message.reply_text("Your type is not currently supported.")
        return

    except Exception as e:
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))

async def logout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /logout"""
    regex = r'^/logout$'
    user_input = update.message.text
    # Check whether the format is correct
    if not check_input_format(user_input, regex):
        await update.message.reply_text(os.getenv("CORRECT_USAGE_MESSAGE") + " /logout")
        return
    try:
        telegram_id = update.effective_user.id
        if not telegram_id in logged_in_users:
            await update.message.reply_text(os.getenv("NOT_LOGGED_IN_MESSAGE"))
            return

        # Look for the user in the database
        user = query_db(
            ["pedestrians","cars"],
            [{"_id": logged_in_users[telegram_id]["_id"]}]
            )[0]
        if user:
            remove_from_logged_in(telegram_id, user)
            await update.message.reply_text("You've successfully logged out!")
            return
        else:
            await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
            return

    except Exception as e:
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))