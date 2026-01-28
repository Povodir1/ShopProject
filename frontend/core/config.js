/**
 * Core Configuration
 * Centralized configuration for the application
 */

const config = {
  // API Configuration
  apiBaseUrl: 'http://localhost:8000/api',
  apiTimeout: 10000,
  apiPrefix: '/api',

  // Storage Keys
  sessionKey: 'shop_session_id',
  cartStorageKey: 'shop_cart',
  searchHistoryKey: 'shop_search_history',

  // Pagination
  pagination: {
    defaultLimit: 20,
    maxLimit: 100,
    defaultOffset: 0
  },

  // Storage Settings
  storage: {
    sessionDuration: 86400000, // 24 hours in milliseconds
    searchHistoryLimit: 10
  },

  // UI Settings
  ui: {
    searchDebounceDelay: 300, // milliseconds
    toastDuration: 3000, // milliseconds
    loadingSpinnerDelay: 200 // milliseconds
  },

  // Currency
  currency: {
    default: 'USD',
    locale: 'en-US'
  }
};

export default config;
