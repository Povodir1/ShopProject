/**
 * Product Filter Component
 * Product filtering sidebar controls
 */

import eventBus from '/core/event-bus.js';

export class ProductFilterComponent {
  /**
   * @param {HTMLElement} container - Container element
   * @param {Object} options - Component options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      showPriceFilter: true,
      showStockFilter: true,
      showSortOptions: true,
      ...options
    };
    this.element = null;
    this.filters = {
      priceMin: null,
      priceMax: null,
      inStock: false,
      sortBy: 'created_at',
      sortOrder: 'desc'
    };
  }

  /**
   * Render the product filter
   * @returns {HTMLElement} Filter element
   */
  render() {
    const wrapper = document.createElement('aside');
    wrapper.className = 'product-filter';

    const title = document.createElement('h3');
    title.className = 'product-filter-title';
    title.textContent = 'Filters';

    wrapper.appendChild(title);

    // Price filter
    if (this.options.showPriceFilter) {
      wrapper.appendChild(this.renderPriceFilter());
    }

    // Stock filter
    if (this.options.showStockFilter) {
      wrapper.appendChild(this.renderStockFilter());
    }

    // Sort options
    if (this.options.showSortOptions) {
      wrapper.appendChild(this.renderSortOptions());
    }

    // Actions
    const actions = this.renderActions();
    wrapper.appendChild(actions);

    this.attachEventListeners(wrapper);
    this.element = wrapper;
    return wrapper;
  }

  /**
   * Render price filter
   * @returns {HTMLElement} Price filter element
   */
  renderPriceFilter() {
    const section = document.createElement('div');
    section.className = 'product-filter-section';

    const label = document.createElement('label');
    label.className = 'product-filter-label';
    label.textContent = 'Price Range';

    const inputs = document.createElement('div');
    inputs.className = 'product-filter-price';

    const minInput = document.createElement('input');
    minInput.type = 'number';
    minInput.className = 'input input-small product-filter-price-min';
    minInput.placeholder = 'Min';
    minInput.min = '0';
    minInput.step = '0.01';
    minInput.setAttribute('aria-label', 'Minimum price');

    const separator = document.createElement('span');
    separator.className = 'product-filter-price-separator';
    separator.textContent = '—';

    const maxInput = document.createElement('input');
    maxInput.type = 'number';
    maxInput.className = 'input input-small product-filter-price-max';
    maxInput.placeholder = 'Max';
    maxInput.min = '0';
    maxInput.step = '0.01';
    maxInput.setAttribute('aria-label', 'Maximum price');

    inputs.appendChild(minInput);
    inputs.appendChild(separator);
    inputs.appendChild(maxInput);

    section.appendChild(label);
    section.appendChild(inputs);

    return section;
  }

  /**
   * Render stock filter
   * @returns {HTMLElement} Stock filter element
   */
  renderStockFilter() {
    const section = document.createElement('div');
    section.className = 'product-filter-section';

    const label = document.createElement('label');
    label.className = 'product-filter-checkbox-label';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'product-filter-checkbox';
    checkbox.id = 'filter-in-stock';
    checkbox.setAttribute('aria-label', 'Show only in stock items');

    const text = document.createElement('span');
    text.textContent = 'In Stock Only';

    label.appendChild(checkbox);
    label.appendChild(text);

    section.appendChild(label);

    return section;
  }

  /**
   * Render sort options
   * @returns {HTMLElement} Sort options element
   */
  renderSortOptions() {
    const section = document.createElement('div');
    section.className = 'product-filter-section';

    const label = document.createElement('label');
    label.className = 'product-filter-label';
    label.textContent = 'Sort By';

    const select = document.createElement('select');
    select.className = 'input input-small product-filter-sort';
    select.setAttribute('aria-label', 'Sort products by');

    const options = [
      { value: 'created_at-desc', label: 'Newest First' },
      { value: 'created_at-asc', label: 'Oldest First' },
      { value: 'name-asc', label: 'Name: A to Z' },
      { value: 'name-desc', label: 'Name: Z to A' },
      { value: 'price-asc', label: 'Price: Low to High' },
      { value: 'price-desc', label: 'Price: High to Low' }
    ];

    options.forEach(opt => {
      const option = document.createElement('option');
      option.value = opt.value;
      option.textContent = opt.label;

      const [sortBy, sortOrder] = opt.value.split('-');
      if (sortBy === this.filters.sortBy && sortOrder === this.filters.sortOrder) {
        option.selected = true;
      }

      select.appendChild(option);
    });

    section.appendChild(label);
    section.appendChild(select);

    return section;
  }

