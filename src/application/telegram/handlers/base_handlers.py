import os
from telegram import Update
from telegram.ext import ContextTypes
from src.application.telegram.handlers.pedestrian_handlers import (
    register_pedestrian,
    delete_pedestrian,
    find_pedestrian
)
from src.application.telegram.handlers.car_handlers import (
    register_car,
    delete_car,
    find_car
)
from src.application.telegram.handlers.stat_handlers import (
    get_open_times,
    get_total_open_times,
    get_open_times_stats
)
from config.utils import (
    raise_error,
    is_admin,
    check_auth,
    ask_for_admin_pwd,
    verify_password
)

def help(telegram_id, user_input, admin_password):
    try:
        return """
Available commands:
/start
    Start the bot

/help
    Show this help message

/login <username> <password>
    Login to the system
    E.g. /login John paSs 

/logout
    Logout from the system

/get_open_times <start> <end> <open> <user>
    See statistics about a user's door's 
        usage
    E.g. /get_open_times 01_01_22-12:00:00 
        01_01_22-12:30:00 enter John

/get_total_open_times <start> <end> <open> 
    [collection]
    See statistics about the total number 
        of times a door was opened
    E.g. /get_total_open_times 01_01_22-12:00:00 
        01_01_22-12:30:00 enter
        OR /get_total_open_times 01_01_22-12:00:00
        01_01_22-12:30:00 enter cars

/get_open_times_stats <start> <end> [collection]
    See statistics about the yearly, monthly,
        weekly or daily number of times a 
        door was opened
    E.g. /get_open_times_stats 01_01_22-12:00:00
        01_01_22-12:30:00 cars
        OR /get_open_times_stats 01_01_22-12:00:00
        01_01_22-12:30:00

/register_pedestrian <usr> <pwd> <uid>
    Register a new pedestrian
    E.g. /register_pedestrian John paSs 
        123

/delete_pedestrian <username>
    Delete a pedestrian
    E.g. /delete_pedestrian John

/find_pedestrian [username or id]
    Find all pedestrians or one pedestrian
    E.g. /find_pedestrian John
    OR /find_pedestrian P1234
    OR /find_pedestrian

/register_car <reg_plate> <pwd> <uid>
    Register a new car
    E.g. /register_car ABC123 paSs 123

/delete_car <reg_plate>
    Delete a car
    E.g. /delete_car ABC123

/find_car [reg_plate or id]
    Find all cars or one car
    E.g. /find_car ABC123
    OR /find_car C1234
    OR /find_car
    """
    except Exception as e:
        raise_error(e, __file__, help.__name__,[telegram_id, user_input, admin_password])
        return os.getenv("ERROR_MESSAGE")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start"""
    try:
        split_message = update.message.text.split(" ")
        if not len(split_message) == 1:
            await update.message.reply_text("Please, write only \"/start\".")
            return
        await update.message.reply_text(
            "Hello!\n"
            "Use /login username password to access.\n"
            "Use /help to see the possible commands."
        )
    except Exception as e:
        raise_error(e, __file__, start_handler.__name__,[update, context])
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
        return

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        """Handler for /help [admin]"""
        split_message = update.message.text.split(" ")
        #Case 0: normal user
        if len(split_message) == 1:
            #Case 0.0: logged-out user
            if not check_auth(update.effective_user.id):
                help_text = """
Available commands:
/start
    Start the bot

/help
    Show this help message

/login <username> <password>
    Login to the system
    E.g. /login John paSs

/logout
    Logout from the system"""
                await update.message.reply_text(help_text)
                return
            #Case 0.1: logged-in user
            elif check_auth(update.effective_user.id):
                help_text = """
Available commands:
/start
    Start the bot

/help
    Show this help message

/login <username> <password>
    Login to the system
    E.g. /login John paSs

/logout
    Logout from the system

