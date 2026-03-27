from flask import Blueprint, request
from telegram import Update
import os

webhook = Blueprint("webhook", __name__, url_prefix=os.getenv("TELEGRAM_BLUE_PRINT"))
application = None

def register_webhook(app):
    app.register_blueprint(webhook)
    print("Webhook registered at ", os.getenv("TELEGRAM_BLUE_PRINT"))

def init_routes(app):
    global application
    application = app

@webhook.route("/telegram", methods=["POST"])
def telegram_webhook():
    """Webhook endpoint for receiving updates from Telegram"""
    if request.method == "POST":
        update = Update.de_json(request.get_json(), application.bot)
        application.loop.run_until_complete(application.process_update(update))
    return "OK"

@webhook.route("/", methods=["GET"])
def index():
    return "Bot is up and running!"
