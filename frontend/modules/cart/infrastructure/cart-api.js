/**
 * Cart API Client
 * Infrastructure layer for cart API communication
 */

import api from '../../../../core/shared/api.js';

export class CartAPI {
  /**
   * Get cart by session ID
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Cart data
   */
  async get(sessionId) {
    try {
      return await api.get('/cart', { params: { session_id: sessionId } });
    } catch (error) {
      console.error('Cart API: get error', error);
      throw error;
    }
  }

  /**
   * Add item to cart
   * @param {string} sessionId - Session ID
   * @param {string} productId - Product ID
   * @param {number} quantity - Quantity
   * @returns {Promise<Object>} Updated cart data
   */
  async addItem(sessionId, productId, quantity = 1) {
    try {
      return await api.post('/cart/items', {
        session_id: sessionId,
        product_id: productId,
        quantity
      });
    } catch (error) {
      console.error('Cart API: addItem error', error);
      throw error;
    }
  }

  /**
   * Update item quantity
   * @param {string} sessionId - Session ID
   * @param {string} itemId - Cart item ID
   * @param {number} quantity - New quantity
   * @returns {Promise<Object>} Updated cart data
   */
  async updateItemQuantity(sessionId, itemId, quantity) {
    try {
      return await api.put(`/cart/items/${itemId}`, {
        quantity
      }, { params: { session_id: sessionId } });
    } catch (error) {
      console.error('Cart API: updateItemQuantity error', error);
      throw error;
    }
  }

  /**
   * Remove item from cart
   * @param {string} sessionId - Session ID
   * @param {string} itemId - Cart item ID
   * @returns {Promise<Object>} Updated cart data
   */
  async removeItem(sessionId, itemId) {
    try {
      return await api.delete(`/cart/items/${itemId}`, {
        params: { session_id: sessionId }
      });
    } catch (error) {
      console.error('Cart API: removeItem error', error);
      throw error;
    }
  }

  /**
   * Clear cart
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Cleared cart data
   */
  async clear(sessionId) {
    try {
      return await api.delete('/cart', {
        params: { session_id: sessionId }
      });
    } catch (error) {
      console.error('Cart API: clear error', error);
      throw error;
    }
  }
}

// Create and export singleton instance
const cartAPI = new CartAPI();

export default cartAPI;
