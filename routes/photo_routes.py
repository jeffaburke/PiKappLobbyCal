"""
Photo Routes
"""
import os
from flask import Blueprint, jsonify, current_app, url_for
from werkzeug.exceptions import NotFound
from utils.logger import setup_logger

logger = setup_logger(__name__)
photo_routes = Blueprint('photo_routes', __name__)

@photo_routes.route('/get_photos')
def get_photos():
    """
    Grabs a json list of the photos in the album
    Returns:
        JSON array of photo URLs
    """
    try:
        album_path = os.path.join(current_app.static_folder, 'album')
        logger.debug("Scanning album directory: %s", album_path)

        if not os.path.exists(album_path):
            logger.error("Album directory not found: %s", album_path)
            return jsonify([])

        photos = []
        for file in os.listdir(album_path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                photos.append(url_for('static', filename=f'album/{file}'))

        logger.info("Found %d photos in album", len(photos))
        return jsonify(photos)
    except (OSError, NotFound) as e:
        logger.error("Error accessing photos: %s", str(e))
        return jsonify([])
