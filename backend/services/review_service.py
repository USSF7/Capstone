"""
Review service module.

Business logic for review CRUD operations. Creating, updating, or deleting
a review automatically invalidates the cached AI review summary for the
reviewed entity.
"""

from flask import jsonify
from models import Review, User
from database import db
from sqlalchemy.orm import joinedload


class ReviewService:
    """Business logic for Review management.

    All methods are static — no instance state is needed.
    """

    @staticmethod
    def create_review(submitter_id, model_type, model_id, rating, review=None, deleted=False):
        """Create a new review and invalidate the AI summary cache.

        Args:
            submitter_id: Primary key of the User writing the review.
            model_type: 'equipment' or 'user'.
            model_id: Primary key of the reviewed entity.
            rating: Integer rating from 1 to 5.
            review: Optional free-text review body.
            deleted: Initial soft-delete flag (default False).

        Returns:
            The created Review instance.

        Raises:
            ValueError: If required fields missing or rating out of range.
        """
        if not all([submitter_id, model_type, model_id, rating]):
            raise ValueError("submitter_id, model_type, model_id, and rating are required")
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        rev = Review(submitter_id=submitter_id, model_type=model_type, model_id=model_id, rating=rating, review=review, deleted=deleted)
        db.session.add(rev)
        db.session.commit()

        from services.ai_service import AIService
        AIService.invalidate_cached_summary(model_type, model_id)

        return rev

    @staticmethod
    def get_review(review_id):
        """Get a review by ID"""
        return Review.query.get(review_id)

    @staticmethod
    def get_all_reviews():
        """Get all reviews"""
        return Review.query.filter_by(deleted=False).all()

    @staticmethod
    def get_reviews_for_model(model_type, model_id):
        """Get all reviews for a specific model"""
        return Review.query.filter_by(model_type=model_type, model_id=model_id, deleted=False).all()

    @staticmethod
    def get_reviews_by_submitter(submitter_id):
        """Get all reviews by a user"""
        return Review.query.filter_by(submitter_id=submitter_id, deleted=False).all()

    @staticmethod
    def update_review(review_id, rating=None, review=None, deleted=None):
        """Update a review's rating, text, or deleted status.

        Only non-None arguments are applied. Invalidates the AI summary
        cache after changes.

        Args:
            review_id: The review's primary key.
            rating: New rating (1-5).
            review: New review text.
            deleted: New soft-delete flag.

        Returns:
            The updated Review instance.

        Raises:
            ValueError: If review not found or rating out of range.
        """
        rev = Review.query.get(review_id)
        if not rev:
            raise ValueError("Review not found")
        
        if rating is not None:
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
            rev.rating = rating
        if review is not None:
            rev.review = review
        if deleted is not None:
            rev.deleted = deleted
        
        db.session.commit()

        from services.ai_service import AIService
        AIService.invalidate_cached_summary(rev.model_type, rev.model_id)

        return rev

    @staticmethod
    def delete_review(review_id):
        """Permanently delete a review and invalidate the AI summary cache.

        Args:
            review_id: The review's primary key.

        Returns:
            True on success.

        Raises:
            ValueError: If review not found.
        """
        rev = Review.query.get(review_id)
        if not rev:
            raise ValueError("Review not found")

        model_type = rev.model_type
        model_id = rev.model_id
        
        db.session.delete(rev)
        db.session.commit()

        from services.ai_service import AIService
        AIService.invalidate_cached_summary(model_type, model_id)

        return True