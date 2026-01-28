/**
 * Catalog Controller
 * Manages catalog page logic and component coordination
 */

import { GetProductsUseCase } from '../../application/use-cases/get-products.use-case.js';
import { GetCategoriesUseCase } from '../../application/use-cases/get-categories.use-case.js';
import { SearchProductsUseCase } from '../../application/use-cases/search-products.use-case.js';
import { FilterVO } from '../../domain/filter.value-object.js';
import productAPI from '../../infrastructure/product-api.js';
import categoryAPI from '../../infrastructure/category-api.js';
import { ProductCardComponent } from '../components/product-card.component.js';
import { CategoryTreeComponent } from '../components/category-tree.component.js';
import { SearchBarComponent } from '../components/search-bar.component.js';
import { ProductFilterComponent } from '../components/product-filter.component.js';
import eventBus from '/core/event-bus.js';
import config from '/core/config.js';

export class CatalogController {
  constructor() {
    // Initialize use cases
    this.getProductsUseCase = new GetProductsUseCase(productAPI);
    this.getCategoriesUseCase = new GetCategoriesUseCase(categoryAPI);
    this.searchProductsUseCase = new SearchProductsUseCase(productAPI);

    // State
    this.products = [];
    this.categories = [];
    this.currentFilter = new FilterVO();
    this.isLoading = false;
    this.error = null;

    // Components
    this.components = {};

    // DOM elements
    this.elements = {};
  }

  /**
   * Initialize the controller
   */
  async initialize() {
    this.cacheElements();
    this.attachEventListeners();
    await this.loadInitialData();
  }

  /**
   * Cache DOM elements
   */
  cacheElements() {
    this.elements = {
      productsGrid: document.querySelector('.products-grid'),
      categoryTree: document.querySelector('.category-tree-container'),
      searchBar: document.querySelector('.search-bar-container'),
      productFilter: document.querySelector('.product-filter-container'),
      loadingState: document.querySelector('.loading-state'),
      errorState: document.querySelector('.error-state'),
      emptyState: document.querySelector('.empty-state'),
      pagination: document.querySelector('.pagination'),
      cartBadge: document.querySelector('.cart-badge-container'),
      mainContent: document.querySelector('#main-content')
    };
  }

  /**
   * Attach event listeners
   */
  attachEventListeners() {
    // Listen to event bus
    eventBus.subscribe('catalog:category-changed', (data) => this.onCategoryChanged(data));
    eventBus.subscribe('catalog:search', (data) => this.onSearch(data));
    eventBus.subscribe('catalog:filter-changed', (data) => this.onFilterChanged(data));
    eventBus.subscribe('catalog:filter-reset', () => this.onFilterReset());
    eventBus.subscribe('cart:item-added', () => this.updateCartBadge());

    // Listen to popstate for back/forward navigation
    window.addEventListener('popstate', (e) => {
      this.loadProductsFromURL();
    });
  }

