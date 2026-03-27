import asyncio, os, time, psutil

from config.utils import load_schemas, raise_error, clear_logged_in_users, getenv_array

from flask import Flask
from flask_cors import CORS
from pyngrok import ngrok
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from pymongo import MongoClient

from config.config_loader import ConfigLoader

from src.application.http.api import register_api_blueprints
from src.application.http.car_apis import car_blueprint
from src.application.http.pedestrian_apis import pedestrian_blueprint
from src.application.http.stat_apis import stat_blueprint

from src.application.mqtt.mqtt_handler import MQTTHandler

from src.application.telegram.handlers.base_handlers import (
    start_handler,
    help_handler,
    echo_handler,
    unknown_command
)
from src.application.telegram.handlers.login_handlers import (
    login_handler,
    logout_handler,
)
from src.application.telegram.handlers.stat_handlers import (
    get_open_times_handler,
    get_total_open_times_handler,
    get_open_times_stats_handler
)

from src.application.telegram.handlers.pedestrian_handlers import (
    register_pedestrian_handler,
    delete_pedestrian_handler,
    find_pedestrian_handler
)
from src.application.telegram.handlers.car_handlers import (
    register_car_handler,
    delete_car_handler,
    find_car_handler
)
from src.application.telegram.routes.webhook_routes import register_webhook, init_routes

#from src.digital_twin.dt_factory import DTFactory

from src.services.database_service import DatabaseService

from src.virtualization.digital_replica.schema_registry import SchemaRegistry

class FlaskServer:
    def __init__(self):
        self.app = Flask(__name__)
        # Set logger to DEBUG level to get verbose output
        self.app.logger.setLevel("DEBUG")
        # Enable the interactive debugger
        self.app.config["DEBUG"] = True
        # Enable CORS for cross-origin requests
        CORS(self.app)
        # Declare the ngrok tunnel variable
        self.ngrok_tunnel = None
        # Initialise components
        self._init_components()
        # Register blueprints
        self._register_blueprints()
        # Set the Flask app to not use the reloader so that it has to be manually restarted
        self.app.config["USE_RELOADER"] = False
        # Store the MQTT broker configuration
        self.app.config["MQTT_CONFIG"] = {
            "broker": os.getenv("MQTT_BROKER"),
            "port": os.getenv("MQTT_PORT"),
        }
        # Create the MQTT Handler
        self.app.mqtt_handler = MQTTHandler(self.app)

    def setup_handlers(self, application):
        KNOWN_COMMANDS = ["/start", "/help", "/login", "/logout", "/get_open_times",
            "/register_pedestrian", "/delete_pedestrian", "/find_pedestrian",
            "/register_car", "/delete_car", "/find_car", "/get_total_open_times",
            "/get_open_times_stats"
        ]
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(CommandHandler("help", help_handler))
        application.add_handler(CommandHandler("login", login_handler))
        application.add_handler(CommandHandler("logout", logout_handler))
        application.add_handler(CommandHandler("get_open_times", get_open_times_handler))
        application.add_handler(CommandHandler("get_total_open_times", get_total_open_times_handler))
        application.add_handler(CommandHandler("get_open_times_stats", get_open_times_stats_handler))
        application.add_handler(CommandHandler("register_pedestrian", register_pedestrian_handler))
        application.add_handler(CommandHandler("delete_pedestrian", delete_pedestrian_handler))
        application.add_handler(CommandHandler("find_pedestrian", find_pedestrian_handler))
        application.add_handler(CommandHandler("register_car", register_car_handler))
        application.add_handler(CommandHandler("delete_car", delete_car_handler))
        application.add_handler(CommandHandler("find_car", find_car_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))
        application.add_handler(MessageHandler(
            filters.Regex(r"^/") & ~filters.Regex(r"^/(" + "|".join(cmd.strip("/") for cmd in KNOWN_COMMANDS) + r")\b"),
        unknown_command
    ))

    def _init_components(self):
        try:
            # Tear down any existing ngrok processes
            for proc in psutil.process_iter(["pid", "name"]):
                if "ngrok" in proc.info["name"].lower():
                    try:
                        psutil.Process(proc.info["pid"]).terminate()
                        print(
                            f"Terminated existing ngrok process: PID {proc.info['pid']}"
                        )
                    except:
                        pass
            # Load YAML schemas
            schema_registry = SchemaRegistry()
            load_schemas()

            # Build and configure the database
            db_config = ConfigLoader.load_database_config(os.getenv('DB_SCHEMA'))
            connection_string = ConfigLoader.build_connection_string(db_config)

            # Start an asyncio event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            time.sleep(2)

            # Start ngrok tunnel to expose the Flask server to the internet
            ngrok.set_auth_token(os.getenv("NGROK_TOKEN"))
            self.ngrok_tunnel = ngrok.connect(os.getenv("FLASK_PORT"))
            
            # Set the webhook URL for Telegram bot
            webhook_url = (
                f"{self.ngrok_tunnel.public_url}{os.getenv('TELEGRAM_BLUE_PRINT')}{os.getenv('WEBHOOK_PATH')}"
            )
            print(f"Webhook URL: {webhook_url}")

            application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
            application.loop = loop
            self.setup_handlers(application)
            init_routes(application)
            loop.run_until_complete(application.initialize())
            loop.run_until_complete(application.start())
            loop.run_until_complete(application.bot.set_webhook(webhook_url))

            # Connect to the database
            db_service = DatabaseService(
                connection_string=connection_string,
                db_name=db_config["settings"]["name"],
                schema_registry=schema_registry,
            )
            db_service.connect()
            self.app.config["DB_SERVICE"] = db_service


        except Exception as e:
            print(f"Initialisation error: {str(e)}")
            if self.ngrok_tunnel:
                ngrok.disconnect(self.ngrok_tunnel.public_url)
            raise e

    def _register_blueprints(self):
        register_api_blueprints(self.app)
        car_blueprint(self.app)
        pedestrian_blueprint(self.app)
        register_webhook(self.app)
        stat_blueprint(self.app)

    def run(self, host, port):
        try:
            self.app.mqtt_handler.start()
            self.app.run(host=host, port=port, use_reloader=False)
        finally:
            self.closing_server()
            if "DB_SERVICE" in self.app.config:
                self.app.config["DB_SERVICE"].disconnect()
            if self.ngrok_tunnel:
                ngrok.disconnect(self.ngrok_tunnel.public_url)

    def closing_server(self):
        try:
            os.system("cls" if os.name == "nt" else "clear")
            print("EXIT INVOKED")
            # Opening a new MongoDB connection as the previous one was closing
            client = MongoClient(f'{os.getenv("DB_PROTOCOL")}://{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/')
            db = client[os.getenv("DB_NAME")]
            collections = getenv_array("COLLECTIONS")
            for collection_name in collections:
                collection = db[collection_name]
                elements = collection.find()
                for el in elements:
                    try:
                        collection.update_one(
                            {"_id": el["_id"]},
                            {"$set": {"metadata.logged_as": None}}
                        )
                    except:
                        pass
                    try:
                        collection.update_one(
                            {"_id": el["_id"]},
                            {"$set": {"profile.atHome": False}}
                        )
                    except:
                        pass
            client.close()
            clear_logged_in_users()
            print("All users logged out and out of home\nGoodbye!")
        except Exception as e:
            raise_error(e, __file__, self.closing_server.__name__, self)