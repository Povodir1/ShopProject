/**
 * Get Categories Use Case
 * Retrieves category tree or flat list
 */

import { Category } from '../../domain/category.entity.js';

export class GetCategoriesUseCase {
  /**
   * @param {Object} categoryRepository - Category repository (API client)
   */
  constructor(categoryRepository) {
    this.categoryRepository = categoryRepository;
  }

  /**
   * Execute use case
   * @param {Object} options - Options
   * @param {boolean} options.tree - Return as tree structure (default: true)
   * @param {boolean} options.flat - Return as flat list
   * @returns {Promise<Array|Object>} Categories
   */
  async execute(options = {}) {
    const { tree = true, flat = false } = options;

    try {
      if (flat) {
        return await this.getFlatList();
      }

      if (tree) {
        return await this.getTree();
      }

      // Default to tree
      return await this.getTree();
    } catch (error) {
      console.error('GetCategories use case error:', error);
      throw new Error(`Failed to get categories: ${error.message}`);
    }
  }

  /**
   * Get categories as tree structure
   * @returns {Promise<Array<Category>>} Category tree
   */
  async getTree() {
    const data = await this.categoryRepository.getTree();
    return Category.fromAPIList(data);
  }

  /**
   * Get categories as flat list
   * @returns {Promise<Array<Category>>} Flat category list
   */
  async getFlatList() {
    const data = await this.categoryRepository.findAll();
    return Category.fromAPIList(data);
  }

  /**
   * Get single category by ID
   * @param {string} categoryId - Category ID
   * @returns {Promise<Category>} Category entity
   */
  async getCategoryById(categoryId) {
    if (!categoryId) {
      throw new Error('Category ID is required');
    }

    try {
      const data = await this.categoryRepository.findById(categoryId);
      return Category.fromAPI(data);
    } catch (error) {
      console.error('GetCategoryById use case error:', error);

      if (error.status === 404) {
        throw new Error('Category not found');
      }

      throw new Error(`Failed to get category: ${error.message}`);
    }
  }
}

export default GetCategoriesUseCase;
