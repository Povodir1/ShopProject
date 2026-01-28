/**
 * Get Cart Use Case
 * Retrieves current user's cart
 */

import { Cart } from '../../domain/cart.entity.js';

export class GetCartUseCase {
  /**
   * @param {Object} cartRepository - Cart repository (API client)
   * @param {Object} cartStorage - Cart storage wrapper
   */
  constructor(cartRepository, cartStorage) {
    this.cartRepository = cartRepository;
    this.cartStorage = cartStorage;
  }

  /**
   * Execute use case
   * @param {string} sessionId - Session ID
   * @returns {Promise<Cart>} Cart entity
   */
  async execute(sessionId) {
    if (!sessionId) {
      throw new Error('Session ID is required');
    }

    try {
      const data = await this.cartRepository.get(sessionId);
      const cart = Cart.fromAPI(data);

      // Cache cart in storage
      this.cartStorage.saveCart(cart);

      return cart;
    } catch (error) {
      console.error('GetCart use case error:', error);

      // Return cached cart if available
      const cachedCart = this.cartStorage.getCart();
      if (cachedCart) {
        return cachedCart;
      }

      throw new Error(`Failed to get cart: ${error.message}`);
    }
  }
}

export default GetCartUseCase;
