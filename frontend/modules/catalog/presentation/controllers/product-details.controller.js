/**
 * Product Details Controller
 * Manages product details page logic
 */

import { GetProductDetailsUseCase } from '../../application/use-cases/get-product-details.use-case.js';
import productAPI from '../../infrastructure/product-api.js';
import eventBus from '/core/event-bus.js';

export class ProductDetailsController {
  constructor() {
    // Initialize use cases
    this.getProductDetailsUseCase = new GetProductDetailsUseCase(productAPI);

    // State
    this.product = null;
    this.quantity = 1;
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
    await this.loadProduct();
  }

  /**
   * Cache DOM elements
   */
  cacheElements() {
    this.elements = {
      productDetails: document.querySelector('.product-details'),
      productImage: document.querySelector('.product-details-image'),
      productInfo: document.querySelector('.product-details-info'),
      addToCartForm: document.querySelector('.product-details-add-to-cart'),
      quantityInput: document.querySelector('.quantity-input'),
      loadingState: document.querySelector('.loading-state'),
      errorState: document.querySelector('.error-state')
    };
  }

  /**
   * Attach event listeners
   */
  attachEventListeners() {
    // Quantity controls
    const quantityDecrease = document.querySelector('.quantity-decrease');
    const quantityIncrease = document.querySelector('.quantity-increase');
    const quantityInput = this.elements.quantityInput;

    quantityDecrease?.addEventListener('click', () => this.changeQuantity(-1));
    quantityIncrease?.addEventListener('click', () => this.changeQuantity(1));
    quantityInput?.addEventListener('change', (e) => this.onQuantityChange(e));

    // Add to cart button
    const addToCartBtn = document.querySelector('.btn-add-to-cart');
    addToCartBtn?.addEventListener('click', () => this.addToCart());
  }

  /**
   * Load product from URL
   */
  async loadProduct() {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');

    if (!productId) {
      this.setError('Product ID is required');
      return;
    }

    try {
      this.setLoading(true);
      this.clearError();

      this.product = await this.getProductDetailsUseCase.execute(productId);
      this.render();

    } catch (error) {
      console.error('Failed to load product:', error);
      this.setError(error.message);
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Render product details
   */
  render() {
    if (!this.product || !this.elements.productDetails) return;

    // Render image
    if (this.elements.productImage) {
      const imageUrl = this.product.imageUrl || 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500"%3E%3Crect fill="%231e293b" width="500" height="500"/%3E%3Ctext fill="%2394a3b8" font-family="sans-serif" font-size="18" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E';

      this.elements.productImage.innerHTML = `
        <img src="${imageUrl}" alt="${this.escapeHtml(this.product.name)}" class="product-details-img">
      `;
    }

    // Render info
    if (this.elements.productInfo) {
      this.elements.productInfo.innerHTML = `
        <h1 class="product-details-name">${this.escapeHtml(this.product.name)}</h1>

        <div class="product-details-meta">
          <span class="product-details-price">${this.product.getFormattedPrice()}</span>
          <span class="product-details-stock ${this.product.getStockStatusClass()}">${this.product.getStockStatus()}</span>
        </div>

        <div class="product-details-description">
          <h3>Description</h3>
          <p>${this.escapeHtml(this.product.description) || 'No description available.'}</p>
        </div>

        <div class="product-details-specs">
          <div class="spec-item">
            <span class="spec-label">Availability:</span>
            <span class="spec-value ${this.product.getStockStatusClass()}">${this.product.getStockStatus()}</span>
          </div>

          ${this.product.stock > 0 ? `
            <div class="spec-item">
              <span class="spec-label">In Stock:</span>
              <span class="spec-value">${this.product.stock} items</span>
            </div>
          ` : ''}

          <div class="spec-item">
            <span class="spec-label">SKU:</span>
            <span class="spec-value">${this.product.id.substring(0, 8).toUpperCase()}</span>
          </div>
        </div>
      `;
    }

    // Update add to cart button state
    this.updateAddToCartButton();
  }

  /**
   * Change quantity
   * @param {number} delta - Quantity change
   */
  changeQuantity(delta) {
    const newQuantity = this.quantity + delta;

    if (newQuantity >= 1 && newQuantity <= (this.product?.stock || 100)) {
      this.quantity = newQuantity;
      this.updateQuantityDisplay();
    }
  }

  /**
   * Handle quantity input change
   * @param {Event} e - Input event
   */
  onQuantityChange(e) {
    let value = parseInt(e.target.value) || 1;

    // Validate
    if (value < 1) value = 1;
    if (this.product && value > this.product.stock) {
      value = this.product.stock;
    }

    this.quantity = value;
    this.updateQuantityDisplay();
  }

  /**
   * Update quantity display
   */
  updateQuantityDisplay() {
    if (this.elements.quantityInput) {
      this.elements.quantityInput.value = this.quantity;
    }

    // Update decrease button state
    const decreaseBtn = document.querySelector('.quantity-decrease');
    if (decreaseBtn) {
      decreaseBtn.disabled = this.quantity <= 1;
    }

    // Update increase button state
    const increaseBtn = document.querySelector('.quantity-increase');
    if (increaseBtn) {
      increaseBtn.disabled = this.product && this.quantity >= this.product.stock;
    }
  }

  /**
   * Add product to cart
   */
  addToCart() {
    if (!this.product || !this.product.isInStock()) {
      return;
    }

    // Publish add to cart event
    eventBus.publish('cart:add-item', {
      productId: this.product.id,
      quantity: this.quantity
    });

    // Show feedback
    this.showAddToCartFeedback();
  }

  /**
   * Show add to cart feedback
   */
  showAddToCartFeedback() {
    const button = document.querySelector('.btn-add-to-cart');

    if (button) {
      const originalText = button.textContent;
      const originalDisabled = button.disabled;

      button.textContent = 'Added!';
      button.disabled = true;

      setTimeout(() => {
        button.textContent = originalText;
        button.disabled = originalDisabled;
      }, 2000);
    }
  }

  /**
   * Update add to cart button state
   */
  updateAddToCartButton() {
    const button = document.querySelector('.btn-add-to-cart');

    if (button) {
      if (!this.product || !this.product.isInStock()) {
        button.textContent = 'Out of Stock';
        button.disabled = true;
        button.className = 'btn btn-secondary';
      } else {
        button.textContent = 'Add to Cart';
        button.disabled = false;
        button.className = 'btn btn-primary btn-large';
      }
    }

    // Update max quantity
    if (this.elements.quantityInput && this.product) {
      this.elements.quantityInput.max = this.product.stock;

      // Adjust current quantity if needed
      if (this.quantity > this.product.stock) {
        this.quantity = this.product.stock;
        this.updateQuantityDisplay();
      }
    }
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

    if (this.elements.productDetails) {
      this.elements.productDetails.style.display = loading ? 'none' : 'block';
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
        const errorElement = this.elements.errorState;
        errorElement.querySelector('.error-message').textContent = message;
        errorElement.style.display = 'flex';
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
   * Escape HTML to prevent XSS
   * @param {string} text - Text to escape
   * @returns {string} Escaped text
   */
  escapeHtml(text) {
    if (!text) return '';

    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Destroy the controller
   */
  destroy() {
    this.elements = {};
  }
}

export default ProductDetailsController;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const controller = new ProductDetailsController();
    controller.initialize().catch(error => {
      console.error('Failed to initialize product details controller:', error);
    });
  });
} else {
  const controller = new ProductDetailsController();
  controller.initialize().catch(error => {
    console.error('Failed to initialize product details controller:', error);
  });
}
