from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from bson import ObjectId
import os, signal

# Create blueprints for different API groups
dt_api = Blueprint('dt_api', __name__, url_prefix='/api/dt')
dr_api = Blueprint('dr_api', __name__, url_prefix='/api/dr')
dt_management_api = Blueprint('dt_management_api', __name__, url_prefix='/api/dt-management')


def register_api_blueprints(app):
    """Register all API blueprints with the Flask app"""
    app.register_blueprint(dt_api)
    app.register_blueprint(dr_api)
    app.register_blueprint(dt_management_api)