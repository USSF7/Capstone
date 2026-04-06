from flask import Blueprint, request, jsonify
from services import ReviewService

review_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')

@review_bp.route('/', methods=['GET'])
def get_all_reviews():
    """Get all reviews"""
    try:
        reviews = ReviewService.get_all_reviews()
        return jsonify([r.to_dict() for r in reviews]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """Get a review by ID"""
    try:
        review = ReviewService.get_review(review_id)
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        return jsonify(review.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/model/<model_type>/<int:model_id>', methods=['GET'])
def get_reviews_for_model(model_type, model_id):
    """Get all reviews for a specific model"""
    try:
        reviews = ReviewService.get_reviews_for_model(model_type, model_id)
        return jsonify([r.to_dict() for r in reviews]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/submitter/<int:submitter_id>', methods=['GET'])
def get_reviews_by_submitter(submitter_id):
    """Get all reviews by a user"""
    try:
        reviews = ReviewService.get_reviews_by_submitter(submitter_id)
        return jsonify([r.to_dict() for r in reviews]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/', methods=['POST'])
def create_review():
    """Create a new review"""
    try:
        data = request.get_json()
        review = ReviewService.create_review(
            data.get('submitter_id'),
            data.get('model_type'),
            data.get('model_id'),
            data.get('rating'),
            data.get('review')
        )
        return jsonify(review.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    """Update a review"""
    try:
        data = request.get_json()
        review = ReviewService.update_review(review_id, data.get('rating'), data.get('review'))
        return jsonify(review.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@review_bp.route('switch-deleted-review-status/<int:review_id>', methods=['PUT'])
def switch_deleted_review_status(review_id):
    """Switch the deleted review status"""
    try:
        data = request.get_json()
        review = ReviewService.update_review(review_id, deleted=data.get('deleted_status'))
        return jsonify(review.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """Delete a review"""
    try:
        ReviewService.delete_review(review_id)
        return jsonify({'message': 'Review deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500