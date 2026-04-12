import os
from flask import Blueprint, request, jsonify, send_from_directory

images_bp = Blueprint('images', __name__, url_prefix='/images')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_FOLDER = os.path.join(BASE_DIR, "images", "equipment")

@images_bp.route('/equipment/<filename>')
def get_equipment_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@images_bp.route('/users/<filename>')
def get_user_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)