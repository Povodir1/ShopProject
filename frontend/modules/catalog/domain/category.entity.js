/**
 * Category Entity
 * Domain entity for categories with tree support
 */

export class Category {
  /**
   * @param {Object} data - Category data
   * @param {string} data.id - Category ID (UUID)
   * @param {string} data.name - Category name
   * @param {string|null} data.parent_id - Parent category ID
   * @param {Array} data.children - Child categories
   */
  constructor(data) {
    this.id = data.id;
    this.name = data.name;
    this.parentId = data.parent_id || null;
    this.children = (data.children || []).map(child => new Category(child));
  }

  /**
   * Check if category has children
   * @returns {boolean}
   */
  hasChildren() {
    return this.children.length > 0;
  }

  /**
   * Get category level in tree (0 = root)
   * @param {number} level - Current level (used internally)
   * @returns {number} Category level
   */
  getLevel(level = 0) {
    return level;
  }

  /**
   * Check if category is a root category (no parent)
   * @returns {boolean}
   */
  isRoot() {
    return !this.parentId;
  }

  /**
   * Find category by ID in tree
   * @param {string} id - Category ID to find
   * @returns {Category|null} Found category or null
   */
  findById(id) {
    if (this.id === id) {
      return this;
    }

    for (const child of this.children) {
      const found = child.findById(id);
      if (found) {
        return found;
      }
    }

    return null;
  }

  /**
   * Get all category IDs in tree
   * @returns {Array<string>} Array of category IDs
   */
  getAllIds() {
    const ids = [this.id];

    for (const child of this.children) {
      ids.push(...child.getAllIds());
    }

    return ids;
  }

  /**
   * Get path to root category
   * @param {Array} path - Current path (used internally)
   * @returns {Array<Category>} Path from root to this category
   */
  getPath(path = []) {
    path.unshift(this);

    // Note: This is simplified - in real implementation, you'd need parent reference
    // to build full path. For now, returns current category.

    return path;
  }

  /**
   * Flatten tree to array
   * @returns {Array<Category>} Flat array of all categories
   */
  flatten() {
    const categories = [this];

    for (const child of this.children) {
      categories.push(...child.flatten());
    }

    return categories;
  }

  /**
   * Convert to plain object
   * @param {boolean} includeChildren - Include children in output
   * @returns {Object} Plain object representation
   */
  toJSON(includeChildren = true) {
    const obj = {
      id: this.id,
      name: this.name,
      parent_id: this.parentId
    };

    if (includeChildren) {
      obj.children = this.children.map(child => child.toJSON(true));
    }

    return obj;
  }

  /**
   * Create Category from API response
   * @param {Object} data - API response data
   * @returns {Category} Category instance
   */
  static fromAPI(data) {
    return new Category(data);
  }

  /**
   * Create list of Categories from API response
   * @param {Array} data - Array of API response data
   * @returns {Array<Category>} Array of Category instances
   */
  static fromAPIList(data) {
    return data.map(item => Category.fromAPI(item));
  }

  /**
   * Build tree from flat category list
   * @param {Array} categories - Flat array of categories
   * @returns {Array<Category>} Tree structure
   */
  static buildTree(categories) {
    const categoryMap = new Map();
    const rootCategories = [];

    // First pass: create all category instances
    for (const cat of categories) {
      const category = new Category({
        id: cat.id,
        name: cat.name,
        parent_id: cat.parent_id,
        children: []
      });
      categoryMap.set(cat.id, category);
    }

    // Second pass: build tree structure
    for (const cat of categories) {
      const category = categoryMap.get(cat.id);

      if (!cat.parent_id) {
        rootCategories.push(category);
      } else {
        const parent = categoryMap.get(cat.parent_id);
        if (parent) {
          parent.children.push(category);
        }
      }
    }

    return rootCategories;
  }
}

export default Category;
