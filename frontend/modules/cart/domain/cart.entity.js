/**
 * Cart Entity
 * Domain entity for shopping cart
 */

import { CartItem } from './cart-item.entity.js';
import { CartCalculatorService } from './cart-calculator.service.js';

export class Cart {
  /**
   * @param {Object} data - Cart data
   * @param {string} data.id - Cart ID (UUID)
   * @param {string} data.session_id - Session ID
   * @param {Array} data.items - Cart items
   * @param {number} data.total - Total price
   * @param {number} data.item_count - Total item count
   */
  constructor(data) {
    this.id = data.id;
    this.sessionId = data.session_id;
    this.items = (data.items || []).map(item => new CartItem(item));
    this.total = Number(data.total) || 0;
    this.itemCount = Number(data.item_count) || 0;

    this.calculator = new CartCalculatorService();
  }

  /**
   * Add item to cart
   * @param {string} productId - Product ID
   * @param {number} quantity - Quantity to add
   * @param {number} price - Price at add
   * @param {string} currency - Currency code
   * @returns {Cart} Updated cart (for chaining)
   */
  addItem(productId, quantity, price, currency = 'USD') {
    // Check if item already exists
    const existingItem = this.items.find(item => item.productId === productId);

    if (existingItem) {
      existingItem.quantity += quantity;
    } else {
      const newItem = new CartItem({
        id: this.generateTempId(),
        product_id: productId,
        quantity,
        price_at_add: price,
        currency,
        subtotal: price * quantity
      });
      this.items.push(newItem);
    }

    this.recalculate();
    return this;
  }

  /**
   * Remove item from cart
   * @param {string} itemId - Item ID
   * @returns {Cart} Updated cart (for chaining)
   */
  removeItem(itemId) {
    this.items = this.items.filter(item => item.id !== itemId);
    this.recalculate();
    return this;
  }

  /**
   * Update item quantity
   * @param {string} itemId - Item ID
   * @param {number} quantity - New quantity
   * @returns {Cart} Updated cart (for chaining)
   */
  updateItemQuantity(itemId, quantity) {
    const item = this.items.find(item => item.id === itemId);

    if (item) {
      if (quantity <= 0) {
        this.removeItem(itemId);
      } else {
        item.quantity = quantity;
        this.recalculate();
      }
    }

    return this;
  }

  /**
   * Clear all items from cart
   * @returns {Cart} Updated cart (for chaining)
   */
  clear() {
    this.items = [];
    this.recalculate();
    return this;
  }

  /**
   * Recalculate totals
   */
  recalculate() {
    this.total = this.calculator.calculateTotal(this.items);
    this.itemCount = this.calculator.calculateItemCount(this.items);
  }

  /**
   * Check if cart is empty
   * @returns {boolean}
   */
  isEmpty() {
    return this.items.length === 0;
  }

  /**
   * Get item by product ID
   * @param {string} productId - Product ID
   * @returns {CartItem|null} Found item or null
   */
  getItemByProductId(productId) {
    return this.items.find(item => item.productId === productId) || null;
  }

  /**
   * Get item by ID
   * @param {string} itemId - Item ID
   * @returns {CartItem|null} Found item or null
   */
  getItemById(itemId) {
    return this.items.find(item => item.id === itemId) || null;
  }

  /**
   * Get all items
   * @returns {Array<CartItem>} Array of cart items
   */
  getAllItems() {
    return [...this.items];
  }

  /**
   * Get formatted total
   * @returns {string} Formatted total price
   */
  getFormattedTotal() {
    if (this.items.length === 0) return '$0.00';

    const currency = this.items[0]?.currency || 'USD';
    return this.formatPrice(this.total, currency);
  }

  /**
   * Format price
   * @param {number} price - Price value
   * @param {string} currency - Currency code
   * @returns {string} Formatted price
   */
  formatPrice(price, currency = 'USD') {
    try {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
      }).format(price);
    } catch (error) {
      return `${currency} ${price.toFixed(2)}`;
    }
  }

  /**
   * Generate temporary ID for new items
   * @returns {string} Temporary ID
   */
  generateTempId() {
    return 'temp_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Convert to plain object
   * @returns {Object} Plain object representation
   */
  toJSON() {
    return {
      id: this.id,
      session_id: this.sessionId,
      items: this.items.map(item => item.toJSON()),
      total: this.total,
      item_count: this.itemCount
    };
  }

  /**
   * Create Cart from API response
   * @param {Object} data - API response data
   * @returns {Cart} Cart instance
   */
  static fromAPI(data) {
    return new Cart(data);
  }
}

export default Cart;
