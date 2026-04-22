"""
AI service module.

Provides AI-powered review summarization using Google Gemini. Summaries
are cached on the reviewed entity (Equipment or User) and invalidated
when reviews are created, updated, or deleted.
"""

from flask import current_app
from google import genai
from datetime import datetime
from database import db
from models import Review, Equipment, User


class AIService:
    """Business logic for AI-powered features.

    Currently supports review summarization via Google Gemini with
    caching on the target model (Equipment or User).
    """

    @staticmethod
    def _validate_model_ref(model_type, model_id):
        """Validate that model_type and model_id are present.

        Args:
            model_type: 'equipment' or 'user'.
            model_id: Primary key of the entity.

        Raises:
            ValueError: If either argument is missing.
        """
        if not model_type or model_id is None:
            raise ValueError("model_type and model_id are required")

    @staticmethod
    def _get_target_model(model_type, model_id):
        """Look up the Equipment or User instance for a model reference.

        Args:
            model_type: 'equipment' or 'user'.
            model_id: Primary key of the entity.

        Returns:
            The Equipment or User instance, or None if not found.

        Raises:
            ValueError: If model_type is not 'equipment' or 'user'.
        """
        AIService._validate_model_ref(model_type, model_id)
        normalized = str(model_type).strip().lower()

        if normalized in ('equipment',):
            return Equipment.query.get(model_id)
        if normalized in ('user', 'users'):
            return User.query.get(model_id)

        raise ValueError("model_type must be 'equipment' or 'user'")

    @staticmethod
    def get_cached_summary(model_type, model_id):
        """Retrieve a previously cached AI review summary.

        Args:
            model_type: 'equipment' or 'user'.
            model_id: Primary key of the entity.

        Returns:
            The cached summary string, or None if not cached.
        """
        target = AIService._get_target_model(model_type, model_id)
        if not target:
            return None
        return target.ai_review_summary

    @staticmethod
    def set_cached_summary(model_type, model_id, summary):
        """Store an AI review summary on the target entity.

        Args:
            model_type: 'equipment' or 'user'.
            model_id: Primary key of the entity.
            summary: The summary text to cache.
        """
        if not summary:
            return

        target = AIService._get_target_model(model_type, model_id)
        if not target:
            return

        target.ai_review_summary = summary
        target.ai_review_summary_updated_at = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def invalidate_cached_summary(model_type, model_id):
        """Clear the cached AI review summary for an entity.

        Called after reviews are created, updated, or deleted to ensure
        the next summary request generates a fresh one.

        Args:
            model_type: 'equipment' or 'user'.
            model_id: Primary key of the entity.
        """
        target = AIService._get_target_model(model_type, model_id)
        if not target:
            return

        target.ai_review_summary = None
        target.ai_review_summary_updated_at = None
        db.session.commit()

    @staticmethod
    def _get_gemini_client():
        """Create a Google Gemini API client.

        Returns:
            A ``genai.Client`` instance.

        Raises:
            ValueError: If the Gemini API key is not configured.
        """
        api_key = current_app.config['GEMINI_API_KEY']
        if not api_key:
            raise ValueError("Gemini API key is not configured")
        return genai.Client(api_key=api_key)

    @staticmethod
    def _generate_text(prompt, model='gemini-2.5-flash'):
        """Generate text using Google Gemini.

        Args:
            prompt: The prompt string to send to the model.
            model: The Gemini model ID to use.

        Returns:
            The generated text response.
        """
        client = AIService._get_gemini_client()

        response = client.models.generate_content(model=model, contents=prompt)

        return response.text

    @staticmethod
    def summarize_reviews(model_type, model_id):
        """Generate a natural-language summary of reviews for an entity.

        Returns a cached summary if one exists. Otherwise, fetches all
        reviews for the entity, builds a prompt with the review data,
        calls Google Gemini to generate a summary, caches it, and returns it.

        Args:
            model_type: 'equipment' or 'user'.
            model_id: Primary key of the entity.

        Returns:
            Summary text string. Returns a fallback message if there are
            no reviews or if the AI call fails.
        """
        AIService._validate_model_ref(model_type, model_id)

        cached_summary = AIService.get_cached_summary(model_type, model_id)
        if cached_summary:
            return cached_summary

        reviews = Review.query.filter_by(model_type=model_type, model_id=model_id).order_by(Review.date.desc()).all()
        if not reviews:
            return f"No reviews found for {model_type} {model_id}."

        avg_rating = sum(r.rating for r in reviews) / len(reviews)

        review_lines = []
        for idx, review in enumerate(reviews, start=1):
            review_text = (review.review or '').strip()
            if not review_text:
                review_text = '[No written comment]'
            review_lines.append(
                f"{idx}. rating={review.rating}/5, date={review.date.isoformat()}, text={review_text}"
            )

        prompt = (
            "You are summarizing user reviews for a marketplace item or user.\n\n"
            
            "Write a single short paragraph (3–5 sentences) that summarizes the overall feedback.\n"
            "Include the general sentiment, the most common positive points, and the most common complaints.\n"
            
            "Guidelines:\n"
            "- Be neutral and objective\n"
            "- Focus only on recurring themes across reviews\n"
            "- Do not list or use bullet points\n"
            "- Do not mention individual reviewers\n"
            "- Do not mention the model ID\n"
            "- Keep it under 100 words\n\n"

            f"Average rating: {avg_rating:.2f}/5\n"
            f"Total reviews: {len(reviews)}\n\n"

            "Reviews:\n"
            + "\n".join(review_lines)
        )

        try:
            summary = AIService._generate_text(prompt, model='gemini-2.5-flash')
            if not summary:
                return "Unable to generate summary at this time."
            AIService.set_cached_summary(model_type, model_id, summary)
            return summary
        except Exception as e:
            current_app.logger.error(f"Error summarizing reviews for {model_type} {model_id}: {e}")
            return "Unable to generate summary at this time."

