/**
 * Cart Item Entity
 * Domain entity for cart items
 */

export class CartItem {
  /**
   * @param {Object} data - Cart item data
   * @param {string} data.id - Item ID (UUID)
   * @param {string} data.product_id - Product ID
   * @param {number} data.quantity - Quantity
   * @param {number} data.price_at_add - Price at time of adding
   * @param {string} data.currency - Currency code
   * @param {number} data.subtotal - Subtotal for this item
   */
  constructor(data) {
    this.id = data.id;
    this.productId = data.product_id;
    this.quantity = Number(data.quantity);
    this.priceAtAdd = Number(data.price_at_add);
    this.currency = data.currency || 'USD';
    this.subtotal = Number(data.subtotal) || 0;
  }

  /**
   * Calculate subtotal
   * @returns {number} Subtotal
   */
  calculateSubtotal() {
    this.subtotal = this.priceAtAdd * this.quantity;
    return this.subtotal;
  }

  /**
   * Get formatted subtotal
   * @returns {string} Formatted subtotal
   */
  getFormattedSubtotal() {
    return this.formatPrice(this.subtotal, this.currency);
  }

  /**
   * Get formatted unit price
   * @returns {string} Formatted price
   */
  getFormattedPrice() {
    return this.formatPrice(this.priceAtAdd, this.currency);
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
   * Check if quantity is valid
   * @returns {boolean}
   */
  isValid() {
    return this.quantity > 0 && this.priceAtAdd >= 0;
  }

  /**
   * Check if item is on sale (price changed since added)
   * @param {number} currentPrice - Current product price
   * @returns {boolean}
   */
  isOnSale(currentPrice) {
    return currentPrice < this.priceAtAdd;
  }

  /**
   * Update quantity
   * @param {number} quantity - New quantity
   */
  updateQuantity(quantity) {
    this.quantity = quantity;
    this.calculateSubtotal();
  }

  /**
   * Convert to plain object
   * @returns {Object} Plain object representation
   */
  toJSON() {
    return {
      id: this.id,
      product_id: this.productId,
      quantity: this.quantity,
      price_at_add: this.priceAtAdd,
      currency: this.currency,
      subtotal: this.subtotal
    };
  }

  /**
   * Create CartItem from API response
   * @param {Object} data - API response data
   * @returns {CartItem} CartItem instance
   */
  static fromAPI(data) {
    return new CartItem(data);
  }
}

export default CartItem;
