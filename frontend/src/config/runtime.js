/**
 * Shared frontend runtime configuration.
 */

/**
 * Normalizes a configured backend URL by removing a trailing slash.
 * Preserves the empty string so production can use same-origin paths.
 *
 * @param {string|undefined} value
 * @returns {string}
 */
function normalizeBackendUrl(value) {
  if (value === undefined) {
    return 'http://localhost:5000'
  }

  return value.endsWith('/') ? value.slice(0, -1) : value
}

/**
 * Base backend URL used for API calls and uploaded assets.
 */
export const BACKEND_URL = normalizeBackendUrl(import.meta.env.VITE_BACKEND_URL)

/**
 * Base URL for API requests.
 */
export const API_BASE_URL = `${BACKEND_URL}/api`
