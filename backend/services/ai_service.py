from flask import current_app
from google import genai
from models import Review

class AIService:

    @staticmethod
    def _get_gemini_client():
        api_key = current_app.config['GEMINI_API_KEY']
        if not api_key:
            raise ValueError("Gemini API key is not configured")
        return genai.Client(api_key=api_key)

    @staticmethod
    def _generate_text(prompt, model='gemini-2.5-flash'):
        client = AIService._get_gemini_client()

        response = client.models.generate_content(model=model, contents=prompt)

        return response.text

    @staticmethod
    def summarize_reviews(model_type, model_id):
        if not model_type or model_id is None:
            raise ValueError("model_type and model_id are required")

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
            "- If reviews are limited, mention that briefly\n"
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
            return summary
        except Exception as e:
            current_app.logger.error(f"Error summarizing reviews for {model_type} {model_id}: {e}")
            return "Unable to generate summary at this time."

