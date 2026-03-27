import api from './api'

class AIService {
  async summarizeReviews(modelType, modelId) {
    return api.post('/ai/reviews/summary', {
      model_type: modelType,
      model_id: modelId,
    })
  }
}

export default new AIService()
