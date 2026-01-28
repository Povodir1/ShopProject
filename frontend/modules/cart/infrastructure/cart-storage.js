/**
 * Cart Storage
 * LocalStorage wrapper for cart caching
 */

import storage from '../../../../core/shared/storage.js';
import config from '../../../../core/config.js';

export class CartStorage {
  constructor() {
    this.storageKey = config.cartStorageKey;
  }

  /**
   * Save cart to storage
   * @param {Object} cart - Cart entity or plain object
   */
  saveCart(cart) {
    try {
      const data = cart.toJSON ? cart.toJSON() : cart;
      storage.set(this.storageKey, data, config.storage.sessionDuration);
    } catch (error) {
      console.error('Failed to save cart to storage:', error);
    }
  }

  /**
   * Get cart from storage
   * @returns {Object|null} Cart data or null
   */
  getCart() {
    try {
      return storage.get(this.storageKey);
    } catch (error) {
      console.error('Failed to get cart from storage:', error);
      return null;
    }
  }

  /**
   * Clear cart from storage
   */
  clearCart() {
    try {
      storage.remove(this.storageKey);
    } catch (error) {
      console.error('Failed to clear cart from storage:', error);
    }
  }

  /**
   * Get session ID from storage
   * @returns {string|null} Session ID or null
   */
  getSessionId() {
    try {
      return storage.get(config.sessionKey);
    } catch (error) {
      console.error('Failed to get session ID from storage:', error);
      return null;
    }
  }

  /**
   * Save session ID to storage
   * @param {string} sessionId - Session ID
   */
  saveSessionId(sessionId) {
    try {
      storage.set(config.sessionKey, sessionId, config.storage.sessionDuration);
    } catch (error) {
      console.error('Failed to save session ID to storage:', error);
    }
  }

  /**
   * Generate and save new session ID
   * @returns {string} New session ID
   */
  generateSessionId() {
    const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    this.saveSessionId(sessionId);
    return sessionId;
  }

  /**
   * Get or create session ID
   * @returns {string} Session ID
   */
  getOrCreateSessionId() {
    let sessionId = this.getSessionId();

    if (!sessionId) {
      sessionId = this.generateSessionId();
    }

    return sessionId;
  }
}

// Create and export singleton instance
const cartStorage = new CartStorage();

export default cartStorage;
