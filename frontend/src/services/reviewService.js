import api from './api'

class ReviewService {
  async getReviews() {
    return api.get('/reviews')
  }

  async getReview(reviewId) {
    return api.get(`/reviews/${reviewId}`)
  }

  async getReviewsForModel(modelType, modelId) {
    return api.get(`/reviews/model/${modelType}/${modelId}`)
  }

  async getReviewsBySubmitter(submitterId) {
    return api.get(`/reviews/submitter/${submitterId}`)
  }

  async createReview(submitterId, modelType, modelId, rating, review) {
    return api.post('/reviews', {
      submitter_id: submitterId,
      model_type: modelType,
      model_id: modelId,
      rating,
      review,
    })
  }

  async updateReview(reviewId, rating, review) {
    return api.put(`/reviews/${reviewId}`, { rating, review })
  }

  async deleteReview(reviewId) {
    return api.delete(`/reviews/${reviewId}`)
  }
}

export default new ReviewService()
