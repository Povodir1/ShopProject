/**
 * Update Quantity Use Case
 * Updates cart item quantity
 */

import { Cart } from '../../domain/cart.entity.js';

export class UpdateQuantityUseCase {
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
   * @param {number} quantity - New quantity
   * @returns {Promise<Cart>} Updated cart
   */
  async execute(sessionId, itemId, quantity) {
    if (!sessionId) {
      throw new Error('Session ID is required');
    }

    if (!itemId) {
      throw new Error('Item ID is required');
    }

    if (quantity < 1 || quantity > 100) {
      throw new Error('Quantity must be between 1 and 100');
    }

    try {
      const data = await this.cartRepository.updateItemQuantity(sessionId, itemId, quantity);
      const cart = Cart.fromAPI(data);

      // Update cache
      this.cartStorage.saveCart(cart);

      // Publish event
      this.eventBus.publish('cart:quantity-changed', {
        itemId,
        quantity,
        itemCount: cart.itemCount
      });

      // Publish count update
      this.eventBus.publish('cart:count-updated', {
        count: cart.itemCount
      });

      return cart;
    } catch (error) {
      console.error('UpdateQuantity use case error:', error);
      throw new Error(`Failed to update item quantity: ${error.message}`);
    }
  }
}

export default UpdateQuantityUseCase;
