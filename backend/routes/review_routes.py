"""
Review routes module.

Provides CRUD endpoints for review management, including polymorphic
queries by model type/ID and by submitter.

Routes:
    GET    /api/reviews/                              -- List all non-deleted reviews.
    GET    /api/reviews/<id>                          -- Get review by ID.
    GET    /api/reviews/model/<type>/<id>             -- Get reviews for an entity.
    GET    /api/reviews/submitter/<id>                -- Get reviews by a submitter.
    POST   /api/reviews/                              -- Create a new review.
    PUT    /api/reviews/<id>                          -- Update a review's rating/text.
    PUT    /api/reviews/switch-deleted-review-status/<id> -- Toggle soft-delete flag.
    DELETE /api/reviews/<id>                          -- Hard-delete a review.
"""

from flask import Blueprint, request, jsonify
from services import ReviewService

review_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')


@review_bp.route('/', methods=['GET'])
def get_all_reviews():
    """Get all non-deleted reviews.

    Returns:
        200: List of review dicts.
    """
    try:
        reviews = ReviewService.get_all_reviews()
        return jsonify([r.to_dict() for r in reviews]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """Get a single review by ID.

    Args:
        review_id: The review's primary key.

    Returns:
        200: Review dict.
        404: Review not found.
    """
    try:
        review = ReviewService.get_review(review_id)
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        return jsonify(review.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/model/<model_type>/<int:model_id>', methods=['GET'])
def get_reviews_for_model(model_type, model_id):
    """Get all non-deleted reviews for a specific equipment or user.

    Args:
        model_type: 'equipment' or 'user'.
        model_id: Primary key of the reviewed entity.

    Returns:
        200: List of review dicts.
    """
    try:
        reviews = ReviewService.get_reviews_for_model(model_type, model_id)
        return jsonify([r.to_dict() for r in reviews]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/submitter/<int:submitter_id>', methods=['GET'])
def get_reviews_by_submitter(submitter_id):
    """Get all non-deleted reviews written by a specific user.

    Args:
        submitter_id: The submitter User's primary key.

    Returns:
        200: List of review dicts.
    """
    try:
        reviews = ReviewService.get_reviews_by_submitter(submitter_id)
        return jsonify([r.to_dict() for r in reviews]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/', methods=['POST'])
def create_review():
    """Create a new review.

    Expects JSON body with ``submitter_id``, ``model_type``, ``model_id``,
    ``rating`` (1-5), and optional ``review`` text. Invalidates any cached
    AI review summary for the target entity.

    Returns:
        201: Created review dict.
        400: Validation error.
    """
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
    """Update a review's rating and/or text.

    Args:
        review_id: The review's primary key.

    Returns:
        200: Updated review dict.
        400: Validation error (e.g. rating out of range).
    """
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
    """Toggle the soft-delete flag on a review.

    Expects JSON body with ``deleted_status`` (boolean).

    Args:
        review_id: The review's primary key.

    Returns:
        200: Updated review dict.
    """
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
    """Permanently delete a review and invalidate its AI summary cache.

    Args:
        review_id: The review's primary key.

    Returns:
        200: Success message.
        404: Review not found.
    """
    try:
        ReviewService.delete_review(review_id)
        return jsonify({'message': 'Review deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500