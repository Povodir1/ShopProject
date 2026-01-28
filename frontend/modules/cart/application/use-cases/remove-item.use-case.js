/**
 * Remove Item Use Case
 * Removes item from cart
 */

import { Cart } from '../../domain/cart.entity.js';

export class RemoveItemUseCase {
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
   * @param {string} itemId - Cart item ID
   * @returns {Promise<Cart>} Updated cart
   */
  async execute(sessionId, itemId) {
    if (!sessionId) {
      throw new Error('Session ID is required');
    }

    if (!itemId) {
      throw new Error('Item ID is required');
    }

    try {
      const data = await this.cartRepository.removeItem(sessionId, itemId);
      const cart = Cart.fromAPI(data);

      // Update cache
      this.cartStorage.saveCart(cart);

      // Publish event
      this.eventBus.publish('cart:item-removed', {
        itemId,
        itemCount: cart.itemCount
      });

      // Publish count update
      this.eventBus.publish('cart:count-updated', {
        count: cart.itemCount
      });

      return cart;
    } catch (error) {
      console.error('RemoveItem use case error:', error);
      throw new Error(`Failed to remove item from cart: ${error.message}`);
    }
  }
}

export default RemoveItemUseCase;
