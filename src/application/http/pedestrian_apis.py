import os
from flask import Blueprint, request
from config.utils import( 
    register_user, 
    delete_user, 
    find_users, 
    find_user,
    check_api_source,
    destroy_temporary_token
)

def pedestrian_blueprint(app):
    app.register_blueprint(pedestrian_api)

pedestrian_api = Blueprint("pedestrian_api", __name__, url_prefix="/api/pedestrian")

#Register a new pedestrian
@pedestrian_api.route("/register", methods=["POST"])
def register_pedestrian():
    data = request.get_json()
    if check_api_source(data) == "Telegram":
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return register_user(data, "pedestrians")
    else:
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }

@pedestrian_api.route("/delete/<pedestrian_username>", methods=["POST"])
def delete_pedestrian(pedestrian_username):
    data = request.get_json()
    if check_api_source(data) == "Telegram":
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return delete_user(data, pedestrian_username, "pedestrians")
    else:
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }

@pedestrian_api.route("/find", methods=["POST"])
def find_pedestrians():
    data = request.get_json()
    if check_api_source(data) == "Telegram":
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return find_users(data, "pedestrians")
    else:
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    
@pedestrian_api.route("/find/<command>", methods=["POST"])
def find_pedestrian(command):
    data = request.get_json()
    if check_api_source(data) == "Telegram":
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return find_user(data, command, "pedestrians")
    else:
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }