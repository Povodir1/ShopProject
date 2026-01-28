/**
 * Global Cart Event Handler
 * Handles cart events across all pages
 * This script should be loaded on every page
 */

import api from './shared/api.js';
import storage from './shared/storage.js';
import eventBus from './event-bus.js';

class CartHandler {
  constructor() {
    this.sessionId = this.getOrCreateSessionId();
  }

  /**
   * Get or create session ID
   * @returns {string} Session ID
   */
  getOrCreateSessionId() {
    let sessionId = storage.get('shop_session_id');

    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      storage.set('shop_session_id', sessionId, 86400000); // 24 hours
    }

    return sessionId;
  }

  /**
   * Initialize the cart handler
   */
  initialize() {
    // Listen for add-to-cart events
    eventBus.subscribe('cart:add-item', (data) => this.handleAddItem(data));

    // Listen for cart count requests
    eventBus.subscribe('cart:request-count', () => this.publishCartCount());

    // Listen for cart update requests
    eventBus.subscribe('cart:request-update', () => this.loadAndPublishCart());

    // Initial cart count publication
    this.publishCartCount();
  }

  /**
   * Handle add to cart event
   * @param {Object} data - Event data
   */
  async handleAddItem(data) {
    try {
      const response = await api.post('/cart/items', {
        session_id: this.sessionId,
        product_id: data.productId,
        quantity: data.quantity || 1
      });

      // Show success notification
      this.showNotification('Item added to cart!', 'success');

      // Publish cart updated event
      eventBus.publish('cart:item-added', {
        productId: data.productId,
        quantity: data.quantity || 1,
        cart: response
      });

      // Request cart update (for cart page reload)
      eventBus.publish('cart:request-update');

      // Update cart count
      this.publishCartCount();

    } catch (error) {
      console.error('Failed to add item to cart:', error);
      this.showNotification('Failed to add item to cart', 'error');
    }
  }

  /**
   * Load cart and publish count
   */
  async loadAndPublishCart() {
    try {
      const cart = await api.get('/cart', {
        params: { session_id: this.sessionId }
      });

      eventBus.publish('cart:updated', { cart });

      this.publishCartCount();
    } catch (error) {
      console.error('Failed to load cart:', error);
    }
  }

  /**
   * Publish cart count
   */
  async publishCartCount() {
    try {
      const cart = await api.get('/cart', {
        params: { session_id: this.sessionId }
      });

      const count = this.calculateCartCount(cart);
      eventBus.publish('cart:count-updated', { count });
    } catch (error) {
      console.error('Failed to get cart count:', error);
      eventBus.publish('cart:count-updated', { count: 0 });
    }
  }

  /**
   * Calculate cart count from cart data
   * @param {Object} cart - Cart data
   * @returns {number} Cart count
   */
  calculateCartCount(cart) {
    if (!cart || !cart.items) return 0;
    return cart.items.reduce((sum, item) => sum + (item.quantity || 0), 0);
  }

  /**
   * Show notification
   * @param {string} message - Notification message
   * @param {string} type - Notification type (success, error, warning, info)
   */
  showNotification(message, type = 'info') {
    // Create toast element if it doesn't exist
    let container = document.querySelector('.toast-container');

    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    // Auto-remove after 3 seconds
    setTimeout(() => {
      toast.classList.add('toast-hiding');
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, 3000);
  }

  /**
   * Destroy the handler
   */
  destroy() {
    // Cleanup if needed
  }
}

// Create singleton instance
const cartHandler = new CartHandler();

// Auto-initialize
cartHandler.initialize();

export default cartHandler;
