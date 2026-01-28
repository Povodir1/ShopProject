/**
 * Get Product Details Use Case
 * Retrieves details of a single product
 */

import { Product } from '../../domain/product.entity.js';

export class GetProductDetailsUseCase {
  /**
   * @param {Object} productRepository - Product repository (API client)
   */
  constructor(productRepository) {
    this.productRepository = productRepository;
  }

  /**
   * Execute use case
   * @param {string} productId - Product ID
   * @returns {Promise<Product>} Product entity
   */
  async execute(productId) {
    if (!productId) {
      throw new Error('Product ID is required');
    }

    try {
      const data = await this.productRepository.findById(productId);
      return Product.fromAPI(data);
    } catch (error) {
      console.error('GetProductDetails use case error:', error);

      if (error.status === 404) {
        throw new Error('Product not found');
      }

      throw new Error(`Failed to get product details: ${error.message}`);
    }
  }
}

export default GetProductDetailsUseCase;
