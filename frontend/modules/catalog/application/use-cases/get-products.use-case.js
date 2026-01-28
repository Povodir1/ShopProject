/**
 * Get Products Use Case
 * Retrieves a list of products with optional filtering
 */

import { Product } from '../../domain/product.entity.js';
import { FilterVO } from '../../domain/filter.value-object.js';

export class GetProductsUseCase {
  /**
   * @param {Object} productRepository - Product repository (API client)
   */
  constructor(productRepository) {
    this.productRepository = productRepository;
  }

  /**
   * Execute use case
   * @param {Object} filters - Filter options
   * @returns {Promise<Object>} Products with pagination info
   */
  async execute(filters = {}) {
    try {
      const filterVO = filters instanceof FilterVO
        ? filters
        : new FilterVO(filters);

      const params = filterVO.toQueryParams();

      const response = await this.productRepository.findAll(params);

      // Map response to domain entities
      const products = Product.fromAPIList(response.items || response);

      return {
        products,
        total: response.total || 0,
        limit: response.limit || params.limit,
        offset: response.offset || 0,
        page: filterVO.page,
        hasMore: (response.offset || 0) + products.length < (response.total || 0)
      };
    } catch (error) {
      console.error('GetProducts use case error:', error);
      throw new Error(`Failed to get products: ${error.message}`);
    }
  }
}

export default GetProductsUseCase;