/get_open_times <start_time> <end_time> 
    <open> <user>
    See statistics about your door's usage
    E.g. /get_open_times 01_01_22-12:00:00 
        01_01_22-12:30:00 enter John"""
                await update.message.reply_text(help_text)
                return
        #Case 1: admin user
        elif len(split_message) == 2 and split_message[1] == 'admin':
            #Case 1.0: logged-out admin
            if not check_auth(update.effective_user.id):
                await update.message.reply_text("You must be logged in as an admin to access admin help.")
                return
            #Case 1.1: logged-in admin
            elif check_auth(update.effective_user.id):
                try:
                    if is_admin(update.effective_user.id):
                        response, update, context = ask_for_admin_pwd(update, context, "help")
                        await update.message.reply_text(response)
                        return
                    else:
                        await update.message.reply_text("You must be logged in as an admin to access admin help.")
                        return
                except:
                    await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
                    return
        #Case 2: anything else
        else:
            await update.message.reply_text("Please, write only \"/help\" or \"/help admin\".")
            return
    except Exception as e:
        raise_error(e, __file__, help_handler.__name__,[update, context])
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
        return

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("I don't understand. Please, write \"/help\" to see the list of commands.")
    except Exception as e:
        raise_error(e, __file__, unknown_command.__name__,[update, context])
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
        return

async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if verify_password(os.getenv("ADMIN_PASSWORD"), update.message.text):
            if context.user_data.get("conversation") == 'register_pedestrian':
                context.user_data.pop("conversation", None)
                await update.message.reply_text(register_pedestrian(
                    update.effective_user.id, 
                    context.user_data.get("input", "unknown"), 
                    update.message.text)
                )
            elif context.user_data.get("conversation") == 'delete_pedestrian':
                context.user_data.pop("conversation", None)
                await update.message.reply_text(delete_pedestrian(
                    update.effective_user.id, 
                    context.user_data.get("input", "unknown"), 
                    update.message.text)
                )
            elif context.user_data.get("conversation") == 'find_pedestrian':
                context.user_data.pop("conversation", None)
                await update.message.reply_text(find_pedestrian(
                    update.effective_user.id, 
                    context.user_data.get("input", "unknown"), 
                    update.message.text)
                )
            elif context.user_data.get("conversation") == 'register_car':
                context.user_data.pop("conversation", None)
                await update.message.reply_text(register_car(
                    update.effective_user.id, 
                    context.user_data.get("input", "unknown"), 
                    update.message.text)
                )
            elif context.user_data.get("conversation") == 'delete_car':
                context.user_data.pop("conversation", None)
                await update.message.reply_text(delete_car(
                    update.effective_user.id, 
                    context.user_data.get("input", "unknown"), 
                    update.message.text)
                )
            elif context.user_data.get("conversation") == 'find_car':
                context.user_data.pop("conversation", None)
                await update.message.reply_text(find_car(
                    update.effective_user.id, 
                    context.user_data.get("input", "unknown"), 
                    update.message.text)
                )
            elif context.user_data.get("conversation") == 'get_open_times':
                context.user_data.pop("conversation", None)
                await update.message.reply_text(get_open_times(
                    update.effective_user.id, 
                    context.user_data.get("input", "unknown"), 
                    update.message.text)
                )
            elif context.user_data.get("conversation") == 'get_total_open_times':
                context.user_data.pop("conversation", None)
                await update.message.reply_text(get_total_open_times(
                    update.effective_user.id, 
                    context.user_data.get("input", "unknown"), 
                    update.message.text)
                )
            elif context.user_data.get("conversation") == 'get_open_times_stats':
                context.user_data.pop("conversation", None)
                await update.message.reply_text(get_open_times_stats(
                    update.effective_user.id, 
                    context.user_data.get("input", "unknown"), 
                    update.message.text)
                )
            elif context.user_data.get("conversation") == 'help':
                context.user_data.pop("conversation", None)
                await update.message.reply_text(help(
                    update.effective_user.id, 
                    context.user_data.get("input", "unknown"), 
                    update.message.text)
                )
            else:
                await update.message.reply_text("I don't understand. Please, write \"/help\" to see the list of commands.")
                return
        else:
            if context.user_data.get("conversation"):
                await update.message.reply_text("You're not authorized to do this.")
                return
            else:
                await update.message.reply_text("I don't understand. Please, write \"/help\" to see the list of commands.")
                return
            return
    except Exception as e:
        raise_error(e, __file__, echo_handler.__name__,[update, context])
        await update.message.reply_text(os.getenv("ERROR_MESSAGE"))
        return