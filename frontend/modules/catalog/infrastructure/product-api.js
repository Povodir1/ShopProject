/**
 * Product API Client
 * Infrastructure layer for product API communication
 */

import api from '/core/shared/api.js';

export class ProductAPI {
  /**
   * Get all products with filters
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Products response
   */
  async findAll(params = {}) {
    try {
      return await api.get('/products', { params });
    } catch (error) {
      console.error('Product API: findAll error', error);
      throw error;
    }
  }

  /**
   * Get product by ID
   * @param {string} id - Product ID
   * @returns {Promise<Object>} Product data
   */
  async findById(id) {
    try {
      return await api.get(`/products/${id}`);
    } catch (error) {
      console.error('Product API: findById error', error);
      throw error;
    }
  }

  /**
   * Search products
   * @param {Object} params - Search parameters
   * @param {string} params.q - Search query
   * @param {number} params.limit - Max results
   * @param {number} params.offset - Pagination offset
   * @returns {Promise<Object>} Search results
   */
  async search(params = {}) {
    try {
      return await api.get('/products/search', { params });
    } catch (error) {
      console.error('Product API: search error', error);
      throw error;
    }
  }

  /**
   * Get products by category
   * @param {string} categoryId - Category ID
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Products response
   */
  async getByCategory(categoryId, options = {}) {
    try {
      const params = {
        category_id: categoryId,
        ...options
      };
      return await this.findAll(params);
    } catch (error) {
      console.error('Product API: getByCategory error', error);
      throw error;
    }
  }
}

// Create and export singleton instance
const productAPI = new ProductAPI();

export default productAPI;
