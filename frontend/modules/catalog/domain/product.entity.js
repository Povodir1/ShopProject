/**
 * Product Entity
 * Domain entity for products
 */

import { formatPrice } from "/core/shared/formatters.js';

export class Product {
  /**
   * @param {Object} data - Product data
   * @param {string} data.id - Product ID (UUID)
   * @param {string} data.name - Product name
   * @param {string} data.description - Product description
   * @param {number} data.price - Product price
   * @param {string} data.currency - Currency code (USD, EUR, etc.)
   * @param {string|null} data.category_id - Category ID
   * @param {number} data.stock - Stock quantity
   * @param {boolean} data.is_available - Availability flag
   * @param {string|null} data.image_url - Product image URL
   * @param {string|null} data.created_at - Creation date
   * @param {string|null} data.updated_at - Last update date
   */
  constructor(data) {
    this.id = data.id;
    this.name = data.name;
    this.description = data.description || '';
    this.price = Number(data.price);
    this.currency = data.currency || 'USD';
    this.categoryId = data.category_id;
    this.stock = Number(data.stock);
    this.isAvailable = Boolean(data.is_available);
    this.imageUrl = data.image_url || null;
    this.createdAt = data.created_at ? new Date(data.created_at) : null;
    this.updatedAt = data.updated_at ? new Date(data.updated_at) : null;
  }

  /**
   * Check if product is in stock
   * @returns {boolean}
   */
  isInStock() {
    return this.isAvailable && this.stock > 0;
  }

  /**
   * Check if product has low stock
   * @param {number} threshold - Low stock threshold (default: 10)
   * @returns {boolean}
   */
  hasLowStock(threshold = 10) {
    return this.isInStock() && this.stock < threshold;
  }

  /**
   * Calculate subtotal for given quantity
   * @param {number} quantity - Quantity
   * @returns {number} Subtotal
   */
  calculateSubtotal(quantity) {
    return this.price * quantity;
  }

  /**
   * Get formatted price
   * @returns {string} Formatted price
   */
  getFormattedPrice() {
    return formatPrice(this.price, this.currency);
  }

  /**
   * Get stock status text
   * @returns {string} Stock status
   */
  getStockStatus() {
    if (!this.isAvailable) {
      return 'Unavailable';
    }

    if (this.stock === 0) {
      return 'Out of stock';
    }

    if (this.hasLowStock()) {
      return `Only ${this.stock} left`;
    }

    return 'In stock';
  }

  /**
   * Get stock status color class
   * @returns {string} CSS class name
   */
  getStockStatusClass() {
    if (!this.isAvailable || this.stock === 0) {
      return 'text-error';
    }

    if (this.hasLowStock()) {
      return 'text-warning';
    }

    return 'text-success';
  }

  /**
   * Get truncated description
   * @param {number} maxLength - Maximum length
   * @returns {string} Truncated description
   */
  getShortDescription(maxLength = 150) {
    if (!this.description) {
      return '';
    }

    if (this.description.length <= maxLength) {
      return this.description;
    }

    return this.description.substr(0, maxLength - 3) + '...';
  }

  /**
   * Convert to plain object
   * @returns {Object} Plain object representation
   */
  toJSON() {
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      price: this.price,
      currency: this.currency,
      category_id: this.categoryId,
      stock: this.stock,
      is_available: this.isAvailable,
      image_url: this.imageUrl,
      created_at: this.createdAt?.toISOString() || null,
      updated_at: this.updatedAt?.toISOString() || null
    };
  }

  /**
   * Create Product from API response
   * @param {Object} data - API response data
   * @returns {Product} Product instance
   */
  static fromAPI(data) {
    return new Product(data);
  }

  /**
   * Create list of Products from API response
   * @param {Array} data - Array of API response data
   * @returns {Array<Product>} Array of Product instances
   */
  static fromAPIList(data) {
    return data.map(item => Product.fromAPI(item));
  }
}

export default Product;
