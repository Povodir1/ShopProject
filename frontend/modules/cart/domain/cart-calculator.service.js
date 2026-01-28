/**
 * Cart Calculator Service
 * Service for calculating cart totals
 */

export class CartCalculatorService {
  /**
   * Calculate total price of all items
   * @param {Array<CartItem>} items - Array of cart items
   * @returns {number} Total price
   */
  calculateTotal(items) {
    return items.reduce((sum, item) => {
      return sum + (Number(item.priceAtAdd) * Number(item.quantity));
    }, 0);
  }

  /**
   * Calculate total item count
   * @param {Array<CartItem>} items - Array of cart items
   * @returns {number} Total item count
   */
  calculateItemCount(items) {
    return items.reduce((sum, item) => {
      return sum + Number(item.quantity);
    }, 0);
  }

  /**
   * Calculate subtotal for a single item
   * @param {number} price - Price per unit
   * @param {number} quantity - Quantity
   * @returns {number} Subtotal
   */
  calculateItemSubtotal(price, quantity) {
    return Number(price) * Number(quantity);
  }

  /**
   * Calculate discount amount
   * @param {number} subtotal - Subtotal before discount
   * @param {number} discountPercent - Discount percentage (0-100)
   * @returns {number} Discount amount
   */
  calculateDiscount(subtotal, discountPercent) {
    return subtotal * (discountPercent / 100);
  }

  /**
   * Calculate tax amount
   * @param {number} subtotal - Subtotal before tax
   * @param {number} taxPercent - Tax percentage (0-100)
   * @returns {number} Tax amount
   */
  calculateTax(subtotal, taxPercent) {
    return subtotal * (taxPercent / 100);
  }

  /**
   * Calculate final total with discounts and tax
   * @param {number} subtotal - Base subtotal
   * @param {number} discountPercent - Discount percentage
   * @param {number} taxPercent - Tax percentage
   * @returns {Object} Calculation result
   */
  calculateFinalTotal(subtotal, discountPercent = 0, taxPercent = 0) {
    const discount = this.calculateDiscount(subtotal, discountPercent);
    const subtotalAfterDiscount = subtotal - discount;
    const tax = this.calculateTax(subtotalAfterDiscount, taxPercent);
    const total = subtotalAfterDiscount + tax;

    return {
      subtotal,
      discount,
      subtotalAfterDiscount,
      tax,
      total
    };
  }

  /**
   * Calculate savings from discounts
   * @param {Array<CartItem>} items - Array of cart items
   * @param {Object} currentPrices - Map of product_id -> current price
   * @returns {number} Total savings
   */
  calculateSavings(items, currentPrices) {
    return items.reduce((sum, item) => {
      const currentPrice = currentPrices[item.productId];
      if (currentPrice && currentPrice < item.priceAtAdd) {
        const savings = (item.priceAtAdd - currentPrice) * item.quantity;
        return sum + savings;
      }
      return sum;
    }, 0);
  }
}

export default CartCalculatorService;
