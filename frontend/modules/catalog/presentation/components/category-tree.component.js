/**
 * Category Tree Component
 * Displays category dropdown selector
 */

import eventBus from '/core/event-bus.js';

export class CategoryTreeComponent {
  /**
   * @param {Array<Category>} categories - Category tree
   * @param {HTMLElement} container - Container element
   * @param {Object} options - Component options
   */
  constructor(categories, container, options = {}) {
    this.categories = categories;
    this.container = container;
    this.options = {
      selectedCategoryId: null,
      showProductCount: false,
      ...options
    };
    this.element = null;
  }

  /**
   * Render the category dropdown
   * @returns {HTMLElement} Select element
   */
  render() {
    const wrapper = document.createElement('div');
    wrapper.className = 'category-dropdown';

    const label = document.createElement('label');
    label.className = 'category-dropdown-label';
    label.textContent = 'Category';
    label.setAttribute('for', 'category-select');

    const select = document.createElement('select');
    select.id = 'category-select';
    select.className = 'category-dropdown-select form-select';

    if (this.categories.length === 0) {
      const option = document.createElement('option');
      option.textContent = 'No categories available';
      option.disabled = true;
      select.appendChild(option);
    } else {
      // Add "All Categories" option
      const allOption = document.createElement('option');
      allOption.value = '';
      allOption.textContent = 'All Categories';
      allOption.selected = !this.options.selectedCategoryId;
      select.appendChild(allOption);

      // Add categories with nesting
      this.categories.forEach(category => {
        this.renderCategoryOptions(category, select, 0);
      });
    }

    wrapper.appendChild(label);
    wrapper.appendChild(select);

    // Attach event listener
    select.addEventListener('change', () => this.onCategoryChange(select));

    this.element = wrapper;
    return wrapper;
  }

  /**
   * Render category options recursively
   * @param {Category} category - Category entity
   * @param {HTMLElement} select - Select element
   * @param {number} level - Nesting level
   */
  renderCategoryOptions(category, select, level) {
    const option = document.createElement('option');
    option.value = category.id;

    // Add indentation for nested categories
    const indent = '\u00A0\u00A0\u00A0'.repeat(level);
    option.textContent = `${indent}${category.name}`;

    if (this.options.selectedCategoryId === category.id) {
      option.selected = true;
    }

    select.appendChild(option);

    // Render children
    if (category.hasChildren()) {
      category.children.forEach(child => {
        this.renderCategoryOptions(child, select, level + 1);
      });
    }
  }

  /**
   * Handle category change
   * @param {HTMLSelectElement} select - Select element
   */
  onCategoryChange(select) {
    const categoryId = select.value || null;
    const category = this.findCategory(categoryId);

    this.options.selectedCategoryId = categoryId;

    // Publish event
    eventBus.publish('catalog:category-changed', {
      categoryId: categoryId,
      category: category
    });
  }

  /**
   * Find category by ID in tree
   * @param {string} categoryId - Category ID to find
   * @returns {Category|null} Found category or null
   */
  findCategory(categoryId) {
    if (!categoryId) return null;

    for (const category of this.categories) {
      const found = this.searchInTree(category, categoryId);
      if (found) return found;
    }

    return null;
  }

  /**
   * Search for category in tree
   * @param {Category} category - Current category
   * @param {string} targetId - Target category ID
   * @returns {Category|null} Found category or null
   */
  searchInTree(category, targetId) {
    if (category.id === targetId) {
      return category;
    }

    for (const child of category.children) {
      const found = this.searchInTree(child, targetId);
      if (found) return found;
    }

    return null;
  }

  /**
   * Set selected category
   * @param {string|null} categoryId - Category ID or null to clear selection
   */
  setSelectedCategory(categoryId) {
    this.options.selectedCategoryId = categoryId;
    this.update();
  }

  /**
   * Update the component
   */
  update() {
    if (this.element && this.element.parentNode) {
      const newElement = this.render();
      this.element.parentNode.replaceChild(newElement, this.element);
      this.element = newElement;
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

export default CategoryTreeComponent;