  /**
   * Render action buttons
   * @returns {HTMLElement} Actions element
   */
  renderActions() {
    const actions = document.createElement('div');
    actions.className = 'product-filter-actions';

    const applyBtn = document.createElement('button');
    applyBtn.type = 'button';
    applyBtn.className = 'btn btn-primary btn-small product-filter-apply';
    applyBtn.textContent = 'Apply Filters';

    const resetBtn = document.createElement('button');
    resetBtn.type = 'button';
    resetBtn.className = 'btn btn-ghost btn-small product-filter-reset';
    resetBtn.textContent = 'Reset';

    actions.appendChild(applyBtn);
    actions.appendChild(resetBtn);

    return actions;
  }

  /**
   * Attach event listeners
   * @param {HTMLElement} wrapper - Wrapper element
   */
  attachEventListeners(wrapper) {
    // Price inputs
    const minInput = wrapper.querySelector('.product-filter-price-min');
    const maxInput = wrapper.querySelector('.product-filter-price-max');

    minInput?.addEventListener('input', () => this.onPriceChange());
    maxInput?.addEventListener('input', () => this.onPriceChange());

    // Stock checkbox
    const stockCheckbox = wrapper.querySelector('.product-filter-checkbox');
    stockCheckbox?.addEventListener('change', (e) => {
      this.filters.inStock = e.target.checked;
    });

    // Sort select
    const sortSelect = wrapper.querySelector('.product-filter-sort');
    sortSelect?.addEventListener('change', (e) => {
      const [sortBy, sortOrder] = e.target.value.split('-');
      this.filters.sortBy = sortBy;
      this.filters.sortOrder = sortOrder;
      this.applyFilters();
    });

    // Apply button
    const applyBtn = wrapper.querySelector('.product-filter-apply');
    applyBtn?.addEventListener('click', () => this.applyFilters());

    // Reset button
    const resetBtn = wrapper.querySelector('.product-filter-reset');
    resetBtn?.addEventListener('click', () => this.resetFilters());
  }

  /**
   * Handle price input change
   */
  onPriceChange() {
    const minInput = this.element.querySelector('.product-filter-price-min');
    const maxInput = this.element.querySelector('.product-filter-price-max');

    const min = minInput.value ? parseFloat(minInput.value) : null;
    const max = maxInput.value ? parseFloat(maxInput.value) : null;

    // Validate min < max
    if (min !== null && max !== null && min > max) {
      maxInput.setCustomValidity('Maximum price must be greater than minimum');
    } else {
      maxInput.setCustomValidity('');
    }

    this.filters.priceMin = min;
    this.filters.priceMax = max;
  }

  /**
   * Apply filters
   */
  applyFilters() {
    // Don't apply if min > max
    if (this.filters.priceMin !== null &&
        this.filters.priceMax !== null &&
        this.filters.priceMin > this.filters.priceMax) {
      return;
    }

    eventBus.publish('catalog:filter-changed', {
      priceRange: {
        min: this.filters.priceMin,
        max: this.filters.priceMax
      },
      inStock: this.filters.inStock,
      sortBy: this.filters.sortBy,
      sortOrder: this.filters.sortOrder
    });
  }

  /**
   * Reset filters to defaults
   */
  resetFilters() {
    this.filters = {
      priceMin: null,
      priceMax: null,
      inStock: false,
      sortBy: 'created_at',
      sortOrder: 'desc'
    };

    // Reset UI
    const minInput = this.element.querySelector('.product-filter-price-min');
    const maxInput = this.element.querySelector('.product-filter-price-max');
    const stockCheckbox = this.element.querySelector('.product-filter-checkbox');
    const sortSelect = this.element.querySelector('.product-filter-sort');

    if (minInput) minInput.value = '';
    if (maxInput) {
      maxInput.value = '';
      maxInput.setCustomValidity('');
    }
    if (stockCheckbox) stockCheckbox.checked = false;
    if (sortSelect) sortSelect.value = 'created_at-desc';

    // Publish reset event
    eventBus.publish('catalog:filter-reset');
  }

  /**
   * Update the component
   * @param {Object} filters - New filter values
   */
  update(filters) {
    if (filters.priceRange) {
      this.filters.priceMin = filters.priceRange.min;
      this.filters.priceMax = filters.priceRange.max;

      const minInput = this.element.querySelector('.product-filter-price-min');
      const maxInput = this.element.querySelector('.product-filter-price-max');

      if (minInput) minInput.value = filters.priceRange.min || '';
      if (maxInput) maxInput.value = filters.priceRange.max || '';
    }

    if (filters.inStock !== undefined) {
      this.filters.inStock = filters.inStock;

      const stockCheckbox = this.element.querySelector('.product-filter-checkbox');
      if (stockCheckbox) stockCheckbox.checked = filters.inStock;
    }

    if (filters.sortBy && filters.sortOrder) {
      this.filters.sortBy = filters.sortBy;
      this.filters.sortOrder = filters.sortOrder;

      const sortSelect = this.element.querySelector('.product-filter-sort');
      if (sortSelect) sortSelect.value = `${filters.sortBy}-${filters.sortOrder}`;
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

export default ProductFilterComponent;
