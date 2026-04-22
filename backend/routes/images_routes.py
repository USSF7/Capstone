"""
Image serving routes module.

Serves static equipment and user profile images from the ``images/``
directory on disk. These routes are used by the frontend to display
uploaded photos.

Routes:
    GET /images/equipment/<filename> -- Serve an equipment image.
    GET /images/users/<filename>     -- Serve a user profile image.
"""

import os
from flask import Blueprint, request, jsonify, send_from_directory

images_bp = Blueprint('images', __name__, url_prefix='/images')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_FOLDER_EQUIPMENT = os.path.join(BASE_DIR, "images", "equipment")
IMAGE_FOLDER_USERS = os.path.join(BASE_DIR, "images", "users")


@images_bp.route('/equipment/<filename>')
def get_equipment_image(filename):
    """Serve an equipment image file from disk.

    Args:
        filename: The image filename (e.g. 'Pickleball-Paddle-Pro.jpg').

    Returns:
        200: The image file.
        404: File not found.
    """
    return send_from_directory(IMAGE_FOLDER_EQUIPMENT, filename)


@images_bp.route('/users/<filename>')
def get_user_image(filename):
    """Serve a user profile image file from disk.

    Args:
        filename: The image filename (e.g. 'Sarah-Mitchell.jpg').

    Returns:
        200: The image file.
        404: File not found.
    """
    return send_from_directory(IMAGE_FOLDER_USERS, filename)