/**
 * Category API Client
 * Infrastructure layer for category API communication
 */

import api from "/core/shared/api.js';

export class CategoryAPI {
  /**
   * Get all categories (flat list)
   * @returns {Promise<Array>} Categories list
   */
  async findAll() {
    try {
      return await api.get('/categories');
    } catch (error) {
      console.error('Category API: findAll error', error);
      throw error;
    }
  }

  /**
   * Get category tree
   * @returns {Promise<Array>} Category tree
   */
  async getTree() {
    try {
      return await api.get('/categories/tree');
    } catch (error) {
      console.error('Category API: getTree error', error);
      throw error;
    }
  }

  /**
   * Get category by ID
   * @param {string} id - Category ID
   * @returns {Promise<Object>} Category data
   */
  async findById(id) {
    try {
      return await api.get(`/categories/${id}`);
    } catch (error) {
      console.error('Category API: findById error', error);
      throw error;
    }
  }

  /**
   * Get category with products
   * @param {string} id - Category ID
   * @param {Object} options - Product options
   * @returns {Promise<Object>} Category with products
   */
  async getWithProducts(id, options = {}) {
    try {
      const params = {
        limit: options.limit || 20,
        offset: options.offset || 0
      };

      // This would need a specific endpoint if available
      // For now, we'll fetch both separately
      const [category, products] = await Promise.all([
        this.findById(id),
        api.get('/products', { params: { category_id: id, ...params } })
      ]);

      return {
        ...category,
        products: products.items || products
      };
    } catch (error) {
      console.error('Category API: getWithProducts error', error);
      throw error;
    }
  }
}

// Create and export singleton instance
const categoryAPI = new CategoryAPI();

export default categoryAPI;
