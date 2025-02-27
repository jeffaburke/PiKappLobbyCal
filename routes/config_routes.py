"""Configuration routes"""
from flask import Blueprint, jsonify, current_app

config_routes = Blueprint('config_routes', __name__)

@config_routes.route('/config')
def get_config():
    """Get client-side configuration"""
    return jsonify({
        'CALENDAR_INTERVAL': current_app.config['CALENDAR_INTERVAL'],
        'PHOTO_INTERVAL': current_app.config['PHOTO_INTERVAL']
    })
