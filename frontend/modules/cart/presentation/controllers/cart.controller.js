/**
 * Cart Controller
 * Manages cart page logic
 */

import { GetCartUseCase } from '../../application/use-cases/get-cart.use-case.js';
import { RemoveItemUseCase } from '../../application/use-cases/remove-item.use-case.js';
import { UpdateQuantityUseCase } from '../../application/use-cases/update-quantity.use-case.js';
import { ClearCartUseCase } from '../../application/use-cases/clear-cart.use-case.js';
import cartAPI from '../../infrastructure/cart-api.js';
import cartStorage from '../../infrastructure/cart-storage.js';
import eventBus from '/core/event-bus.js';

export class CartController {
  constructor() {
    // Get or create session ID
    this.sessionId = cartStorage.getOrCreateSessionId();

    // Initialize use cases
    this.getCartUseCase = new GetCartUseCase(cartAPI, cartStorage);
    this.removeItemUseCase = new RemoveItemUseCase(cartAPI, cartStorage, eventBus);
    this.updateQuantityUseCase = new UpdateQuantityUseCase(cartAPI, cartStorage, eventBus);
    this.clearCartUseCase = new ClearCartUseCase(cartAPI, cartStorage, eventBus);

    // State
    this.cart = null;
    this.isLoading = false;
    this.error = null;

    // DOM elements
    this.elements = {};
  }

  /**
   * Initialize the controller
   */
  async initialize() {
    this.cacheElements();
    this.attachEventListeners();
    await this.loadCart();

    // Listen for cart updates from other pages
    eventBus.subscribe('cart:request-update', () => this.loadCart());
    eventBus.subscribe('cart:request-count', () => this.publishCartCount());
  }

  /**
   * Cache DOM elements
   */
  cacheElements() {
    this.elements = {
      cartContent: document.querySelector('.cart-content'),
      cartItems: document.querySelector('.cart-items'),
      cartSummary: document.querySelector('.cart-summary'),
      emptyCart: document.querySelector('.empty-cart'),
      loadingState: document.querySelector('.loading-state'),
      errorState: document.querySelector('.error-state'),
      clearCartBtn: document.querySelector('.btn-clear-cart'),
      checkoutBtn: document.querySelector('.btn-checkout'),
      continueShoppingBtn: document.querySelector('.btn-continue-shopping')
    };
  }

  /**
   * Attach event listeners
   */
  attachEventListeners() {
    // Clear cart button
    this.elements.clearCartBtn?.addEventListener('click', () => this.clearCart());

    // Continue shopping button
    this.elements.continueShoppingBtn?.addEventListener('click', () => {
      window.location.href = '/modules/catalog/presentation/pages/catalog.html';
    });

    // Checkout button (placeholder)
    this.elements.checkoutBtn?.addEventListener('click', () => {
      alert('Checkout functionality would be implemented here');
    });
  }

