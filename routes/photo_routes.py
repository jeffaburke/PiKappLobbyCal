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
            logger.error("Album directory missing: %s", album_path)
            return jsonify([])

        photos = []
        skipped_files = []
        for file in os.listdir(album_path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                photos.append(url_for('static', filename=f'album/{file}'))
            else:
                skipped_files.append(file)

        if skipped_files:
            logger.warning("Skipped non-image files: %s", skipped_files)

        logger.info("Found %d photos, skipped %d files", len(photos), len(skipped_files))
        return jsonify(photos)
    except (OSError, NotFound) as e:
        logger.error("Error accessing photos: %s", str(e), exc_info=True)
        return jsonify([])
