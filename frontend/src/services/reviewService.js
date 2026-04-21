import api from './api'

/**
 * Service for handling review-related API operations.
 *
 * @class ReviewService
 */
class ReviewService {
  /**
   * Retrieves all reviews.
   *
   * @returns {Promise<Object>} List of all reviews.
   */
  async getReviews() {
    return api.get('/reviews')
  }

  /**
   * Retrieves a single review by ID.
   *
   * @param {number|string} reviewId - Review ID.
   * @returns {Promise<Object>} Review object.
   */
  async getReview(reviewId) {
    return api.get(`/reviews/${reviewId}`)
  }

  /**
   * Retrieves reviews for a specific model.
   *
   * @param {string} modelType - Type of model.
   * @param {number|string} modelId - ID of the model being reviewed.
   * @returns {Promise<Object>} List of reviews for the model.
   */
  async getReviewsForModel(modelType, modelId) {
    return api.get(`/reviews/model/${modelType}/${modelId}`)
  }

  /**
   * Retrieves all reviews submitted by a specific user.
   *
   * @param {number|string} submitterId - User ID of the reviewer.
   * @returns {Promise<Object>} List of submitted reviews.
   */
  async getReviewsBySubmitter(submitterId) {
    return api.get(`/reviews/submitter/${submitterId}`)
  }

  /**
   * Creates a new review.
   *
   * @param {number|string} submitterId - ID of the user submitting the review.
   * @param {string} modelType - Type of entity being reviewed.
   * @param {number|string} modelId - ID of the entity being reviewed.
   * @param {number} rating - Rating value.
   * @param {string} review - Review text content.
   * @returns {Promise<Object>} Created review object.
   */
  async createReview(submitterId, modelType, modelId, rating, review) {
    return api.post('/reviews', {
      submitter_id: submitterId,
      model_type: modelType,
      model_id: modelId,
      rating,
      review,
    })
  }

  /**
   * Updates an existing review.
   *
   * @param {number|string} reviewId - Review ID.
   * @param {number} rating - Updated rating.
   * @param {string} review - Updated review text.
   * @returns {Promise<Object>} Updated review object.
   */
  async updateReview(reviewId, rating, review) {
    return api.put(`/reviews/${reviewId}`, { rating, review })
  }

  /**
   * Toggles or sets the deleted status of a review.
   *
   * @param {number|string} reviewId - Review ID.
   * @param {boolean} status - Deleted status flag.
   * @returns {Promise<Object>} Updated review object.
   */
  async switchDeletedReviewStatus(reviewId, status) {
    return api.put(`/reviews/switch-deleted-review-status/${reviewId}`, { deleted_status: status })
  }

  /**
   * Deletes a review permanently.
   *
   * @param {number|string} reviewId - Review ID.
   * @returns {Promise<Object>} Deletion response.
   */
  async deleteReview(reviewId) {
    return api.delete(`/reviews/${reviewId}`)
  }
}

export default new ReviewService()
