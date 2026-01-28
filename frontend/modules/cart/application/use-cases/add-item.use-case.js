/**
 * Add Item Use Case
 * Adds item to cart
 */

import { Cart } from '../../domain/cart.entity.js';

export class AddItemUseCase {
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
   * @param {string} productId - Product ID
   * @param {number} quantity - Quantity to add
   * @returns {Promise<Cart>} Updated cart
   */
  async execute(sessionId, productId, quantity = 1) {
    if (!sessionId) {
      throw new Error('Session ID is required');
    }

    if (!productId) {
      throw new Error('Product ID is required');
    }

    if (quantity < 1 || quantity > 100) {
      throw new Error('Quantity must be between 1 and 100');
    }

    try {
      const data = await this.cartRepository.addItem(sessionId, productId, quantity);
      const cart = Cart.fromAPI(data);

      // Update cache
      this.cartStorage.saveCart(cart);

      // Publish event
      this.eventBus.publish('cart:item-added', {
        productId,
        quantity,
        itemCount: cart.itemCount
      });

      // Publish count update for badges
      this.eventBus.publish('cart:count-updated', {
        count: cart.itemCount
      });

      return cart;
    } catch (error) {
      console.error('AddItem use case error:', error);
      throw new Error(`Failed to add item to cart: ${error.message}`);
    }
  }
}

export default AddItemUseCase;
