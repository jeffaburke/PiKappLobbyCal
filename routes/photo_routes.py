"""
Photo Routes
"""
import os
from flask import Blueprint, jsonify, current_app, url_for

photo_routes = Blueprint('photo_routes', __name__)

@photo_routes.route('/get_photos')
def get_photos():
    """
    Grabs a json list of the photos in the album
    Returns:
        JSON array of photo URLs
    """
    album_path = os.path.join(current_app.static_folder, 'album')
    photos = []
    for file in os.listdir(album_path):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            photos.append(url_for('static', filename=f'album/{file}'))
    return jsonify(photos)
