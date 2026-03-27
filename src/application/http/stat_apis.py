import os
from flask import Blueprint, request
from datetime import datetime
from config.utils import (
    check_temp_token, 
    destroy_temporary_token,
    get_num_of_open_times,
    get_anonymous_open_times,
    get_open_times_stats
    )

stat_api = Blueprint("stat_api", __name__, url_prefix="/api/stat")

def stat_blueprint(app):
    app.register_blueprint(stat_api)

@stat_api.route("/get_open_times_stats/<collection>", methods=["POST"])
def get_open_times_stats_api_collection(collection):
    data = request.get_json()
    if not all(k in data for k in ["start_time", "end_time", "admin_username", "admin_password", "temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    if not check_temp_token(data["temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
    return get_open_times_stats(data, collection)

@stat_api.route("/get_open_times_stats/", methods=["POST"])
def get_open_times_stats_api():
    data = request.get_json()
    if not all(k in data for k in ["start_time", "end_time", "admin_username", "admin_password", "temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    if not check_temp_token(data["temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    destroy_temporary_token(data["temp_token"])    
    return get_open_times_stats(data)

@stat_api.route("/get_total_open_times/<collection>", methods=["POST"])
def get_total_open_times_api_collection(collection):
    data = request.get_json()
    if not all(k in data for k in ["start_time", "end_time", "open", "admin_username", "admin_password", "temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    if not check_temp_token(data["temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    destroy_temporary_token(data["temp_token"])
    return get_anonymous_open_times(data, collection)

@stat_api.route("/get_total_open_times/", methods=["POST"])
def get_total_open_times_api():
    data = request.get_json()
    if not all(k in data for k in ["start_time", "end_time", "open", "admin_username", "admin_password", "temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    if not check_temp_token(data["temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    destroy_temporary_token(data["temp_token"])
    return get_anonymous_open_times(data)

@stat_api.route("/get_open_times/<identifier>", methods=["POST"])
def get_open_times_api_admin(identifier):
    data = request.get_json()
    if not all(k in data for k in ["start_time", "end_time", "open", "admin_username", "admin_password", "temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    if not check_temp_token(data["temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    destroy_temporary_token(data["temp_token"])
    return get_num_of_open_times(data, identifier)

@stat_api.route("/get_open_times/", methods=["POST"])
def get_open_times_api_user():
    data = request.get_json()
    if not all(k in data for k in ["start_time", "end_time", "open", "temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    if not check_temp_token(data["temp_token"]):
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }
    if "username" in data:
        return get_num_of_open_times(data, data["username"])
    elif "reg_plate" in data:
        return get_num_of_open_times(data, data["reg_plate"])