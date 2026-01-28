/**
 * Search Products Use Case
 * Searches for products by query
 */

import { Product } from '../../domain/product.entity.js';

export class SearchProductsUseCase {
  /**
   * @param {Object} productRepository - Product repository (API client)
   */
  constructor(productRepository) {
    this.productRepository = productRepository;
  }

  /**
   * Execute use case
   * @param {string} query - Search query
   * @param {Object} options - Search options
   * @param {number} options.limit - Max results (default: 100)
   * @param {number} options.offset - Pagination offset (default: 0)
   * @returns {Promise<Object>} Search results with pagination info
   */
  async execute(query, options = {}) {
    if (!query || query.trim().length < 2) {
      throw new Error('Search query must be at least 2 characters');
    }

    const { limit = 100, offset = 0 } = options;

    try {
      const params = {
        q: query.trim(),
        limit,
        offset
      };

      const response = await this.productRepository.search(params);

      // Map to domain entities
      const products = Product.fromAPIList(response.items || response);

      return {
        products,
        query,
        total: response.total || products.length,
        limit,
        offset,
        hasMore: (offset || 0) + products.length < (response.total || products.length)
      };
    } catch (error) {
      console.error('SearchProducts use case error:', error);
      throw new Error(`Failed to search products: ${error.message}`);
    }
  }
}

export default SearchProductsUseCase;
