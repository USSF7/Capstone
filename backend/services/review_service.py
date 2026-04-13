from flask import jsonify
from models import Review, User
from database import db
from sqlalchemy.orm import joinedload

class ReviewService:
    """Service layer for Review business logic"""

    @staticmethod
    def create_review(submitter_id, model_type, model_id, rating, review=None, deleted=False):
        """Create a new review"""
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
        """Update a review"""
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
        """Delete a review"""
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