  /**
   * Load initial data
   */
  async loadInitialData() {
    try {
      this.setLoading(true);

      // Load categories and products in parallel
      const [categoriesResult, productsResult] = await Promise.allSettled([
        this.loadCategories(),
        this.loadProductsFromURL()
      ]);

      if (categoriesResult.status === 'rejected') {
        console.error('Failed to load categories:', categoriesResult.reason);
      }

      if (productsResult.status === 'rejected') {
        this.setError(productsResult.reason.message);
      }

      // Initialize components
      this.initializeComponents();
      this.updateCartBadge();

    } catch (error) {
      console.error('Failed to load initial data:', error);
      this.setError('Failed to load catalog. Please try again.');
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Load categories
   */
  async loadCategories() {
    this.categories = await this.getCategoriesUseCase.execute({ tree: true });

    // Initialize category tree component
    if (this.elements.categoryTree && this.categories.length > 0) {
      this.components.categoryTree = new CategoryTreeComponent(
        this.categories,
        this.elements.categoryTree,
        { selectedCategoryId: this.currentFilter.categoryId }
      );
      this.elements.categoryTree.appendChild(this.components.categoryTree.render());
    }
  }

  /**
   * Load products from URL query params
   */
  async loadProductsFromURL() {
    const urlParams = new URLSearchParams(window.location.search);

    const categoryId = urlParams.get('category') || null;
    const searchQuery = urlParams.get('q') || null;
    const page = parseInt(urlParams.get('page')) || 0;

    if (categoryId || searchQuery || page > 0) {
      this.currentFilter = this.currentFilter.withUpdates({
        categoryId,
        searchQuery,
        page
      });
    }

    await this.loadProducts();
  }

  /**
   * Load products with current filter
   */
  async loadProducts() {
    try {
      this.setLoading(true);
      this.clearError();

      const result = this.currentFilter.searchQuery
        ? await this.searchProductsUseCase.execute(this.currentFilter.searchQuery, {
            limit: this.currentFilter.limit,
            offset: this.currentFilter.page * this.currentFilter.limit
          })
        : await this.getProductsUseCase.execute(this.currentFilter);

      this.products = result.products;

      this.renderProducts();
      this.renderPagination(result);

      // Update URL
      this.updateURL();

    } catch (error) {
      console.error('Failed to load products:', error);
      this.setError(error.message);
      this.products = [];
      this.renderProducts();
      this.renderPagination(null);
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Initialize UI components
   */
  initializeComponents() {
    // Search bar
    if (this.elements.searchBar && !this.components.searchBar) {
      this.components.searchBar = new SearchBarComponent(this.elements.searchBar);
      this.elements.searchBar.appendChild(this.components.searchBar.render());
    }

    // Product filter
    if (this.elements.productFilter && !this.components.productFilter) {
      this.components.productFilter = new ProductFilterComponent(this.elements.productFilter);
      this.elements.productFilter.appendChild(this.components.productFilter.render());
    }
  }

  /**
   * Render products grid
   */
  renderProducts() {
    if (!this.elements.productsGrid) return;

    this.elements.productsGrid.innerHTML = '';

    if (this.products.length === 0) {
      this.showEmptyState();
      return;
    }

    this.hideEmptyState();

    this.products.forEach(product => {
      const card = new ProductCardComponent(product, this.elements.productsGrid);
      this.elements.productsGrid.appendChild(card.render());
    });
  }

  /**
   * Render pagination
   * @param {Object} result - Products result with pagination info
   */
  renderPagination(result) {
    if (!this.elements.pagination) return;

    this.elements.pagination.innerHTML = '';

    if (!result || result.total <= this.currentFilter.limit) {
      this.elements.pagination.style.display = 'none';
      return;
    }

    this.elements.pagination.style.display = 'flex';

    const totalPages = Math.ceil(result.total / this.currentFilter.limit);
    const currentPage = this.currentFilter.page;

    // Previous button
    const prevBtn = this.createPaginationButton('Previous', currentPage > 0, () => {
      this.goToPage(currentPage - 1);
    });
    this.elements.pagination.appendChild(prevBtn);

    // Page numbers
    const pageNumbers = this.getPageNumbers(currentPage, totalPages);
    pageNumbers.forEach(pageNum => {
      if (pageNum === '...') {
        const ellipsis = document.createElement('span');
        ellipsis.className = 'pagination-ellipsis';
        ellipsis.textContent = '...';
        this.elements.pagination.appendChild(ellipsis);
      } else {
        const pageBtn = this.createPaginationButton(
          pageNum + 1,
          true,
          () => this.goToPage(pageNum),
          pageNum === currentPage
        );
        this.elements.pagination.appendChild(pageBtn);
      }
    });

    // Next button
    const nextBtn = this.createPaginationButton('Next', result.hasMore, () => {
      this.goToPage(currentPage + 1);
    });
    this.elements.pagination.appendChild(nextBtn);
  }

  /**
   * Create pagination button
   * @param {string} text - Button text
   * @param {boolean} enabled - Whether button is enabled
   * @param {Function} onClick - Click handler
   * @param {boolean} isActive - Whether page is active
   * @returns {HTMLElement} Button element
   */
  createPaginationButton(text, enabled, onClick, isActive = false) {
    const button = document.createElement('button');
    button.className = `btn btn-small pagination-button ${isActive ? 'btn-primary' : 'btn-ghost'}`;
    button.textContent = text;
    button.disabled = !enabled;

    if (enabled) {
      button.addEventListener('click', onClick);
    }

    return button;
  }

  /**
   * Get page numbers for pagination
   * @param {number} currentPage - Current page
   * @param {number} totalPages - Total pages
   * @returns {Array<number|string>} Page numbers
   */
  getPageNumbers(currentPage, totalPages) {
    const pages = [];
    const showPages = 5;

    if (totalPages <= showPages) {
      for (let i = 0; i < totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(0);

      let start = Math.max(1, currentPage - 1);
      let end = Math.min(totalPages - 2, currentPage + 1);

      if (currentPage <= 1) {
        end = 3;
      } else if (currentPage >= totalPages - 2) {
        start = totalPages - 4;
      }

      if (start > 1) {
        pages.push('...');
      }

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (end < totalPages - 2) {
        pages.push('...');
      }

      // Always show last page
      pages.push(totalPages - 1);
    }

    return pages;
  }

  /**
   * Go to specific page
   * @param {number} page - Page number
   */
  goToPage(page) {
    if (page < 0) return;

    this.currentFilter = this.currentFilter.setPage(page);
    this.loadProducts();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /**
   * Handle category change
   * @param {Object} data - Event data
   */
  onCategoryChanged(data) {
    this.currentFilter = this.currentFilter.setCategory(data.categoryId);
    this.loadProducts();
  }

  /**
   * Handle search
   * @param {Object} data - Event data
   */
  onSearch(data) {
    this.currentFilter = this.currentFilter.setSearch(data.query);
    this.loadProducts();
  }

  /**
   * Handle filter change
   * @param {Object} data - Event data
   */
  onFilterChanged(data) {
    this.currentFilter = new FilterVO({
      ...this.currentFilter.toJSON(),
      ...data
    });
    this.loadProducts();
  }

  /**
   * Handle filter reset
   */
  onFilterReset() {
    // Keep category but reset other filters
    this.currentFilter = new FilterVO({
      categoryId: this.currentFilter.categoryId
    });
    this.loadProducts();
  }

  /**
   * Update URL with current filter
   */
  updateURL() {
    const params = new URLSearchParams();

    if (this.currentFilter.categoryId) {
      params.set('category', this.currentFilter.categoryId);
    }

    if (this.currentFilter.searchQuery) {
      params.set('q', this.currentFilter.searchQuery);
    }

    if (this.currentFilter.page > 0) {
      params.set('page', this.currentFilter.page);
    }

    const url = params.toString()
      ? `${window.location.pathname}?${params.toString()}`
      : window.location.pathname;

    window.history.replaceState({}, '', url);
  }

  /**
   * Update cart badge
   */
  async updateCartBadge() {
    if (!this.elements.cartBadge) return;

    // This will be handled by cart module
    // Just emit event to request cart update
    eventBus.publish('cart:request-update');
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

    if (this.elements.mainContent) {
      this.elements.mainContent.style.display = loading ? 'none' : 'block';
    }

    if (this.elements.productsGrid) {
      this.elements.productsGrid.style.opacity = loading ? '0.5' : '1';
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
   * Show empty state
   */
  showEmptyState() {
    if (this.elements.emptyState) {
      this.elements.emptyState.style.display = 'flex';
    }
  }

  /**
   * Hide empty state
   */
  hideEmptyState() {
    if (this.elements.emptyState) {
      this.elements.emptyState.style.display = 'none';
    }
  }

  /**
   * Destroy the controller
   */
  destroy() {
    // Destroy components
    Object.values(this.components).forEach(component => {
      if (component && component.destroy) {
        component.destroy();
      }
    });

    this.components = {};
    this.elements = {};
  }
}

export default CatalogController;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const controller = new CatalogController();
    controller.initialize().catch(error => {
      console.error('Failed to initialize catalog controller:', error);
    });
  });
} else {
  // DOM is already ready
  const controller = new CatalogController();
  controller.initialize().catch(error => {
    console.error('Failed to initialize catalog controller:', error);
  });
}
