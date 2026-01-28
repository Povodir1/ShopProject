/**
 * Base API Client
 * HTTP client with error handling, session management, and logging
 */

import config from '../config.js';
import storage from './storage.js';

class ApiClient {
  constructor() {
    this.baseURL = config.apiBaseUrl;
    this.timeout = config.apiTimeout;
  }

  /**
   * Get session ID from storage or generate new one
   * @returns {string} Session ID
   */
  getSessionId() {
    let sessionId = storage.get(config.sessionKey);

    if (!sessionId) {
      sessionId = this.generateSessionId();
      storage.set(config.sessionKey, sessionId, config.storage.sessionDuration);
    }

    return sessionId;
  }

  /**
   * Generate a unique session ID
   * @returns {string} Session ID
   */
  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Build URL with query parameters
   * @param {string} endpoint - API endpoint
   * @param {Object} params - Query parameters
   * @returns {string} Full URL with query params
   */
  buildUrl(endpoint, params = {}) {
    let url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;

    // Add session_id to params for cart endpoints
    if (endpoint.includes('/cart')) {
      params.session_id = this.getSessionId();
    }

    // Build query string
    const queryString = new URLSearchParams(
      Object.entries(params)
        .filter(([_, value]) => value !== undefined && value !== null)
        .map(([key, value]) => [key, String(value)])
    ).toString();

    return queryString ? `${url}?${queryString}` : url;
  }

  /**
   * Create abort controller with timeout
   * @param {number} customTimeout - Custom timeout in ms
   * @returns {AbortController}
   */
  createTimeoutController(customTimeout = null) {
    const controller = new AbortController();
    const timeout = customTimeout || this.timeout;

    setTimeout(() => controller.abort(), timeout);
    return controller;
  }

  /**
   * Make HTTP request
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise} Response data
   */
  async request(endpoint, options = {}) {
    const url = this.buildUrl(endpoint, options.params);
    const controller = this.createTimeoutController(options.timeout);

    const requestOptions = {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    };

    // Remove params from options as they're in the URL now
    delete requestOptions.params;
    delete requestOptions.timeout;

    try {
      const response = await fetch(url, requestOptions);

      if (!response.ok) {
        throw new ApiError(response.status, response.statusText, url);
      }

      // Handle empty responses (e.g., DELETE with no content)
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        return null;
      }

      return await response.json();

    } catch (error) {
      if (error.name === 'AbortError') {
        throw new ApiError(408, 'Request timeout', url);
      }

      if (error instanceof ApiError) {
        throw error;
      }

      throw new ApiError(0, error.message, url);
    }
  }

  /**
   * GET request
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Request options
   * @returns {Promise} Response data
   */
  get(endpoint, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'GET'
    });
  }

  /**
   * POST request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @param {Object} options - Request options
   * @returns {Promise} Response data
   */
  post(endpoint, data = null, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    });
  }

  /**
   * PUT request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @param {Object} options - Request options
   * @returns {Promise} Response data
   */
  put(endpoint, data = null, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined
    });
  }

  /**
   * DELETE request
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Request options
   * @returns {Promise} Response data
   */
  delete(endpoint, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'DELETE'
    });
  }

  /**
   * PATCH request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @param {Object} options - Request options
   * @returns {Promise} Response data
   */
  patch(endpoint, data = null, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined
    });
  }
}

/**
 * API Error class
 */
class ApiError extends Error {
  constructor(status, message, url) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.url = url;
  }

  /**
   * Check if error is a network error
   * @returns {boolean}
   */
  isNetworkError() {
    return this.status === 0;
  }

  /**
   * Check if error is a timeout
   * @returns {boolean}
   */
  isTimeout() {
    return this.status === 408;
  }

  /**
   * Check if error is a client error (4xx)
   * @returns {boolean}
   */
  isClientError() {
    return this.status >= 400 && this.status < 500;
  }

  /**
   * Check if error is a server error (5xx)
   * @returns {boolean}
   */
  isServerError() {
    return this.status >= 500 && this.status < 600;
  }

  /**
   * Get user-friendly error message
   * @returns {string}
   */
  getUserMessage() {
    if (this.isTimeout()) {
      return 'Request timeout. Please try again.';
    }

    if (this.isNetworkError()) {
      return 'Network error. Please check your connection.';
    }

    if (this.status === 404) {
      return 'Resource not found.';
    }

    if (this.isServerError()) {
      return 'Server error. Please try again later.';
    }

    return this.message || 'An error occurred. Please try again.';
  }
}

// Create and export singleton instance
const api = new ApiClient();

export default api;
export { ApiError };
