"""
AI routes module.

Provides endpoints for AI-powered features, currently limited to
generating review summaries via Google Gemini.

Routes:
    POST /api/ai/reviews/summary -- Generate an AI summary of reviews for an entity.
"""

from flask import Blueprint, request, jsonify
from services import AIService

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/reviews/summary', methods=['POST'])
def summarize_reviews():
    """Generate an AI-powered summary of reviews for an equipment or user.

    Expects JSON body with ``model_type`` ('equipment' or 'user') and
    ``model_id`` (integer). Returns a cached summary if available;
    otherwise generates a new one via Google Gemini and caches it.

    Returns:
        200: Dict with ``summary`` text.
        400: Missing or invalid parameters.
    """
    try:
        data = request.get_json() or {}
        model_type = data.get('model_type')
        model_id = data.get('model_id')

        if not model_type or model_id is None:
            return jsonify({'error': 'model_type and model_id are required'}), 400

        try:
            model_id = int(model_id)
        except (TypeError, ValueError):
            return jsonify({'error': 'model_id must be an integer'}), 400

        summary = AIService.summarize_reviews(model_type, model_id)
        return jsonify({'summary': summary}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