  /**
   * Load cart
   */
  async loadCart() {
    try {
      this.setLoading(true);
      this.clearError();

      this.cart = await this.getCartUseCase.execute(this.sessionId);
      this.render();

    } catch (error) {
      console.error('Failed to load cart:', error);
      this.setError(error.message);
      this.cart = null;
      this.render();
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Render cart
   */
  render() {
    if (!this.cart) {
      this.showEmptyCart();
      return;
    }

    if (this.cart.isEmpty()) {
      this.showEmptyCart();
      return;
    }

    this.hideEmptyCart();
    this.renderCartItems();
    this.renderCartSummary();
  }

  /**
   * Render cart items
   */
  renderCartItems() {
    if (!this.elements.cartItems) return;

    this.elements.cartItems.innerHTML = '';

    this.cart.getAllItems().forEach(item => {
      const itemElement = this.createCartItemElement(item);
      this.elements.cartItems.appendChild(itemElement);
    });
  }

  /**
   * Create cart item element
   * @param {CartItem} item - Cart item entity
   * @returns {HTMLElement} Item element
   */
  createCartItemElement(item) {
    const div = document.createElement('div');
    div.className = 'cart-item';
    div.dataset.itemId = item.id;

    div.innerHTML = `
      <div class="cart-item-image">
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Crect fill='%231e293b' width='80' height='80'/%3E%3Ctext fill='%2394a3b8' font-family='sans-serif' font-size='12' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3EProduct%3C/text%3E%3C/svg%3E" alt="Product">
      </div>

      <div class="cart-item-info">
        <h3 class="cart-item-name">Product ID: ${item.productId.substring(0, 8)}...</h3>
        <p class="cart-item-price">${item.getFormattedPrice()} each</p>
      </div>

      <div class="cart-item-quantity">
        <button type="button" class="btn btn-ghost btn-icon cart-item-decrease" data-item-id="${item.id}" aria-label="Decrease quantity">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
        <input type="number" class="input cart-item-quantity-input" value="${item.quantity}" min="1" max="100" data-item-id="${item.id}" aria-label="Quantity">
        <button type="button" class="btn btn-ghost btn-icon cart-item-increase" data-item-id="${item.id}" aria-label="Increase quantity">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
      </div>

      <div class="cart-item-subtotal">
        <span class="cart-item-subtotal-amount">${item.getFormattedSubtotal()}</span>
      </div>

      <div class="cart-item-actions">
        <button type="button" class="btn btn-ghost btn-icon cart-item-remove" data-item-id="${item.id}" aria-label="Remove item">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      </div>
    `;

    // Add event listeners
    const decreaseBtn = div.querySelector('.cart-item-decrease');
    const increaseBtn = div.querySelector('.cart-item-increase');
    const quantityInput = div.querySelector('.cart-item-quantity-input');
    const removeBtn = div.querySelector('.cart-item-remove');

    decreaseBtn.addEventListener('click', () => this.changeQuantity(item.id, -1));
    increaseBtn.addEventListener('click', () => this.changeQuantity(item.id, 1));
    quantityInput.addEventListener('change', (e) => this.onQuantityInputChange(item.id, e));
    removeBtn.addEventListener('click', () => this.removeItem(item.id));

    return div;
  }

  /**
   * Render cart summary
   */
  renderCartSummary() {
    if (!this.elements.cartSummary || !this.cart) return;

    this.elements.cartSummary.innerHTML = `
      <h3 class="cart-summary-title">Order Summary</h3>

      <div class="cart-summary-row">
        <span class="cart-summary-label">Subtotal (${this.cart.itemCount} items)</span>
        <span class="cart-summary-value">${this.cart.getFormattedTotal()}</span>
      </div>

      <div class="cart-summary-row">
        <span class="cart-summary-label">Shipping</span>
        <span class="cart-summary-value">Calculated at checkout</span>
      </div>

      <div class="cart-summary-row">
        <span class="cart-summary-label">Tax</span>
        <span class="cart-summary-value">Calculated at checkout</span>
      </div>

      <hr class="cart-summary-divider">

      <div class="cart-summary-row cart-summary-total">
        <span class="cart-summary-label">Total</span>
        <span class="cart-summary-value cart-summary-total-amount">${this.cart.getFormattedTotal()}</span>
      </div>

      <div class="cart-summary-actions">
        <button type="button" class="btn btn-primary btn-large btn-checkout">Proceed to Checkout</button>
        <button type="button" class="btn btn-ghost cart-clear-cart-btn">Clear Cart</button>
      </div>

      <a href="/modules/catalog/presentation/pages/catalog.html" class="btn btn-secondary btn-large btn-continue-shopping">Continue Shopping</a>
    `;

    // Re-attach event listeners for new buttons
    const clearBtn = this.elements.cartSummary.querySelector('.cart-clear-cart-btn');
    clearBtn?.addEventListener('click', () => this.clearCart());
  }

  /**
   * Change item quantity
   * @param {string} itemId - Item ID
   * @param {number} delta - Quantity change
   */
  async changeQuantity(itemId, delta) {
    const item = this.cart?.getItemById(itemId);
    if (!item) return;

    const newQuantity = item.quantity + delta;

    if (newQuantity < 1) {
      await this.removeItem(itemId);
    } else if (newQuantity <= 100) {
      await this.updateQuantity(itemId, newQuantity);
    }
  }

  /**
   * Handle quantity input change
   * @param {string} itemId - Item ID
   * @param {Event} e - Input event
   */
  async onQuantityInputChange(itemId, e) {
    let quantity = parseInt(e.target.value) || 1;

    if (quantity < 1) quantity = 1;
    if (quantity > 100) quantity = 100;

    e.target.value = quantity;

    await this.updateQuantity(itemId, quantity);
  }

  /**
   * Update item quantity
   * @param {string} itemId - Item ID
   * @param {number} quantity - New quantity
   */
  async updateQuantity(itemId, quantity) {
    try {
      this.cart = await this.updateQuantityUseCase.execute(this.sessionId, itemId, quantity);
      this.render();
    } catch (error) {
      console.error('Failed to update quantity:', error);
    }
  }

  /**
   * Remove item from cart
   * @param {string} itemId - Item ID
   */
  async removeItem(itemId) {
    if (!confirm('Remove this item from cart?')) return;

    try {
      this.cart = await this.removeItemUseCase.execute(this.sessionId, itemId);
      this.render();
    } catch (error) {
      console.error('Failed to remove item:', error);
    }
  }

  /**
   * Clear cart
   */
  async clearCart() {
    if (!confirm('Are you sure you want to clear your cart?')) return;

    try {
      this.cart = await this.clearCartUseCase.execute(this.sessionId);
      this.render();
    } catch (error) {
      console.error('Failed to clear cart:', error);
    }
  }

  /**
   * Publish cart count for badges
   */
  publishCartCount() {
    eventBus.publish('cart:count-updated', {
      count: this.cart?.itemCount || 0
    });
  }

  /**
   * Set loading state
   * @param {boolean} loading - Loading state
   */
  setLoading(loading) {
    this.isLoading = loading;

    if (this.elements.loadingState) {
      this.elements.loadingState.style.display = loading ? 'flex' : 'none';
    }

    if (this.elements.cartContent) {
      this.elements.cartContent.style.opacity = loading ? '0.5' : '1';
    }
  }

  /**
   * Set error state
   * @param {string} message - Error message
   */
  setError(message) {
    this.error = message;

    if (this.elements.errorState) {
      if (message) {
        this.elements.errorState.querySelector('.error-message').textContent = message;
        this.elements.errorState.style.display = 'flex';
      } else {
        this.elements.errorState.style.display = 'none';
      }
    }
  }

  /**
   * Clear error state
   */
  clearError() {
    this.setError(null);
  }

  /**
   * Show empty cart
   */
  showEmptyCart() {
    if (this.elements.cartContent) {
      this.elements.cartContent.style.display = 'none';
    }
    if (this.elements.emptyCart) {
      this.elements.emptyCart.style.display = 'flex';
    }
  }

  /**
   * Hide empty cart
   */
  hideEmptyCart() {
    if (this.elements.cartContent) {
      this.elements.cartContent.style.display = 'block';
    }
    if (this.elements.emptyCart) {
      this.elements.emptyCart.style.display = 'none';
    }
  }

  /**
   * Destroy the controller
   */
  destroy() {
    this.elements = {};
  }
}

export default CartController;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const controller = new CartController();
    controller.initialize().catch(error => {
      console.error('Failed to initialize cart controller:', error);
    });
  });
} else {
  const controller = new CartController();
  controller.initialize().catch(error => {
    console.error('Failed to initialize cart controller:', error);
  });
}
