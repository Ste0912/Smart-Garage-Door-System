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

def car_blueprint(app):
    app.register_blueprint(car_api)

car_api = Blueprint("car_api", __name__, url_prefix="/api/car")

#Register a new car
@car_api.route("/register", methods=["POST"])
def register_car():
    data = request.get_json()
    if check_api_source(data) == "Telegram":
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return register_user(data, "cars")
    else:
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }

@car_api.route("/delete/<car_reg_plate>", methods=["POST"])
def delete_car(car_reg_plate):
    data = request.get_json()
    if check_api_source(data) == "Telegram":
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return delete_user(data, car_reg_plate, "cars")
    else:
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }

@car_api.route("/find", methods=["POST"])
def find_cars():
    data = request.get_json()
    if check_api_source(data) == "Telegram":
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return find_users(data, "cars")
    else:
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }

@car_api.route("/find/<command>", methods=["POST"])
def find_car(command):
    data = request.get_json()
    if check_api_source(data) == "Telegram":
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return find_user(data, command, "cars")
    else:
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }