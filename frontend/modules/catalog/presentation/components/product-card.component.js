/**
 * Product Card Component
 * Displays product information in card format
 */

import eventBus from '/core/event-bus.js';

export class ProductCardComponent {
  /**
   * @param {Product} product - Product entity
   * @param {HTMLElement} container - Container element
   * @param {Object} options - Component options
   */
  constructor(product, container, options = {}) {
    this.product = product;
    this.container = container;
    this.options = {
      showAddToCart: true,
      showViewDetails: true,
      ...options
    };
    this.element = null;
  }

  /**
   * Render the product card
   * @returns {HTMLElement} Card element
   */
  render() {
    const card = document.createElement('article');
    card.className = 'card card-clickable product-card';
    card.dataset.productId = this.product.id;

    const imageUrl = this.product.imageUrl || 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="280" height="200" viewBox="0 0 280 200"%3E%3Crect fill="%231e293b" width="280" height="200"/%3E%3Ctext fill="%2394a3b8" font-family="sans-serif" font-size="14" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E';

    card.innerHTML = `
      <div class="product-card-image">
        <img src="${imageUrl}" alt="${this.escapeHtml(this.product.name)}" loading="lazy">
        ${!this.product.isInStock() ? '<div class="product-card-badge">Out of Stock</div>' : ''}
        ${this.product.hasLowStock() ? '<div class="product-card-badge product-card-badge-warning">Low Stock</div>' : ''}
      </div>

      <div class="product-card-content">
        <h3 class="product-card-title">${this.escapeHtml(this.product.name)}</h3>
        <p class="product-card-description">${this.escapeHtml(this.product.getShortDescription(100))}</p>

        <div class="product-card-meta">
          <span class="product-card-price">${this.product.getFormattedPrice()}</span>
          <span class="product-card-stock ${this.product.getStockStatusClass()}">${this.product.getStockStatus()}</span>
        </div>

        <div class="product-card-actions">
          ${this.options.showViewDetails ? `
            <button type="button" class="btn btn-secondary btn-small product-card-view-details" data-product-id="${this.product.id}">
              View Details
            </button>
          ` : ''}

          ${this.options.showAddToCart ? `
            <button type="button" class="btn btn-primary btn-small product-card-add-to-cart ${!this.product.isInStock() ? 'btn-disabled' : ''}" data-product-id="${this.product.id}" ${!this.product.isInStock() ? 'disabled' : ''}>
              ${this.product.isInStock() ? 'Add to Cart' : 'Unavailable'}
            </button>
          ` : ''}
        </div>
      </div>
    `;

    this.attachEventListeners(card);
    this.element = card;
    return card;
  }

  /**
   * Attach event listeners to card elements
   * @param {HTMLElement} card - Card element
   */
  attachEventListeners(card) {
    // View details button
    const viewDetailsBtn = card.querySelector('.product-card-view-details');
    if (viewDetailsBtn) {
      viewDetailsBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.onViewDetails();
      });
    }

    // Add to cart button
    const addToCartBtn = card.querySelector('.product-card-add-to-cart');
    if (addToCartBtn) {
      addToCartBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.onAddToCart();
      });
    }

    // Card click (navigate to details)
    if (this.options.showViewDetails) {
      card.addEventListener('click', () => {
        this.onViewDetails();
      });
    }
  }

  /**
   * Handle view details click
   */
  onViewDetails() {
    eventBus.publish('catalog:product-selected', {
      productId: this.product.id,
      product: this.product
    });

    // Navigate to product details page
    const detailsUrl = `/modules/catalog/presentation/pages/product-details.html?id=${this.product.id}`;
    window.location.href = detailsUrl;
  }

  /**
   * Handle add to cart click
   */
  onAddToCart() {
    eventBus.publish('cart:add-item', {
      productId: this.product.id,
      product: this.product,
      quantity: 1
    });
  }

  /**
   * Escape HTML to prevent XSS
   * @param {string} text - Text to escape
   * @returns {string} Escaped text
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Update product data and re-render
   * @param {Product} product - Updated product entity
   */
  update(product) {
    this.product = product;

    if (this.element && this.element.parentNode) {
      const newElement = this.render();
      this.element.parentNode.replaceChild(newElement, this.element);
      this.element = newElement;
    }
  }

  /**
   * Destroy the component
   */
  destroy() {
    if (this.element && this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
    this.element = null;
  }
}

export default ProductCardComponent;
