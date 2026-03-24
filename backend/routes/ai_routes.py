from flask import Blueprint, request, jsonify
from services import AIService

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/reviews/summary', methods=['POST'])
def summarize_reviews():
    """Generate an AI summary for reviews by model_type and model_id."""
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
