/**
 * Filter Value Object
 * Encapsulates product filtering logic
 */

import { validateQuantity } from '/core/shared/validators.js';
import config from '/core/config.js';

export class FilterVO {
  /**
   * @param {Object} filters - Filter options
   * @param {string|null} filters.categoryId - Category ID to filter by
   * @param {string|null} filters.searchQuery - Search query string
   * @param {Object|null} filters.priceRange - Price range { min, max }
   * @param {string} filters.sortBy - Sort field (name, price, created_at)
   * @param {string} filters.sortOrder - Sort order (asc, desc)
   * @param {number} filters.page - Page number
   * @param {number} filters.limit - Items per page
   * @param {boolean} filters.inStock - Only show items in stock
   */
  constructor(filters = {}) {
    const defaults = {
      categoryId: null,
      searchQuery: null,
      priceRange: null,
      sortBy: 'created_at',
      sortOrder: 'desc',
      page: 0,
      limit: config.pagination.defaultLimit,
      inStock: false
    };

    Object.assign(this, defaults, filters);
    this.validate();
  }

  /**
   * Validate filter values
   * @throws {Error} If validation fails
   */
  validate() {
    // Validate page
    if (this.page < 0) {
      throw new Error('Page cannot be negative');
    }

    // Validate limit
    const limitValidation = validateQuantity(this.limit, {
      min: 1,
      max: config.pagination.maxLimit
    });

    if (!limitValidation.isValid) {
      throw new Error(limitValidation.error);
    }

    // Validate price range
    if (this.priceRange) {
      if (this.priceRange.min != null && this.priceRange.min < 0) {
        throw new Error('Minimum price cannot be negative');
      }

      if (this.priceRange.max != null && this.priceRange.max < 0) {
        throw new Error('Maximum price cannot be negative');
      }

      if (
        this.priceRange.min != null &&
        this.priceRange.max != null &&
        this.priceRange.min > this.priceRange.max
      ) {
        throw new Error('Minimum price cannot be greater than maximum price');
      }
    }

    // Validate sort order
    const validSortOrders = ['asc', 'desc'];
    if (!validSortOrders.includes(this.sortOrder)) {
      throw new Error(`Invalid sort order. Must be one of: ${validSortOrders.join(', ')}`);
    }

    // Validate search query length
    if (this.searchQuery && this.searchQuery.length < 2) {
      throw new Error('Search query must be at least 2 characters');
    }
  }

  /**
   * Convert to query parameters for API
   * @returns {Object} Query parameters object
   */
  toQueryParams() {
    const params = {
      offset: this.page * this.limit,
      limit: this.limit
    };

    if (this.categoryId) {
      params.category_id = this.categoryId;
    }

    if (this.searchQuery) {
      params.q = this.searchQuery;
    }

    if (this.priceRange) {
      if (this.priceRange.min != null) {
        params.price_min = this.priceRange.min;
      }

      if (this.priceRange.max != null) {
        params.price_max = this.priceRange.max;
      }
    }

    if (this.sortBy) {
      params.order_by = this.sortBy;
      params.order_dir = this.sortOrder;
    }

    if (this.inStock) {
      params.in_stock = true;
    }

    return params;
  }

  /**
   * Create a new filter with updated values
   * @param {Object} updates - Values to update
   * @returns {FilterVO} New filter instance
   */
  withUpdates(updates) {
    return new FilterVO({
      categoryId: this.categoryId,
      searchQuery: this.searchQuery,
      priceRange: this.priceRange,
      sortBy: this.sortBy,
      sortOrder: this.sortOrder,
      page: this.page,
      limit: this.limit,
      inStock: this.inStock,
      ...updates
    });
  }

  /**
   * Reset to default values
   * @returns {FilterVO} New filter instance with defaults
   */
  reset() {
    return new FilterVO();
  }

  /**
   * Go to next page
   * @returns {FilterVO} New filter with incremented page
   */
  nextPage() {
    return this.withUpdates({ page: this.page + 1 });
  }

  /**
   * Go to previous page
   * @returns {FilterVO} New filter with decremented page
   */
  previousPage() {
    return this.withUpdates({ page: Math.max(0, this.page - 1) });
  }

  /**
   * Set page number
   * @param {number} page - Page number
   * @returns {FilterVO} New filter with set page
   */
  setPage(page) {
    return this.withUpdates({ page: Math.max(0, page) });
  }

  /**
   * Set category filter
   * @param {string|null} categoryId - Category ID or null to clear
   * @returns {FilterVO} New filter with set category
   */
  setCategory(categoryId) {
    return this.withUpdates({ categoryId, page: 0 });
  }

  /**
   * Set search query
   * @param {string|null} query - Search query or null to clear
   * @returns {FilterVO} New filter with set search query
   */
  setSearch(query) {
    return this.withUpdates({ searchQuery: query, page: 0 });
  }

  /**
   * Set sort options
   * @param {string} sortBy - Sort field
   * @param {string} sortOrder - Sort order (asc, desc)
   * @returns {FilterVO} New filter with set sort options
   */
  setSort(sortBy, sortOrder = 'asc') {
    return this.withUpdates({ sortBy, sortOrder });
  }

  /**
   * Check if filter is active (has any non-default values)
   * @returns {boolean} True if any filter is active
   */
  isActive() {
    return !!(
      this.categoryId ||
      this.searchQuery ||
      this.priceRange ||
      this.inStock ||
      this.page > 0
    );
  }

  /**
   * Check if has active filters (excluding pagination)
   * @returns {boolean} True if has active filters
   */
  hasActiveFilters() {
    return !!(
      this.categoryId ||
      this.searchQuery ||
      this.priceRange ||
      this.inStock
    );
  }

  /**
   * Get active filter count
   * @returns {number} Number of active filters
   */
  getActiveFilterCount() {
    let count = 0;

    if (this.categoryId) count++;
    if (this.searchQuery) count++;
    if (this.priceRange) count++;
    if (this.inStock) count++;

    return count;
  }

  /**
   * Convert to plain object
   * @returns {Object} Plain object representation
   */
  toJSON() {
    return {
      categoryId: this.categoryId,
      searchQuery: this.searchQuery,
      priceRange: this.priceRange,
      sortBy: this.sortBy,
      sortOrder: this.sortOrder,
      page: this.page,
      limit: this.limit,
      inStock: this.inStock
    };
  }

  /**
   * Create from plain object
   * @param {Object} data - Plain object data
   * @returns {FilterVO} Filter instance
   */
  static fromJSON(data) {
    return new FilterVO(data);
  }
}

export default FilterVO;
