/**
 * Clear Cart Use Case
 * Clears all items from cart
 */

import { Cart } from '../../domain/cart.entity.js';

export class ClearCartUseCase {
  /**
   * @param {Object} cartRepository - Cart repository (API client)
   * @param {Object} cartStorage - Cart storage wrapper
   * @param {Object} eventBus - Event bus for publishing events
   */
  constructor(cartRepository, cartStorage, eventBus) {
    this.cartRepository = cartRepository;
    this.cartStorage = cartStorage;
    this.eventBus = eventBus;
  }

  /**
   * Execute use case
   * @param {string} sessionId - Session ID
   * @returns {Promise<Cart>} Cleared cart
   */
  async execute(sessionId) {
    if (!sessionId) {
      throw new Error('Session ID is required');
    }

    try {
      const data = await this.cartRepository.clear(sessionId);
      const cart = Cart.fromAPI(data);

      // Update cache
      this.cartStorage.saveCart(cart);

      // Publish event
      this.eventBus.publish('cart:cleared', {
        itemCount: 0
      });

      // Publish count update
      this.eventBus.publish('cart:count-updated', {
        count: 0
      });

      return cart;
    } catch (error) {
      console.error('ClearCart use case error:', error);
      throw new Error(`Failed to clear cart: ${error.message}`);
    }
  }
}

export default ClearCartUseCase;
