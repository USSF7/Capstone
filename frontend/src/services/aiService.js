import api from './api'

/**
 * Service for interacting with AI-related backend endpoints.
 *
 * @class AIService
 */
class AIService {
  /**
   * Generate an AI summary of reviews for a given model.
   *
   * @param {string} modelType - Type of entity
   * @param {number|string} modelId - Unique identifier of the entity
   *
   * @returns {Promise<any>} Resolves with API response containing summary data
   */
  async summarizeReviews(modelType, modelId) {
    return api.post('/ai/reviews/summary', {
      model_type: modelType,
      model_id: modelId,
    })
  }
}

export default new AIService()
